"""
Test script for End-to-End Encryption (E2EE) functionality
"""

from e2ee import E2EEManager, encrypt, decrypt, generate_user_keys, get_user_public_key

def test_e2ee():
    """Test the E2EE functionality"""
    print("Testing End-to-End Encryption functionality...")
    
    # Create E2EE manager
    e2ee = E2EEManager()
    
    # Test data
    test_data = "This is a secret message that should be encrypted!"
    print(f"Original data: {test_data}")
    
    # Generate keys for sender and receiver
    print("\nGenerating keys for sender and receiver...")
    sender_private_key, sender_public_key = generate_user_keys(1)  # User ID 1
    receiver_private_key, receiver_public_key = generate_user_keys(2)  # User ID 2
    
    print("Sender public key stored in database:", get_user_public_key(1) is not None)
    print("Receiver public key stored in database:", get_user_public_key(2) is not None)
    
    # Encrypt data using receiver's public key
    print("\nEncrypting data for receiver...")
    encrypted_data = encrypt(test_data, receiver_public_key)
    print(f"Encrypted data (base64): {encrypted_data[:50]}...")
    
    # Decrypt data using receiver's private key
    print("\nDecrypting data with receiver's private key...")
    decrypted_data = decrypt(encrypted_data, receiver_private_key)
    print(f"Decrypted data: {decrypted_data}")
    
    # Verify the data matches
    if test_data == decrypted_data:
        print("\n✅ Encryption/Decryption test PASSED!")
    else:
        print("\n❌ Encryption/Decryption test FAILED!")
    
    # Test encryption for user by user ID
    print("\nTesting encryption for user by ID...")
    encrypted_for_user = e2ee.encrypt_for_user(test_data, 2)  # Encrypt for user ID 2
    decrypted_for_user = decrypt(encrypted_for_user, receiver_private_key)
    
    if test_data == decrypted_for_user:
        print("✅ User-based encryption test PASSED!")
    else:
        print("❌ User-based encryption test FAILED!")
    
    # Test corrupted data handling
    print("\nTesting corrupted data handling...")
    corrupted_data = encrypted_data[:-5] + "XXXXX"  # Corrupt the encrypted data
    result = e2ee.handle_corrupted_data(corrupted_data, receiver_private_key)
    print(f"Result for corrupted data: {result}")

if __name__ == "__main__":
    test_e2ee()