#!/usr/bin/env python3
"""
OAuth Framework Validation Test
Tests all the critical fixes implemented for the OAuth 2.0 integration framework.
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sqlite3

# Add modules to path
sys.path.append('.')
sys.path.append('modules')

from core.database import DatabaseManager
from modules.integrations.oauth_manager import OAuthManager
from modules.integrations.security_manager import SecurityManager
from modules.integrations.service_connectors import ServiceConnectorFactory


class TestOAuthFrameworkFixes(unittest.TestCase):
    """Test suite for OAuth framework fixes"""
    
    def setUp(self):
        """Set up test environment"""
        # Use existing database manager - OAuth tests don't need isolated DB
        self.db_manager = DatabaseManager()
        
    def tearDown(self):
        """Clean up test environment"""
        pass  # No cleanup needed for shared database
    
    def test_1_security_manager_requires_encryption_key(self):
        """Test that SecurityManager requires OAUTH_ENCRYPTION_KEY"""
        print("✓ Testing SecurityManager requires OAUTH_ENCRYPTION_KEY...")
        
        # Test without OAUTH_ENCRYPTION_KEY - should raise ValueError
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                SecurityManager()
            self.assertIn("OAUTH_ENCRYPTION_KEY", str(context.exception))
        
        # Test with valid OAUTH_ENCRYPTION_KEY - should work
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        with patch.dict(os.environ, {'OAUTH_ENCRYPTION_KEY': test_key}):
            security_manager = SecurityManager()
            self.assertIsNotNone(security_manager._cipher_suite)
        
        print("   ✅ SecurityManager properly requires OAUTH_ENCRYPTION_KEY")
    
    def test_2_pkce_schema_consistency(self):
        """Test that PKCE schema is consistent across table creation"""
        print("✓ Testing PKCE schema consistency...")
        
        # Mock environment for security manager
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        with patch.dict(os.environ, {'OAUTH_ENCRYPTION_KEY': test_key}):
            oauth_manager = OAuthManager(self.db_manager)
            
            # Check that both table creation methods create consistent schema
            with self.db_manager.engine.connect() as conn:
                # Get table info for oauth_states
                result = conn.execute("PRAGMA table_info(oauth_states)")
                columns = {row[1]: row[2] for row in result.fetchall()}
                
                # Verify pkce_verifier column exists
                self.assertIn('pkce_verifier', columns)
                self.assertEqual(columns['pkce_verifier'], 'TEXT')
        
        print("   ✅ PKCE schema is consistent with pkce_verifier column")
    
    def test_3_url_encoding_fix(self):
        """Test that URL encoding uses urllib.parse.urlencode"""
        print("✓ Testing URL encoding fix...")
        
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        with patch.dict(os.environ, {'OAUTH_ENCRYPTION_KEY': test_key}):
            oauth_manager = OAuthManager(self.db_manager)
            
            # Test URL generation with special characters
            auth_data = oauth_manager.generate_auth_url(
                service_name="github",
                client_id="test_client",
                redirect_uri="https://example.com/callback?param=value&other=test"
            )
            
            # Verify URL is properly encoded
            auth_url = auth_data['auth_url']
            self.assertIn("redirect_uri=https%3A//example.com/callback%3Fparam%3Dvalue%26other%3Dtest", auth_url)
            self.assertIn("scope=repo%20user%3Aemail", auth_url)  # Space should be encoded as %20
        
        print("   ✅ URL encoding properly uses urllib.parse.urlencode")
    
    def test_4_service_connector_factory(self):
        """Test ServiceConnectorFactory implementation"""
        print("✓ Testing ServiceConnectorFactory implementation...")
        
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        with patch.dict(os.environ, {'OAUTH_ENCRYPTION_KEY': test_key}):
            oauth_manager = OAuthManager(self.db_manager)
            
            # Test all supported services
            supported_services = ["github", "linear", "notion", "google", "slack"]
            
            for service in supported_services:
                connector = ServiceConnectorFactory.create_connector(
                    service_name=service,
                    oauth_manager=oauth_manager,
                    connection_id="test_connection"
                )
                self.assertEqual(connector.service_name, service)
            
            # Test unsupported service
            with self.assertRaises(ValueError):
                ServiceConnectorFactory.create_connector(
                    service_name="unsupported_service",
                    oauth_manager=oauth_manager,
                    connection_id="test_connection"
                )
        
        print("   ✅ ServiceConnectorFactory supports all required services including Slack")
    
    def test_5_http_timeout_configuration(self):
        """Test that HTTP timeouts are properly configured"""
        print("✓ Testing HTTP timeout configuration...")
        
        from modules.integrations.service_connectors import BaseServiceConnector
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        
        with patch.dict(os.environ, {'OAUTH_ENCRYPTION_KEY': test_key}):
            oauth_manager = OAuthManager(self.db_manager)
            
            # Create a base connector to test timeout behavior
            connector = BaseServiceConnector(oauth_manager, "test_connection")
            connector.base_url = "https://httpbin.org"
            
            # Mock the oauth_manager to return a test token
            with patch.object(oauth_manager, 'get_connection_token', return_value='test_token'):
                # Mock requests to capture timeout parameter
                with patch('modules.integrations.service_connectors.requests.request') as mock_request:
                    mock_response = MagicMock()
                    mock_response.raise_for_status.return_value = None
                    mock_request.return_value = mock_response
                    
                    # Make a request
                    connector._make_request("GET", "/test")
                    
                    # Verify timeout was set
                    mock_request.assert_called_once()
                    call_kwargs = mock_request.call_args[1]
                    self.assertIn('timeout', call_kwargs)
                    self.assertEqual(call_kwargs['timeout'], 30)
        
        print("   ✅ HTTP requests have proper timeout configuration")

    def test_6_oauth_workflow_integration(self):
        """Test complete OAuth workflow integration"""
        print("✓ Testing OAuth workflow integration...")
        
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        with patch.dict(os.environ, {'OAUTH_ENCRYPTION_KEY': test_key}):
            oauth_manager = OAuthManager(self.db_manager)
            
            # Test auth URL generation
            auth_data = oauth_manager.generate_auth_url(
                service_name="github",
                client_id="test_client_id",
                redirect_uri="https://example.com/callback"
            )
            
            # Verify all required components are present
            self.assertIn('auth_url', auth_data)
            self.assertIn('state', auth_data)
            self.assertIn('code_verifier', auth_data)
            
            # Verify URL contains PKCE parameters
            auth_url = auth_data['auth_url']
            self.assertIn('code_challenge=', auth_url)
            self.assertIn('code_challenge_method=S256', auth_url)
            
            # Test state storage and retrieval
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    "SELECT * FROM oauth_states WHERE state_id = ?", 
                    (auth_data['state'],)
                )
                state_row = result.fetchone()
                self.assertIsNotNone(state_row)
                self.assertEqual(state_row[6], auth_data['code_verifier'])  # pkce_verifier column
        
        print("   ✅ OAuth workflow integration is working correctly")


def run_oauth_validation():
    """Run OAuth framework validation tests"""
    print("🔍 Running OAuth Framework Validation Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOAuthFrameworkFixes)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    print("\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All OAuth framework fixes are working correctly!")
        return True
    else:
        print("\n⚠️  Some tests failed. OAuth framework needs attention.")
        return False


if __name__ == "__main__":
    success = run_oauth_validation()
    sys.exit(0 if success else 1)