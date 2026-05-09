# python imports
import os
import re
import ssl
import smtplib
import logging
import traceback
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# installed imports
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info("Logging is configured.")

app = Flask(__name__, static_folder="", template_folder="")


def send_email(
    receiver_email,
    subject="You're in! Welcome to Desktop 🚀",
    plaintext="Welcome to Desktop - You're on the list!",
):
    # Connection configuration
    SMTP_SERVER = os.environ.get("SMTP_HOST")
    PORT = 587  # For starttls
    USERNAME = os.environ.get("SMTP_USERNAME")
    PASSWORD = os.environ.get("SMTP_PASSWORD")

    # Outer message for mixed content
    message = MIMEMultipart("mixed")
    message["Subject"] = Header(subject)
    message["From"] = "The Desktop Company <desktop@desktop.ng>"
    message["To"] = Header(receiver_email)

    # Build alternative part (plaintext + HTML)
    alternative = MIMEMultipart("alternative")
    alternative.attach(MIMEText(plaintext, "plain"))

    # load HTML template
    with open("email.html", "r") as f:
        template = Template(f.read())

    # Build related part (HTML + inline images)
    related = MIMEMultipart("related")
    related.attach(MIMEText(template.render(), "html"))

    # load image attachments
    with open("images/email-logo.png", "rb") as img_file:
        img_data = img_file.read()

    # add logo image
    logo_image = MIMEImage(img_data)
    logo_image.add_header("Content-ID", "<desktop_logo>")
    logo_image.add_header("Content-Disposition", "inline", filename="logo.png")
    related.attach(logo_image)

    # add signature image
    signature_image = MIMEImage(img_data)
    signature_image.add_header("Content-ID", "<signature_image>")
    signature_image.add_header("Content-Disposition", "inline", filename="signature.png")
    related.attach(signature_image)

    alternative.attach(related)
    message.attach(alternative)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.starttls(context=context)
            server.login(USERNAME, PASSWORD)
            server.sendmail(USERNAME, receiver_email, message.as_string())
        return True
    except Exception:
        logger.error(traceback.format_exc())
        return False


@app.get("/")
def index():
    logger.info("Serving index page.")
    return render_template("index.html")


@app.get("/email")
def email_page():
    logger.info("Serving email page.")
    return render_template("email.html")


@app.post("/submit-email")
def submit_email():
    try:
        data = request.form
        logger.info(f"DATA: {data}")
        email = data.get("email")

        # Basic email validation
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify(success=False, msg="Please enter a valid email."), 500

        with open("emails.txt", "a") as file:
            file.write(f"{email}\n")
        logger.info(f"Email {email} saved successfully.")

        send_email(email)
        return jsonify(success=True)

    except:
        logger.error(traceback.format_exc())
        return (
            jsonify(
                success=False, msg="An error occurred while processing your request."
            ),
            500,
        )


if __name__ == "__main__":
    logger.info("Starting Flask development server.")
    app.run(debug=True)
