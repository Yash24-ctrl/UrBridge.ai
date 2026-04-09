"""
AI Resume Analyzer - Usage Guide & Troubleshooting
==================================================

This guide explains how to use the application and troubleshoot common issues.
"""

def print_usage_guide():
    print("=" * 60)
    print("AI RESUME ANALYZER - USAGE GUIDE")
    print("=" * 60)
    
    print("\n🎯 MAIN FEATURES:")
    print("• Resume Analysis (PDF upload or manual input)")
    print("• Job Matching (Compare resume to job descriptions)")
    print("• Career Roadmap Generation")
    print("• Performance Analytics")
    print("• History Tracking")
    
    print("\n🔐 AUTHENTICATION FLOW:")
    print("1. Register → Complete Profile → Watch Video Tutorial → Access App")
    print("2. Login → Watch Video Tutorial (if not seen) → Access App")
    print("3. Social Login (Google/LinkedIn) → Complete Profile (if new) → Watch Tutorial → Access App")
    
    print("\n📋 REQUIRED PROFILE INFORMATION:")
    print("- First Name")
    print("- Last Name") 
    print("- Phone Number")
    print("- (Bio is optional)")
    
    print("\n🔄 APPLICATION FLOW AFTER LOGIN:")
    print("After logging in, you will be redirected to:")
    print("1. Profile page (if profile is incomplete)")
    print("2. Video tutorial (if not completed yet)")
    print("3. Main analyzer page (if everything is complete)")
    
    print("\n🔍 AVAILABLE PAGES:")
    print("🏠 Home: /")
    print("🔐 Login: /login")
    print("📝 Register: /register") 
    print("👤 Profile: /profile")
    print("🎥 Video Tutorial: /how-it-works-video")
    print("📄 PDF Upload: /pdf_upload")
    print("✍️ Manual Input: /manual_input")
    print("📊 Analyzer: /analyzer")
    print("💼 Job Match: /jobmatch")
    print("📈 Results: /analyzer/results")
    print("📚 History: /history")
    print("🗺️ Roadmap: /roadmap")
    print("💡 Guest Analyzer: /guest/analyzer")
    
    print("\n⚠️ TROUBLESHOOTING LOGIN ISSUES:")
    print("Q: Why does the login page reload without error?")
    print("A: Check your username/password. Valid users in DB:")
    
    # Show sample users
    import sqlite3
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, username FROM users LIMIT 5")
        users = c.fetchall()
        conn.close()
        
        for user in users:
            print(f"   - ID: {user[0]}, Username: '{user[1]}'")
    except Exception as e:
        print(f"   Could not connect to database: {e}")
    
    print("\nQ: Why can't I access analyzer after login?")
    print("A: You may need to:")
    print("   1. Complete your profile (first name, last name, phone)")
    print("   2. Watch the mandatory video tutorial")
    print("   3. Make sure your session hasn't expired")
    
    print("\n💡 TIPS:")
    print("• Complete your profile immediately after registration")
    print("• Watch the video tutorial to unlock full features")
    print("• Use 'guest/analyzer' to try features without registering")
    print("• Your session lasts 24 hours")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_usage_guide()