import logging
import smtplib
import threading
from email.message import EmailMessage

from app.config import Config


def _one_line(text):
    return " ".join((text or "").split())


def _send(doc):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"New portfolio message from {_one_line(doc['name'])}"[:200]
        msg["From"] = Config.SMTP_FROM or Config.SMTP_USER
        msg["To"] = Config.CONTACT_RECEIVER
        msg["Reply-To"] = doc["email"]  # already validated, cannot contain line breaks
        msg.set_content(f"From: {doc['name']} <{doc['email']}>\n\n{doc['message']}")
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            if Config.SMTP_USER:
                smtp.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            smtp.send_message(msg)
    except Exception:
        # The message is already saved in MongoDB, so an email problem must not break the form.
        logging.exception("Could not send contact email")


def send_contact_email(doc):
    if not (Config.SMTP_HOST and Config.CONTACT_RECEIVER):
        return
    threading.Thread(target=_send, args=(doc,), daemon=True).start()
