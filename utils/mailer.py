import smtplib
import os
from email.message import EmailMessage

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email(subject: str, body: str, to: str):
    if not EMAIL_USER or not EMAIL_PASS:
        print("⚠️ Email credentials not set")
        return

    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
