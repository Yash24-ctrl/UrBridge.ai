"""
Export Utilities for AI Resume Analyzer
Provides functions to export user data in various formats (PDF, CSV, Excel, JSON, ZIP)
"""

import sqlite3
import json
import csv
import os
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime
from flask import session
import zipfile
# Import E2EE module
from e2ee import encrypt_for_user

# Database configuration
DATABASE = 'users.db'

def get_user_data(user_id):
    """Fetch all user-related data from the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Fetch user profile data
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = c.fetchone()
    user_columns = [description[0] for description in c.description]
    
    # Fetch user profile details
    c.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
    profile_data = c.fetchone()
    profile_columns = [description[0] for description in c.description]
    
    # Fetch analysis history
    c.execute("SELECT * FROM analysis_history WHERE user_id = ?", (user_id,))
    history_data = c.fetchall()
    history_columns = [description[0] for description in c.description]
    
    conn.close()
    
    # Organize data
    user_dict = dict(zip(user_columns, user_data)) if user_data else {}
    profile_dict = dict(zip(profile_columns, profile_data)) if profile_data else {}
    history_list = [dict(zip(history_columns, row)) for row in history_data]
    
    return {
        'user': user_dict,
        'profile': profile_dict,
        'history': history_list
    }

def export_to_json(user_id):
    """Export user data to JSON format"""
    data = get_user_data(user_id)
    
    # Convert datetime objects to strings
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    json_data = json.dumps(data, default=serialize_datetime, indent=2)
    return json_data.encode('utf-8')

def export_to_encrypted_json(user_id, receiver_user_id):
    """Export user data to encrypted JSON format"""
    try:
        # Get the raw JSON data
        json_data = export_to_json(user_id)
        
        # Convert to string for encryption
        json_string = json_data.decode('utf-8')
        
        # Encrypt the data
        encrypted_data = encrypt_for_user(json_string, receiver_user_id)
        
        if encrypted_data:
            # Return encrypted data as bytes
            return encrypted_data.encode('utf-8')
        else:
            raise Exception("Failed to encrypt JSON data")
    except Exception as e:
        print(f"Error creating encrypted JSON export: {str(e)}")
        raise

def export_to_csv(user_id):
    """Export user data to CSV format"""
    data = get_user_data(user_id)
    
    output = BytesIO()
    
    # Create a CSV writer
    writer = csv.writer(output)
    
    # Write user data
    writer.writerow(['User Data'])
    if data['user']:
        writer.writerow(data['user'].keys())
        writer.writerow(data['user'].values())
    
    writer.writerow([])  # Empty row
    
    # Write profile data
    writer.writerow(['Profile Data'])
    if data['profile']:
        writer.writerow(data['profile'].keys())
        writer.writerow(data['profile'].values())
    
    writer.writerow([])  # Empty row
    
    # Write history data
    writer.writerow(['Analysis History'])
    if data['history']:
        # Write headers
        writer.writerow(data['history'][0].keys())
        # Write rows
        for record in data['history']:
            writer.writerow(record.values())
    
    output.seek(0)
    return output.getvalue()

def export_to_encrypted_csv(user_id, receiver_user_id):
    """Export user data to encrypted CSV format"""
    try:
        # Get the raw CSV data
        csv_data = export_to_csv(user_id)
        
        # Convert to string for encryption
        csv_string = csv_data.decode('utf-8')
        
        # Encrypt the data
        encrypted_data = encrypt_for_user(csv_string, receiver_user_id)
        
        if encrypted_data:
            # Return encrypted data as bytes
            return encrypted_data.encode('utf-8')
        else:
            raise Exception("Failed to encrypt CSV data")
    except Exception as e:
        print(f"Error creating encrypted CSV export: {str(e)}")
        raise

def export_to_excel(user_id):
    """Export user data to Excel format"""
    data = get_user_data(user_id)
    
    output = BytesIO()
    
    # Create a Pandas Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write user data
        if data['user']:
            user_df = pd.DataFrame([data['user']])
            user_df.to_excel(writer, sheet_name='User_Data', index=False)
        
        # Write profile data
        if data['profile']:
            profile_df = pd.DataFrame([data['profile']])
            profile_df.to_excel(writer, sheet_name='Profile_Data', index=False)
        
        # Write history data
        if data['history']:
            history_df = pd.DataFrame(data['history'])
            history_df.to_excel(writer, sheet_name='Analysis_History', index=False)
    
    output.seek(0)
    return output.getvalue()

def export_to_encrypted_excel(user_id, receiver_user_id):
    """Export user data to encrypted Excel format"""
    try:
        # Get the raw Excel data
        excel_data = export_to_excel(user_id)
        
        # Convert to string for encryption (base64 encode binary data)
        import base64
        excel_string = base64.b64encode(excel_data).decode('utf-8')
        
        # Encrypt the data
        encrypted_data = encrypt_for_user(excel_string, receiver_user_id)
        
        if encrypted_data:
            # Return encrypted data as bytes
            return encrypted_data.encode('utf-8')
        else:
            raise Exception("Failed to encrypt Excel data")
    except Exception as e:
        print(f"Error creating encrypted Excel export: {str(e)}")
        raise

def export_to_pdf(user_id):
    """Export user data to PDF format"""
    data = get_user_data(user_id)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set fonts
    pdf.set_font("Arial", "B", 16)
    
    # Title
    pdf.cell(0, 10, "User Data Export", ln=True, align="C")
    pdf.ln(10)
    
    # Timestamp
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    
    # User Data Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "User Information:", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    if data['user']:
        for key, value in data['user'].items():
            if key not in ['password_hash', 'reset_token']:  # Exclude sensitive data
                pdf.cell(0, 10, f"{key}: {value}", ln=True)
    else:
        pdf.cell(0, 10, "No user data available", ln=True)
    
    pdf.ln(10)
    
    # Profile Data Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Profile Information:", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    if data['profile']:
        for key, value in data['profile'].items():
            pdf.cell(0, 10, f"{key}: {value}", ln=True)
    else:
        pdf.cell(0, 10, "No profile data available", ln=True)
    
    pdf.ln(10)
    
    # Analysis History Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Analysis History:", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    if data['history']:
        for i, record in enumerate(data['history'], 1):
            pdf.cell(0, 10, f"Record {i}:", ln=True)
            for key, value in record.items():
                # Limit the length of text to prevent issues
                str_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                pdf.cell(0, 10, f"  {key}: {str_value}", ln=True)
            pdf.ln(5)
    else:
        pdf.cell(0, 10, "No analysis history available", ln=True)
    
    # Generate PDF bytes
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue()

def export_to_encrypted_pdf(user_id, receiver_user_id):
    """Export user data to encrypted PDF format"""
    try:
        # Get the raw PDF data
        pdf_data = export_to_pdf(user_id)
        
        # Convert to string for encryption
        pdf_string = pdf_data.decode('latin-1')
        
        # Encrypt the data
        encrypted_data = encrypt_for_user(pdf_string, receiver_user_id)
        
        if encrypted_data:
            # Return encrypted data as bytes
            return encrypted_data.encode('utf-8')
        else:
            raise Exception("Failed to encrypt PDF data")
    except Exception as e:
        print(f"Error creating encrypted PDF export: {str(e)}")
        raise

def create_zip_export(user_id):
    """Create a ZIP file containing exports in multiple formats"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add JSON export
        json_data = export_to_json(user_id)
        zip_file.writestr('user_data.json', json_data)
        
        # Add CSV export
        csv_data = export_to_csv(user_id)
        zip_file.writestr('user_data.csv', csv_data)
        
        # Add Excel export
        excel_data = export_to_excel(user_id)
        zip_file.writestr('user_data.xlsx', excel_data)
        
        # Add PDF export
        pdf_data = export_to_pdf(user_id)
        zip_file.writestr('user_data.pdf', pdf_data)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Admin export functions
def get_all_users_data():
    """Fetch data for all users (admin only)"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Fetch all users
    c.execute("SELECT * FROM users")
    users_data = c.fetchall()
    users_columns = [description[0] for description in c.description]
    
    # Fetch all profiles
    c.execute("SELECT * FROM user_profiles")
    profiles_data = c.fetchall()
    profiles_columns = [description[0] for description in c.description]
    
    # Fetch all analysis history
    c.execute("SELECT * FROM analysis_history")
    history_data = c.fetchall()
    history_columns = [description[0] for description in c.description]
    
    conn.close()
    
    # Organize data
    users_list = [dict(zip(users_columns, row)) for row in users_data]
    profiles_list = [dict(zip(profiles_columns, row)) for row in profiles_data]
    history_list = [dict(zip(history_columns, row)) for row in history_data]
    
    return {
        'users': users_list,
        'profiles': profiles_list,
        'history': history_list
    }

def export_all_users_to_json():
    """Export all users data to JSON format (admin only)"""
    data = get_all_users_data()
    
    # Convert datetime objects to strings
    def serialize_datetime(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    json_data = json.dumps(data, default=serialize_datetime, indent=2)
    return json_data.encode('utf-8')

def export_all_users_to_csv():
    """Export all users data to CSV format (admin only)"""
    data = get_all_users_data()
    
    output = BytesIO()
    writer = csv.writer(output)
    
    # Write users data
    writer.writerow(['All Users Data'])
    if data['users']:
        writer.writerow(data['users'][0].keys())
        for user in data['users']:
            writer.writerow(user.values())
    
    writer.writerow([])  # Empty row
    
    # Write profiles data
    writer.writerow(['All Profiles Data'])
    if data['profiles']:
        writer.writerow(data['profiles'][0].keys())
        for profile in data['profiles']:
            writer.writerow(profile.values())
    
    writer.writerow([])  # Empty row
    
    # Write history data
    writer.writerow(['All Analysis History'])
    if data['history']:
        writer.writerow(data['history'][0].keys())
        for record in data['history']:
            writer.writerow(record.values())
    
    output.seek(0)
    return output.getvalue()

def export_all_users_to_excel():
    """Export all users data to Excel format (admin only)"""
    data = get_all_users_data()
    
    output = BytesIO()
    
    # Create a Pandas Excel writer
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write users data
        if data['users']:
            users_df = pd.DataFrame(data['users'])
            users_df.to_excel(writer, sheet_name='All_Users', index=False)
        
        # Write profiles data
        if data['profiles']:
            profiles_df = pd.DataFrame(data['profiles'])
            profiles_df.to_excel(writer, sheet_name='All_Profiles', index=False)
        
        # Write history data
        if data['history']:
            history_df = pd.DataFrame(data['history'])
            history_df.to_excel(writer, sheet_name='All_History', index=False)
    
    output.seek(0)
    return output.getvalue()

def export_logs():
    """Export system logs (admin only)"""
    # For now, we'll create a simple log export
    # In a real application, you would read from actual log files
    
    output = BytesIO()
    writer = csv.writer(output)
    
    # Write log header
    writer.writerow(['Timestamp', 'Level', 'Message'])
    
    # Add some sample log entries
    # In a real application, you would read from actual log files
    sample_logs = [
        [datetime.now().isoformat(), 'INFO', 'System started'],
        [datetime.now().isoformat(), 'INFO', 'User logged in'],
        [datetime.now().isoformat(), 'WARNING', 'Large file upload detected'],
        [datetime.now().isoformat(), 'INFO', 'Analysis completed']
    ]
    
    for log_entry in sample_logs:
        writer.writerow(log_entry)
    
    output.seek(0)
    return output.getvalue()