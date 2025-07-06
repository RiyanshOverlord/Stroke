from flask_mail import Message
from flask import url_for, current_app, render_template
from itsdangerous import URLSafeTimedSerializer
from app import mail

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def generate_token(email):
    s = get_serializer()
    return s.dumps(email, salt='password-reset-salt')

def verify_token(token, expiration=3600):
    try:
        s = get_serializer()
        return s.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None

def send_reset_email(email, name, reset_url):
    subject = "Password Reset Request"
    body = f"""
Hi {name},

You requested a password reset. Click the link below to reset your password:
{reset_url}

If you did not make this request, please ignore this email.

Regards,
Your App Team
"""
    msg = Message(subject, recipients=[email], body=body)
    mail.send(msg)
