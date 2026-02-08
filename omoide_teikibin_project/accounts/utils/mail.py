import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.core.mail import send_mail
from django.conf import settings

def send_token_mail(subject, message, to_email):
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])

"""
def send_token_mail(subject, message, to_email):
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587

    from_email = 'keigo2680@gmail.com'
    app_password = 'rxzf tjlx jrdy tmpu'  # アプリパスワード

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain', 'utf-8'))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(from_email, app_password)
        server.send_message(msg)
"""