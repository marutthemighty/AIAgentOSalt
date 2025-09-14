"""
Service Connectors - Specific implementations for each third-party service
"""
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from .oauth_manager import OAuthManager

class BaseServiceConnector:
    """Base class for service connectors"""
    
    def __init__(self, oauth_manager: OAuthManager, connection_id: str):
        self.oauth_manager = oauth_manager
        self.connection_id = connection_id
        self.service_name = ""
        self.base_url = ""
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        token = self.oauth_manager.get_connection_token(self.connection_id)
        if not token:
            raise Exception("No valid token for connection")
        
        return {"Authorization": f"Bearer {token}"}
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated API request"""
        headers = self._get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response

class GitHubConnector(BaseServiceConnector):
    """GitHub API connector"""
    
    def __init__(self, oauth_manager: OAuthManager, connection_id: str):
        super().__init__(oauth_manager, connection_id)
        self.service_name = "github"
        self.base_url = "https://api.github.com"
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        response = self._make_request("GET", "/user")
        return response.json()
    
    def get_repositories(self, type: str = "owner") -> List[Dict[str, Any]]:
        """Get user repositories"""
        response = self._make_request("GET", f"/user/repos?type={type}&sort=updated")
        return response.json()
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create a new repository"""
        data = {
            "name": name,
            "description": description,
            "private": private
        }
        response = self._make_request("POST", "/user/repos", json=data)
        return response.json()
    
    def get_issues(self, repo_owner: str, repo_name: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get repository issues"""
        response = self._make_request("GET", f"/repos/{repo_owner}/{repo_name}/issues?state={state}")
        return response.json()
    
    def create_issue(self, repo_owner: str, repo_name: str, title: str, body: str = "") -> Dict[str, Any]:
        """Create a new issue"""
        data = {
            "title": title,
            "body": body
        }
        response = self._make_request("POST", f"/repos/{repo_owner}/{repo_name}/issues", json=data)
        return response.json()

class LinearConnector(BaseServiceConnector):
    """Linear API connector"""
    
    def __init__(self, oauth_manager: OAuthManager, connection_id: str):
        super().__init__(oauth_manager, connection_id)
        self.service_name = "linear"
        self.base_url = "https://api.linear.app/graphql"
    
    def _graphql_request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GraphQL request to Linear API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = self._make_request("POST", "", json=payload)
        return response.json()
    
    def get_viewer_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        query = """
        {
            viewer {
                id
                name
                email
                displayName
            }
        }
        """
        return self._graphql_request(query)
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get user teams"""
        query = """
        {
            teams {
                nodes {
                    id
                    name
                    description
                    key
                }
            }
        }
        """
        result = self._graphql_request(query)
        return result.get("data", {}).get("teams", {}).get("nodes", [])
    
    def get_issues(self, team_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get issues"""
        filter_clause = f'filter: {{ team: {{ id: {{ eq: "{team_id}" }} }} }}' if team_id else ""
        
        query = f"""
        {{
            issues(first: {limit} {filter_clause}) {{
                nodes {{
                    id
                    title
                    description
                    state {{
                        name
                    }}
                    priority
                    assignee {{
                        name
                    }}
                    team {{
                        name
                    }}
                    createdAt
                    updatedAt
                }}
            }}
        }}
        """
        result = self._graphql_request(query)
        return result.get("data", {}).get("issues", {}).get("nodes", [])
    
    def create_issue(self, team_id: str, title: str, description: str = "", priority: int = 0) -> Dict[str, Any]:
        """Create a new issue"""
        query = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    title
                    identifier
                }
            }
        }
        """
        variables = {
            "input": {
                "teamId": team_id,
                "title": title,
                "description": description,
                "priority": priority
            }
        }
        return self._graphql_request(query, variables)

class NotionConnector(BaseServiceConnector):
    """Notion API connector"""
    
    def __init__(self, oauth_manager: OAuthManager, connection_id: str):
        super().__init__(oauth_manager, connection_id)
        self.service_name = "notion"
        self.base_url = "https://api.notion.com/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers with Notion version"""
        headers = super()._get_headers()
        headers["Notion-Version"] = "2022-06-28"
        return headers
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        response = self._make_request("GET", "/users/me")
        return response.json()
    
    def search_pages(self, query: str = "", page_size: int = 100) -> List[Dict[str, Any]]:
        """Search for pages"""
        data = {
            "page_size": page_size
        }
        if query:
            data["query"] = query
        
        response = self._make_request("POST", "/search", json=data)
        return response.json().get("results", [])
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get page content"""
        response = self._make_request("GET", f"/pages/{page_id}")
        return response.json()
    
    def create_page(self, parent_id: str, title: str, content: List[Dict] = None) -> Dict[str, Any]:
        """Create a new page"""
        data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        }
        if content:
            data["children"] = content
        
        response = self._make_request("POST", "/pages", json=data)
        return response.json()
    
    def get_database(self, database_id: str) -> Dict[str, Any]:
        """Get database information"""
        response = self._make_request("GET", f"/databases/{database_id}")
        return response.json()
    
    def query_database(self, database_id: str, filter_obj: Optional[Dict] = None, 
                      sorts: Optional[List[Dict]] = None, page_size: int = 100) -> List[Dict[str, Any]]:
        """Query database entries"""
        data = {"page_size": page_size}
        if filter_obj:
            data["filter"] = filter_obj
        if sorts:
            data["sorts"] = sorts
        
        response = self._make_request("POST", f"/databases/{database_id}/query", json=data)
        return response.json().get("results", [])

class GoogleConnector(BaseServiceConnector):
    """Google APIs connector"""
    
    def __init__(self, oauth_manager: OAuthManager, connection_id: str):
        super().__init__(oauth_manager, connection_id)
        self.service_name = "google"
        self.base_url = "https://www.googleapis.com"
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        response = self._make_request("GET", "/oauth2/v2/userinfo")
        return response.json()
    
    def list_drive_files(self, page_size: int = 100, q: str = "") -> List[Dict[str, Any]]:
        """List Google Drive files"""
        params = {"pageSize": page_size}
        if q:
            params["q"] = q
        
        response = self._make_request("GET", "/drive/v3/files", params=params)
        return response.json().get("files", [])
    
    def upload_to_drive(self, file_name: str, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Upload file to Google Drive"""
        # This is a simplified version - full implementation would use multipart upload
        metadata = {"name": file_name}
        
        files = {
            'metadata': (None, json.dumps(metadata), 'application/json'),
            'data': (file_name, file_content, mime_type)
        }
        
        # Note: This would need proper multipart handling in production
        response = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers={"Authorization": f"Bearer {self.oauth_manager.get_connection_token(self.connection_id)}"},
            files=files
        )
        response.raise_for_status()
        return response.json()
    
    def list_calendar_events(self, calendar_id: str = "primary", time_min: Optional[str] = None, 
                           time_max: Optional[str] = None, max_results: int = 250) -> List[Dict[str, Any]]:
        """List calendar events"""
        params = {"maxResults": max_results, "singleEvents": True, "orderBy": "startTime"}
        if time_min:
            params["timeMin"] = time_min
        if time_max:
            params["timeMax"] = time_max
        
        response = self._make_request("GET", f"/calendar/v3/calendars/{calendar_id}/events", params=params)
        return response.json().get("items", [])
    
    def create_calendar_event(self, calendar_id: str = "primary", summary: str = "", 
                            start_time: str = "", end_time: str = "", description: str = "") -> Dict[str, Any]:
        """Create calendar event"""
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"}
        }
        
        response = self._make_request("POST", f"/calendar/v3/calendars/{calendar_id}/events", json=event)
        return response.json()

class SlackConnector(BaseServiceConnector):
    """Slack API connector"""
    
    def __init__(self, oauth_manager: OAuthManager, connection_id: str):
        super().__init__(oauth_manager, connection_id)
        self.service_name = "slack"
        self.base_url = "https://slack.com/api"
    
    def test_auth(self) -> Dict[str, Any]:
        """Test authentication"""
        response = self._make_request("GET", "/auth.test")
        return response.json()
    
    def get_channels(self, types: str = "public_channel,private_channel") -> List[Dict[str, Any]]:
        """Get channels list"""
        params = {"types": types, "limit": 1000}
        response = self._make_request("GET", "/conversations.list", params=params)
        return response.json().get("channels", [])
    
    def send_message(self, channel: str, text: str, blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send message to channel"""
        data = {"channel": channel, "text": text}
        if blocks:
            data["blocks"] = blocks
        
        response = self._make_request("POST", "/chat.postMessage", json=data)
        return response.json()
    
    def get_channel_history(self, channel: str, limit: int = 100, 
                          oldest: Optional[str] = None, latest: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get channel message history"""
        params = {"channel": channel, "limit": limit}
        if oldest:
            params["oldest"] = oldest
        if latest:
            params["latest"] = latest
        
        response = self._make_request("GET", "/conversations.history", params=params)
        return response.json().get("messages", [])
    
    def upload_file(self, channels: str, file_content: bytes, filename: str, 
                   title: str = "", initial_comment: str = "") -> Dict[str, Any]:
        """Upload file to Slack"""
        files = {"file": (filename, file_content)}
        data = {
            "channels": channels,
            "title": title,
            "initial_comment": initial_comment
        }
        
        # Note: Slack file upload requires form data, not JSON
        headers = self._get_headers()
        response = requests.post(
            f"{self.base_url}/files.upload",
            headers=headers,
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()

class ServiceConnectorFactory:
    """Factory for creating service connectors"""
    
    @staticmethod
    def create_connector(service_name: str, oauth_manager: OAuthManager, connection_id: str) -> BaseServiceConnector:
        """Create appropriate connector for service"""
        connectors = {
            "github": GitHubConnector,
            "linear": LinearConnector,
            "notion": NotionConnector,
            "google": GoogleConnector,
            "slack": SlackConnector
        }
        
        if service_name not in connectors:
            raise ValueError(f"Unsupported service: {service_name}")
        
        return connectors[service_name](oauth_manager, connection_id)