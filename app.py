import re
import logging
import traceback
from flask import Flask, render_template, request, jsonify

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info("Logging is configured.")

app = Flask(__name__, static_folder="", template_folder="")


@app.get("/")
def index():
    logger.info("Serving index page.")
    return render_template("index.html")


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
