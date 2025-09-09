import streamlit as st
import asyncio
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Client Portal - Creative Workflow AI OS",
    page_icon="👥",
    layout="wide"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    from core.agent_orchestrator import AgentOrchestrator
    st.session_state.orchestrator = AgentOrchestrator()

if 'db_manager' not in st.session_state:
    from core.database import DatabaseManager
    st.session_state.db_manager = DatabaseManager()

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    st.title("👥 Client Portal Assistant")
    st.markdown("### AI-powered client communication and project tracking")
    
    # Status check
    col1, col2 = st.columns([3, 1])
    with col2:
        portal_assistant = st.session_state.orchestrator.get_agent("client_portal_assistant")
        if portal_assistant:
            st.success("🟢 Portal Assistant Online")
        else:
            st.error("🔴 Portal Assistant Offline")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Client Chat", "📊 Project Status", "📁 Client Files", "⚙️ Portal Settings"])
    
    with tab1:
        st.subheader("💬 AI Client Assistant")
        
        # Client selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            client_id = st.selectbox(
                "Select Client",
                ["client_001", "client_002", "client_003"],
                format_func=lambda x: f"Client {x.split('_')[1]}"
            )
        
        with col2:
            project_id = st.selectbox(
                "Select Project",
                ["proj_001", "proj_002", "proj_003"],
                format_func=lambda x: f"Project {x.split('_')[1]}"
            )
        
        # Chat interface
        st.subheader("Chat History")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if st.session_state.chat_history:
                for i, message in enumerate(st.session_state.chat_history):
                    if message['type'] == 'user':
                        st.chat_message("user").write(message['content'])
                    else:
                        st.chat_message("assistant").write(message['content'])
            else:
                st.info("No conversation yet. Ask a question to get started!")
        
        # Client query input
        st.subheader("Ask About Your Project")
        
        # Sample questions
        st.write("**Quick Questions:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 What's the project status?"):
                query = "What's the current status of my project?"
                process_client_query(query, client_id, project_id)
            
            if st.button("📅 When will it be completed?"):
                query = "When will my project be completed?"
                process_client_query(query, client_id, project_id)
        
        with col2:
            if st.button("📄 What deliverables will I receive?"):
                query = "What deliverables will I receive for this project?"
                process_client_query(query, client_id, project_id)
            
            if st.button("💰 What about the invoice?"):
                query = "Can you tell me about the project billing and payments?"
                process_client_query(query, client_id, project_id)
        
        # Custom query input
        query = st.text_input("Ask a question about your project:", placeholder="Type your question here...")
        
        if st.button("📤 Send", type="primary") and query:
            process_client_query(query, client_id, project_id)
    
    with tab2:
        st.subheader("📊 Project Dashboard")
        
        # Project overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Project Progress", "65%", delta="15%")
        with col2:
            st.metric("Days Remaining", "18", delta="-3")
        with col3:
            st.metric("Deliverables", "8/12", delta="2")
        with col4:
            st.metric("Team Rating", "4.8/5", delta="0.2")
        
        # Timeline view
        st.subheader("🗓️ Project Timeline")
        
        timeline_data = [
            {"phase": "Discovery", "status": "✅ Complete", "date": "2024-01-15"},
            {"phase": "Design", "status": "✅ Complete", "date": "2024-02-10"},
            {"phase": "Development", "status": "🟡 In Progress", "date": "2024-03-15"},
            {"phase": "Testing", "status": "⏳ Pending", "date": "2024-04-01"},
            {"phase": "Launch", "status": "⏳ Pending", "date": "2024-04-15"}
        ]
        
        for item in timeline_data:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{item['phase']}**")
            with col2:
                st.write(item['status'])
            with col3:
                st.write(item['date'])
        
        # Recent updates
        st.subheader("📝 Recent Updates")
        
        updates = [
            {"date": "2024-01-20", "update": "Homepage design approved", "author": "Design Team"},
            {"date": "2024-01-18", "update": "Development phase started", "author": "Project Manager"},
            {"date": "2024-01-15", "update": "Brand guidelines finalized", "author": "Brand Team"}
        ]
        
        for update in updates:
            with st.expander(f"{update['date']} - {update['update']}"):
                st.write(f"**Author:** {update['author']}")
                st.write(f"**Update:** {update['update']}")
        
        # Team contact info
        st.subheader("👥 Your Project Team")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Project Manager**")
            st.write("Sarah Johnson")
            st.write("📧 sarah@agency.com")
            st.write("📞 (555) 123-4567")
        
        with col2:
            st.write("**Lead Designer**")
            st.write("Mike Chen")
            st.write("📧 mike@agency.com")
            st.write("🎨 Lead Creative")
        
        with col3:
            st.write("**Developer**")
            st.write("Alex Rodriguez")
            st.write("📧 alex@agency.com")
            st.write("💻 Full Stack Dev")
    
    with tab3:
        st.subheader("📁 Project Files & Deliverables")
        
        # File categories
        file_categories = {
            "Final Deliverables": [
                {"name": "Homepage_Design_v3.pdf", "size": "2.4 MB", "date": "2024-01-20"},
                {"name": "Brand_Guidelines.pdf", "size": "5.1 MB", "date": "2024-01-15"}
            ],
            "Work in Progress": [
                {"name": "Product_Page_Draft.pdf", "size": "1.8 MB", "date": "2024-01-19"},
                {"name": "Mobile_Wireframes.pdf", "size": "3.2 MB", "date": "2024-01-17"}
            ],
            "Reference Materials": [
                {"name": "Project_Brief.pdf", "size": "0.5 MB", "date": "2024-01-10"},
                {"name": "Competitor_Analysis.pdf", "size": "4.1 MB", "date": "2024-01-12"}
            ]
        }
        
        for category, files in file_categories.items():
            with st.expander(f"📂 {category} ({len(files)} files)"):
                for file in files:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"📄 {file['name']}")
                    with col2:
                        st.write(file['size'])
                    with col3:
                        st.write(file['date'])
                    with col4:
                        st.button("📥", key=f"download_{file['name']}", help="Download file")
        
        # Upload area for client feedback
        st.subheader("📤 Upload Feedback or Assets")
        
        uploaded_file = st.file_uploader(
            "Upload files for the team",
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'png', 'doc', 'docx', 'txt']
        )
        
        if uploaded_file:
            st.success(f"✅ {len(uploaded_file)} file(s) uploaded successfully!")
        
        feedback_text = st.text_area(
            "Add a message with your upload",
            placeholder="Describe the files or provide feedback..."
        )
        
        if st.button("📤 Send to Team", type="primary"):
            if uploaded_file or feedback_text:
                st.success("✅ Your feedback has been sent to the project team!")
            else:
                st.warning("Please upload files or add a message.")
    
    with tab4:
        st.subheader("⚙️ Portal Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Notification Preferences**")
            
            email_updates = st.checkbox("Email project updates", value=True)
            sms_alerts = st.checkbox("SMS for urgent matters", value=False)
            weekly_reports = st.checkbox("Weekly progress reports", value=True)
            milestone_notifications = st.checkbox("Milestone notifications", value=True)
            
            st.write("**Communication Preferences**")
            communication_style = st.selectbox(
                "Preferred communication style",
                ["Professional", "Casual", "Detailed", "Brief"]
            )
            
            update_frequency = st.selectbox(
                "Update frequency",
                ["Daily", "Weekly", "Bi-weekly", "Monthly", "As needed"]
            )
        
        with col2:
            st.write("**Account Information**")
            
            client_name = st.text_input("Client Name", value="John Doe")
            company_name = st.text_input("Company", value="ABC Corp")
            email = st.text_input("Email", value="john@abccorp.com")
            phone = st.text_input("Phone", value="(555) 123-4567")
            
            st.write("**Portal Access**")
            enable_file_downloads = st.checkbox("Enable file downloads", value=True)
            enable_team_chat = st.checkbox("Enable direct team chat", value=True)
            enable_project_history = st.checkbox("Show project history", value=True)
        
        if st.button("💾 Save Preferences", type="primary"):
            st.success("✅ Preferences saved successfully!")

def process_client_query(query, client_id, project_id):
    """Process client query using the portal assistant"""
    
    # Add user message to chat history
    st.session_state.chat_history.append({
        'type': 'user',
        'content': query,
        'timestamp': datetime.now().isoformat()
    })
    
    with st.spinner("Processing your question..."):
        try:
            # Sample project data (in real implementation, this would come from database)
            project_data = {
                'id': project_id,
                'name': 'Website Redesign Project',
                'status': 'In Progress',
                'progress': 65,
                'current_phase': 'Development',
                'estimated_completion': '2024-04-15',
                'deliverables': [
                    {'name': 'Homepage Design', 'status': 'Complete'},
                    {'name': 'Product Pages', 'status': 'In Progress'},
                    {'name': 'Contact Form', 'status': 'Pending'}
                ]
            }
            
            # Process query with portal assistant
            response_result = st.session_state.orchestrator.process_with_agent(
                'client_portal_assistant',
                {
                    'query': query,
                    'client_id': client_id,
                    'project_data': project_data,
                    'context': {'portal_access': True}
                }
            )
            
            if response_result.get('success'):
                result_data = response_result.get('result', {})
                response_message = result_data.get('response', {}).get('message', 'I apologize, but I couldn\'t generate a proper response to your question.')
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    'type': 'assistant',
                    'content': response_message,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Check if escalation is needed
                escalation = result_data.get('escalation', {})
                if escalation.get('needed'):
                    st.warning(f"⚠️ This query may need attention from your {escalation.get('to_whom', 'project manager')}")
                
                # Show follow-up questions if available
                follow_ups = result_data.get('follow_up_questions', [])
                if follow_ups:
                    st.info("💡 You might also want to ask:")
                    for question in follow_ups[:2]:  # Show first 2 follow-ups
                        st.write(f"• {question}")
            
            else:
                error_message = "I'm having trouble processing your question right now. Please try again or contact your project manager directly."
                st.session_state.chat_history.append({
                    'type': 'assistant',
                    'content': error_message,
                    'timestamp': datetime.now().isoformat()
                })
        
        except Exception as e:
            error_message = f"I encountered an error while processing your question. Please contact your project manager for assistance."
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': error_message,
                'timestamp': datetime.now().isoformat()
            })
    
    # Rerun to show updated chat
    st.rerun()

if __name__ == "__main__":
    main()