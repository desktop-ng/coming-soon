# python imports
import os
import re
import ssl
import smtplib
import logging
import traceback
from typing import Union
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# installed imports
import requests
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

TOKEN = os.getenv("META_VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
BASE_URL = "https://graph.facebook.com/v17.0"
URL = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}",
}

app = Flask(__name__, static_folder="", template_folder="")


def send_text(message: str, recipient: str) -> Union[str, None]:
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": True, "body": message},
    }
    response = requests.post(URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        data = response.json()
        return str(data["messages"][0]["id"])
    return None


def send_email(
    receiver_email,
    subject="You're in! Welcome to Desktop 🚀",
    plaintext="Welcome to Desktop - You're on the list!",
):
    # Connection configuration
    SMTP_SERVER = os.environ.get("SMTP_HOST")  # For starttls
    PORT = 587  # For starttls
    USERNAME = os.environ.get("USERNAME")
    PASSWORD = os.environ.get("PASSWORD")

    # Message setup
    message = MIMEMultipart()
    message["Subject"] = Header(subject)
    message["From"] = Header("The Desktop Company")
    message["To"] = Header(receiver_email)

    # load HTML template
    with open("email.html", "r") as f:
        template = Template(f.read())

    # render HTML template with receiver email
    html = MIMEText(template.render(), "html")
    # add text to the message
    text = MIMEText(plaintext, "plain")
    # attach HTML and plaintext
    # message.attach(text)
    message.attach(html)

    # load image attachments
    with open("images/email-logo.png", "rb") as img_file:
        img_data = img_file.read()

    # add logo image
    logo_image = MIMEImage(img_data)
    logo_image.add_header(
        "Content-ID", "<desktop_logo>"
    )  # Add Content-ID for inline display
    logo_image.add_header("Content-Disposition", "inline", filename="logo.png")
    message.attach(logo_image)

    # add signature image
    signature_image = MIMEImage(img_data)
    signature_image.add_header(
        "Content-ID", "<signature_image>"
    )  # Add Content-ID for inline display
    signature_image.add_header(
        "Content-Disposition", "inline", filename="signature.png"
    )
    message.attach(signature_image)

    success = False  # Initialize success variable
    # Try to log in to server and send email
    try:
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.sendmail(USERNAME, receiver_email, message.as_string())
            success = True  # Set success to True on successful send
    except Exception as e:
        # Print error messages to stdout
        logger.error(traceback.format_exc())
        return success
    finally:
        return success  # Return success value


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

        # Send confirmation message via WhatsApp
        message = f"New email submitted: {email}"
        recipient = "+2349016456964"
        send_text(message, recipient)
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
