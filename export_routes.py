"""
Export Routes for AI Resume Analyzer
Provides Flask routes for exporting user data in various formats
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from functools import wraps
from export_utils import export_to_json, export_to_csv, export_to_excel, export_to_pdf, create_zip_export, export_all_users_to_json, export_all_users_to_csv, export_all_users_to_excel, export_logs, export_to_encrypted_json, export_to_encrypted_csv, export_to_encrypted_excel, export_to_encrypted_pdf

def require_complete_profile(f):
    """Decorator to require complete user profile with video tutorial check"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
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

def register_export_routes(app):
    """Register all export routes with the Flask app"""
    
    @app.route('/export/json')
    @require_complete_profile
    def export_user_data_json():
        """Export user data in JSON format"""
        try:
            user_id = session.get('user_id')
            json_data = export_to_json(user_id)
            
            response = Response(json_data)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}.json'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/csv')
    @require_complete_profile
    def export_user_data_csv():
        """Export user data in CSV format"""
        try:
            user_id = session.get('user_id')
            csv_data = export_to_csv(user_id)
            
            response = Response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}.csv'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/excel')
    @require_complete_profile
    def export_user_data_excel():
        """Export user data in Excel format"""
        try:
            user_id = session.get('user_id')
            excel_data = export_to_excel(user_id)
            
            response = Response(excel_data)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}.xlsx'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/pdf')
    @require_complete_profile
    def export_user_data_pdf():
        """Export user data in PDF format"""
        try:
            user_id = session.get('user_id')
            pdf_data = export_to_pdf(user_id)
            
            response = Response(pdf_data)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}.pdf'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/zip')
    @require_complete_profile
    def export_user_data_zip():
        """Export user data in ZIP format containing all formats"""
        try:
            user_id = session.get('user_id')
            zip_data = create_zip_export(user_id)
            
            response = Response(zip_data)
            response.headers['Content-Type'] = 'application/zip'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}.zip'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/encrypted/json')
    @require_complete_profile
    def export_user_data_encrypted_json():
        """Export user data in encrypted JSON format"""
        try:
            user_id = session.get('user_id')
            # For now, we'll encrypt for the same user
            # In a real implementation, you would specify the recipient
            encrypted_data = export_to_encrypted_json(user_id, user_id)
            
            response = Response(encrypted_data)
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}_encrypted.json'
            
            return response
        except Exception as e:
            flash(f"Error exporting encrypted data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/encrypted/csv')
    @require_complete_profile
    def export_user_data_encrypted_csv():
        """Export user data in encrypted CSV format"""
        try:
            user_id = session.get('user_id')
            # For now, we'll encrypt for the same user
            # In a real implementation, you would specify the recipient
            encrypted_data = export_to_encrypted_csv(user_id, user_id)
            
            response = Response(encrypted_data)
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}_encrypted.csv'
            
            return response
        except Exception as e:
            flash(f"Error exporting encrypted data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/encrypted/excel')
    @require_complete_profile
    def export_user_data_encrypted_excel():
        """Export user data in encrypted Excel format"""
        try:
            user_id = session.get('user_id')
            # For now, we'll encrypt for the same user
            # In a real implementation, you would specify the recipient
            encrypted_data = export_to_encrypted_excel(user_id, user_id)
            
            response = Response(encrypted_data)
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}_encrypted.xlsx'
            
            return response
        except Exception as e:
            flash(f"Error exporting encrypted data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/export/encrypted/pdf')
    @require_complete_profile
    def export_user_data_encrypted_pdf():
        """Export user data in encrypted PDF format"""
        try:
            user_id = session.get('user_id')
            # For now, we'll encrypt for the same user
            # In a real implementation, you would specify the recipient
            encrypted_data = export_to_encrypted_pdf(user_id, user_id)
            
            response = Response(encrypted_data)
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename=user_data_{session["user_id"]}_encrypted.pdf'
            
            return response
        except Exception as e:
            flash(f"Error exporting encrypted data: {str(e)}", "error")
            return redirect(url_for('profile'))

    # Admin Export Routes

    @app.route('/admin/export/users/json')
    def admin_export_users_json():
        """Export all users data in JSON format (admin only)"""
        # Check if user is admin (you'll need to implement your own admin check)
        # For now, we'll just check if user is logged in
        if "user_id" not in session:
            return redirect(url_for('login'))
        
        try:
            json_data = export_all_users_to_json()
            
            response = Response(json_data)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = 'attachment; filename=all_users_data.json'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/admin/export/users/csv')
    def admin_export_users_csv():
        """Export all users data in CSV format (admin only)"""
        # Check if user is admin (you'll need to implement your own admin check)
        # For now, we'll just check if user is logged in
        if "user_id" not in session:
            return redirect(url_for('login'))
        
        try:
            csv_data = export_all_users_to_csv()
            
            response = Response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=all_users_data.csv'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/admin/export/users/excel')
    def admin_export_users_excel():
        """Export all users data in Excel format (admin only)"""
        # Check if user is admin (you'll need to implement your own admin check)
        # For now, we'll just check if user is logged in
        if "user_id" not in session:
            return redirect(url_for('login'))
        
        try:
            excel_data = export_all_users_to_excel()
            
            response = Response(excel_data)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = 'attachment; filename=all_users_data.xlsx'
            
            return response
        except Exception as e:
            flash(f"Error exporting data: {str(e)}", "error")
            return redirect(url_for('profile'))

    @app.route('/admin/export/logs')
    def admin_export_logs():
        """Export system logs (admin only)"""
        # Check if user is admin (you'll need to implement your own admin check)
        # For now, we'll just check if user is logged in
        if "user_id" not in session:
            return redirect(url_for('login'))
        
        try:
            log_data = export_logs()
            
            response = Response(log_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=system_logs.csv'
            
            return response
        except Exception as e:
            flash(f"Error exporting logs: {str(e)}", "error")
            return redirect(url_for('profile'))