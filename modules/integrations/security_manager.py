"""
Security Manager - Handles secure token storage and encryption for OAuth integrations
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional

class SecurityManager:
    """Manages encryption and decryption of sensitive OAuth data"""
    
    def __init__(self):
        self._cipher_suite = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption key from environment - REQUIRED for security"""
        
        # Get encryption key from environment - REQUIRED
        key_data = os.getenv('OAUTH_ENCRYPTION_KEY')
        
        if not key_data:
            raise ValueError(
                "OAUTH_ENCRYPTION_KEY environment variable is required for secure token storage. "
                "Generate a secure key using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )
        
        try:
            # Validate and use the provided key
            key = base64.urlsafe_b64decode(key_data.encode())
            self._cipher_suite = Fernet(key)
        except Exception as e:
            raise ValueError(f"Invalid OAUTH_ENCRYPTION_KEY format. Key must be a valid Fernet key: {e}")
    
    def generate_secure_key(self) -> str:
        """Generate a new secure encryption key for initial setup"""
        # This method is for initial key generation only
        # The generated key should be stored securely in environment variables
        return Fernet.generate_key().decode()
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token for secure storage"""
        if not self._cipher_suite:
            raise Exception("Encryption not initialized - OAUTH_ENCRYPTION_KEY required")
        
        if not token:
            return ""
        
        try:
            encrypted_token = self._cipher_suite.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted_token).decode()
        except Exception as e:
            raise Exception(f"Failed to encrypt token: {e}")
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token for use"""
        if not self._cipher_suite:
            raise Exception("Encryption not initialized")
        
        if not encrypted_token:
            return ""
        
        try:
            # Try to decrypt (new format)
            encrypted_data = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted_token = self._cipher_suite.decrypt(encrypted_data)
            return decrypted_token.decode()
        except Exception:
            # If decryption fails, assume it's plaintext (backward compatibility)
            return encrypted_token
    
    def is_token_encrypted(self, token: str) -> bool:
        """Check if a token is encrypted"""
        if not token:
            return False
        
        try:
            # Try to base64 decode - encrypted tokens are base64 encoded
            base64.urlsafe_b64decode(token.encode())
            return True
        except Exception:
            return False
    
    def migrate_plaintext_token(self, plaintext_token: str) -> str:
        """Migrate a plaintext token to encrypted format"""
        if self.is_token_encrypted(plaintext_token):
            return plaintext_token  # Already encrypted
        
        return self.encrypt_token(plaintext_token)
    
    def generate_secure_state(self) -> str:
        """Generate a cryptographically secure state parameter"""
        import secrets
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    
    def hash_client_secret(self, client_secret: str) -> str:
        """Hash client secret for secure storage (optional)"""
        import hashlib
        return hashlib.sha256(client_secret.encode()).hexdigest()
    
    def verify_client_secret(self, client_secret: str, stored_hash: str) -> bool:
        """Verify client secret against stored hash"""
        return self.hash_client_secret(client_secret) == stored_hash