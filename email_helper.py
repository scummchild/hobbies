"""Wrapper to simplify the calls to smtp mail"""

import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SSL_PORT = 465

def send_email(smtp_server: str,
               sender_email: str,
               sender_email_password: str,
               receiver_email: str,
               message_subject: str,
               message_plain_text: str = None,
               message_html: str = None):
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = message_subject

    if message_plain_text:
        message.attach(MIMEText(message_plain_text, "plain"))

    if message_html:
        message.attach(MIMEText(message_html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, SSL_PORT, context=context) as server:
        server.login(sender_email, sender_email_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
