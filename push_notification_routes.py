"""
Push Notification Routes for AI Resume Analyzer
Provides Flask routes for push notification functionality
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from functools import wraps
from push_notifications import store_device_token, get_user_tokens, remove_device_token, send_realtime_notification, schedule_notification, send_broadcast_notification, get_user_notifications, mark_notification_as_read, get_unread_notification_count
from datetime import datetime, timedelta
import json

def require_login(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def register_push_notification_routes(app):
    """Register all push notification routes with the Flask app"""
    
    @app.route('/api/notifications/token', methods=['POST'])
    @require_login
    def register_device_token():
        """Register a device token for push notifications"""
        try:
            data = request.get_json()
            
            if not data or 'device_token' not in data or 'device_type' not in data:
                return jsonify({'error': 'Device token and type are required'}), 400
            
            device_token = data['device_token']
            device_type = data['device_type']
            browser_info = data.get('browser_info', '')
            user_id = session['user_id']
            
            # Store the device token
            success = store_device_token(user_id, device_token, device_type, browser_info)
            
            if success:
                return jsonify({'status': 'success', 'message': 'Device token registered successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to register device token'}), 500
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/notifications/token', methods=['DELETE'])
    @require_login
    def unregister_device_token():
        """Unregister a device token for push notifications"""
        try:
            data = request.get_json()
            
            if not data or 'device_token' not in data:
                return jsonify({'error': 'Device token is required'}), 400
            
            device_token = data['device_token']
            user_id = session['user_id']
            
            # Remove the device token
            success = remove_device_token(user_id, device_token)
            
            if success:
                return jsonify({'status': 'success', 'message': 'Device token unregistered successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to unregister device token'}), 500
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/notifications/send', methods=['POST'])
    @require_login
    def send_notification_to_user():
        """Send a real-time notification to the current user"""
        try:
            data = request.get_json()
            
            if not data or 'title' not in data or 'message' not in data:
                return jsonify({'error': 'Title and message are required'}), 400
            
            title = data['title']
            message = data['message']
            user_id = session['user_id']
            
            # Send the notification
            success = send_realtime_notification(user_id, title, message)
            
            if success:
                return jsonify({'status': 'success', 'message': 'Notification sent successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to send notification'}), 500
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/notifications/schedule', methods=['POST'])
    @require_login
    def schedule_user_notification():
        """Schedule a notification for the current user"""
        try:
            data = request.get_json()
            
            if not data or 'title' not in data or 'message' not in data or 'scheduled_time' not in data:
                return jsonify({'error': 'Title, message, and scheduled_time are required'}), 400
            
            title = data['title']
            message = data['message']
            scheduled_time_str = data['scheduled_time']
            user_id = session['user_id']
            
            # Parse the scheduled time
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid scheduled time format. Use ISO format.'}), 400
            
            # Schedule the notification
            success = schedule_notification(user_id, title, message, scheduled_time)
            
            if success:
                return jsonify({'status': 'success', 'message': 'Notification scheduled successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to schedule notification'}), 500
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/notifications/broadcast', methods=['POST'])
    @require_login
    def send_broadcast_notification_route():
        """Send a broadcast notification to all users (admin only)"""
        try:
            # In a real implementation, you would check if the user is an admin
            # For now, we'll allow any logged-in user to send broadcasts (for testing)
            
            data = request.get_json()
            
            if not data or 'title' not in data or 'message' not in data:
                return jsonify({'error': 'Title and message are required'}), 400
            
            title = data['title']
            message = data['message']
            
            # Send the broadcast notification
            success = send_broadcast_notification(title, message)
            
            if success:
                return jsonify({'status': 'success', 'message': 'Broadcast notification sent successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to send broadcast notification'}), 500
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/notifications/history')
    @require_login
    def get_notification_history():
        """Get notification history for the current user"""
        try:
            user_id = session['user_id']
            limit = request.args.get('limit', 50, type=int)
            
            # Get notifications
            notifications = get_user_notifications(user_id, limit)
            
            return jsonify({'status': 'success', 'notifications': notifications})
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    @require_login
    def mark_notification_read(notification_id):
        """Mark a notification as read"""
        try:
            user_id = session['user_id']
            
            # Mark notification as read
            success = mark_notification_as_read(notification_id, user_id)
            
            if success:
                return jsonify({'status': 'success', 'message': 'Notification marked as read'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to mark notification as read'}), 404
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/notifications/unread-count')
    @require_login
    def get_unread_count():
        """Get the count of unread notifications for the current user"""
        try:
            user_id = session['user_id']
            
            # Get unread count
            count = get_unread_notification_count(user_id)
            
            return jsonify({'status': 'success', 'unread_count': count})
                
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/notifications')
    @require_login
    def notifications_page():
        """Render the notifications history page"""
        try:
            user_id = session['user_id']
            
            # Get notifications
            notifications = get_user_notifications(user_id, 50)
            
            return render_template('notifications.html', 
                                 notifications=notifications,
                                 title="Notifications")
        except Exception as e:
            return render_template('error.html', 
                                 error="Unable to load notifications",
                                 title="Notifications Error")