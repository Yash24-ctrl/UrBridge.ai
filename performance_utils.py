"""
Performance Metrics Utilities for AI Resume Analyzer
Provides functions to track, collect, and analyze application performance metrics
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, session
import os

# Database configuration
DATABASE = 'users.db'

def track_performance(metric_type, response_time=None, status_code=None, metadata=None):
    """
    Track a performance metric in the database
    
    Args:
        metric_type (str): Type of metric (e.g., 'page_load', 'api_call', 'user_action')
        response_time (float): Response time in seconds
        status_code (int): HTTP status code
        metadata (dict): Additional metadata about the metric
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        user_id = session.get('user_id') if 'user_id' in session else None
        endpoint = request.endpoint if request else None
        
        # Convert metadata to JSON string
        metadata_str = json.dumps(metadata) if metadata else None
        
        c.execute('''
            INSERT INTO performance_metrics 
            (metric_type, user_id, endpoint, response_time, status_code, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (metric_type, user_id, endpoint, response_time, status_code, metadata_str))
        
        conn.commit()
        conn.close()
    except Exception as e:
        # Silently fail to avoid disrupting user experience
        pass

def performance_tracker(metric_type, metadata=None):
    """
    Decorator to track performance of functions/routes
    
    Args:
        metric_type (str): Type of metric to track
        metadata (dict): Additional metadata to store
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                response_time = end_time - start_time
                track_performance(metric_type, response_time=response_time, metadata=metadata)
                return result
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                track_performance(metric_type, response_time=response_time, status_code=500, metadata=metadata)
                raise e
        return wrapper
    return decorator

def get_daily_active_users(days=30):
    """
    Get daily active users for the past N days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        list: List of dictionaries with date and active user count
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query for daily active users
        c.execute('''
            SELECT DATE(timestamp) as date, COUNT(DISTINCT user_id) as active_users
            FROM performance_metrics 
            WHERE timestamp >= ? AND user_id IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (threshold_date,))
        
        results = c.fetchall()
        conn.close()
        
        # Format results
        return [{'date': row[0], 'active_users': row[1]} for row in results]
    except Exception as e:
        return []

def get_login_counts(days=30):
    """
    Get login counts for the past N days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        list: List of dictionaries with date and login count
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query for login counts
        c.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as login_count
            FROM performance_metrics 
            WHERE timestamp >= ? AND metric_type = 'login'
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (threshold_date,))
        
        results = c.fetchall()
        conn.close()
        
        # Format results
        return [{'date': row[0], 'login_count': row[1]} for row in results]
    except Exception as e:
        return []

def get_page_load_times(days=30):
    """
    Get average page load times for the past N days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        list: List of dictionaries with date and average load time
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query for page load times
        c.execute('''
            SELECT DATE(timestamp) as date, AVG(response_time) as avg_load_time
            FROM performance_metrics 
            WHERE timestamp >= ? AND metric_type = 'page_load' AND response_time IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (threshold_date,))
        
        results = c.fetchall()
        conn.close()
        
        # Format results
        return [{'date': row[0], 'avg_load_time': round(row[1], 3) if row[1] else 0} for row in results]
    except Exception as e:
        return []

def get_api_response_times(days=30):
    """
    Get average API response times for the past N days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        list: List of dictionaries with date and average response time
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query for API response times
        c.execute('''
            SELECT DATE(timestamp) as date, AVG(response_time) as avg_response_time
            FROM performance_metrics 
            WHERE timestamp >= ? AND metric_type = 'api_call' AND response_time IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (threshold_date,))
        
        results = c.fetchall()
        conn.close()
        
        # Format results
        return [{'date': row[0], 'avg_response_time': round(row[1], 3) if row[1] else 0} for row in results]
    except Exception as e:
        return []

def get_error_rates(days=30):
    """
    Get error rates for the past N days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        list: List of dictionaries with date and error rate percentage
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query for error rates
        c.execute('''
            SELECT DATE(timestamp) as date, 
                   SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
                   COUNT(*) as total_count
            FROM performance_metrics 
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (threshold_date,))
        
        results = c.fetchall()
        conn.close()
        
        # Calculate error rates
        error_rates = []
        for row in results:
            total_count = row[2]
            error_count = row[1]
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            error_rates.append({
                'date': row[0],
                'error_rate': round(error_rate, 2),
                'error_count': error_count,
                'total_count': total_count
            })
        
        return error_rates
    except Exception as e:
        return []

def get_uptime_percentage(days=30):
    """
    Calculate uptime percentage for the past N days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        float: Uptime percentage
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query for uptime calculation
        c.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(CASE WHEN status_code < 500 THEN 1 ELSE 0 END) as successful_requests
            FROM performance_metrics 
            WHERE timestamp >= ?
        ''', (threshold_date,))
        
        result = c.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total = result[0]
            successful = result[1]
            uptime = (successful / total) * 100
            return round(uptime, 2)
        
        return 100.0  # Default to 100% if no data
    except Exception as e:
        return 100.0  # Default to 100% on error

def get_feature_usage(days=30):
    """
    Get feature usage statistics for the past N days
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        list: List of dictionaries with feature name and usage count
    """
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        
        # Query for feature usage
        c.execute('''
            SELECT metric_type, COUNT(*) as usage_count
            FROM performance_metrics 
            WHERE timestamp >= ? AND metric_type IN 
                ('analyzer', 'pdf_upload', 'jobmatch', 'history', 'profile')
            GROUP BY metric_type
            ORDER BY usage_count DESC
        ''', (threshold_date,))
        
        results = c.fetchall()
        conn.close()
        
        # Format results
        return [{'feature': row[0], 'usage_count': row[1]} for row in results]
    except Exception as e:
        return []

def get_all_performance_data(days=30):
    """
    Get all performance data for the dashboard
    
    Args:
        days (int): Number of days to look back
        
    Returns:
        dict: Dictionary containing all performance metrics
    """
    return {
        'daily_active_users': get_daily_active_users(days),
        'login_counts': get_login_counts(days),
        'page_load_times': get_page_load_times(days),
        'api_response_times': get_api_response_times(days),
        'error_rates': get_error_rates(days),
        'uptime_percentage': get_uptime_percentage(days),
        'feature_usage': get_feature_usage(days)
    }