# Security Features in AI Resume Analyzer

This document outlines the security features implemented in the AI Resume Analyzer application.

> **Note:** For security features to work properly, you need to configure your `.env` file with proper credentials as detailed in [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md).

## Data Encryption

### Fernet AES Encryption
- Sensitive user data is encrypted using Fernet AES encryption
- Encryption keys are stored in environment variables
- Data is encrypted both at rest and in transit

### SHA-256 Hashing
- User identifiers (emails) are hashed using SHA-256
- Hashed values are used for database lookups
- Original identifiers are not stored in plain text

## Data Minimization & Anonymization

### PII Removal Policy
- Personal Identifiable Information (PII) is removed from analysis data
- Only essential fields are stored: years of experience, skills, and education level
- Names, addresses, and other personal details are stripped from resume data

### Anonymization Process
- Resume data is anonymized before processing
- User identifiers are hashed for analytics while preserving privacy

## Implementation Details

### Database Security
- Email addresses are stored as SHA-256 hashes
- Sensitive fields can be encrypted using Fernet if needed
- All database queries use parameterized statements to prevent SQL injection

### Authentication Security
- OAuth login flows use hashed email comparisons
- Password reset functionality works with hashed emails
- Session management follows security best practices

### File Security
- Uploaded resume files can be encrypted before storage
- Temporary files are automatically cleaned up
- File upload validation prevents malicious content

## Configuration

### Environment Variables
The following environment variables are required for security features:

```
ENCRYPTION_KEY=your_fernet_encryption_key_here
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
```

Generate an encryption key using:
```bash
python generate_key.py
```

## Compliance

These security measures comply with the project's Data Minimization Policy and Pseudonymization Standard, ensuring that PII such as names and emails are removed or anonymized, with only specific fields like years of experience, skills, and education level being stored.