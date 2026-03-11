import smtplib
from email.mime.text import MIMEText
from config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

FROM_EMAIL = "no-reply@scraftil.ru"

def send_email(to: str, subject: str, body: str):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, [to], msg.as_string())
