"""
Data Encryption Module for AI Resume Analyzer
Implements Fernet AES encryption for sensitive data as per Pseudonymization Standard
"""

import os
from cryptography.fernet import Fernet
from hashlib import sha256
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get encryption key from environment variable
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

# Initialize Fernet instance if key exists
fernet = None
if ENCRYPTION_KEY:
    try:
        fernet = Fernet(ENCRYPTION_KEY.encode())
    except Exception as e:
        print(f"Warning: Invalid encryption key format: {e}")
        print("Please generate a proper Fernet key using: Fernet.generate_key()")

def generate_encryption_key():
    """Generate a new encryption key for Fernet"""
    return Fernet.generate_key().decode()

def encrypt_data(data):
    """Encrypt sensitive data using Fernet AES encryption"""
    if not fernet or not data:
        return data
    try:
        if isinstance(data, str):
            data = data.encode()
        encrypted_data = fernet.encrypt(data)
        return encrypted_data.decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return data

def decrypt_data(encrypted_data):
    """Decrypt sensitive data using Fernet AES encryption"""
    if not fernet or not encrypted_data:
        return encrypted_data
    try:
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_data

def hash_identifier(identifier):
    """Hash user identifiers using SHA-256 as per Pseudonymization Standard"""
    if not identifier:
        return identifier
    try:
        return sha256(identifier.encode()).hexdigest()
    except Exception as e:
        print(f"Hashing error: {e}")
        return identifier

def anonymize_resume_data(resume_data):
    """Anonymize resume data by removing PII as per Data Minimization Policy"""
    if not resume_data or not isinstance(resume_data, dict):
        return resume_data
    
    anonymized_data = resume_data.copy()
    
    # Remove PII fields that should not be stored
    pii_fields = ['name', 'email', 'phone', 'address', 'personal_info']
    for field in pii_fields:
        if field in anonymized_data:
            del anonymized_data[field]
    
    return anonymized_data