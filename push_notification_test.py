"""
Test script for Push Notification functionality
"""

from push_notifications import PushNotificationManager, store_device_token, get_user_tokens, send_realtime_notification, schedule_notification, get_user_notifications
from datetime import datetime, timedelta

def test_push_notifications():
    """Test the push notification functionality"""
    print("Testing Push Notification functionality...")
    
    # Create push notification manager
    push_manager = PushNotificationManager()
    
    # Test user ID
    user_id = 1
    
    # Test storing device token
    print("\n1. Testing device token storage...")
    success = store_device_token(user_id, "test_device_token_123", "web", "Chrome 98.0.4758.102")
    if success:
        print("✅ Device token stored successfully")
    else:
        print("❌ Failed to store device token")
    
    # Test retrieving user tokens
    print("\n2. Testing user token retrieval...")
    tokens = get_user_tokens(user_id)
    if tokens:
        print(f"✅ Retrieved {len(tokens)} token(s):")
        for token in tokens:
            print(f"   - Token: {token['device_token'][:20]}...")
            print(f"   - Type: {token['device_type']}")
            print(f"   - Browser: {token['browser_info']}")
    else:
        print("❌ No tokens found for user")
    
    # Test sending real-time notification
    print("\n3. Testing real-time notification...")
    success = send_realtime_notification(user_id, "Test Notification", "This is a test real-time notification")
    if success:
        print("✅ Real-time notification sent successfully")
    else:
        print("❌ Failed to send real-time notification")
    
    # Test scheduling notification
    print("\n4. Testing scheduled notification...")
    scheduled_time = datetime.now() + timedelta(minutes=5)
    success = schedule_notification(user_id, "Scheduled Notification", "This is a test scheduled notification", scheduled_time)
    if success:
        print("✅ Scheduled notification created successfully")
    else:
        print("❌ Failed to create scheduled notification")
    
    # Test retrieving notification history
    print("\n5. Testing notification history retrieval...")
    notifications = get_user_notifications(user_id, 10)
    if notifications:
        print(f"✅ Retrieved {len(notifications)} notification(s):")
        for notification in notifications:
            print(f"   - Title: {notification['title']}")
            print(f"   - Message: {notification['message'][:30]}...")
            print(f"   - Type: {notification['type']}")
            print(f"   - Read: {'Yes' if notification['is_read'] else 'No'}")
    else:
        print("❌ No notifications found for user")
    
    print("\n🎉 Push Notification tests completed!")

if __name__ == "__main__":
    test_push_notifications()