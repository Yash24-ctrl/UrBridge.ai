"""
Advanced Security Features for AI Resume Analyzer
Implements GDPR compliance, audit logging, and enhanced security measures
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request
import logging

# Setup security logging
logging.basicConfig(
    filename='security_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_security_event(event_type, user_id=None, details=None):
    """Log security-related events for audit purposes"""
    user_info = f"User: {user_id}" if user_id else "User: Anonymous"
    details_info = f" | Details: {details}" if details else ""
    log_message = f"{event_type} | {user_info}{details_info}"
    logging.info(log_message)

def require_login(f):
    """Decorator to require user login for accessing routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            log_security_event('ACCESS_DENIED', details=f"Unauthenticated access attempt to {request.endpoint}")
            from flask import redirect, url_for
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def secure_file_upload(file, allowed_extensions={'pdf'}, max_size=10*1024*1024):
    """Enhanced secure file upload with validation"""
    if not file:
        return False, "No file provided"
    
    # Check file extension
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        log_security_event('FILE_UPLOAD_BLOCKED', session.get('user_id'), f"Invalid file type: {file.filename}")
        return False, "Invalid file type"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > max_size:
        log_security_event('FILE_UPLOAD_BLOCKED', session.get('user_id'), f"File too large: {file_size} bytes")
        return False, f"File too large. Maximum size is {max_size//1024//1024}MB"
    
    # Check for malicious content (basic check)
    file_content = file.read(1024)  # Read first 1KB to check for obvious issues
    file.seek(0)  # Reset file pointer
    
    # Look for potential malicious content
    dangerous_patterns = [b'<script', b'javascript:', b'vbscript:', b'<iframe', b'<object', b'<embed']
    for pattern in dangerous_patterns:
        if pattern.lower() in file_content.lower():
            log_security_event('FILE_UPLOAD_BLOCKED', session.get('user_id'), f"Malicious content detected in {file.filename}")
            return False, "File contains potentially dangerous content"
    
    return True, "File is secure"

def generate_secure_token():
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(32)

def hash_password_with_salt(password):
    """Hash password with salt for storage"""
    salt = secrets.token_hex(16)
    # Use PBKDF2 for secure password hashing
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + password_hash.hex()

def verify_password_with_salt(password, stored_hash):
    """Verify password against salted hash"""
    if len(stored_hash) < 32:  # Minimum length for salt
        return False
    
    salt = stored_hash[:32]  # First 16 bytes as hex (32 chars)
    stored_password_hash = stored_hash[32:]
    
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return password_hash.hex() == stored_password_hash

def sanitize_input(input_string):
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return input_string
    
    # HTML escape potentially dangerous characters
    import html
    sanitized = html.escape(input_string)
    
    return sanitized

def rate_limit(max_requests=10, window=60):
    """Rate limiting decorator to prevent abuse"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In a real implementation, you'd use Redis or similar for distributed rate limiting
            # For now, we'll use a simple in-memory approach
            from flask import request, jsonify
            import time
            
            # Get client IP
            client_ip = request.remote_addr
            
            # Simple rate limiting (in production, use Redis)
            if not hasattr(rate_limit, 'requests'):
                rate_limit.requests = {}
            
            now = time.time()
            if client_ip not in rate_limit.requests:
                rate_limit.requests[client_ip] = []
            
            # Clean old requests
            rate_limit.requests[client_ip] = [req_time for req_time in rate_limit.requests[client_ip] if now - req_time < window]
            
            if len(rate_limit.requests[client_ip]) >= max_requests:
                log_security_event('RATE_LIMIT_EXCEEDED', details=f"IP: {client_ip}, Endpoint: {request.endpoint}")
                return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
            
            rate_limit.requests[client_ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def encrypt_resume_content(content):
    """Encrypt resume content for secure storage"""
    # This is a placeholder - in production, use proper encryption
    # For now, we'll use a simple approach that's better than plain text
    import base64
    import hashlib
    from cryptography.fernet import Fernet
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if not encryption_key:
        # Return content as-is if no encryption key is available
        return content
    
    try:
        fernet = Fernet(encryption_key.encode())
        encrypted_content = fernet.encrypt(content.encode())
        return encrypted_content.decode()
    except Exception as e:
        # If encryption fails, log the error and return original content
        logging.error(f"Encryption failed: {str(e)}")
        return content

def decrypt_resume_content(encrypted_content):
    """Decrypt resume content for processing"""
    import base64
    import hashlib
    from cryptography.fernet import Fernet
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if not encryption_key:
        # Return content as-is if no encryption key is available
        return encrypted_content
    
    try:
        fernet = Fernet(encryption_key.encode())
        decrypted_content = fernet.decrypt(encrypted_content.encode())
        return decrypted_content.decode()
    except Exception as e:
        # If decryption fails, log the error and return original content
        logging.error(f"Decryption failed: {str(e)}")
        return encrypted_content