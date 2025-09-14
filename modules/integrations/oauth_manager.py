"""
OAuth 2.0 Manager - Handles authentication flows for third-party integrations
"""
import json
import uuid
import secrets
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from core.database import DatabaseManager
from .security_manager import SecurityManager

class OAuthManager:
    """Manages OAuth 2.0 authentication flows for third-party services"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.security_manager = SecurityManager()
        self._ensure_tables()
        
        # OAuth configurations for different services
        self.oauth_configs = {
            "github": {
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "scopes": ["repo", "user:email"]
            },
            "linear": {
                "auth_url": "https://linear.app/oauth/authorize",
                "token_url": "https://api.linear.app/oauth/token",
                "scopes": ["read", "write"]
            },
            "notion": {
                "auth_url": "https://api.notion.com/v1/oauth/authorize",
                "token_url": "https://api.notion.com/v1/oauth/token",
                "scopes": ["read_content", "update_content"]
            },
            "google": {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "scopes": ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/calendar"]
            },
            "slack": {
                "auth_url": "https://slack.com/oauth/v2/authorize",
                "token_url": "https://slack.com/api/oauth.v2.access",
                "scopes": ["channels:read", "chat:write", "files:read"]
            }
        }
    
    def _ensure_tables(self):
        """Create OAuth tables if they don't exist"""
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS oauth_connections (
                        id TEXT PRIMARY KEY,
                        service_name TEXT NOT NULL,
                        user_id TEXT,
                        access_token TEXT NOT NULL,
                        refresh_token TEXT,
                        token_expires_at TIMESTAMP,
                        scopes TEXT,
                        service_user_id TEXT,
                        service_username TEXT,
                        connection_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        token_encrypted BOOLEAN DEFAULT FALSE,
                        pkce_verifier TEXT
                    )
                """))
                
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS oauth_states (
                        state_id TEXT PRIMARY KEY,
                        service_name TEXT NOT NULL,
                        redirect_uri TEXT NOT NULL,
                        user_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        used BOOLEAN DEFAULT FALSE
                    )
                """))
                
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not create OAuth tables: {e}")
    
    def generate_auth_url(self, service_name: str, client_id: str, 
                         redirect_uri: str, user_id: Optional[str] = None) -> Dict[str, str]:
        """Generate OAuth 2.0 authorization URL with PKCE support"""
        
        if service_name not in self.oauth_configs:
            raise ValueError(f"Unsupported service: {service_name}")
        
        config = self.oauth_configs[service_name]
        state = self.security_manager.generate_secure_state()
        
        # Generate PKCE parameters for enhanced security
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = self._generate_code_challenge(code_verifier)
        
        # Store state for verification (including PKCE verifier)
        self._store_oauth_state(state, service_name, redirect_uri, user_id, code_verifier)
        
        # Build authorization URL
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(config["scopes"]),
            "state": state,
            "response_type": "code",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        # Service-specific parameters
        if service_name == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        elif service_name == "github":
            params["allow_signup"] = "true"
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{config['auth_url']}?{query_string}"
        
        return {
            "auth_url": auth_url,
            "state": state,
            "code_verifier": code_verifier
        }
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        import hashlib
        import base64
        
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    def _store_oauth_state(self, state: str, service_name: str, redirect_uri: str, 
                          user_id: Optional[str], code_verifier: Optional[str] = None):
        """Store OAuth state for verification"""
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # 10 minute expiry
        
        try:
            with self.db_manager.engine.connect() as conn:
                # First check if table has PKCE column
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS oauth_states (
                        state_id TEXT PRIMARY KEY,
                        service_name TEXT NOT NULL,
                        redirect_uri TEXT NOT NULL,
                        user_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        pkce_verifier TEXT
                    )
                """))
                
                conn.execute(text("""
                    INSERT INTO oauth_states (state_id, service_name, redirect_uri, user_id, expires_at, pkce_verifier)
                    VALUES (:state_id, :service_name, :redirect_uri, :user_id, :expires_at, :pkce_verifier)
                """), {
                    'state_id': state,
                    'service_name': service_name,
                    'redirect_uri': redirect_uri,
                    'user_id': user_id,
                    'expires_at': expires_at,
                    'pkce_verifier': code_verifier
                })
                conn.commit()
        except Exception as e:
            print(f"Error storing OAuth state: {e}")
    
    def exchange_code_for_token(self, code: str, state: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        
        # Verify state
        state_data = self._verify_state(state)
        if not state_data:
            raise ValueError("Invalid or expired state")
        
        service_name = state_data['service_name']
        redirect_uri = state_data['redirect_uri']
        
        if service_name not in self.oauth_configs:
            raise ValueError(f"Unsupported service: {service_name}")
        
        config = self.oauth_configs[service_name]
        
        # Prepare token request with PKCE
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        # Add PKCE verifier if available
        if state_data.get('pkce_verifier'):
            token_data["code_verifier"] = state_data['pkce_verifier']
        
        headers = {"Accept": "application/json"}
        
        # Make token request
        response = requests.post(config["token_url"], data=token_data, headers=headers)
        response.raise_for_status()
        
        token_response = response.json()
        
        # Store connection
        connection_id = self._store_connection(service_name, token_response, state_data)
        
        return {
            "connection_id": connection_id,
            "service_name": service_name,
            "access_token": token_response.get("access_token"),
            "status": "connected"
        }
    
    def _verify_state(self, state: str) -> Optional[Dict[str, Any]]:
        """Verify OAuth state and return state data"""
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT service_name, redirect_uri, user_id, expires_at, used, pkce_verifier
                    FROM oauth_states 
                    WHERE state_id = :state_id
                """), {'state_id': state})
                
                row = result.fetchone()
                
                if not row:
                    return None
                
                # Check if expired
                if row.expires_at < datetime.utcnow():
                    return None
                
                # Check if already used
                if row.used:
                    return None
                
                # Mark as used (one-time use enforcement)
                conn.execute(text("""
                    UPDATE oauth_states 
                    SET used = TRUE 
                    WHERE state_id = :state_id
                """), {'state_id': state})
                conn.commit()
                
                return {
                    'service_name': row.service_name,
                    'redirect_uri': row.redirect_uri,
                    'user_id': row.user_id,
                    'pkce_verifier': row.pkce_verifier
                }
                
        except Exception as e:
            print(f"Error verifying state: {e}")
            return None
    
    def _store_connection(self, service_name: str, token_response: Dict[str, Any], state_data: Dict[str, Any]) -> str:
        """Store OAuth connection"""
        connection_id = str(uuid.uuid4())
        
        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in")
        
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Encrypt tokens for secure storage
        encrypted_access_token = self.security_manager.encrypt_token(access_token) if access_token else None
        encrypted_refresh_token = self.security_manager.encrypt_token(refresh_token) if refresh_token else None
        
        try:
            with self.db_manager.engine.connect() as conn:
                # Ensure table has encryption columns
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS oauth_connections (
                        id TEXT PRIMARY KEY,
                        service_name TEXT NOT NULL,
                        user_id TEXT,
                        access_token TEXT NOT NULL,
                        refresh_token TEXT,
                        token_expires_at TIMESTAMP,
                        scopes TEXT,
                        service_user_id TEXT,
                        service_username TEXT,
                        connection_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        token_encrypted BOOLEAN DEFAULT FALSE,
                        pkce_verifier TEXT
                    )
                """))
                
                conn.execute(text("""
                    INSERT INTO oauth_connections 
                    (id, service_name, user_id, access_token, refresh_token, token_expires_at, 
                     scopes, connection_data, token_encrypted)
                    VALUES (:id, :service_name, :user_id, :access_token, :refresh_token, 
                            :expires_at, :scopes, :connection_data, :token_encrypted)
                """), {
                    'id': connection_id,
                    'service_name': service_name,
                    'user_id': state_data.get('user_id'),
                    'access_token': encrypted_access_token,
                    'refresh_token': encrypted_refresh_token,
                    'expires_at': expires_at,
                    'scopes': token_response.get("scope", ""),
                    'connection_data': json.dumps({k: v for k, v in token_response.items() 
                                                 if k not in ['access_token', 'refresh_token']}),
                    'token_encrypted': True
                })
                conn.commit()
                
            return connection_id
            
        except Exception as e:
            print(f"Error storing connection: {e}")
            raise
    
    def get_active_connections(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active OAuth connections"""
        try:
            with self.db_manager.engine.connect() as conn:
                query = """
                    SELECT id, service_name, service_username, scopes, created_at, token_expires_at
                    FROM oauth_connections 
                    WHERE is_active = TRUE
                """
                params = {}
                
                if user_id:
                    query += " AND user_id = :user_id"
                    params['user_id'] = user_id
                
                query += " ORDER BY created_at DESC"
                
                result = conn.execute(text(query), params)
                rows = result.fetchall()
                
                connections = []
                for row in rows:
                    connections.append({
                        'id': row.id,
                        'service_name': row.service_name,
                        'service_username': row.service_username,
                        'scopes': row.scopes,
                        'connected_at': row.created_at.isoformat() if row.created_at else None,
                        'expires_at': row.token_expires_at.isoformat() if row.token_expires_at else None,
                        'is_expired': row.token_expires_at < datetime.utcnow() if row.token_expires_at else False
                    })
                
                return connections
                
        except Exception as e:
            print(f"Error getting connections: {e}")
            return []
    
    def get_connection_token(self, connection_id: str) -> Optional[str]:
        """Get access token for a connection (refresh if needed)"""
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT access_token, refresh_token, token_expires_at, service_name, token_encrypted
                    FROM oauth_connections 
                    WHERE id = :connection_id AND is_active = TRUE
                """), {'connection_id': connection_id})
                
                row = result.fetchone()
                
                if not row:
                    return None
                
                # Decrypt token if it's encrypted
                access_token = row.access_token
                if hasattr(row, 'token_encrypted') and row.token_encrypted:
                    access_token = self.security_manager.decrypt_token(access_token)
                
                # Check if token needs refresh
                if row.token_expires_at and row.token_expires_at < datetime.utcnow():
                    if row.refresh_token:
                        # Decrypt refresh token if needed
                        refresh_token = row.refresh_token
                        if hasattr(row, 'token_encrypted') and row.token_encrypted:
                            refresh_token = self.security_manager.decrypt_token(refresh_token)
                        
                        # Attempt to refresh token
                        new_token = self._refresh_token(connection_id, refresh_token, row.service_name)
                        if new_token:
                            return new_token
                    
                    # Token expired and can't refresh
                    return None
                
                return access_token
                
        except Exception as e:
            print(f"Error getting connection token: {e}")
            return None
    
    def _refresh_token(self, connection_id: str, refresh_token: str, service_name: str) -> Optional[str]:
        """Refresh OAuth token"""
        # This would implement token refresh logic for each service
        # For now, return None (manual re-authorization required)
        return None
    
    def revoke_connection(self, connection_id: str) -> bool:
        """Revoke/deactivate an OAuth connection"""
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE oauth_connections 
                    SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :connection_id
                """), {'connection_id': connection_id})
                conn.commit()
                
                return True
                
        except Exception as e:
            print(f"Error revoking connection: {e}")
            return False
    
    def test_connection(self, connection_id: str) -> Dict[str, Any]:
        """Test an OAuth connection by making a simple API call"""
        token = self.get_connection_token(connection_id)
        
        if not token:
            return {"status": "error", "message": "No valid token"}
        
        try:
            # Get service name
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT service_name FROM oauth_connections 
                    WHERE id = :connection_id
                """), {'connection_id': connection_id})
                
                row = result.fetchone()
                if not row:
                    return {"status": "error", "message": "Connection not found"}
                
                service_name = row.service_name
            
            # Make test API call based on service
            if service_name == "github":
                response = requests.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {token}"}
                )
            elif service_name == "linear":
                response = requests.post(
                    "https://api.linear.app/graphql",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"query": "{ viewer { id name } }"}
                )
            elif service_name == "notion":
                response = requests.get(
                    "https://api.notion.com/v1/users/me",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Notion-Version": "2022-06-28"
                    }
                )
            elif service_name == "google":
                response = requests.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
            elif service_name == "slack":
                response = requests.get(
                    "https://slack.com/api/auth.test",
                    headers={"Authorization": f"Bearer {token}"}
                )
            else:
                return {"status": "error", "message": f"Unsupported service: {service_name}"}
            
            if response.status_code == 200:
                return {"status": "success", "message": "Connection is working"}
            else:
                return {"status": "error", "message": f"API call failed: {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Test failed: {str(e)}"}