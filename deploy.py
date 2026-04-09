#!/usr/bin/env python3
"""
Production Deployment Script for AI Resume Analyzer
This script prepares the application for production deployment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_environment():
    """Check if the environment is ready for production deployment"""
    print("🔍 Checking environment for production deployment...")
    
    # Check if running as admin/root (optional for security review)
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() if os.name == 'nt' else os.getuid() == 0
        print(f"   Admin privileges: {'✅ Yes' if is_admin else '⚠️  No (recommended for production)'}")
    except:
        print("   Admin privileges: Unable to determine")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ Environment file (.env) found")
        # Check if required variables are set
        with open(env_file, 'r') as f:
            content = f.read()
            required_vars = [
                'SECRET_KEY', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET',
                'LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET', 'EMAIL_USER', 'EMAIL_PASS'
            ]
            missing_vars = []
            for var in required_vars:
                if f"{var}=" in content and f"{var}=" != f"{var}=\n":  # Has value
                    continue
                else:
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"   ⚠️  Missing or empty variables in .env: {', '.join(missing_vars)}")
            else:
                print("   ✅ All required environment variables are set")
    else:
        print("   ❌ Environment file (.env) not found - create from .env.example")
        return False
    
    return True

def run_security_check():
    """Run basic security checks"""
    print("\n🔒 Running security checks...")
    
    # Check for debug mode
    if os.environ.get('FLASK_DEBUG', '').lower() == 'true':
        print("   ⚠️  FLASK_DEBUG is enabled - disable for production")
    else:
        print("   ✅ Debug mode is disabled")
    
    # Check for SECRET_KEY in environment
    secret_key = os.environ.get('SECRET_KEY', '')
    if not secret_key or secret_key == 'your_secret_key_here':
        print("   ❌ SECRET_KEY is not properly set")
        return False
    else:
        print("   ✅ SECRET_KEY is set")
    
    # Check for strong SECRET_KEY
    if len(secret_key) < 32:
        print("   ⚠️  SECRET_KEY should be at least 32 characters long")
    else:
        print("   ✅ SECRET_KEY length is appropriate")
    
    return True

def prepare_production_files():
    """Prepare files for production"""
    print("\n📦 Preparing production files...")
    
    # Create production config if needed
    prod_config_content = '''# Production Configuration for AI Resume Analyzer
# This file contains production-specific settings

import os

# Force HTTPS in production
os.environ['FORCE_HTTPS'] = 'true'

# Security settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Performance settings
DEBUG = False
TESTING = False

# Database settings (production)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users_prod.db')

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FILE = 'production.log'

# Rate limiting (stricter in production)
LOGIN_ATTEMPTS_PER_MINUTE = 5
REGISTRATION_ATTEMPTS_PER_MINUTE = 3
'''
    
    try:
        with open('production_config.py', 'w') as f:
            f.write(prod_config_content)
        print("   ✅ Created production configuration")
    except Exception as e:
        print(f"   ❌ Failed to create production config: {e}")
        return False
    
    return True

def create_startup_script():
    """Create production startup script"""
    print("\n🚀 Creating production startup script...")
    
    startup_content = '''@echo off
REM Production Startup Script for AI Resume Analyzer
REM Run this script to start the application in production mode

echo Starting AI Resume Analyzer in PRODUCTION MODE...
echo ======================================================

REM Set production environment
set FLASK_ENV=production
set PYTHONPATH=%~dp0;%PYTHONPATH%

REM Check if running on Windows or Unix-like system
if "%OS%"=="Windows_NT" (
    echo Detected Windows system
    REM Use Waitress for Windows
    python -c "from waitress import serve; exec(open('app.py').read()); serve(app, host='0.0.0.0', port=8000)"
) else (
    echo Detected Unix-like system
    REM Use Gunicorn for Unix-like systems
    gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 5 app:app
)

pause
'''
    
    windows_content = '''#!/bin/bash
# Production Startup Script for AI Resume Analyzer (Unix/Linux/macOS)
# Run this script to start the application in production mode

echo "Starting AI Resume Analyzer in PRODUCTION MODE..."
echo "======================================================"

# Set production environment
export FLASK_ENV=production
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Detect OS and use appropriate server
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected Unix-like system"
    echo "Using Gunicorn for production..."
    
    # Check if gunicorn is available
    if command -v gunicorn &> /dev/null; then
        echo "Starting with Gunicorn..."
        gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 5 --access-logfile - --error-logfile - app:app
    else
        echo "Gunicorn not found. Installing..."
        pip install gunicorn
        gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 5 --access-logfile - --error-logfile - app:app
    fi
else
    echo "Detected Windows system"
    echo "Using Waitress for production..."
    python -c "
import os
os.environ['FLASK_ENV'] = 'production'
from waitress import serve
exec(open('app.py').read())
serve(app, host='0.0.0.0', port=8000)
"
fi
'''

    try:
        # Windows batch file
        with open('start_production.bat', 'w') as f:
            f.write(startup_content)
        print("   ✅ Created Windows production startup script (start_production.bat)")
        
        # Unix shell script
        with open('start_production.sh', 'w') as f:
            f.write(windows_content)
        print("   ✅ Created Unix production startup script (start_production.sh)")
        
        # Make shell script executable
        os.chmod('start_production.sh', 0o755)
        
    except Exception as e:
        print(f"   ❌ Failed to create startup scripts: {e}")
        return False
    
    return True

def create_health_check():
    """Create a health check endpoint script"""
    print("\n🏥 Creating health check endpoint...")
    
    health_check_content = '''# Health Check Endpoint
# Add this to your app.py for production monitoring

from flask import jsonify
import os
import time
import psutil  # You might need to install this: pip install psutil

def add_health_check_endpoint(app):
    """Add health check endpoints for production monitoring"""
    
    @app.route('/health')
    def health_check():
        """Basic health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime': getattr(app, '_start_time', time.time()),
            'version': '1.0.0'
        })
    
    @app.route('/health/detail')
    def detailed_health_check():
        """Detailed health check with system metrics"""
        try:
            # Get system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            # Check database connectivity (basic check)
            db_ok = True  # Implement your actual DB check here
            db_latency = 0  # Implement actual latency check
            
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'system_stats': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_percent': disk_percent
                },
                'database': {
                    'connected': db_ok,
                    'latency_ms': db_latency
                },
                'app': {
                    'version': '1.0.0',
                    'environment': os.getenv('FLASK_ENV', 'development')
                }
            })
        except Exception as e:
            return jsonify({
                'status': 'degraded',
                'error': str(e),
                'timestamp': time.time()
            }), 500

# To use this, call add_health_check_endpoint(app) after creating your Flask app
'''
    
    try:
        with open('health_check.py', 'w') as f:
            f.write(health_check_content)
        print("   ✅ Created health check endpoint module")
    except Exception as e:
        print(f"   ❌ Failed to create health check: {e}")
        return False
    
    return True

def create_deployment_docs():
    """Create deployment documentation"""
    print("\n📚 Creating deployment documentation...")
    
    docs_content = '''# Production Deployment Guide for AI Resume Analyzer

## Overview
This guide explains how to deploy the AI Resume Analyzer application in a production environment.

## Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)
- Valid OAuth credentials (Google & LinkedIn)
- Email configuration for notifications

## Environment Setup

### 1. Create Virtual Environment
```bash
python -m venv production_env
production_env\\Scripts\\activate  # Windows
source production_env/bin/activate  # Unix/Linux/macOS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
# Edit .env with your actual values
```

## Production Configuration

### Security Settings
- Session cookies are secured with HTTPS
- Debug mode is disabled
- Rate limiting is enforced
- Security headers are added to all responses

### Performance Settings
- Session timeout: 24 hours
- Multiple workers for concurrent requests
- Optimized database connections

## Starting the Application

### Windows:
```bash
start_production.bat
```

### Unix/Linux/macOS:
```bash
./start_production.sh
```

## Monitoring

### Health Checks
- `/health` - Basic health status
- `/health/detail` - Detailed system metrics

### Logs
- Application logs: `production.log`
- Security events: `security_audit.log`
- Performance metrics: Stored in database

## Security Best Practices

1. **Environment Variables**: Never commit sensitive data to version control
2. **HTTPS**: Always use HTTPS in production
3. **Secret Keys**: Use strong, randomly generated secret keys
4. **Database**: Use a production-grade database (PostgreSQL/MySQL) instead of SQLite
5. **Firewall**: Restrict access to necessary ports only
6. **Updates**: Keep dependencies updated for security patches

## Scaling Recommendations

1. Use a WSGI server (Gunicorn/Waitress) with multiple workers
2. Implement a proper database (not SQLite) for production
3. Use Redis for session storage and caching
4. Implement CDN for static assets
5. Use a reverse proxy (nginx) in front of the application

## Troubleshooting

### Common Issues:
- "Address already in use": Kill the process using the port
- "Permission denied": Run with appropriate permissions
- "Module not found": Install missing dependencies
- "Database locked": Use a proper database for production

## Rollback Procedure
1. Stop the current application
2. Restore previous version from backup
3. Restart the application
'''
    
    try:
        with open('PRODUCTION_DEPLOYMENT.md', 'w') as f:
            f.write(docs_content)
        print("   ✅ Created production deployment documentation")
    except Exception as e:
        print(f"   ❌ Failed to create deployment docs: {e}")
        return False
    
    return True

def main():
    """Main deployment preparation function"""
    print("🚀 AI Resume Analyzer - Production Deployment Preparation Tool")
    print("=" * 60)
    
    steps = [
        check_environment,
        run_security_check,
        prepare_production_files,
        create_startup_script,
        create_health_check,
        create_deployment_docs
    ]
    
    success_count = 0
    for step in steps:
        try:
            if step():
                success_count += 1
            else:
                print(f"   ❌ Step {step.__name__} failed")
        except Exception as e:
            print(f"   ❌ Step {step.__name__} failed with error: {e}")
    
    print(f"\n✅ Deployment preparation completed: {success_count}/{len(steps)} steps successful")
    
    if success_count == len(steps):
        print("\n🎉 The application is now prepared for production deployment!")
        print("\n📋 Next steps:")
        print("   1. Review the environment variables in .env")
        print("   2. Test the application in a staging environment")
        print("   3. Run security scans if available")
        print("   4. Deploy using start_production.(bat/sh)")
        print("   5. Monitor the application after deployment")
    else:
        print(f"\n⚠️  Some steps failed. Please address the issues before deploying to production.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)