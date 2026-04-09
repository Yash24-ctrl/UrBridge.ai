#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_vars():
    """Test that required environment variables are set"""
    print("Testing environment variables...")
    
    # Test Google OAuth credentials
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    print(f"GOOGLE_CLIENT_ID: {google_client_id}")
    print(f"GOOGLE_CLIENT_SECRET: {'*' * len(google_client_secret) if google_client_secret else None}")
    
    if not google_client_id or google_client_id == "your_google_client_id_here":
        print("❌ Google OAuth credentials not properly configured")
        print("   Please set your actual GOOGLE_CLIENT_ID in the .env file")
    else:
        print("✓ Google OAuth credentials found")
    
    # Test LinkedIn OAuth credentials
    linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID")
    linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    
    print(f"LINKEDIN_CLIENT_ID: {linkedin_client_id}")
    print(f"LINKEDIN_CLIENT_SECRET: {'*' * len(linkedin_client_secret) if linkedin_client_secret else None}")
    
    if not linkedin_client_id or linkedin_client_id == "your_linkedin_client_id_here":
        print("❌ LinkedIn OAuth credentials not properly configured")
        print("   Please set your actual LINKEDIN_CLIENT_ID in the .env file")
    else:
        print("✓ LinkedIn OAuth credentials found")
    
    # Test email configuration
    email_host = os.getenv("EMAIL_HOST")
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    
    print(f"EMAIL_HOST: {email_host}")
    print(f"EMAIL_USER: {email_user}")
    print(f"EMAIL_PASS: {'*' * len(email_pass) if email_pass else None}")
    
    if not email_pass or email_pass == "your_app_password_here":
        print("⚠️  Email password not properly configured (optional for testing)")
    else:
        print("✓ Email configuration found")

if __name__ == "__main__":
    test_env_vars()