#!/usr/bin/env python3
"""
Simple test to verify resend OTP functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import generate_2fa_code, save_2fa_code

def test_resend_logic():
    """Test the core logic for resending OTP codes"""
    print("Testing resend OTP logic...")
    
    # Test user ID
    user_id = 999999
    
    # Generate first code
    print("\n1. Generating first OTP code...")
    first_code = generate_2fa_code()
    print(f"First code: {first_code}")
    
    # Save first code
    save_result1 = save_2fa_code(user_id, first_code)
    print(f"First code save result: {save_result1}")
    
    # Generate second code (simulating resend)
    print("\n2. Generating second OTP code (simulating resend)...")
    second_code = generate_2fa_code()
    print(f"Second code: {second_code}")
    
    # Save second code (this should replace the first)
    save_result2 = save_2fa_code(user_id, second_code)
    print(f"Second code save result: {save_result2}")
    
    # Verify codes are different
    if first_code != second_code:
        print("✅ Success! Generated two different codes as expected")
        print(f"   First:  {first_code}")
        print(f"   Second: {second_code}")
    else:
        print("❌ Error! Both codes are the same")
        return False
    
    # Verify both saves succeeded
    if save_result1 and save_result2:
        print("✅ Both codes were saved successfully")
    else:
        print("❌ Error saving codes")
        return False
    
    print("\n🎉 All tests passed! Resend functionality logic is correct.")
    return True

if __name__ == "__main__":
    test_resend_logic()