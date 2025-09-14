import streamlit as st
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import our integration modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Integrations - Creative Workflow AI OS",
    page_icon="🔗",
    layout="wide"
)

# Initialize session state
if 'db_manager' not in st.session_state:
    from core.database import DatabaseManager
    st.session_state.db_manager = DatabaseManager()

def initialize_integration_system():
    """Initialize the OAuth integration system"""
    try:
        from modules.integrations.oauth_manager import OAuthManager
        from modules.integrations.service_connectors import ServiceConnectorFactory
        
        if 'integration_system' not in st.session_state:
            st.session_state.integration_system = {
                'oauth_manager': OAuthManager(st.session_state.db_manager),
                'connector_factory': ServiceConnectorFactory()
            }
        return True
    except Exception as e:
        st.error(f"Failed to initialize integration system: {str(e)}")
        return False

def main():
    st.title("🔗 Deep Integrations")
    st.markdown("### OAuth 2.0 connections with third-party services for enhanced workflow automation")
    
    # Initialize integration system
    if not initialize_integration_system():
        st.error("Integration system unavailable")
        return
    
    integration_system = st.session_state.integration_system
    oauth_manager = integration_system['oauth_manager']
    
    # Tabs for different integration functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔌 Active Connections", 
        "➕ Add Integration", 
        "🚀 Quick Actions", 
        "📊 Integration Analytics",
        "⚙️ Management"
    ])
    
    with tab1:
        active_connections_tab(oauth_manager)
    
    with tab2:
        add_integration_tab(oauth_manager)
    
    with tab3:
        quick_actions_tab(oauth_manager, integration_system)
    
    with tab4:
        integration_analytics_tab(oauth_manager)
    
    with tab5:
        management_tab(oauth_manager)

def active_connections_tab(oauth_manager):
    """Display active OAuth connections"""
    st.header("🔌 Active Connections")
    
    try:
        connections = oauth_manager.get_active_connections()
        
        if connections:
            st.success(f"Found {len(connections)} active connections")
            
            # Display connections in a nice format
            for conn in connections:
                with st.expander(f"{conn['service_name'].title()} - {conn.get('service_username', 'Unknown User')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Service:** {conn['service_name'].title()}")
                        st.write(f"**Connected:** {conn['connected_at'][:10] if conn['connected_at'] else 'Unknown'}")
                        
                        # Status indicator
                        if conn.get('is_expired', False):
                            st.error("🔴 Token Expired")
                        else:
                            st.success("🟢 Active")
                    
                    with col2:
                        st.write(f"**Scopes:** {conn.get('scopes', 'N/A')}")
                        if conn.get('expires_at'):
                            st.write(f"**Expires:** {conn['expires_at'][:10]}")
                        else:
                            st.write("**Expires:** Never")
                    
                    with col3:
                        # Test connection
                        if st.button(f"Test Connection", key=f"test_{conn['id']}"):
                            with st.spinner("Testing connection..."):
                                test_result = oauth_manager.test_connection(conn['id'])
                                
                                if test_result['status'] == 'success':
                                    st.success(test_result['message'])
                                else:
                                    st.error(test_result['message'])
                        
                        # Revoke connection
                        if st.button(f"Revoke", key=f"revoke_{conn['id']}", type="secondary"):
                            if oauth_manager.revoke_connection(conn['id']):
                                st.success("Connection revoked")
                                st.rerun()
                            else:
                                st.error("Failed to revoke connection")
            
            # Connection summary chart
            if len(connections) > 1:
                st.subheader("📊 Connection Overview")
                
                service_counts = {}
                for conn in connections:
                    service = conn['service_name'].title()
                    service_counts[service] = service_counts.get(service, 0) + 1
                
                fig = px.pie(
                    values=list(service_counts.values()),
                    names=list(service_counts.keys()),
                    title="Connected Services"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No active connections found. Add your first integration in the 'Add Integration' tab!")
            
            # Show available services
            st.subheader("🌟 Available Services")
            
            services = [
                {"name": "GitHub", "icon": "🐙", "description": "Code repositories, issues, and project management"},
                {"name": "Linear", "icon": "📋", "description": "Issue tracking and project planning"},
                {"name": "Notion", "icon": "📝", "description": "Documentation and knowledge management"},
                {"name": "Google", "icon": "🔍", "description": "Drive, Calendar, and productivity tools"},
                {"name": "Slack", "icon": "💬", "description": "Team communication and notifications"}
            ]
            
            cols = st.columns(len(services))
            for i, service in enumerate(services):
                with cols[i]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 10px; margin: 10px;">
                        <h3>{service['icon']} {service['name']}</h3>
                        <p>{service['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
    except Exception as e:
        st.error(f"Error loading connections: {str(e)}")

def add_integration_tab(oauth_manager):
    """Add new OAuth integrations"""
    st.header("➕ Add Integration")
    
    # Service selection
    st.subheader("1. Choose Service")
    
    services = {
        "github": {
            "name": "GitHub",
            "icon": "🐙",
            "description": "Connect to GitHub for repository management, issue tracking, and code collaboration.",
            "capabilities": ["Repository access", "Issue management", "Code collaboration", "Project tracking"]
        },
        "linear": {
            "name": "Linear",
            "icon": "📋", 
            "description": "Connect to Linear for advanced project management and issue tracking.",
            "capabilities": ["Issue tracking", "Project planning", "Team management", "Workflow automation"]
        },
        "notion": {
            "name": "Notion",
            "icon": "📝",
            "description": "Connect to Notion for documentation, knowledge management, and database operations.",
            "capabilities": ["Page management", "Database queries", "Content creation", "Team collaboration"]
        },
        "google": {
            "name": "Google Workspace",
            "icon": "🔍",
            "description": "Connect to Google services including Drive, Calendar, and Gmail.",
            "capabilities": ["File management", "Calendar integration", "Email automation", "Document collaboration"]
        },
        "slack": {
            "name": "Slack",
            "icon": "💬",
            "description": "Connect to Slack for team communication and workflow notifications.",
            "capabilities": ["Message posting", "Channel management", "File sharing", "Workflow notifications"]
        }
    }
    
    selected_service = st.selectbox(
        "Select Service",
        options=list(services.keys()),
        format_func=lambda x: f"{services[x]['icon']} {services[x]['name']}"
    )
    
    if selected_service:
        service_info = services[selected_service]
        
        # Show service details
        st.markdown(f"### {service_info['icon']} {service_info['name']}")
        st.write(service_info['description'])
        
        st.write("**Capabilities:**")
        for capability in service_info['capabilities']:
            st.write(f"• {capability}")
        
        # OAuth setup
        st.subheader("2. OAuth Configuration")
        
        st.warning("⚠️ **Note:** You need to register your application with the service provider first to get Client ID and Client Secret.")
        
        with st.form("oauth_setup"):
            client_id = st.text_input("Client ID", help="OAuth Client ID from the service provider")
            client_secret = st.text_input("Client Secret", type="password", help="OAuth Client Secret from the service provider")
            redirect_uri = st.text_input("Redirect URI", value="http://localhost:5000/oauth/callback", help="Must match your registered redirect URI")
            user_id = st.text_input("User ID (optional)", help="Associate connection with specific user")
            
            if st.form_submit_button("Generate Authorization URL"):
                if client_id and client_secret:
                    try:
                        # Generate OAuth URL with PKCE
                        auth_result = oauth_manager.generate_auth_url(
                            selected_service, client_id, redirect_uri, user_id if user_id else None
                        )
                        
                        st.success("Authorization URL generated with PKCE security!")
                        st.code(auth_result["auth_url"], language="text")
                        
                        # Store state for reference
                        st.info(f"🔐 State parameter: `{auth_result['state']}`")
                        
                        st.markdown("### 3. Complete Authorization")
                        st.markdown("""
                        1. **Click the URL above** to authorize the application
                        2. **Complete the authorization** on the service provider's website
                        3. **Copy the authorization code** from the redirect URL
                        4. **Enter the code below** to complete the connection
                        """)
                        
                        # Store credentials in session for callback
                        st.session_state[f"oauth_creds_{selected_service}"] = {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "redirect_uri": redirect_uri
                        }
                        
                    except Exception as e:
                        st.error(f"Error generating authorization URL: {str(e)}")
                else:
                    st.error("Please enter both Client ID and Client Secret")
        
        # Authorization code exchange
        if f"oauth_creds_{selected_service}" in st.session_state:
            st.subheader("4. Complete Connection")
            
            with st.form("complete_oauth"):
                auth_code = st.text_input("Authorization Code", help="Code from the redirect URL after authorization")
                state = st.text_input("State", help="State parameter from the redirect URL")
                
                if st.form_submit_button("Complete Connection"):
                    if auth_code and state:
                        try:
                            creds = st.session_state[f"oauth_creds_{selected_service}"]
                            
                            # Exchange code for token
                            result = oauth_manager.exchange_code_for_token(
                                auth_code, state, creds["client_id"], creds["client_secret"]
                            )
                            
                            st.success(f"✅ Successfully connected to {service_info['name']}!")
                            st.write(f"**Connection ID:** {result['connection_id']}")
                            
                            # Clean up session
                            del st.session_state[f"oauth_creds_{selected_service}"]
                            
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"Error completing connection: {str(e)}")
                    else:
                        st.error("Please enter both Authorization Code and State")

def quick_actions_tab(oauth_manager, integration_system):
    """Quick actions using connected services"""
    st.header("🚀 Quick Actions")
    
    connections = oauth_manager.get_active_connections()
    
    if not connections:
        st.info("No active connections available. Please add integrations first.")
        return
    
    # Group connections by service
    services = {}
    for conn in connections:
        service = conn['service_name']
        if service not in services:
            services[service] = []
        services[service].append(conn)
    
    # Quick actions by service
    for service_name, service_connections in services.items():
        if service_connections:
            st.subheader(f"{service_name.title()} Actions")
            
            # Use the first active connection for demonstrations
            active_conn = next((c for c in service_connections if not c.get('is_expired', False)), None)
            
            if not active_conn:
                st.warning(f"All {service_name} connections are expired")
                continue
                
            connection_id = active_conn['id']
            
            try:
                # Create service connector
                connector = integration_system['connector_factory'].create_connector(
                    service_name, oauth_manager, connection_id
                )
                
                if service_name == "github":
                    github_quick_actions(connector)
                elif service_name == "linear":
                    linear_quick_actions(connector)
                elif service_name == "notion":
                    notion_quick_actions(connector)
                elif service_name == "google":
                    google_quick_actions(connector)
                elif service_name == "slack":
                    slack_quick_actions(connector)
                    
            except Exception as e:
                st.error(f"Error with {service_name} actions: {str(e)}")

def github_quick_actions(connector):
    """GitHub quick actions"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 List Repositories"):
            try:
                repos = connector.get_repositories()
                repo_df = pd.DataFrame([
                    {
                        "Name": repo["name"],
                        "Private": "🔒" if repo["private"] else "🌐",
                        "Language": repo.get("language", "N/A"),
                        "Stars": repo["stargazers_count"],
                        "Updated": repo["updated_at"][:10]
                    }
                    for repo in repos[:10]  # Show first 10
                ])
                st.dataframe(repo_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching repositories: {str(e)}")
    
    with col2:
        if st.button("👤 Get User Info"):
            try:
                user_info = connector.get_user_info()
                st.json({
                    "Username": user_info.get("login"),
                    "Name": user_info.get("name"),
                    "Public Repos": user_info.get("public_repos"),
                    "Followers": user_info.get("followers"),
                    "Following": user_info.get("following")
                })
            except Exception as e:
                st.error(f"Error fetching user info: {str(e)}")

def linear_quick_actions(connector):
    """Linear quick actions"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 List Teams"):
            try:
                teams = connector.get_teams()
                team_df = pd.DataFrame([
                    {
                        "Name": team["name"],
                        "Key": team["key"],
                        "Description": team.get("description", "")[:50] + "..." if team.get("description", "") else "N/A"
                    }
                    for team in teams
                ])
                st.dataframe(team_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching teams: {str(e)}")
    
    with col2:
        if st.button("📝 List Issues"):
            try:
                issues = connector.get_issues(limit=10)
                issue_df = pd.DataFrame([
                    {
                        "Title": issue["title"][:50] + "..." if len(issue["title"]) > 50 else issue["title"],
                        "State": issue["state"]["name"],
                        "Priority": issue.get("priority", "N/A"),
                        "Team": issue["team"]["name"],
                        "Assignee": issue["assignee"]["name"] if issue.get("assignee") else "Unassigned"
                    }
                    for issue in issues
                ])
                st.dataframe(issue_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching issues: {str(e)}")

def notion_quick_actions(connector):
    """Notion quick actions"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Search Pages"):
            try:
                pages = connector.search_pages()
                page_df = pd.DataFrame([
                    {
                        "Title": page.get("properties", {}).get("title", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")[:50],
                        "Type": page.get("object", "N/A"),
                        "Created": page.get("created_time", "")[:10] if page.get("created_time") else "N/A",
                        "Updated": page.get("last_edited_time", "")[:10] if page.get("last_edited_time") else "N/A"
                    }
                    for page in pages[:10]
                ])
                st.dataframe(page_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error searching pages: {str(e)}")
    
    with col2:
        if st.button("👤 Get User Info"):
            try:
                user_info = connector.get_user_info()
                st.json({
                    "Name": user_info.get("name"),
                    "Type": user_info.get("type"),
                    "Email": user_info.get("person", {}).get("email") if user_info.get("type") == "person" else "N/A"
                })
            except Exception as e:
                st.error(f"Error fetching user info: {str(e)}")

def google_quick_actions(connector):
    """Google quick actions"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 List Drive Files"):
            try:
                files = connector.list_drive_files(page_size=10)
                file_df = pd.DataFrame([
                    {
                        "Name": file.get("name", "Untitled"),
                        "Type": file.get("mimeType", "").split("/")[-1] if file.get("mimeType") else "Unknown",
                        "ID": file.get("id", "")[:20] + "..." if file.get("id") else "N/A"
                    }
                    for file in files
                ])
                st.dataframe(file_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching Drive files: {str(e)}")
    
    with col2:
        if st.button("📅 List Calendar Events"):
            try:
                from datetime import datetime, timedelta
                time_min = datetime.utcnow().isoformat() + "Z"
                time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
                
                events = connector.list_calendar_events(time_min=time_min, time_max=time_max, max_results=10)
                event_df = pd.DataFrame([
                    {
                        "Summary": event.get("summary", "No Title")[:40],
                        "Start": event.get("start", {}).get("dateTime", event.get("start", {}).get("date", ""))[:16],
                        "End": event.get("end", {}).get("dateTime", event.get("end", {}).get("date", ""))[:16]
                    }
                    for event in events
                ])
                st.dataframe(event_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching calendar events: {str(e)}")

def slack_quick_actions(connector):
    """Slack quick actions"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💬 List Channels"):
            try:
                channels = connector.get_channels()
                channel_df = pd.DataFrame([
                    {
                        "Name": f"#{channel.get('name', 'unknown')}",
                        "Members": channel.get("num_members", 0),
                        "Topic": channel.get("topic", {}).get("value", "")[:50] if channel.get("topic", {}).get("value") else "No topic",
                        "Private": "🔒" if channel.get("is_private") else "🌐"
                    }
                    for channel in channels[:10]
                ])
                st.dataframe(channel_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching channels: {str(e)}")
    
    with col2:
        if st.button("🔍 Test Auth"):
            try:
                auth_info = connector.test_auth()
                st.json({
                    "User": auth_info.get("user"),
                    "Team": auth_info.get("team"),
                    "URL": auth_info.get("url"),
                    "Bot ID": auth_info.get("bot_id")
                })
            except Exception as e:
                st.error(f"Error testing auth: {str(e)}")

def integration_analytics_tab(oauth_manager):
    """Integration usage analytics"""
    st.header("📊 Integration Analytics")
    
    connections = oauth_manager.get_active_connections()
    
    if not connections:
        st.info("No connections available for analytics")
        return
    
    # Connection metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Connections", len(connections))
    
    with col2:
        expired_count = sum(1 for c in connections if c.get('is_expired', False))
        st.metric("Expired Connections", expired_count)
    
    with col3:
        active_count = len(connections) - expired_count
        st.metric("Active Connections", active_count)
    
    # Service distribution
    service_counts = {}
    for conn in connections:
        service = conn['service_name'].title()
        service_counts[service] = service_counts.get(service, 0) + 1
    
    if service_counts:
        fig_services = px.bar(
            x=list(service_counts.keys()),
            y=list(service_counts.values()),
            title="Connections by Service",
            labels={"x": "Service", "y": "Connection Count"}
        )
        st.plotly_chart(fig_services, use_container_width=True)
    
    # Connection timeline
    connection_dates = [c.get('connected_at', '') for c in connections if c.get('connected_at')]
    if connection_dates:
        df_timeline = pd.DataFrame({
            'Date': [d[:10] for d in connection_dates],
            'Service': [c['service_name'].title() for c in connections if c.get('connected_at')]
        })
        
        timeline_counts = df_timeline.groupby(['Date', 'Service']).size().reset_index(name='Count')
        
        fig_timeline = px.line(
            timeline_counts,
            x='Date',
            y='Count',
            color='Service',
            title="Connection Timeline"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

def management_tab(oauth_manager):
    """Integration management and utilities"""
    st.header("⚙️ Management")
    
    # Connection cleanup
    st.subheader("🧹 Connection Cleanup")
    
    connections = oauth_manager.get_active_connections()
    expired_connections = [c for c in connections if c.get('is_expired', False)]
    
    if expired_connections:
        st.warning(f"Found {len(expired_connections)} expired connections")
        
        if st.button("Clean Up Expired Connections"):
            cleaned = 0
            for conn in expired_connections:
                if oauth_manager.revoke_connection(conn['id']):
                    cleaned += 1
            
            st.success(f"Cleaned up {cleaned} expired connections")
            st.rerun()
    else:
        st.success("No expired connections found")
    
    # Integration status
    st.subheader("📊 System Status")
    
    # Database status
    db_status = st.session_state.db_manager.check_connection()
    st.write(f"**Database Connection:** {'✅ Connected' if db_status else '❌ Disconnected'}")
    
    # OAuth system status
    st.write("**OAuth Manager:** ✅ Initialized")
    st.write("**Service Connectors:** ✅ Available")
    
    # Supported services
    st.subheader("🌐 Supported Services")
    
    supported_services = [
        "GitHub - Repository and issue management",
        "Linear - Project management and issue tracking", 
        "Notion - Documentation and knowledge base",
        "Google - Drive, Calendar, and productivity tools",
        "Slack - Team communication and notifications"
    ]
    
    for service in supported_services:
        st.write(f"• {service}")
    
    # Manual connection testing
    st.subheader("🔍 Manual Testing")
    
    if connections:
        test_connection_id = st.selectbox(
            "Select Connection to Test",
            options=[c['id'] for c in connections],
            format_func=lambda x: next(c['service_name'].title() for c in connections if c['id'] == x)
        )
        
        if st.button("Run Detailed Test"):
            with st.spinner("Testing connection..."):
                result = oauth_manager.test_connection(test_connection_id)
                
                if result['status'] == 'success':
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ {result['message']}")
                    
                st.json(result)

if __name__ == "__main__":
    main()