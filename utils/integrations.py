import os
import logging
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime
import json

class SlackIntegration:
    """
    Slack integration for notifications and communication
    """
    
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    async def send_message(self, text: str, blocks: List[Dict] = None, thread_ts: str = None) -> Dict[str, Any]:
        """Send message to Slack channel"""
        
        try:
            payload = {
                "channel": self.channel_id,
                "text": text
            }
            
            if blocks:
                payload["blocks"] = blocks
            
            if thread_ts:
                payload["thread_ts"] = thread_ts
            
            response = requests.post(
                f"{self.base_url}/chat.postMessage",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")
            
            return {
                "success": True,
                "message_ts": result.get("ts"),
                "channel": result.get("channel")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_project_update(self, project_name: str, status: str, details: str, priority: str = "normal") -> Dict[str, Any]:
        """Send formatted project update to Slack"""
        
        # Color coding based on status
        color_map = {
            "completed": "#28a745",
            "in_progress": "#ffc107", 
            "delayed": "#dc3545",
            "on_hold": "#6c757d"
        }
        
        color = color_map.get(status.lower(), "#007bff")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 Project Update: {project_name}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status.title()}"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*Priority:*\n{priority.title()}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{details}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        return await self.send_message(
            text=f"Project Update: {project_name} - {status}",
            blocks=blocks
        )
    
    async def send_agent_notification(self, agent_name: str, action: str, result: str, success: bool = True) -> Dict[str, Any]:
        """Send agent execution notification"""
        
        emoji = "✅" if success else "❌"
        color = "#28a745" if success else "#dc3545"
        
        text = f"{emoji} {agent_name}: {action}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{emoji} Agent Execution*\n*Agent:* {agent_name}\n*Action:* {action}\n*Result:* {result}"
                }
            }
        ]
        
        return await self.send_message(text=text, blocks=blocks)


class NotionIntegration:
    """
    Notion integration for project documentation and tracking
    """
    
    def __init__(self, integration_token: str, database_id: str):
        self.integration_token = integration_token
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {integration_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.logger = logging.getLogger(__name__)
    
    async def create_project_page(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project page in Notion"""
        
        try:
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Name": {
                        "title": [
                            {
                                "text": {
                                    "content": project_data.get("name", "Untitled Project")
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": project_data.get("status", "Planning")
                        }
                    },
                    "Client": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": project_data.get("client_name", "Unknown Client")
                                }
                            }
                        ]
                    },
                    "Start Date": {
                        "date": {
                            "start": project_data.get("start_date", datetime.now().isoformat()[:10])
                        }
                    }
                }
            }
            
            if project_data.get("end_date"):
                payload["properties"]["End Date"] = {
                    "date": {
                        "start": project_data["end_date"]
                    }
                }
            
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "page_id": result.get("id"),
                "url": result.get("url")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create Notion page: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_project_status(self, page_id: str, status: str, progress: int = None) -> Dict[str, Any]:
        """Update project status in Notion"""
        
        try:
            payload = {
                "properties": {
                    "Status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            }
            
            if progress is not None:
                payload["properties"]["Progress"] = {
                    "number": progress
                }
            
            response = requests.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "page_id": result.get("id"),
                "last_edited_time": result.get("last_edited_time")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update Notion page: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_project_note(self, page_id: str, note_content: str) -> Dict[str, Any]:
        """Add a note to project page"""
        
        try:
            payload = {
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": note_content
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            response = requests.patch(
                f"{self.base_url}/blocks/{page_id}/children",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "blocks_added": len(result.get("results", []))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add Notion note: {str(e)}")
            return {"success": False, "error": str(e)}


class JiraIntegration:
    """
    JIRA integration for task and project management
    """
    
    def __init__(self, jira_url: str, api_token: str, email: str = None):
        self.jira_url = jira_url.rstrip('/')
        self.api_token = api_token
        self.email = email or "api@example.com"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    def _get_auth(self):
        """Get authentication for JIRA API"""
        return (self.email, self.api_token)
    
    async def create_epic(self, project_key: str, epic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an epic in JIRA"""
        
        try:
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": epic_data.get("name", "Creative Project Epic"),
                    "description": epic_data.get("description", ""),
                    "issuetype": {"name": "Epic"},
                    "customfield_10011": epic_data.get("epic_name", epic_data.get("name", "Creative Project"))  # Epic Name field
                }
            }
            
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue",
                headers=self.headers,
                auth=self._get_auth(),
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "epic_key": result.get("key"),
                "epic_id": result.get("id")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create JIRA epic: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_task(self, project_key: str, task_data: Dict[str, Any], epic_key: str = None) -> Dict[str, Any]:
        """Create a task in JIRA"""
        
        try:
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": task_data.get("title", "Creative Task"),
                    "description": task_data.get("description", ""),
                    "issuetype": {"name": "Task"},
                    "priority": {"name": task_data.get("priority", "Medium").title()}
                }
            }
            
            # Link to epic if provided
            if epic_key:
                payload["fields"]["customfield_10014"] = epic_key  # Epic Link field
            
            # Set assignee if provided
            if task_data.get("assignee"):
                payload["fields"]["assignee"] = {"emailAddress": task_data["assignee"]}
            
            # Set due date if provided
            if task_data.get("due_date"):
                payload["fields"]["duedate"] = task_data["due_date"]
            
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue",
                headers=self.headers,
                auth=self._get_auth(),
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "task_key": result.get("key"),
                "task_id": result.get("id")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create JIRA task: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_task_status(self, issue_key: str, status: str) -> Dict[str, Any]:
        """Update task status in JIRA"""
        
        try:
            # First, get available transitions
            transitions_response = requests.get(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                headers=self.headers,
                auth=self._get_auth(),
                timeout=10
            )
            
            transitions_response.raise_for_status()
            transitions = transitions_response.json()
            
            # Find the transition ID for the desired status
            transition_id = None
            for transition in transitions.get("transitions", []):
                if transition["to"]["name"].lower() == status.lower():
                    transition_id = transition["id"]
                    break
            
            if not transition_id:
                return {"success": False, "error": f"No transition found for status: {status}"}
            
            # Execute the transition
            payload = {
                "transition": {"id": transition_id}
            }
            
            response = requests.post(
                f"{self.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                headers=self.headers,
                auth=self._get_auth(),
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            
            return {
                "success": True,
                "issue_key": issue_key,
                "new_status": status
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update JIRA task status: {str(e)}")
            return {"success": False, "error": str(e)}


class IntegrationManager:
    """
    Central manager for all external integrations
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.integrations = {}
        
        # Initialize available integrations
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize enabled integrations"""
        
        # Slack Integration
        if self.config.is_integration_enabled('slack'):
            try:
                self.integrations['slack'] = SlackIntegration(
                    self.config.integrations.slack_bot_token,
                    self.config.integrations.slack_channel_id
                )
                self.logger.info("Slack integration initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Slack integration: {str(e)}")
        
        # Notion Integration
        if self.config.is_integration_enabled('notion'):
            try:
                self.integrations['notion'] = NotionIntegration(
                    self.config.integrations.notion_token,
                    self.config.integrations.notion_database_id
                )
                self.logger.info("Notion integration initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Notion integration: {str(e)}")
        
        # JIRA Integration
        if self.config.is_integration_enabled('jira'):
            try:
                self.integrations['jira'] = JiraIntegration(
                    self.config.integrations.jira_url,
                    self.config.integrations.jira_token
                )
                self.logger.info("JIRA integration initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize JIRA integration: {str(e)}")
    
    def get_integration(self, name: str):
        """Get specific integration by name"""
        return self.integrations.get(name.lower())
    
    def is_available(self, integration_name: str) -> bool:
        """Check if integration is available"""
        return integration_name.lower() in self.integrations
    
    def get_available_integrations(self) -> List[str]:
        """Get list of available integrations"""
        return list(self.integrations.keys())
    
    async def notify_project_update(self, project_data: Dict[str, Any], channels: List[str] = None) -> Dict[str, Any]:
        """Send project update to specified channels"""
        
        channels = channels or ['slack', 'notion']
        results = {}
        
        for channel in channels:
            if channel == 'slack' and self.is_available('slack'):
                result = await self.integrations['slack'].send_project_update(
                    project_data.get('name', 'Unknown Project'),
                    project_data.get('status', 'Unknown'),
                    project_data.get('description', 'No details provided')
                )
                results['slack'] = result
            
            elif channel == 'notion' and self.is_available('notion'):
                result = await self.integrations['notion'].update_project_status(
                    project_data.get('notion_page_id', ''),
                    project_data.get('status', 'In Progress'),
                    project_data.get('progress', None)
                )
                results['notion'] = result
        
        return results
    
    async def create_project_tasks(self, project_data: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create project tasks across integrated platforms"""
        
        results = {}
        
        # Create in JIRA if available
        if self.is_available('jira'):
            jira_results = []
            
            # Create epic first
            epic_result = await self.integrations['jira'].create_epic(
                project_data.get('jira_project_key', 'CW'),
                {
                    'name': project_data.get('name', 'Creative Project'),
                    'description': project_data.get('description', '')
                }
            )
            
            if epic_result.get('success'):
                epic_key = epic_result['epic_key']
                
                # Create tasks under the epic
                for task in tasks:
                    task_result = await self.integrations['jira'].create_task(
                        project_data.get('jira_project_key', 'CW'),
                        task,
                        epic_key
                    )
                    jira_results.append(task_result)
            
            results['jira'] = {
                'epic': epic_result,
                'tasks': jira_results
            }
        
        # Create in Notion if available
        if self.is_available('notion'):
            notion_result = await self.integrations['notion'].create_project_page(project_data)
            results['notion'] = notion_result
        
        return results
    
    async def send_agent_notification(self, agent_name: str, action: str, result: str, success: bool = True) -> Dict[str, Any]:
        """Send agent execution notification to available channels"""
        
        results = {}
        
        if self.is_available('slack'):
            slack_result = await self.integrations['slack'].send_agent_notification(
                agent_name, action, result, success
            )
            results['slack'] = slack_result
        
        return results
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        
        status = {
            'total_available': len(self.integrations),
            'integrations': {}
        }
        
        for name, integration in self.integrations.items():
            status['integrations'][name] = {
                'available': True,
                'type': type(integration).__name__,
                'initialized_at': datetime.now().isoformat()
            }
        
        # Add unavailable integrations
        all_possible = ['slack', 'notion', 'jira']
        for integration_name in all_possible:
            if integration_name not in self.integrations:
                status['integrations'][integration_name] = {
                    'available': False,
                    'reason': 'Not configured'
                }
        
        return status
