"""
End-to-End Encryption (E2EE) Module for AI Resume Analyzer
Implements asymmetric encryption for secure data transmission and storage
"""

import sqlite3
import json
import base64
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature
import secrets

# Database configuration
DATABASE = 'users.db'

class E2EEManager:
    """Manages End-to-End Encryption for the application"""
    
    def __init__(self):
        """Initialize the E2EE manager"""
        self._ensure_keys_table_exists()
    
    def _ensure_keys_table_exists(self):
        """Ensure the user_keys table exists in the database"""
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            # Create user_keys table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS user_keys (
                    user_id INTEGER PRIMARY KEY,
                    public_key TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error ensuring keys table exists: {str(e)}")
    
    def generate_user_keys(self, user_id):
        """
        Generate RSA key pair for a user
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            tuple: (private_key_pem, public_key_pem)
        """
        try:
            # Generate RSA private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Get the public key
            public_key = private_key.public_key()
            
            # Serialize private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Serialize public key
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Store public key in database
            self._store_public_key(user_id, public_pem.decode('utf-8'))
            
            return private_pem.decode('utf-8'), public_pem.decode('utf-8')
        except Exception as e:
            print(f"Error generating user keys: {str(e)}")
            raise
    
    def _store_public_key(self, user_id, public_key_pem):
        """
        Store user's public key in the database
        
        Args:
            user_id (int): The user's ID
            public_key_pem (str): The public key in PEM format
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            # Insert or update public key
            c.execute('''
                INSERT OR REPLACE INTO user_keys (user_id, public_key)
                VALUES (?, ?)
            ''', (user_id, public_key_pem))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error storing public key: {str(e)}")
            raise
    
    def get_user_public_key(self, user_id):
        """
        Retrieve a user's public key from the database
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            str: The public key in PEM format, or None if not found
        """
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            
            c.execute('SELECT public_key FROM user_keys WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error retrieving public key: {str(e)}")
            return None
    
    def encrypt(self, data, receiver_public_key_pem):
        """
        Encrypt data using the receiver's public key with hybrid encryption
        
        Args:
            data (str or bytes): The data to encrypt
            receiver_public_key_pem (str): The receiver's public key in PEM format
            
        Returns:
            str: Base64 encoded encrypted data
        """
        try:
            # Convert data to bytes if it's a string
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Load receiver's public key
            receiver_public_key = serialization.load_pem_public_key(
                receiver_public_key_pem.encode('utf-8')
            )
            
            # Generate a random symmetric key for AES
            symmetric_key = secrets.token_bytes(32)  # 256-bit key
            
            # Generate a random IV for AES
            iv = secrets.token_bytes(16)  # 128-bit IV
            
            # Encrypt data with AES
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            
            # Pad data to be multiple of 16 bytes (AES block size)
            pad_length = 16 - (len(data) % 16)
            padded_data = data + bytes([pad_length] * pad_length)
            
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # Encrypt symmetric key with receiver's public key
            encrypted_symmetric_key = receiver_public_key.encrypt(
                symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Combine encrypted symmetric key, IV, and encrypted data
            combined_data = encrypted_symmetric_key + iv + encrypted_data
            
            # Encode as base64 for storage/transmission
            return base64.b64encode(combined_data).decode('utf-8')
        except Exception as e:
            print(f"Error encrypting data: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data_b64, user_private_key_pem):
        """
        Decrypt data using the user's private key
        
        Args:
            encrypted_data_b64 (str): Base64 encoded encrypted data
            user_private_key_pem (str): The user's private key in PEM format
            
        Returns:
            str: Decrypted data
        """
        try:
            # Decode base64 data
            combined_data = base64.b64decode(encrypted_data_b64.encode('utf-8'))
            
            # Load user's private key
            user_private_key = serialization.load_pem_private_key(
                user_private_key_pem.encode('utf-8'),
                password=None
            )
            
            # Extract components (assuming RSA-2048, so encrypted key is 256 bytes)
            encrypted_symmetric_key = combined_data[:256]
            iv = combined_data[256:272]  # 16 bytes IV
            encrypted_data = combined_data[272:]
            
            # Decrypt symmetric key with user's private key
            symmetric_key = user_private_key.decrypt(
                encrypted_symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data with AES
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            
            decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            pad_length = decrypted_padded_data[-1]
            decrypted_data = decrypted_padded_data[:-pad_length]
            
            return decrypted_data.decode('utf-8')
        except Exception as e:
            print(f"Error decrypting data: {str(e)}")
            raise
    
    def encrypt_for_user(self, data, receiver_user_id):
        """
        Encrypt data for a specific user by their user ID
        
        Args:
            data (str): The data to encrypt
            receiver_user_id (int): The receiver's user ID
            
        Returns:
            str: Base64 encoded encrypted data, or None if user not found
        """
        try:
            # Get receiver's public key
            receiver_public_key = self.get_user_public_key(receiver_user_id)
            
            if not receiver_public_key:
                print(f"No public key found for user {receiver_user_id}")
                return None
            
            # Encrypt data
            return self.encrypt(data, receiver_public_key)
        except Exception as e:
            print(f"Error encrypting for user: {str(e)}")
            return None
    
    def handle_corrupted_data(self, encrypted_data_b64, user_private_key_pem):
        """
        Handle corrupted or tampered encrypted data with fallback mechanisms
        
        Args:
            encrypted_data_b64 (str): Base64 encoded encrypted data
            user_private_key_pem (str): The user's private key in PEM format
            
        Returns:
            str: Decrypted data or error message
        """
        try:
            return self.decrypt(encrypted_data_b64, user_private_key_pem)
        except Exception as e:
            # Log the error for debugging
            print(f"Corrupted data detected: {str(e)}")
            
            # Return a safe error message instead of the actual error
            return "ERROR: Data is corrupted or tampered. Please contact support."

# Global instance
e2ee_manager = E2EEManager()

# Convenience functions
def encrypt(data, receiver_public_key):
    """
    Encrypt data for a receiver
    
    Args:
        data (str): The data to encrypt
        receiver_public_key (str): The receiver's public key in PEM format
        
    Returns:
        str: Base64 encoded encrypted data
    """
    return e2ee_manager.encrypt(data, receiver_public_key)

def decrypt(encrypted_data, user_private_key):
    """
    Decrypt data with user's private key
    
    Args:
        encrypted_data (str): Base64 encoded encrypted data
        user_private_key (str): The user's private key in PEM format
        
    Returns:
        str: Decrypted data
    """
    return e2ee_manager.decrypt(encrypted_data, user_private_key)

def encrypt_for_user(data, receiver_user_id):
    """
    Encrypt data for a specific user by their user ID
    
    Args:
        data (str): The data to encrypt
        receiver_user_id (int): The receiver's user ID
        
    Returns:
        str: Base64 encoded encrypted data
    """
    return e2ee_manager.encrypt_for_user(data, receiver_user_id)

def handle_corrupted_data(encrypted_data, user_private_key):
    """
    Handle corrupted or tampered encrypted data
    
    Args:
        encrypted_data (str): Base64 encoded encrypted data
        user_private_key (str): The user's private key in PEM format
        
    Returns:
        str: Decrypted data or error message
    """
    return e2ee_manager.handle_corrupted_data(encrypted_data, user_private_key)

def generate_user_keys(user_id):
    """
    Generate RSA key pair for a user
    
    Args:
        user_id (int): The user's ID
        
    Returns:
        tuple: (private_key_pem, public_key_pem)
    """
    return e2ee_manager.generate_user_keys(user_id)

def get_user_public_key(user_id):
    """
    Get a user's public key
    
    Args:
        user_id (int): The user's ID
        
    Returns:
        str: The public key in PEM format
    """
    return e2ee_manager.get_user_public_key(user_id)