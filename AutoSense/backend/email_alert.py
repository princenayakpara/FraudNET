import smtplib
from email.message import EmailMessage
import os

EMAIL = os.getenv("EMAIL_USER")
APP_PASSWORD = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("ALERT_TO")

def send_alert(message):
    msg = EmailMessage()
    msg.set_content(message)
    msg["Subject"] = "🚨 AutoSense System Health Alert"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(msg)
