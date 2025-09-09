import streamlit as st
import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Project Management - Creative Workflow AI OS",
    page_icon="📊",
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
    st.title("📊 Project Management & Taskboards")
    st.markdown("### Generate actionable taskboards from creative briefs")
    
    # Get the taskboard generator agent
    agent = st.session_state.orchestrator.get_agent('taskboard_generator')
    
    if not agent:
        st.error("Taskboard Generator agent is not available")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🆕 Generate Taskboard", "📋 Active Projects", "📈 Project Analytics"])
    
    with tab1:
        generate_taskboard_tab()
    
    with tab2:
        active_projects_tab()
    
    with tab3:
        project_analytics_tab()


def generate_taskboard_tab():
    st.subheader("🆕 Generate New Taskboard")
    
    # Get available briefs or allow manual input
    input_method = st.radio(
        "Input Method",
        ["Use Existing Brief", "Manual Input", "Upload Brief"],
        horizontal=True
    )
    
    brief_data = {}
    team_members = []
    
    if input_method == "Use Existing Brief":
        # Would normally load from database
        st.info("💡 This would show existing parsed briefs from the database")
        
        # Sample brief for demo
        sample_brief = {
            "project_title": "Website Redesign for TechCorp",
            "project_type": "website", 
            "client_name": "TechCorp Inc.",
            "goals": {
                "primary": "Create a modern, responsive website that increases lead generation",
                "secondary": ["Improve brand perception", "Showcase case studies"]
            },
            "deliverables": [
                {
                    "item": "Homepage design",
                    "description": "Modern landing page with hero section",
                    "format": "HTML/CSS",
                    "priority": "high"
                },
                {
                    "item": "Services pages",
                    "description": "Individual pages for each service offering",
                    "format": "HTML/CSS",
                    "priority": "medium"
                },
                {
                    "item": "Contact form",
                    "description": "Lead capture form with validation",
                    "format": "HTML/CSS/JS",
                    "priority": "high"
                }
            ],
            "timeline": {
                "deadline": "2024-03-15",
                "urgency": "medium"
            }
        }
        
        if st.checkbox("Use Sample Brief (TechCorp Website)"):
            brief_data = sample_brief
            st.json(brief_data)
    
    elif input_method == "Manual Input":
        st.markdown("**Project Information**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_title = st.text_input("Project Title", value="New Creative Project")
            project_type = st.selectbox(
                "Project Type",
                ["website", "branding", "marketing", "general"]
            )
            client_name = st.text_input("Client Name", value="Client")
        
        with col2:
            project_goal = st.text_area("Primary Goal", height=100)
            project_deadline = st.date_input(
                "Deadline",
                value=datetime.now().date() + timedelta(days=30)
            )
            urgency = st.selectbox("Urgency", ["low", "medium", "high"])
        
        # Deliverables
        st.markdown("**Deliverables**")
        deliverables = []
        
        num_deliverables = st.number_input("Number of Deliverables", min_value=1, max_value=10, value=3)
        
        for i in range(num_deliverables):
            with st.expander(f"Deliverable {i+1}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    item = st.text_input(f"Item Name {i+1}", key=f"item_{i}")
                    priority = st.selectbox(f"Priority {i+1}", ["low", "medium", "high"], key=f"priority_{i}")
                
                with col2:
                    description = st.text_input(f"Description {i+1}", key=f"desc_{i}")
                    format_type = st.text_input(f"Format {i+1}", key=f"format_{i}")
                
                if item:
                    deliverables.append({
                        "item": item,
                        "description": description,
                        "format": format_type,
                        "priority": priority
                    })
        
        # Create brief data
        brief_data = {
            "project_title": project_title,
            "project_type": project_type,
            "client_name": client_name,
            "goals": {"primary": project_goal},
            "deliverables": deliverables,
            "timeline": {
                "deadline": project_deadline.isoformat(),
                "urgency": urgency
            }
        }
    
    else:  # Upload Brief
        uploaded_file = st.file_uploader(
            "Upload Brief JSON",
            type=['json'],
            help="Upload a previously exported creative brief"
        )
        
        if uploaded_file is not None:
            try:
                brief_data = json.loads(uploaded_file.read())
                st.success("Brief loaded successfully!")
                st.json(brief_data)
            except Exception as e:
                st.error(f"Error loading brief: {str(e)}")
    
    # Team Configuration
    st.subheader("👥 Team Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        team_input = st.text_area(
            "Team Members (one per line)",
            value="John Doe (Project Manager)\nSarah Smith (Designer)\nMike Johnson (Developer)\nEmily Davis (Content Creator)",
            help="Enter team members with their roles"
        )
        
        team_members = [member.strip() for member in team_input.split('\n') if member.strip()]
    
    with col2:
        st.markdown("**Taskboard Preferences**")
        
        workflow_type = st.selectbox(
            "Workflow Type",
            ["Kanban", "Scrum", "Waterfall", "Hybrid"],
            help="Choose your preferred project management approach"
        )
        
        include_dependencies = st.checkbox(
            "Include Task Dependencies",
            value=True,
            help="Automatically detect and set task dependencies"
        )
        
        estimate_hours = st.checkbox(
            "Include Hour Estimates",
            value=True,
            help="Generate time estimates for tasks"
        )
    
    # Generate Button
    if st.button("🚀 Generate Taskboard", type="primary", use_container_width=True):
        if not brief_data:
            st.error("Please provide a creative brief first")
            return
        
        # Prepare input data
        input_data = {
            'brief': brief_data,
            'team_members': team_members,
            'preferences': {
                'workflow_type': workflow_type,
                'include_dependencies': include_dependencies,
                'estimate_hours': estimate_hours
            }
        }
        
        with st.spinner("Generating taskboard with AI..."):
            try:
                # Execute agent processing
                agent = st.session_state.orchestrator.get_agent('taskboard_generator')
                result = asyncio.run(agent.process(input_data))
                
                if result.get('success'):
                    taskboard_data = result.get('result', {})
                    
                    # Display Results
                    st.success("✅ Taskboard generated successfully!")
                    
                    # Project Information
                    st.subheader("📋 Project Overview")
                    
                    project_info = taskboard_data.get('project_info', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Project Name", project_info.get('name', 'Unknown'))
                    
                    with col2:
                        st.metric("Duration", project_info.get('end_date', 'TBD'))
                    
                    with col3:
                        total_tasks = len(taskboard_data.get('tasks', []))
                        st.metric("Total Tasks", total_tasks)
                    
                    with col4:
                        st.metric("Status", project_info.get('status', 'Planning').title())
                    
                    # Kanban Board View
                    st.subheader("📋 Kanban Board")
                    
                    columns = taskboard_data.get('columns', [])
                    tasks = taskboard_data.get('tasks', [])
                    
                    if columns and tasks:
                        # Create columns
                        kanban_cols = st.columns(len(columns))
                        
                        # Organize tasks by column
                        tasks_by_column = {}
                        for task in tasks:
                            column_id = task.get('column_id', 'todo')
                            if column_id not in tasks_by_column:
                                tasks_by_column[column_id] = []
                            tasks_by_column[column_id].append(task)
                        
                        # Display columns
                        for i, column in enumerate(columns):
                            with kanban_cols[i]:
                                column_name = column.get('name', f'Column {i+1}')
                                column_id = column.get('id', f'col_{i}')
                                
                                st.markdown(f"### {column_name}")
                                st.markdown(f"**{len(tasks_by_column.get(column_id, []))} tasks**")
                                
                                # Display tasks in column
                                for task in tasks_by_column.get(column_id, []):
                                    priority_color = {
                                        'high': '🔴',
                                        'medium': '🟡',
                                        'low': '🟢'
                                    }.get(task.get('priority', 'medium'), '⚪')
                                    
                                    with st.container():
                                        st.markdown(f"""
                                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 8px 0; background: white;">
                                            <div style="font-weight: bold; margin-bottom: 8px;">
                                                {priority_color} {task.get('title', 'Untitled Task')}
                                            </div>
                                            <div style="font-size: 0.9em; color: #666; margin-bottom: 8px;">
                                                {task.get('description', 'No description')[:100]}{'...' if len(task.get('description', '')) > 100 else ''}
                                            </div>
                                            <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #888;">
                                                <span>👤 {task.get('assignee', 'Unassigned')}</span>
                                                <span>⏱️ {task.get('estimated_hours', 0)}h</span>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                    
                    # Task Details
                    st.subheader("📝 Task Details")
                    
                    task_df = pd.DataFrame(tasks)
                    
                    if not task_df.empty:
                        # Task summary
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Priority distribution
                            priority_counts = task_df['priority'].value_counts()
                            fig_priority = px.pie(
                                values=priority_counts.values,
                                names=priority_counts.index,
                                title="Task Priority Distribution"
                            )
                            st.plotly_chart(fig_priority, use_container_width=True)
                        
                        with col2:
                            # Assignee distribution
                            assignee_counts = task_df['assignee'].value_counts()
                            fig_assignee = px.bar(
                                x=assignee_counts.values,
                                y=assignee_counts.index,
                                orientation='h',
                                title="Tasks per Team Member"
                            )
                            st.plotly_chart(fig_assignee, use_container_width=True)
                        
                        # Task table
                        st.markdown("**All Tasks**")
                        
                        # Format task data for display
                        display_tasks = []
                        for task in tasks:
                            display_tasks.append({
                                'Task': task.get('title', 'Untitled'),
                                'Priority': task.get('priority', 'medium').title(),
                                'Assignee': task.get('assignee', 'Unassigned'),
                                'Hours': task.get('estimated_hours', 0),
                                'Due Date': task.get('due_date', 'TBD'),
                                'Status': task.get('column_id', 'todo').replace('_', ' ').title()
                            })
                        
                        display_df = pd.DataFrame(display_tasks)
                        st.dataframe(display_df, use_container_width=True)
                    
                    # Timeline & Milestones
                    milestones = taskboard_data.get('milestones', [])
                    
                    if milestones:
                        st.subheader("🎯 Project Milestones")
                        
                        for milestone in milestones:
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**{milestone.get('name', 'Milestone')}**")
                                    st.write(milestone.get('description', 'No description'))
                                
                                with col2:
                                    st.write(f"📅 {milestone.get('date', 'TBD')}")
                    
                    # Integration Options
                    st.subheader("🔗 Export & Integration")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📤 Export to JIRA", use_container_width=True):
                            st.info("JIRA integration would be implemented here")
                    
                    with col2:
                        if st.button("📋 Export to Trello", use_container_width=True):
                            st.info("Trello integration would be implemented here")
                    
                    with col3:
                        if st.button("📝 Export to Notion", use_container_width=True):
                            st.info("Notion integration would be implemented here")
                    
                    # Download options
                    st.markdown("**Download Taskboard**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Download as JSON
                        st.download_button(
                            label="📄 Download JSON",
                            data=json.dumps(taskboard_data, indent=2),
                            file_name=f"taskboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Download as CSV
                        if tasks:
                            csv_data = pd.DataFrame(tasks).to_csv(index=False)
                            st.download_button(
                                label="📊 Download CSV",
                                data=csv_data,
                                file_name=f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    
                    # Save to database
                    try:
                        # Save project if not exists
                        project_data = {
                            'name': project_info.get('name', 'Generated Project'),
                            'client_name': brief_data.get('client_name', 'Unknown Client'),
                            'description': brief_data.get('goals', {}).get('primary', 'Generated from taskboard'),
                            'status': 'active',
                            'metadata': taskboard_data
                        }
                        
                        project_id = st.session_state.db_manager.save_project(project_data)
                        
                        # Save individual tasks
                        for task in tasks:
                            task_data = {
                                'project_id': project_id,
                                'title': task.get('title', 'Untitled Task'),
                                'description': task.get('description', ''),
                                'assignee': task.get('assignee', 'Unassigned'),
                                'status': task.get('column_id', 'todo'),
                                'priority': task.get('priority', 'medium'),
                                'due_date': task.get('due_date'),
                                'metadata': task
                            }
                            
                            st.session_state.db_manager.save_task(task_data)
                        
                        st.info(f"💾 Project saved with ID: {project_id}")
                        
                        # Log the processing
                        st.session_state.db_manager.log_agent_execution({
                            'agent_name': 'taskboard_generator',
                            'action': 'generate_taskboard',
                            'input_data': input_data,
                            'output_data': taskboard_data,
                            'success': True,
                            'execution_time': result.get('execution_time', 0),
                            'project_id': project_id
                        })
                        
                    except Exception as e:
                        st.warning(f"Could not save to database: {str(e)}")
                
                else:
                    st.error(f"❌ Taskboard generation failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error generating taskboard: {str(e)}")


def active_projects_tab():
    st.subheader("📋 Active Projects")
    
    # This would load actual projects from database
    st.info("This tab would show active projects loaded from the database")
    
    # Placeholder project data
    sample_projects = [
        {
            'id': 'proj_001',
            'name': 'Website Redesign for TechCorp',
            'client': 'TechCorp Inc.',
            'status': 'In Progress',
            'progress': 65,
            'due_date': '2024-03-15',
            'team_size': 4,
            'tasks_completed': 12,
            'tasks_total': 18
        },
        {
            'id': 'proj_002', 
            'name': 'Brand Identity for StartupXYZ',
            'client': 'StartupXYZ',
            'status': 'Planning',
            'progress': 20,
            'due_date': '2024-04-10',
            'team_size': 3,
            'tasks_completed': 3,
            'tasks_total': 15
        }
    ]
    
    # Project cards
    for project in sample_projects:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"### {project['name']}")
                st.write(f"Client: {project['client']}")
                
                # Progress bar
                progress = project['progress'] / 100
                st.progress(progress)
                st.write(f"Progress: {project['progress']}%")
            
            with col2:
                st.metric("Status", project['status'])
                st.metric("Due Date", project['due_date'])
            
            with col3:
                st.metric("Team Size", project['team_size'])
                st.metric("Tasks", f"{project['tasks_completed']}/{project['tasks_total']}")
            
            with col4:
                if st.button(f"View Project", key=f"view_{project['id']}"):
                    st.info(f"Would open detailed view for {project['name']}")
                
                if st.button(f"Edit Tasks", key=f"edit_{project['id']}"):
                    st.info(f"Would open task editor for {project['name']}")
            
            st.divider()


def project_analytics_tab():
    st.subheader("📈 Project Analytics")
    
    # Sample analytics data
    projects_data = {
        'Project': ['Website A', 'Brand B', 'Marketing C', 'Website D', 'Brand E'],
        'Status': ['Completed', 'In Progress', 'Completed', 'Planning', 'In Progress'],
        'Duration (days)': [45, 30, 25, 60, 35],
        'Team Size': [4, 3, 2, 5, 3],
        'Budget': [15000, 8000, 5000, 20000, 12000],
        'Client Satisfaction': [9, 8, 10, 7, 9]
    }
    
    df = pd.DataFrame(projects_data)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_duration = df['Duration (days)'].mean()
        st.metric("Avg Duration", f"{avg_duration:.0f} days")
    
    with col2:
        completed_projects = len(df[df['Status'] == 'Completed'])
        st.metric("Completed Projects", completed_projects)
    
    with col3:
        avg_satisfaction = df['Client Satisfaction'].mean()
        st.metric("Avg Satisfaction", f"{avg_satisfaction:.1f}/10")
    
    with col4:
        total_revenue = df['Budget'].sum()
        st.metric("Total Revenue", f"${total_revenue:,}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Project status distribution
        status_counts = df['Status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Project Status Distribution"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Budget vs Duration scatter
        fig_scatter = px.scatter(
            df, 
            x='Duration (days)', 
            y='Budget',
            size='Team Size',
            color='Status',
            title="Budget vs Duration Analysis",
            hover_data=['Project']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Project performance table
    st.subheader("📊 Project Performance")
    st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
