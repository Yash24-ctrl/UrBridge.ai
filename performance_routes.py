"""
Performance Metrics Routes for AI Resume Analyzer
Provides Flask routes for the performance dashboard and metrics collection
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from performance_utils import get_all_performance_data, track_performance
import json

def require_admin(f):
    """Decorator to require admin access with video tutorial check"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, we'll just check if user is logged in
        # In a real application, you would check for admin privileges
        if "user_id" not in session:
            return redirect(url_for('login'))
        
        # Check if profile is complete
        if not is_profile_complete(session['user_id']):
            flash("Please complete your profile before accessing this feature.", "warning")
            return redirect(url_for('profile'))
        
        # Check if user has seen the video tutorial (mandatory for all users)
        if 'video_tutorial_seen' not in session:
            return redirect(url_for('how_it_works_video'))
        
        return f(*args, **kwargs)
    return decorated_function

def register_performance_routes(app):
    """Register all performance dashboard routes with the Flask app"""
    
    @app.route('/performance/dashboard')
    @require_admin
    def performance_dashboard():
        """Render the performance metrics dashboard"""
        try:
            # Get performance data for the last 30 days
            data = get_all_performance_data(days=30)
            
            return render_template('performance_dashboard.html', 
                                 performance_data=json.dumps(data),
                                 title="Performance Dashboard")
        except Exception as e:
            # Log error and show a simple error page
            print(f"Error loading performance dashboard: {str(e)}")
            return render_template('error.html', 
                                 error="Unable to load performance dashboard",
                                 title="Dashboard Error")

    @app.route('/performance/data')
    @require_admin
    def performance_data():
        """API endpoint to get performance data"""
        try:
            days = request.args.get('days', 30, type=int)
            data = get_all_performance_data(days=days)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/performance/export/json')
    @require_admin
    def export_performance_json():
        """Export performance data in JSON format"""
        try:
            days = request.args.get('days', 30, type=int)
            data = get_all_performance_data(days=days)
            
            from flask import Response
            response = Response(json.dumps(data, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = 'attachment; filename=performance_data.json'
            
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/performance/export/csv')
    @require_admin
    def export_performance_csv():
        """Export performance data in CSV format"""
        try:
            import csv
            from io import StringIO
            
            days = request.args.get('days', 30, type=int)
            data = get_all_performance_data(days=days)
            
            # Create CSV output
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Metric', 'Date', 'Value'])
            
            # Write daily active users data
            for item in data.get('daily_active_users', []):
                writer.writerow(['Daily Active Users', item['date'], item['active_users']])
            
            # Write login counts data
            for item in data.get('login_counts', []):
                writer.writerow(['Login Count', item['date'], item['login_count']])
            
            # Write page load times data
            for item in data.get('page_load_times', []):
                writer.writerow(['Page Load Time', item['date'], item['avg_load_time']])
            
            # Write API response times data
            for item in data.get('api_response_times', []):
                writer.writerow(['API Response Time', item['date'], item['avg_response_time']])
            
            # Write error rates data
            for item in data.get('error_rates', []):
                writer.writerow(['Error Rate (%)', item['date'], item['error_rate']])
            
            # Write uptime percentage
            writer.writerow(['Uptime Percentage', '', data.get('uptime_percentage', 0)])
            
            # Write feature usage data
            for item in data.get('feature_usage', []):
                writer.writerow(['Feature Usage', item['feature'], item['usage_count']])
            
            # Create response
            from flask import Response
            response = Response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=performance_data.csv'
            
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Route to manually track metrics (for testing)
    @app.route('/track_metric', methods=['POST'])
    def track_metric():
        """Endpoint to manually track a metric"""
        try:
            data = request.get_json()
            metric_type = data.get('metric_type', 'manual')
            response_time = data.get('response_time')
            status_code = data.get('status_code')
            metadata = data.get('metadata')
            
            track_performance(metric_type, response_time, status_code, metadata)
            
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500