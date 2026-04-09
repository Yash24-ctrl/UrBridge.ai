"""
Push Notification System for AI Resume Analyzer
Handles web and mobile push notifications, token management, and scheduling
"""

import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

# Database configuration
DATABASE = 'users.db'

class PushNotificationManager:
    """Manages push notifications for the application"""
    
    def __init__(self):
        """Initialize the push notification manager"""
        self._ensure_tables_exist()
        self._start_scheduler()
    
    def _ensure_tables_exist(self):
        """Ensure the push notification tables exist in the database"""
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            # Create push_notification_tokens table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS push_notification_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    device_token TEXT NOT NULL,
                    device_type TEXT NOT NULL,  -- 'web' or 'mobile'
                    browser_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create notifications table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,  -- 'realtime' or 'scheduled'
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scheduled_for TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error ensuring push notification tables exist: {str(e)}")
    
    def _start_scheduler(self):
        """Start the scheduler thread for sending scheduled notifications"""
        scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        scheduler_thread.start()
    
    def _scheduler_worker(self):
        """Worker function that checks for scheduled notifications"""
        while True:
            try:
                # Check for scheduled notifications that should be sent now
                self._send_scheduled_notifications()
                # Sleep for 60 seconds before checking again
                time.sleep(60)
            except Exception as e:
                print(f"Error in scheduler worker: {str(e)}")
                time.sleep(60)
    
    def _send_scheduled_notifications(self):
        """Send scheduled notifications that are due"""
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            # Get scheduled notifications that should be sent now
            now = datetime.now()
            c.execute('''
                SELECT id, user_id, title, message
                FROM notifications
                WHERE type = 'scheduled' 
                AND scheduled_for <= ?
                AND is_read = FALSE
            ''', (now,))
            
            scheduled_notifications = c.fetchall()
            
            # Mark these notifications as sent (read)
            for notification in scheduled_notifications:
                notification_id, user_id, title, message = notification
                
                # In a real implementation, you would actually send the notification here
                # For now, we'll just mark it as read
                c.execute('''
                    UPDATE notifications
                    SET is_read = TRUE
                    WHERE id = ?
                ''', (notification_id,))
            
            conn.commit()
            conn.close()
            
            # Process the notifications (in a real implementation, send them)
            for notification in scheduled_notifications:
                notification_id, user_id, title, message = notification
                print(f"Sending scheduled notification to user {user_id}: {title} - {message}")
                
        except Exception as e:
            print(f"Error sending scheduled notifications: {str(e)}")
    
    def store_device_token(self, user_id: int, device_token: str, device_type: str, browser_info: str = None) -> bool:
        """
        Store a device token for a user
        
        Args:
            user_id (int): The user's ID
            device_token (str): The device token
            device_type (str): The device type ('web' or 'mobile')
            browser_info (str): Optional browser information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            # Deactivate any existing tokens for this user and device
            c.execute('''
                UPDATE push_notification_tokens
                SET is_active = FALSE
                WHERE user_id = ? AND device_type = ?
            ''', (user_id, device_type))
            
            # Insert the new token
            c.execute('''
                INSERT INTO push_notification_tokens 
                (user_id, device_token, device_type, browser_info)
                VALUES (?, ?, ?, ?)
            ''', (user_id, device_token, device_type, browser_info))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing device token: {str(e)}")
            return False
    
    def get_user_tokens(self, user_id: int) -> List[Dict]:
        """
        Get all active tokens for a user
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            List[Dict]: List of token information
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                SELECT device_token, device_type, browser_info, created_at
                FROM push_notification_tokens
                WHERE user_id = ? AND is_active = TRUE
            ''', (user_id,))
            
            tokens = c.fetchall()
            conn.close()
            
            return [
                {
                    'device_token': token[0],
                    'device_type': token[1],
                    'browser_info': token[2],
                    'created_at': token[3]
                }
                for token in tokens
            ]
        except Exception as e:
            print(f"Error retrieving user tokens: {str(e)}")
            return []
    
    def remove_device_token(self, user_id: int, device_token: str) -> bool:
        """
        Remove a device token for a user
        
        Args:
            user_id (int): The user's ID
            device_token (str): The device token to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                UPDATE push_notification_tokens
                SET is_active = FALSE
                WHERE user_id = ? AND device_token = ?
            ''', (user_id, device_token))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing device token: {str(e)}")
            return False
    
    def send_realtime_notification(self, user_id: int, title: str, message: str) -> bool:
        """
        Send a real-time notification to a user
        
        Args:
            user_id (int): The user's ID
            title (str): The notification title
            message (str): The notification message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store notification in database
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO notifications 
                (user_id, title, message, type)
                VALUES (?, ?, ?, 'realtime')
            ''', (user_id, title, message))
            
            conn.commit()
            conn.close()
            
            # In a real implementation, you would send the actual notification here
            # For now, we'll just print it
            print(f"Sending real-time notification to user {user_id}: {title} - {message}")
            
            # Get user's active tokens and send notification to each
            tokens = self.get_user_tokens(user_id)
            for token_info in tokens:
                # In a real implementation, you would use the token to send the notification
                # through a service like Firebase Cloud Messaging (FCM)
                print(f"Would send to {token_info['device_type']} device: {token_info['device_token']}")
            
            return True
        except Exception as e:
            print(f"Error sending real-time notification: {str(e)}")
            return False
    
    def schedule_notification(self, user_id: int, title: str, message: str, scheduled_time: datetime) -> bool:
        """
        Schedule a notification to be sent at a specific time
        
        Args:
            user_id (int): The user's ID
            title (str): The notification title
            message (str): The notification message
            scheduled_time (datetime): When to send the notification
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store notification in database
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO notifications 
                (user_id, title, message, type, scheduled_for)
                VALUES (?, ?, ?, 'scheduled', ?)
            ''', (user_id, title, message, scheduled_time))
            
            conn.commit()
            conn.close()
            
            print(f"Scheduled notification for user {user_id} at {scheduled_time}: {title} - {message}")
            return True
        except Exception as e:
            print(f"Error scheduling notification: {str(e)}")
            return False
    
    def send_broadcast_notification(self, title: str, message: str) -> bool:
        """
        Send a notification to all users
        
        Args:
            title (str): The notification title
            message (str): The notification message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all users
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('SELECT id FROM users')
            users = c.fetchall()
            conn.close()
            
            # Send notification to each user
            for user in users:
                user_id = user[0]
                self.send_realtime_notification(user_id, title, message)
            
            return True
        except Exception as e:
            print(f"Error sending broadcast notification: {str(e)}")
            return False
    
    def get_user_notifications(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        Get notification history for a user
        
        Args:
            user_id (int): The user's ID
            limit (int): Maximum number of notifications to return
            
        Returns:
            List[Dict]: List of notifications
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                SELECT id, title, message, type, is_read, created_at, scheduled_for
                FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            notifications = c.fetchall()
            conn.close()
            
            return [
                {
                    'id': notification[0],
                    'title': notification[1],
                    'message': notification[2],
                    'type': notification[3],
                    'is_read': bool(notification[4]),
                    'created_at': notification[5],
                    'scheduled_for': notification[6]
                }
                for notification in notifications
            ]
        except Exception as e:
            print(f"Error retrieving user notifications: {str(e)}")
            return []
    
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read
        
        Args:
            notification_id (int): The notification ID
            user_id (int): The user's ID (for security check)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                UPDATE notifications
                SET is_read = TRUE
                WHERE id = ? AND user_id = ?
            ''', (notification_id, user_id))
            
            conn.commit()
            conn.close()
            return c.rowcount > 0
        except Exception as e:
            print(f"Error marking notification as read: {str(e)}")
            return False
    
    def get_unread_notification_count(self, user_id: int) -> int:
        """
        Get the count of unread notifications for a user
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            int: Count of unread notifications
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('''
                SELECT COUNT(*) 
                FROM notifications
                WHERE user_id = ? AND is_read = FALSE
            ''', (user_id,))
            
            count = c.fetchone()[0]
            conn.close()
            
            return count
        except Exception as e:
            print(f"Error getting unread notification count: {str(e)}")
            return 0

# Global instance
push_manager = PushNotificationManager()

# Convenience functions
def store_device_token(user_id: int, device_token: str, device_type: str, browser_info: str = None) -> bool:
    """
    Store a device token for a user
    
    Args:
        user_id (int): The user's ID
        device_token (str): The device token
        device_type (str): The device type ('web' or 'mobile')
        browser_info (str): Optional browser information
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_manager.store_device_token(user_id, device_token, device_type, browser_info)

def get_user_tokens(user_id: int) -> List[Dict]:
    """
    Get all active tokens for a user
    
    Args:
        user_id (int): The user's ID
        
    Returns:
        List[Dict]: List of token information
    """
    return push_manager.get_user_tokens(user_id)

def remove_device_token(user_id: int, device_token: str) -> bool:
    """
    Remove a device token for a user
    
    Args:
        user_id (int): The user's ID
        device_token (str): The device token to remove
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_manager.remove_device_token(user_id, device_token)

def send_realtime_notification(user_id: int, title: str, message: str) -> bool:
    """
    Send a real-time notification to a user
    
    Args:
        user_id (int): The user's ID
        title (str): The notification title
        message (str): The notification message
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_manager.send_realtime_notification(user_id, title, message)

def schedule_notification(user_id: int, title: str, message: str, scheduled_time: datetime) -> bool:
    """
    Schedule a notification to be sent at a specific time
    
    Args:
        user_id (int): The user's ID
        title (str): The notification title
        message (str): The notification message
        scheduled_time (datetime): When to send the notification
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_manager.schedule_notification(user_id, title, message, scheduled_time)

def send_broadcast_notification(title: str, message: str) -> bool:
    """
    Send a notification to all users
    
    Args:
        title (str): The notification title
        message (str): The notification message
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_manager.send_broadcast_notification(title, message)

def get_user_notifications(user_id: int, limit: int = 50) -> List[Dict]:
    """
    Get notification history for a user
    
    Args:
        user_id (int): The user's ID
        limit (int): Maximum number of notifications to return
        
    Returns:
        List[Dict]: List of notifications
    """
    return push_manager.get_user_notifications(user_id, limit)

def mark_notification_as_read(notification_id: int, user_id: int) -> bool:
    """
    Mark a notification as read
    
    Args:
        notification_id (int): The notification ID
        user_id (int): The user's ID (for security check)
        
    Returns:
        bool: True if successful, False otherwise
    """
    return push_manager.mark_notification_as_read(notification_id, user_id)

def get_unread_notification_count(user_id: int) -> int:
    """
    Get the count of unread notifications for a user
    
    Args:
        user_id (int): The user's ID
        
    Returns:
        int: Count of unread notifications
    """
    return push_manager.get_unread_notification_count(user_id)