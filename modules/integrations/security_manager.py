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
        """Initialize encryption key from environment or generate new one"""
        
        # Try to get encryption key from environment
        key_data = os.getenv('OAUTH_ENCRYPTION_KEY')
        
        if key_data:
            # Use existing key
            try:
                key = base64.urlsafe_b64decode(key_data.encode())
                self._cipher_suite = Fernet(key)
            except Exception:
                # If key is invalid, generate new one
                self._generate_new_key()
        else:
            # Generate new encryption key
            self._generate_new_key()
    
    def _generate_new_key(self):
        """Generate a new encryption key"""
        
        # Use a default password for key derivation (in production, use secure random)
        password = os.getenv('OAUTH_MASTER_PASSWORD', 'default_creative_workflow_password').encode()
        salt = os.getenv('OAUTH_SALT', 'creative_workflow_salt_2024').encode()
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self._cipher_suite = Fernet(key)
        
        # Store key for future use (in production, use secure key storage)
        key_b64 = base64.urlsafe_b64encode(key).decode()
        print(f"Generated new encryption key. Set OAUTH_ENCRYPTION_KEY={key_b64} in environment")
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token for secure storage"""
        if not self._cipher_suite:
            raise Exception("Encryption not initialized")
        
        if not token:
            return ""
        
        try:
            encrypted_token = self._cipher_suite.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted_token).decode()
        except Exception as e:
            print(f"Error encrypting token: {e}")
            return token  # Fallback to plaintext (not secure)
    
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