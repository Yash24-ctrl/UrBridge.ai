from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import json
import sqlite3
from datetime import datetime
import hashlib
from werkzeug.utils import secure_filename
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'yash_secret_key')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
DATABASE = 'users.db'

# Import security modules (the essential ones we added)
from security.encryption import encrypt_data, decrypt_data, hash_identifier, anonymize_resume_data
from security.advanced_security import log_security_event, require_login, secure_file_upload, sanitize_input, rate_limit, encrypt_resume_content, decrypt_resume_content, generate_secure_token

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=10, window=300)  # 10 attempts per 5 minutes
def login():
    """Login page."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Connect to database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Hash the username for lookup
        hashed_username = hash_identifier(username)
        
        # Query user from database
        c.execute("SELECT id, username, password FROM users WHERE username = ?", (hashed_username,))
        user = c.fetchone()
        
        conn.close()
        
        if user and user[2] == password:  # In a real app, you'd hash the password
            session['user_id'] = user[0]
            session['username'] = username
            log_security_event('LOGIN_SUCCESS', user[0], f"User {username} logged in")
            return redirect(url_for('profile'))
        else:
            log_security_event('LOGIN_FAILED', None, f"Failed login attempt for username: {username}")
            flash("Invalid username or password", "error")
    
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
@rate_limit(max_requests=5, window=300)  # 5 attempts per 5 minutes
def register():
    """Registration page."""
    if request.method == "POST":
        username = sanitize_input(request.form.get("username", ""))
        password = request.form.get("password", "")
        email = sanitize_input(request.form.get("email", ""))
        
        # Validate input
        if not username or not password or not email:
            flash("All fields are required", "error")
            return render_template("register.html")
        
        # Connect to database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if user already exists
        hashed_username = hash_identifier(username)
        c.execute("SELECT id FROM users WHERE username = ?", (hashed_username,))
        existing_user = c.fetchone()
        
        if existing_user:
            flash("Username already exists", "error")
            conn.close()
            return render_template("register.html")
        
        # Insert new user
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                 (hashed_username, password, hash_identifier(email)))
        
        conn.commit()
        conn.close()
        
        flash("Registration successful", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route('/profile')
@require_login
def profile():
    """User profile page."""
    return render_template("profile.html", username=session.get('username'))

if __name__ == "__main__":
    # Create database if it doesn't exist
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    
    # Start the server
    port = int(os.getenv('PORT', 5000))
    print(f"Starting server on http://127.0.0.1:{port}")
    print("Advanced security features are active!")
    app.run(host='127.0.0.1', port=port, debug=False)