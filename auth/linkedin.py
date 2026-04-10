"""
LinkedIn OAuth 2.0 Integration Module
Integrate this with your existing Flask/FastAPI/Django app by:
1. Adding routes for '/auth/linkedin/login' and '/auth/linkedin/callback'
2. Calling linkedin_login() and linkedin_callback() functions respectively
3. Updating your User model to store linkedin_id, linkedin_email, linkedin_name, linkedin_picture
"""

import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LinkedIn OAuth Configuration
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:5000/auth/linkedin/callback")
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USER_INFO_URL = "https://api.linkedin.com/v2/userinfo"

def linkedin_login(redirect_uri=None):
    """
    Initiate LinkedIn OAuth flow
    Call this from your '/auth/linkedin/login' endpoint
    """
    resolved_redirect_uri = redirect_uri or LINKEDIN_REDIRECT_URI
    params = {
        'response_type': 'code',
        'client_id': LINKEDIN_CLIENT_ID,
        'redirect_uri': resolved_redirect_uri,
        'scope': 'openid profile email'  # Using OpenID Connect
    }
    auth_url = f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"
    return auth_url

def linkedin_callback(code, redirect_uri=None):
    """
    Handle LinkedIn OAuth callback
    Call this from your '/auth/linkedin/callback' endpoint
    Returns user info dict or None if failed
    """
    if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
        return None

    resolved_redirect_uri = redirect_uri or LINKEDIN_REDIRECT_URI

    # Exchange authorization code for access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': resolved_redirect_uri,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET
    }
    
    token_response = requests.post(LINKEDIN_TOKEN_URL, data=token_data, timeout=15)
    if token_response.status_code != 200:
        return None
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    # Get user info using access token
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(LINKEDIN_USER_INFO_URL, headers=headers, timeout=15)
    
    if user_response.status_code != 200:
        return None
    
    user_info = user_response.json()
    
    # Return structured user data
    return {
        'linkedin_id': user_info.get('sub'),
        'linkedin_email': user_info.get('email'),
        'linkedin_name': f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip(),
        'linkedin_picture': user_info.get('picture'),
        'access_token': access_token
    }
