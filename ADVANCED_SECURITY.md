# Advanced Security Features Documentation

## Overview
This document describes the advanced security features implemented in the AI Resume Analyzer to enhance data protection, privacy, and system security.

> **Note:** For security features to work properly, you need to configure your `.env` file with proper credentials as detailed in [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md).

## Features Implemented

### 1. Enhanced Data Encryption
- **Resume Content Encryption**: All resume content is encrypted using Fernet (AES) encryption before storage
- **Secure Key Management**: Uses encryption keys from environment variables
- **Automatic Encryption/Decryption**: Transparent handling of encrypted content during storage and retrieval

### 2. Input Sanitization
- **HTML Escaping**: All user inputs are sanitized using HTML escaping to prevent XSS attacks
- **Validation**: Input validation prevents malicious content injection
- **Safe Processing**: All form inputs are sanitized before processing

### 3. Secure File Upload
- **File Type Validation**: Validates file extensions and content types
- **Size Limitation**: Enforces maximum file size limits (10MB)
- **Malicious Content Detection**: Scans for potentially dangerous content
- **Secure Storage**: Files are stored in a controlled upload directory

### 4. Rate Limiting
- **Login Protection**: Limits login attempts to prevent brute force attacks (10 attempts per 5 minutes)
- **Registration Protection**: Limits registration attempts (5 attempts per 5 minutes)
- **Customizable Limits**: Configurable rate limits per endpoint
- **IP-based Tracking**: Tracks requests by IP address

### 5. Security Logging
- **Audit Trail**: Comprehensive logging of security-related events
- **Event Types**: Logs login attempts, file uploads, access violations, etc.
- **User Tracking**: Links events to specific user IDs when available
- **File-based Logging**: Logs stored in `security_audit.log`

### 6. Session Security
- **Login Requirement**: Critical endpoints require authentication
- **Decorator-based Protection**: Uses `@require_login` decorator for route protection
- **Automatic Redirect**: Unauthenticated users redirected to login page

### 7. Password Security
- **Salted Hashing**: Passwords hashed with salt using PBKDF2 (SHA-256)
- **High Iterations**: 100,000 iterations for strong security
- **Secure Verification**: Safe password verification process

### 8. Data Privacy Compliance
- **GDPR Ready**: Implements privacy controls and audit logging
- **Data Minimization**: Follows data minimization policy
- **PII Protection**: Personal Identifiable Information is protected

## Implementation Details

### Encryption Module (`security/advanced_security.py`)
```python
# Key functions:
- encrypt_resume_content(content) - Encrypt resume content
- decrypt_resume_content(encrypted_content) - Decrypt resume content
- sanitize_input(input_string) - Sanitize user inputs
- secure_file_upload(file) - Validate file uploads
- rate_limit(max_requests, window) - Apply rate limiting
- log_security_event(event_type, user_id, details) - Log security events
- require_login - Decorator for login requirement
- hash_password_with_salt(password) - Secure password hashing
- verify_password_with_salt(password, stored_hash) - Password verification
- generate_secure_token() - Generate secure tokens
```

### Integration Points

#### 1. File Upload (`/pdf_upload`)
- Uses `secure_file_upload()` for validation
- Encrypts resume content with `encrypt_resume_content()`
- Stores encrypted content in database
- Decrypts content with `get_decrypted_resume_content()` when displaying

#### 2. Form Processing
- All form inputs sanitized with `sanitize_input()`
- Applies to both manual input and job matching forms

#### 3. Authentication
- Login rate limited with `@rate_limit`
- Registration rate limited with `@rate_limit`
- Protected routes use `@require_login`

#### 4. History Management
- Retrieves encrypted content and decrypts for display
- Uses `get_decrypted_resume_content()` function

## Security Policies Enforced

### 1. Data Minimization Policy
- Only essential data is stored
- PII is removed or anonymized
- Resume content is encrypted at rest

### 2. Pseudonymization and Encryption Standard
- User identifiers hashed with SHA-256
- Sensitive data encrypted with Fernet AES
- Keys stored in environment variables

### 3. Access Control
- Authentication required for sensitive operations
- Session-based access control
- Rate limiting to prevent abuse

## Configuration Requirements

### Environment Variables
- `ENCRYPTION_KEY` - Fernet encryption key (required for encryption features)
- `SECRET_KEY` - Flask session key (existing requirement)

### File Permissions
- `security_audit.log` requires write permissions
- Upload directory requires read/write permissions

## Testing

Run the following command to verify all security features work correctly:
```bash
python test_advanced_security.py
```

## Compliance

This implementation helps meet:
- **GDPR**: Privacy controls and audit logging
- **Data Protection**: Encryption and access controls
- **Security Standards**: Input validation and rate limiting
- **Industry Best Practices**: Secure coding and data handling

## Maintenance

### Regular Tasks
- Monitor `security_audit.log` for suspicious activity
- Rotate encryption keys periodically
- Update dependencies to address security vulnerabilities

### Monitoring
- Track rate limit violations
- Monitor failed login attempts
- Review file upload logs
- Audit data access patterns

## Error Handling

Security features implement proper error handling:
- Graceful degradation when encryption fails
- Secure fallbacks for authentication
- Proper error logging without information disclosure
- User-friendly error messages

## Performance Considerations

- Encryption/decryption operations are efficient
- Rate limiting uses in-memory storage (consider Redis for production)
- Input sanitization has minimal performance impact
- Security logging is asynchronous to avoid blocking