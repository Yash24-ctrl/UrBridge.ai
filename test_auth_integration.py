#!/usr/bin/env python3
"""
Test script for authentication integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_auth_modules():
    """Test that authentication modules can be imported"""
    try:
        # Test Google auth module
        from auth.google import google_login, google_callback
        print("✓ Google authentication module imported successfully")
        
        # Test LinkedIn auth module
        from auth.linkedin import linkedin_login, linkedin_callback
        print("✓ LinkedIn authentication module imported successfully")
        
        # Test email notification module
        from mail.notify import send_login_notification, send_new_user_notification
        print("✓ Email notification module imported successfully")
        
        print("\n🎉 All authentication modules imported successfully!")
        print("\nNext steps:")
        print("1. Create a .env file with your OAuth credentials")
        print("2. Run 'pip install -r requirements.txt' to install dependencies")
        print("3. Restart your Flask application")
        print("4. Test the new authentication features")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that all modules are correctly installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_auth_modules()