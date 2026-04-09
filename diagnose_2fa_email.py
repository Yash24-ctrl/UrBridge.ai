#!/usr/bin/env python3
"""
Diagnostic script for 2FA email functionality
"""

import os
import sys
import sqlite3
from app import (
    send_2fa_email, 
    EMAIL_HOST_USER, 
    EMAIL_HOST_PASSWORD, 
    EMAIL_HOST, 
    EMAIL_PORT, 
    EMAIL_USE_TLS,
    generate_2fa_code
)

def check_email_config():
    """Check email configuration"""
    print("=== Email Configuration Check ===")
    
    print(f"EMAIL_HOST: {EMAIL_HOST}")
    print(f"EMAIL_PORT: {EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(EMAIL_HOST_PASSWORD) if EMAIL_HOST_PASSWORD else 'NOT SET'}")
    
    issues = []
    
    if not EMAIL_HOST_USER:
        issues.append("❌ EMAIL_HOST_USER is not set")
    
    if not EMAIL_HOST_PASSWORD:
        issues.append("❌ EMAIL_HOST_PASSWORD is not set")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ All email configuration variables are set")
        return True

def test_code_generation():
    """Test OTP code generation"""
    print("\n=== OTP Code Generation Test ===")
    
    codes = []
    for i in range(5):
        code = generate_2fa_code()
        codes.append(code)
        print(f"Generated code {i+1}: {code}")
    
    # Check if codes are different
    unique_codes = set(codes)
    if len(unique_codes) == len(codes):
        print("✅ All generated codes are unique")
    else:
        print("⚠️  Some codes are duplicated")
    
    return codes

def test_email_sending():
    """Test email sending functionality"""
    print("\n=== Email Sending Test ===")
    
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        print("❌ Cannot test email sending without credentials")
        return False
    
    test_code = generate_2fa_code()
    test_username = "TestUser"
    
    print(f"Sending test email to: {EMAIL_HOST_USER}")
    print(f"Test code: {test_code}")
    
    try:
        result = send_2fa_email(EMAIL_HOST_USER, test_username, test_code)
        if result:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Failed to send email")
            return False
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False

def check_database_schema():
    """Check if database schema is correct for 2FA"""
    print("\n=== Database Schema Check ===")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if two_factor_codes table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='two_factor_codes'")
        result = c.fetchone()
        
        if result:
            print("✅ two_factor_codes table exists")
            
            # Check table structure
            c.execute("PRAGMA table_info(two_factor_codes)")
            columns = c.fetchall()
            
            print("Table structure:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Check if there are any existing codes
            c.execute("SELECT COUNT(*) FROM two_factor_codes")
            count = c.fetchone()[0]
            print(f"Number of existing codes: {count}")
        else:
            print("❌ two_factor_codes table does not exist")
            
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def main():
    """Main diagnostic function"""
    print("2FA Email Functionality Diagnostic Tool")
    print("=" * 40)
    
    # Check if we're running in the right directory
    if not os.path.exists('app.py') or not os.path.exists('users.db'):
        print("❌ Please run this script from the project root directory")
        print("   Required files: app.py, users.db")
        sys.exit(1)
    
    # Run all checks
    config_ok = check_email_config()
    codes = test_code_generation()
    db_ok = check_database_schema()
    
    if config_ok:
        email_ok = test_email_sending()
        
        if email_ok:
            print("\n🎉 All tests passed! Real-time email OTP should be working.")
            print("📧 Check your inbox for the test email.")
        else:
            print("\n💥 Email test failed!")
            print("🔧 Please check your email configuration.")
    else:
        print("\n📝 Please set the required email environment variables:")
        print("   EMAIL_HOST_USER=your-email@example.com")
        print("   EMAIL_HOST_PASSWORD=your-email-password")

if __name__ == "__main__":
    main()