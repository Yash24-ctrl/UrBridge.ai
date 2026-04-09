"""
Script to generate secure keys for the AI Resume Analyzer application
"""
import secrets
from cryptography.fernet import Fernet

def generate_keys():
    print("# AI Resume Analyzer - Secure Key Generator")
    print("#")
    print("# This script will generate secure keys for your .env file")
    print("#")
    print("# After running this script, copy the values below to your .env file:")
    print("#")
    
    # Generate Fernet encryption key
    fernet_key = Fernet.generate_key().decode()
    print(f"ENCRYPTION_KEY={fernet_key}")
    
    # Generate secret key
    secret_key = secrets.token_urlsafe(32)
    print(f"SECRET_KEY={secret_key}")
    
    # Generate JWT secret
    jwt_secret = secrets.token_urlsafe(32)
    print(f"JWT_SECRET={jwt_secret}")
    
    print()
    print("# After updating your .env file, restart your application")
    print("# Remember to keep your .env file secure and never commit it to version control")

if __name__ == "__main__":
    generate_keys()