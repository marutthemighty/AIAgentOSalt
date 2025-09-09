import streamlit as st
import asyncio
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Meeting Notes Processor - Creative Workflow AI OS",
    page_icon="📝",
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
    st.title("📝 Meeting Notes Processor")
    st.markdown("### Convert meeting notes into structured action items and project updates")
    
    # Get the meeting notes processor agent
    agent = st.session_state.orchestrator.get_agent('meeting_notes_processor')
    
    if not agent:
        st.error("Meeting Notes Processor agent is not available")
        return
    
    # Input Section
    st.subheader("📋 Meeting Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        meeting_date = st.date_input(
            "Meeting Date",
            value=datetime.now().date()
        )
        
        attendees_input = st.text_input(
            "Attendees (comma-separated)",
            placeholder="John Doe, Jane Smith, Mike Johnson"
        )
    
    with col2:
        meeting_type = st.selectbox(
            "Meeting Type",
            ["Client Call", "Team Standup", "Project Kickoff", "Review Meeting", "Planning Session", "Other"]
        )
        
        project_context = st.text_input(
            "Project/Context",
            placeholder="Project name or context"
        )
    
    # Meeting Notes Input
    st.subheader("📝 Meeting Notes")
    
    input_method = st.radio(
        "Input Method",
        ["Type Notes", "Upload File"],
        horizontal=True
    )
    
    meeting_notes = ""
    
    if input_method == "Type Notes":
        meeting_notes = st.text_area(
            "Meeting Notes",
            height=300,
            placeholder="""Paste your meeting notes here. Include:
- Key discussion points
- Decisions made
- Action items mentioned
- Follow-up tasks
- Any blockers or issues
- Next steps

The AI will extract structured information from your notes."""
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Meeting Notes",
            type=['txt', 'md', 'doc', 'docx'],
            help="Upload a text file containing meeting notes"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "text/plain":
                    meeting_notes = str(uploaded_file.read(), "utf-8")
                else:
                    st.warning("File type not fully supported yet. Please use plain text files.")
                    meeting_notes = str(uploaded_file.read(), "utf-8")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    # Processing Options
    st.subheader("⚙️ Processing Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        extract_jira_tasks = st.checkbox(
            "Create JIRA tasks for action items",
            help="Automatically create JIRA tasks from extracted action items"
        )
        
        send_slack_summary = st.checkbox(
            "Send summary to Slack",
            help="Send processed summary to the team Slack channel"
        )
    
    with col2:
        integration_project = st.text_input(
            "JIRA Project Key",
            placeholder="CW",
            help="JIRA project key for task creation"
        )
        
        priority_filter = st.selectbox(
            "Priority Filter",
            ["All Items", "High Priority Only", "Medium and High"],
            help="Filter action items by priority level"
        )
    
    # Process Button
    process_button = st.button(
        "🚀 Process Meeting Notes",
        type="primary",
        use_container_width=True,
        disabled=not meeting_notes.strip()
    )
    
    if process_button and meeting_notes.strip():
        # Parse attendees
        attendees = [name.strip() for name in attendees_input.split(',') if name.strip()] if attendees_input else []
        
        # Prepare input data
        input_data = {
            'meeting_notes': meeting_notes,
            'attendees': attendees,
            'meeting_date': meeting_date.isoformat(),
            'meeting_type': meeting_type,
            'project_context': project_context
        }
        
        with st.spinner("Processing meeting notes with AI..."):
            try:
                # Execute agent processing
                result = asyncio.run(agent.process(input_data))
                
                if result.get('success'):
                    processed_data = result.get('result', {})
                    
                    # Display Results
                    st.success("✅ Meeting notes processed successfully!")
                    
                    # Summary Section
                    st.subheader("📊 Meeting Summary")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Meeting Overview**")
                        st.write(processed_data.get('summary', 'No summary available'))
                        
                        if processed_data.get('key_decisions'):
                            st.markdown("**Key Decisions**")
                            for decision in processed_data['key_decisions']:
                                st.write(f"• {decision}")
                    
                    with col2:
                        st.markdown("**Meeting Details**")
                        st.write(f"**Date:** {meeting_date}")
                        st.write(f"**Type:** {meeting_type}")
                        st.write(f"**Attendees:** {len(attendees)} people")
                        if project_context:
                            st.write(f"**Context:** {project_context}")
                    
                    # Action Items Section
                    st.subheader("✅ Action Items")
                    
                    action_items = processed_data.get('action_items', [])
                    
                    if action_items:
                        for i, item in enumerate(action_items):
                            with st.expander(f"Action Item {i+1}: {item.get('task', 'Unknown Task')}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Task:** {item.get('task', 'N/A')}")
                                    st.write(f"**Assignee:** {item.get('assignee', 'TBD')}")
                                    st.write(f"**Category:** {item.get('category', 'General')}")
                                
                                with col2:
                                    priority = item.get('priority', 'medium')
                                    priority_color = {
                                        'high': '🔴',
                                        'medium': '🟡',
                                        'low': '🟢'
                                    }.get(priority.lower(), '⚪')
                                    
                                    st.write(f"**Priority:** {priority_color} {priority.title()}")
                                    st.write(f"**Due Date:** {item.get('due_date', 'TBD')}")
                    else:
                        st.info("No action items found in the meeting notes")
                    
                    # Follow-ups Section
                    if processed_data.get('follow_ups'):
                        st.subheader("🔄 Follow-ups")
                        for follow_up in processed_data['follow_ups']:
                            st.write(f"• {follow_up}")
                    
                    # Blockers Section
                    if processed_data.get('blockers'):
                        st.subheader("🚫 Blockers & Issues")
                        for blocker in processed_data['blockers']:
                            st.warning(f"⚠️ {blocker}")
                    
                    # Next Meeting
                    if processed_data.get('next_meeting'):
                        st.subheader("📅 Next Steps")
                        st.info(f"📋 {processed_data['next_meeting']}")
                    
                    # Integration Actions
                    if extract_jira_tasks and action_items:
                        st.subheader("🔗 JIRA Integration")
                        
                        with st.spinner("Creating JIRA tasks..."):
                            try:
                                jira_result = asyncio.run(
                                    agent.create_jira_tasks(action_items, integration_project)
                                )
                                
                                if jira_result.get('success'):
                                    st.success(f"✅ Created {jira_result.get('tasks_created', 0)} JIRA tasks")
                                else:
                                    st.error(f"❌ JIRA integration failed: {jira_result.get('error', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"❌ JIRA integration error: {str(e)}")
                    
                    # Save to database
                    try:
                        # Log the processing
                        st.session_state.db_manager.log_agent_execution({
                            'agent_name': 'meeting_notes_processor',
                            'action': 'process_meeting_notes',
                            'input_data': input_data,
                            'output_data': processed_data,
                            'success': True,
                            'execution_time': result.get('execution_time', 0)
                        })
                    except Exception as e:
                        st.warning(f"Could not save to database: {str(e)}")
                    
                    # Export Options
                    st.subheader("📤 Export Options")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📋 Copy Action Items"):
                            action_text = "\n".join([
                                f"• {item.get('task', 'Task')} (Assignee: {item.get('assignee', 'TBD')}, Priority: {item.get('priority', 'medium')})"
                                for item in action_items
                            ])
                            st.code(action_text, language="text")
                    
                    with col2:
                        if st.button("📄 Download Summary"):
                            summary_data = {
                                'meeting_summary': processed_data,
                                'meeting_info': {
                                    'date': meeting_date.isoformat(),
                                    'type': meeting_type,
                                    'attendees': attendees,
                                    'context': project_context
                                }
                            }
                            st.download_button(
                                label="Download JSON",
                                data=json.dumps(summary_data, indent=2),
                                file_name=f"meeting_summary_{meeting_date}.json",
                                mime="application/json"
                            )
                    
                    with col3:
                        if st.button("🔄 Process Another"):
                            st.rerun()
                
                else:
                    st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error processing meeting notes: {str(e)}")
    
    # Help Section
    with st.expander("💡 Tips for Better Results"):
        st.markdown("""
        **To get the best results from the Meeting Notes Processor:**
        
        1. **Include clear action items**: Use phrases like "action item:", "todo:", "follow up:", or "next steps:"
        
        2. **Specify assignees**: Mention who is responsible for each task
        
        3. **Include dates and deadlines**: Mention specific dates when possible
        
        4. **Note decisions**: Clearly state what was decided during the meeting
        
        5. **Mention blockers**: Include any obstacles or issues discussed
        
        6. **Use structured format**: Organize notes with clear sections or bullet points
        
        **Example format:**
        ```
        Meeting: Project Kickoff - Website Redesign
        Date: 2024-01-15
        Attendees: John (PM), Sarah (Designer), Mike (Developer)
        
        Key Decisions:
        - Approved wireframes for homepage
        - Budget approved: $15,000
        
        Action Items:
        - Sarah: Create detailed mockups by Jan 20
        - Mike: Set up development environment by Jan 18
        - John: Schedule client review meeting for Jan 25
        
        Blockers:
        - Waiting for brand guidelines from client
        
        Next Steps:
        - Review meeting scheduled for Jan 25
        ```
        """)
    
    # Agent Status
    with st.expander("🤖 Agent Information"):
        if agent:
            capabilities = agent.get_capabilities()
            st.json(capabilities)
        else:
            st.error("Agent not available")

if __name__ == "__main__":
    main()
