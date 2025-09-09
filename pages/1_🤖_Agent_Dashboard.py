import streamlit as st
import asyncio
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Agent Dashboard - Creative Workflow AI OS",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    from core.agent_orchestrator import AgentOrchestrator
    st.session_state.orchestrator = AgentOrchestrator()

if 'db_manager' not in st.session_state:
    from core.database import DatabaseManager
    st.session_state.db_manager = DatabaseManager()

def main():
    st.title("🤖 Agent Dashboard")
    st.markdown("### Monitor and manage all AI agents")
    
    # Get agent status
    agent_status = st.session_state.orchestrator.get_agent_status()
    system_metrics = st.session_state.orchestrator.get_system_metrics()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_agents = len([s for s in agent_status.values() if s == 'active'])
        st.metric("Active Agents", active_agents, delta=f"/{len(agent_status)}")
    
    with col2:
        queue_size = system_metrics.get('message_queue_size', 0)
        st.metric("Message Queue", queue_size)
    
    with col3:
        ai_status = "Online" if system_metrics.get('ai_service_status', False) else "Offline"
        st.metric("AI Service", ai_status)
    
    with col4:
        db_status = "Connected" if st.session_state.db_manager.check_connection() else "Offline"
        st.metric("Database", db_status)
    
    st.divider()
    
    # Agent Status Grid
    st.subheader("🔧 Agent Status")
    
    # Create agent status DataFrame
    agent_data = []
    for agent_name, status in agent_status.items():
        agent = st.session_state.orchestrator.get_agent(agent_name)
        capabilities = agent.get_capabilities() if agent else {}
        
        agent_data.append({
            'Agent': agent_name.replace('_', ' ').title(),
            'Status': status.title(),
            'Description': capabilities.get('description', 'AI agent for creative workflows'),
            'Version': capabilities.get('version', '1.0.0')
        })
    
    df_agents = pd.DataFrame(agent_data)
    
    # Display agent cards
    cols = st.columns(3)
    for idx, (_, agent_row) in enumerate(df_agents.iterrows()):
        col_idx = idx % 3
        
        with cols[col_idx]:
            status_color = {
                'Active': '🟢',
                'Idle': '🟡', 
                'Error': '🔴'
            }.get(agent_row['Status'], '⚪')
            
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <h4>{status_color} {agent_row['Agent']}</h4>
                    <p><strong>Status:</strong> {agent_row['Status']}</p>
                    <p><strong>Version:</strong> {agent_row['Version']}</p>
                    <p style="font-size: 0.9em; color: #666;">{agent_row['Description']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Agent Performance Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Agent Activity")
        
        # Create sample activity data
        try:
            recent_activity = st.session_state.db_manager.get_recent_activity(limit=20)
            if recent_activity:
                activity_df = pd.DataFrame(recent_activity)
                
                # Count activities by agent
                agent_counts = activity_df['agent'].value_counts()
                
                fig_bar = px.bar(
                    x=agent_counts.index,
                    y=agent_counts.values,
                    labels={'x': 'Agent', 'y': 'Activities'},
                    title="Recent Agent Activity"
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No recent agent activity to display")
        except Exception as e:
            st.error(f"Error loading agent activity: {str(e)}")
    
    with col2:
        st.subheader("⚡ System Performance")
        
        # Status distribution pie chart
        status_counts = pd.Series(list(agent_status.values())).value_counts()
        
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Agent Status Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # Agent Management
    st.subheader("🛠️ Agent Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Agent Operations**")
        
        selected_agent = st.selectbox(
            "Select Agent",
            options=list(agent_status.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if st.button("Get Agent Details", use_container_width=True):
            agent = st.session_state.orchestrator.get_agent(selected_agent)
            if agent:
                capabilities = agent.get_capabilities()
                st.json(capabilities)
            else:
                st.error("Agent not found")
        
        if st.button("Health Check", use_container_width=True):
            agent = st.session_state.orchestrator.get_agent(selected_agent)
            if agent:
                health = agent.health_check()
                if health:
                    st.success(f"{selected_agent} is healthy")
                else:
                    st.error(f"{selected_agent} health check failed")
            else:
                st.error("Agent not found")
    
    with col2:
        st.markdown("**System Operations**")
        
        if st.button("Refresh All Agent Status", use_container_width=True):
            st.rerun()
        
        if st.button("Check AI Service", use_container_width=True):
            ai_healthy = st.session_state.orchestrator.check_ai_service()
            if ai_healthy:
                st.success("AI service is responding")
            else:
                st.error("AI service is not responding")
        
        if st.button("Test Database Connection", use_container_width=True):
            db_healthy = st.session_state.db_manager.check_connection()
            if db_healthy:
                st.success("Database connection is healthy")
            else:
                st.error("Database connection failed")
    
    # Recent Activity Log
    st.divider()
    st.subheader("📋 Recent Activity Log")
    
    try:
        recent_activity = st.session_state.db_manager.get_recent_activity(limit=10)
        if recent_activity:
            for activity in recent_activity:
                status_icon = "✅" if activity.get('success', True) else "❌"
                
                with st.expander(f"{status_icon} {activity['agent']} - {activity['action']} ({activity['timestamp']})"):
                    st.write(f"**Details:** {activity['details']}")
                    if not activity.get('success', True):
                        st.error("This operation encountered an error")
        else:
            st.info("No recent activity to display")
    except Exception as e:
        st.error(f"Error loading activity log: {str(e)}")
    
    # System Information
    with st.expander("🔍 System Information"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**System Metrics**")
            st.json(system_metrics)
        
        with col2:
            st.markdown("**Database Status**")
            try:
                db_info = {
                    "Connection": "Online" if st.session_state.db_manager.check_connection() else "Offline",
                    "Mode": "Online" if st.session_state.db_manager.is_online else "Offline",
                    "Recent Activities": len(st.session_state.db_manager.get_recent_activity())
                }
                st.json(db_info)
            except Exception as e:
                st.error(f"Error getting database info: {str(e)}")

if __name__ == "__main__":
    main()
