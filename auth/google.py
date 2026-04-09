"""
Google OAuth 2.0 Integration Module using Authlib
Integrate this with your existing Flask/FastAPI/Django app by:
1. Adding routes for '/auth/google/login' and '/auth/google/callback'
2. Calling google_login() and google_callback() functions respectively
3. Updating your User model to store google_id, google_email, google_name, google_picture
"""

import os
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
)

def google_login(app):
    """
    Initiate Google OAuth flow
    Call this from your '/auth/google/login' endpoint
    """
    google = oauth.create_client('google')
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/google/callback")
    return google.authorize_redirect(redirect_uri)

def google_callback(app):
    """
    Handle Google OAuth callback
    Call this from your '/auth/google/callback' endpoint
    Returns user info dict or None if failed
    """
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    
    # Return structured user data
    return {
        'google_id': user_info.get('id'),
        'google_email': user_info.get('email'),
        'google_name': user_info.get('name'),
        'google_picture': user_info.get('picture'),
        'access_token': token.get('access_token')
    }