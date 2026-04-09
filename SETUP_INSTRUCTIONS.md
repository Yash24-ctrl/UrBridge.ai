# Setup Instructions for AI Resume Analyzer

This document explains how to properly configure your AI Resume Analyzer application with real credentials.

## Google OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google People API
4. Go to the "Credentials" section
5. Click "Create Credentials" and select "OAuth 2.0 Client IDs"
6. Configure the OAuth consent screen if prompted
7. For Application type, select "Web application"
8. Set Authorized redirect URIs to: `http://localhost:5000/auth/google/callback`
9. Copy the Client ID and Client Secret
10. Add these values to your `.env` file:
    - `GOOGLE_CLIENT_ID=` (paste the client ID here)
    - `GOOGLE_CLIENT_SECRET=` (paste the client secret here)

## LinkedIn OAuth Setup

1. Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Create a new app or select an existing one
3. In the app settings, go to the "Auth" tab
4. Set the authorized redirect URLs to: `http://localhost:5000/auth/linkedin/callback`
5. Copy the Client ID and Client Secret
6. Add these values to your `.env` file:
    - `LINKEDIN_CLIENT_ID=` (paste the client ID here)
    - `LINKEDIN_CLIENT_SECRET=` (paste the client secret here)

## Email Configuration (for login notifications)

1. If using Gmail, enable 2-factor authentication on your Google account
2. Go to Google Account settings
3. Under Security, find "App passwords"
4. Generate an app password for "Mail"
5. Use that 16-character password in your `.env` file:
    - `EMAIL_USER=` (your email address)
    - `EMAIL_PASS=` (the 16-character app password)

## Security Settings

1. Generate a strong secret key for production:
   - You can use Python to generate one: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Add this to your `.env` file: `SECRET_KEY=` (paste the generated key)
   - Also set `JWT_SECRET=` to a similar strong value

## Final Steps

1. After setting up all credentials in your `.env` file, restart your application
2. Make sure your `.env` file is NOT committed to version control (it's already in `.gitignore`)

## Troubleshooting

- If you get "invalid_client" errors, double-check that you've replaced all placeholder values in the `.env` file with actual credentials
- Make sure the redirect URIs match exactly what you configured in the Google Cloud Console and LinkedIn Developer Portal
- Ensure that your Google project has the required APIs enabled (Google+ API and Google People API)