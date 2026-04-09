"""
Email Notification Module
Integrate with your existing authentication system by:
1. Calling send_login_notification() after successful authentication
2. Calling send_new_user_notification() for first-time logins
3. Setting EMAIL_* environment variables in your .env file
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Email Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_login_notification(user_email, user_name, ip_address=None):
    """
    Send notification email for successful login
    Call this after successful authentication in your existing login flow
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = user_email
        msg['Subject'] = "Security Alert: New Login to Your Account"
        
        body = f"""
        Hello {user_name},
        
        We noticed a new login to your account.
        
        Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Location: {ip_address if ip_address else 'Unknown'}
        
        If this was you, you can disregard this email. If you suspect unauthorized access,
        please change your password immediately.
        
        Best regards,
        Your Security Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send login notification: {str(e)}")
        return False

def send_new_user_notification(user_email, user_name):
    """
    Send welcome email for new user registration
    Call this after creating a new user in your existing registration flow
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = user_email
        msg['Subject'] = "Welcome to Our Platform!"
        
        body = f"""
        Hi {user_name},
        
        Welcome to our platform! We're excited to have you on board.
        
        Your account has been successfully created. You can now access all our features.
        
        If you have any questions, feel free to reach out to our support team.
        
        Best regards,
        The Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send new user notification: {str(e)}")
        return False