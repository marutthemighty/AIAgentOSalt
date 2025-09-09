import streamlit as st
from core.agent_orchestrator import AgentOrchestrator
from core.database import DatabaseManager
import os

# Configure page
st.set_page_config(
    page_title="Creative Workflow AI OS",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = AgentOrchestrator()

if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

def main():
    """Main application entry point"""
    
    # Header
    st.title("🚀 Creative Workflow AI OS")
    st.markdown("### Automate your creative agency workflows with 12 powerful AI agents")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # System status
        st.subheader("System Status")
        
        # Check database connection
        try:
            db_status = st.session_state.db_manager.check_connection()
            if db_status:
                st.success("✅ Database Connected")
            else:
                st.error("❌ Database Offline")
        except Exception as e:
            st.error(f"❌ Database Error: {str(e)}")
        
        # Check AI service
        try:
            ai_status = st.session_state.orchestrator.check_ai_service()
            if ai_status:
                st.success("✅ AI Service Active")
            else:
                st.error("❌ AI Service Offline")
        except Exception as e:
            st.error(f"❌ AI Service Error: {str(e)}")
        
        st.divider()
        
        # Agent status overview
        st.subheader("🤖 Agent Status")
        agents = st.session_state.orchestrator.get_agent_status()
        
        for agent_name, status in agents.items():
            if status == "active":
                st.success(f"✅ {agent_name}")
            elif status == "idle":
                st.info(f"⏸️ {agent_name}")
            else:
                st.error(f"❌ {agent_name}")
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown("### 🎯 Quick Actions")
        
        # Quick action buttons
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("📝 Process Meeting Notes", use_container_width=True):
                st.switch_page("pages/2_📝_Meeting_Notes.py")
            
            if st.button("📋 Parse Creative Brief", use_container_width=True):
                st.switch_page("pages/3_📋_Creative_Brief.py")
            
            if st.button("📊 Manage Projects", use_container_width=True):
                st.switch_page("pages/4_📊_Project_Management.py")
            
            if st.button("🎨 Generate Branding", use_container_width=True):
                st.switch_page("pages/5_🎨_Branding.py")
            
            if st.button("📄 Create Proposals", use_container_width=True):
                st.switch_page("pages/6_📄_Proposals.py")
            
            if st.button("📝 Plan Content", use_container_width=True):
                st.switch_page("pages/7_📝_Content_Planning.py")
        
        with col_b:
            if st.button("✅ Quality Assurance", use_container_width=True):
                st.switch_page("pages/8_✅_Quality_Assurance.py")
            
            if st.button("👥 Client Portal", use_container_width=True):
                st.switch_page("pages/9_👥_Client_Portal.py")
            
            if st.button("📦 Package Deliverables", use_container_width=True):
                st.switch_page("pages/10_📦_Deliverables.py")
            
            if st.button("📈 View Analytics", use_container_width=True):
                st.switch_page("pages/11_📈_Analytics.py")
            
            if st.button("⚡ Optimize Workflow", use_container_width=True):
                st.switch_page("pages/12_⚡_Workflow_Optimizer.py")
            
            if st.button("🤖 Agent Dashboard", use_container_width=True):
                st.switch_page("pages/1_🤖_Agent_Dashboard.py")
    
    # Recent activity
    st.markdown("---")
    st.subheader("📊 Recent Activity")
    
    try:
        recent_activity = st.session_state.db_manager.get_recent_activity(limit=5)
        if recent_activity:
            for activity in recent_activity:
                with st.expander(f"{activity['agent']} - {activity['action']} ({activity['timestamp']})"):
                    st.write(activity['details'])
        else:
            st.info("No recent activity to display")
    except Exception as e:
        st.error(f"Error loading recent activity: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Creative Workflow AI OS v1.0 | Powered by Gemini AI & Streamlit
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
