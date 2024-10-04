# utils.py
from flask_mail import Mail, Message
from flask import current_app

def send_verification_email(email, token):
    mail = current_app.extensions.get('mail')
    if not mail:
        print("Mail extension not initialized.")
        return
    
    msg = Message(
        "Email Verification", 
        recipients=[email], 
        html=f"Please verify your email by clicking the link: http://localhost:5000/verify/{token}", 
        sender="noreply@flask.com"
    )
    # msg.body = f"Please verify your email by clicking the link: http://localhost:5000/verify/{token}"
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")
