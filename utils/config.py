import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    pool_size: int = 10
    pool_timeout: int = 30
    echo: bool = False

@dataclass
class AIConfig:
    """AI service configuration settings"""
    api_key: str
    model: str = "gemini-2.5-flash"
    fallback_model: str = "gemini-2.5-pro"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3

@dataclass
class IntegrationConfig:
    """External integration configuration"""
    slack_bot_token: Optional[str] = None
    slack_channel_id: Optional[str] = None
    notion_token: Optional[str] = None
    notion_database_id: Optional[str] = None
    jira_url: Optional[str] = None
    jira_token: Optional[str] = None

class Config:
    """
    Central configuration management for the Creative Workflow AI OS
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        
        # Database Configuration
        database_url = os.getenv('DATABASE_URL', 'sqlite:///creative_workflow.db')
        self.database = DatabaseConfig(
            url=database_url,
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30')),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
        )
        
        # AI Configuration
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            self.logger.warning("GEMINI_API_KEY not found in environment variables")
        
        self.ai = AIConfig(
            api_key=gemini_api_key or '',
            model=os.getenv('AI_MODEL', 'gemini-2.5-flash'),
            fallback_model=os.getenv('AI_FALLBACK_MODEL', 'gemini-2.5-pro'),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '4000')),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.7')),
            timeout=int(os.getenv('AI_TIMEOUT', '30')),
            max_retries=int(os.getenv('AI_MAX_RETRIES', '3'))
        )
        
        # Integration Configuration
        self.integrations = IntegrationConfig(
            slack_bot_token=os.getenv('SLACK_BOT_TOKEN'),
            slack_channel_id=os.getenv('SLACK_CHANNEL_ID'),
            notion_token=os.getenv('NOTION_INTEGRATION_SECRET'),
            notion_database_id=os.getenv('NOTION_DATABASE_ID'),
            jira_url=os.getenv('JIRA_URL'),
            jira_token=os.getenv('JIRA_TOKEN')
        )
        
        # Application Configuration
        self.app = {
            'name': 'Creative Workflow AI OS',
            'version': '1.0.0',
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'timezone': os.getenv('TIMEZONE', 'UTC'),
            'max_file_size': int(os.getenv('MAX_FILE_SIZE', '10485760')),  # 10MB
            'allowed_file_types': os.getenv('ALLOWED_FILE_TYPES', 'jpg,jpeg,png,gif,pdf,doc,docx,txt,csv').split(',')
        }
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup application logging"""
        
        log_level = getattr(logging, self.app['log_level'].upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set specific loggers
        if not self.app['debug']:
            # Reduce noise from third-party libraries in production
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('google').setLevel(logging.WARNING)
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        return self.database
    
    def get_ai_config(self) -> AIConfig:
        """Get AI configuration"""
        return self.ai
    
    def get_integration_config(self) -> IntegrationConfig:
        """Get integration configuration"""
        return self.integrations
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.app
    
    def is_integration_enabled(self, integration: str) -> bool:
        """Check if a specific integration is enabled"""
        
        integration_checks = {
            'slack': self.integrations.slack_bot_token and self.integrations.slack_channel_id,
            'notion': self.integrations.notion_token and self.integrations.notion_database_id,
            'jira': self.integrations.jira_url and self.integrations.jira_token
        }
        
        return bool(integration_checks.get(integration.lower(), False))
    
    def get_enabled_integrations(self) -> list:
        """Get list of enabled integrations"""
        
        enabled = []
        
        if self.is_integration_enabled('slack'):
            enabled.append('slack')
        if self.is_integration_enabled('notion'):
            enabled.append('notion')
        if self.is_integration_enabled('jira'):
            enabled.append('jira')
        
        return enabled
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'integrations_available': self.get_enabled_integrations()
        }
        
        # Check critical configuration
        if not self.ai.api_key:
            validation_results['errors'].append('GEMINI_API_KEY is required')
            validation_results['valid'] = False
        
        # Check database URL format
        if not self.database.url:
            validation_results['errors'].append('DATABASE_URL is required')
            validation_results['valid'] = False
        
        # Warnings for missing integrations
        if not self.is_integration_enabled('slack'):
            validation_results['warnings'].append('Slack integration not configured (SLACK_BOT_TOKEN, SLACK_CHANNEL_ID)')
        
        if not self.is_integration_enabled('notion'):
            validation_results['warnings'].append('Notion integration not configured (NOTION_INTEGRATION_SECRET, NOTION_DATABASE_ID)')
        
        if not self.is_integration_enabled('jira'):
            validation_results['warnings'].append('JIRA integration not configured (JIRA_URL, JIRA_TOKEN)')
        
        return validation_results
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for debugging"""
        
        return {
            'python_version': __import__('sys').version,
            'environment_variables': {
                'DATABASE_URL': '***' if self.database.url else 'Not set',
                'GEMINI_API_KEY': '***' if self.ai.api_key else 'Not set',
                'SLACK_BOT_TOKEN': '***' if self.integrations.slack_bot_token else 'Not set',
                'NOTION_INTEGRATION_SECRET': '***' if self.integrations.notion_token else 'Not set',
                'JIRA_URL': self.integrations.jira_url or 'Not set',
                'DEBUG': str(self.app['debug']),
                'LOG_LEVEL': self.app['log_level']
            },
            'integrations_status': {
                'slack': self.is_integration_enabled('slack'),
                'notion': self.is_integration_enabled('notion'),
                'jira': self.is_integration_enabled('jira')
            }
        }
    
    def reload_config(self):
        """Reload configuration from environment variables"""
        
        self.logger.info("Reloading configuration...")
        self._load_config()
        self.logger.info("Configuration reloaded successfully")
    
    def export_config_template(self) -> str:
        """Export configuration template for .env file"""
        
        template = """# Creative Workflow AI OS Configuration Template

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/creative_workflow
# Or for local development:
# DATABASE_URL=sqlite:///creative_workflow.db

# AI Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional AI Settings
AI_MODEL=gemini-2.5-flash
AI_FALLBACK_MODEL=gemini-2.5-pro
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7
AI_TIMEOUT=30
AI_MAX_RETRIES=3

# Slack Integration (Optional)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=your-channel-id

# Notion Integration (Optional)
NOTION_INTEGRATION_SECRET=secret_your_notion_integration_secret
NOTION_DATABASE_ID=your_notion_database_id

# JIRA Integration (Optional)
JIRA_URL=https://your-domain.atlassian.net
JIRA_TOKEN=your_jira_api_token

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
TIMEZONE=UTC
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,pdf,doc,docx,txt,csv

# Database Pool Settings
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30
DB_ECHO=false
"""
        
        return template

# Global configuration instance
config = Config()
