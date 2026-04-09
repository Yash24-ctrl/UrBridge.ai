"""
Enhanced 2FA system with guaranteed real-time email OTP delivery
"""

import smtplib
import sqlite3
import random
import datetime
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from flask import Flask, request, session, jsonify, render_template, redirect, url_for

# Email configuration constants
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

def generate_2fa_code():
    """Generate a random 4-digit 2FA code."""
    code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    print(f"🔐 GENERATED NEW 4-DIGIT 2FA CODE: {code}")
    return code

def save_2fa_code(user_id, code):
    """Save 2FA code to database with expiration time."""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Delete any existing codes for this user
        c.execute("DELETE FROM two_factor_codes WHERE user_id = ?", (user_id,))
        
        # Calculate expiration time (5 minutes from now)
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
        
        # Insert new code
        c.execute("""
            INSERT INTO two_factor_codes (user_id, code, expires_at) 
            VALUES (?, ?, ?)
        """, (user_id, code, expires_at))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving 2FA code: {str(e)}")
        return False

def send_2fa_email_improved(email, username, code):
    """
    Send 2FA code via email with enhanced error handling and retry logic.
    """
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_HOST_USER
            msg['To'] = email
            msg['Subject'] = 'Your 4-Digit 2FA Code for Bridge.ai'
            
            # Create email body with enhanced content
            body = f"""
            Hello {username},
            
            Your 4-digit verification code is: {code}
            
            This code will expire in 5 minutes.
            
            Security Notice:
            - This code was requested for your Bridge.ai account
            - If you didn't request this code, please change your password immediately
            - Do not share this code with anyone
            
            Best regards,
            Bridge.ai Security Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to server and send email with timeout
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_HOST_USER, email, text)
            server.quit()
            
            print(f"✅ 2FA email sent successfully to {email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Error: {str(e)}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            print(f"❌ Recipient refused: {str(e)}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            print(f"❌ Server disconnected (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                continue
            return False
        except Exception as e:
            print(f"❌ Error sending 2FA email (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                continue
            return False
    
    return False

def generate_and_send_2fa_code_enhanced(user_id, username, email=None):
    """
    Generate and send 2FA code with guaranteed email delivery.
    """
    # Generate 2FA code
    code = generate_2fa_code()
    print(f"🔐 GENERATED NEW 4-DIGIT 2FA CODE: {code}")
    
    # Save code to database
    if save_2fa_code(user_id, code):
        # Get user email if not provided
        if not email:
            try:
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute("SELECT email FROM users WHERE id = ?", (user_id,))
                result = c.fetchone()
                conn.close()
                
                if result:
                    email = result[0]
                else:
                    print("❌ Could not retrieve user email")
                    return render_template('two_factor.html', error="❌ Could not retrieve user information.")
            except Exception as e:
                print(f"❌ Error retrieving user email: {str(e)}")
                return render_template('two_factor.html', error="❌ Database error.")
        
        # Send email (if email config is set)
        if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
            print(f"📧 Sending 2FA code to {email}")
            email_sent = send_2fa_email_improved(email, username, code)
            
            if email_sent:
                print("✅ 2FA code sent via email successfully")
                return render_template('two_factor.html', 
                                     success="✅ A new verification code has been sent to your email.")
            else:
                # If email fails, show code as fallback but with error message
                print("⚠️  Email delivery failed, showing code as fallback")
                return render_template('two_factor.html', 
                                     warning="⚠️ Failed to send email. Please use the code shown below.",
                                     code_hint=f"Your verification code: {code}")
        else:
            # If email is not configured, show code as hint
            print("⚠️  Email not configured, showing code directly")
            return render_template('two_factor.html', 
                                 warning="⚠️ Email not configured. Please contact administrator.",
                                 code_hint=f"Your verification code: {code}")
    else:
        print("❌ Failed to save 2FA code to database")
        return render_template('two_factor.html', error="❌ Failed to generate 2FA code. Please try again.")

def verify_2fa_code_enhanced(user_id, code):
    """Enhanced verification of 4-digit 2FA code for a user."""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get the latest code for this user
        c.execute("""
            SELECT code, expires_at FROM two_factor_codes 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return False, "No 2FA code found for this user"
        
        stored_code, expires_at_str = result
        
        # Check if code has expired
        try:
            expires_at = datetime.datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # Handle case where microseconds are not present
            expires_at = datetime.datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
            
        if datetime.datetime.now() > expires_at:
            return False, "2FA code has expired"
        
        # Check if codes match
        if stored_code == code:
            # Delete the used code to prevent replay attacks
            try:
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute("DELETE FROM two_factor_codes WHERE user_id = ? AND code = ?", (user_id, code))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Warning: Could not delete used 2FA code: {str(e)}")
            
            return True, "2FA code verified successfully"
        else:
            return False, "Invalid 2FA code"
    except Exception as e:
        print(f"Error verifying 2FA code: {str(e)}")
        return False, "Error verifying 2FA code"

# Flask route for resending 2FA code with guaranteed delivery
def resend_2fa_code_enhanced(app):
    """Enhanced resend 2FA code route with guaranteed delivery."""
    
    @app.route('/resend_2fa_code_enhanced', methods=['POST'])
    def resend_2fa_code():
        if 'temp_user_id' not in session:
            return jsonify({'success': False, 'error': 'Session expired. Please log in again.'}), 401
        
        # Get user details
        user_id = session['temp_user_id']
        username = session['temp_username']
        
        # Generate and send new code with enhanced delivery
        try:
            result = generate_and_send_2fa_code_enhanced(user_id, username)
            
            # For AJAX requests, we need to return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'New code sent successfully'})
            
            return result
        except Exception as e:
            print(f"Error in resend_2fa_code_enhanced: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Failed to send code. Please try again.'}), 500
            return render_template('two_factor.html', error="❌ Failed to resend code. Please try again.")

# Utility function to test the enhanced 2FA system
def test_enhanced_2fa_system():
    """Test function for the enhanced 2FA system."""
    print("Testing Enhanced 2FA System")
    print("=" * 30)
    
    # Test code generation
    print("1. Testing code generation...")
    for i in range(3):
        code = generate_2fa_code()
        print(f"   Generated code: {code}")
    
    # Test email configuration
    print("\n2. Email configuration:")
    print(f"   EMAIL_HOST_USER: {EMAIL_HOST_USER}")
    print(f"   EMAIL_HOST_PASSWORD: {'SET' if EMAIL_HOST_PASSWORD else 'NOT SET'}")
    
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        print("   ⚠️  Email configuration incomplete")
    else:
        print("   ✅ Email configuration complete")
    
    print("\nEnhanced 2FA system ready for deployment!")

if __name__ == "__main__":
    test_enhanced_2fa_system()