#!/usr/bin/env python3
"""
Generate an encryption key for the AI Resume Analyzer security module
"""

from cryptography.fernet import Fernet

def generate_encryption_key():
    """Generate a new encryption key for Fernet"""
    key = Fernet.generate_key()
    return key.decode()

if __name__ == "__main__":
    print("Generated Encryption Key:")
    print(generate_encryption_key())
    print("\nAdd this key to your .env file as:")
    print("ENCRYPTION_KEY=your_generated_key_here")