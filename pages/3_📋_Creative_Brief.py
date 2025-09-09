import streamlit as st
import asyncio
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Creative Brief Parser - Creative Workflow AI OS",
    page_icon="📋",
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
    st.title("📋 Creative Brief Parser")
    st.markdown("### Transform unstructured client input into structured creative briefs")
    
    # Get the creative brief parser agent
    agent = st.session_state.orchestrator.get_agent('creative_brief_parser')
    
    if not agent:
        st.error("Creative Brief Parser agent is not available")
        return
    
    # Input Section
    st.subheader("📝 Client Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input(
            "Client Name",
            placeholder="Acme Corporation"
        )
        
        input_type = st.selectbox(
            "Communication Type",
            ["Email", "Chat", "Call Transcript", "Text Input", "Meeting Notes"]
        )
    
    with col2:
        contact_person = st.text_input(
            "Contact Person",
            placeholder="John Doe"
        )
        
        project_budget = st.text_input(
            "Budget (if mentioned)",
            placeholder="$10,000 - $15,000"
        )
    
    # Client Input Section
    st.subheader("💬 Client Communication")
    
    input_method = st.radio(
        "Input Method",
        ["Paste Text", "Upload File"],
        horizontal=True
    )
    
    client_input = ""
    
    if input_method == "Paste Text":
        client_input = st.text_area(
            "Client Input",
            height=400,
            placeholder="""Paste the client's email, chat messages, or call transcript here. Examples:

"Hi, I'm looking for a complete website redesign for my consulting business. 
We help small businesses with digital transformation. Our current site is outdated 
and doesn't reflect our expertise. 

We need something modern and professional that showcases our case studies. 
The site should have about 6-8 pages including services, about us, case studies, 
and contact. We want it to look trustworthy and help us get more leads.

Our target clients are small to medium businesses with 10-50 employees. 
Timeline is flexible but would prefer to launch in 2-3 months. 
Budget is around $8,000-12,000.

Let me know what you think and if you need any other information."
"""
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Client Communication",
            type=['txt', 'md', 'eml', 'doc', 'docx'],
            help="Upload email, document, or text file"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "text/plain":
                    client_input = str(uploaded_file.read(), "utf-8")
                else:
                    st.warning("File type not fully supported yet. Please use plain text files.")
                    client_input = str(uploaded_file.read(), "utf-8")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    # Processing Options
    st.subheader("⚙️ Parsing Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Standard", "Detailed", "Comprehensive"],
            help="Level of detail for brief analysis"
        )
        
        extract_contacts = st.checkbox(
            "Extract Contact Information",
            value=True,
            help="Find phone numbers, emails, and URLs"
        )
    
    with col2:
        auto_categorize = st.checkbox(
            "Auto-categorize Project Type",
            value=True,
            help="Automatically determine project type"
        )
        
        generate_questions = st.checkbox(
            "Generate Clarification Questions",
            value=True,
            help="Create questions for unclear requirements"
        )
    
    # Parse Button
    parse_button = st.button(
        "🔍 Parse Creative Brief",
        type="primary",
        use_container_width=True,
        disabled=not client_input.strip()
    )
    
    if parse_button and client_input.strip():
        # Prepare input data
        input_data = {
            'client_input': client_input,
            'client_name': client_name or 'Unknown Client',
            'input_type': input_type.lower(),
            'contact_person': contact_person,
            'budget_mentioned': project_budget
        }
        
        with st.spinner("Parsing client input with AI..."):
            try:
                # Execute agent processing
                result = asyncio.run(agent.process(input_data))
                
                if result.get('success'):
                    brief_data = result.get('result', {})
                    
                    # Display Results
                    st.success("✅ Creative brief parsed successfully!")
                    
                    # Project Overview
                    st.subheader("📋 Project Overview")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Project Information**")
                        st.write(f"**Title:** {brief_data.get('project_title', 'Untitled Project')}")
                        st.write(f"**Client:** {brief_data.get('client_name', 'Unknown')}")
                        st.write(f"**Type:** {brief_data.get('project_type', 'General').title()}")
                        
                        clarity_score = brief_data.get('clarity_score', 5)
                        st.write(f"**Clarity Score:** {clarity_score}/10")
                        
                        if clarity_score < 6:
                            st.warning("⚠️ Brief clarity is low. Consider asking clarification questions.")
                    
                    with col2:
                        st.markdown("**Quick Stats**")
                        deliverables_count = len(brief_data.get('deliverables', []))
                        st.write(f"**Deliverables:** {deliverables_count} identified")
                        
                        missing_info = brief_data.get('missing_information', [])
                        st.write(f"**Missing Info:** {len(missing_info)} items")
                        
                        if brief_data.get('contact_information'):
                            st.write(f"**Contacts Found:** {len(brief_data['contact_information'])}")
                    
                    # Goals & Objectives
                    st.subheader("🎯 Goals & Objectives")
                    
                    goals = brief_data.get('goals', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if goals.get('primary'):
                            st.markdown("**Primary Goal**")
                            st.write(goals['primary'])
                        
                        if goals.get('secondary'):
                            st.markdown("**Secondary Goals**")
                            for goal in goals['secondary']:
                                st.write(f"• {goal}")
                    
                    with col2:
                        if goals.get('success_metrics'):
                            st.markdown("**Success Metrics**")
                            for metric in goals['success_metrics']:
                                st.write(f"• {metric}")
                    
                    # Deliverables
                    st.subheader("📦 Deliverables")
                    
                    deliverables = brief_data.get('deliverables', [])
                    
                    if deliverables:
                        for i, deliverable in enumerate(deliverables):
                            with st.expander(f"Deliverable {i+1}: {deliverable.get('item', 'Unknown Item')}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Description:** {deliverable.get('description', 'No description')}")
                                    st.write(f"**Format:** {deliverable.get('format', 'Not specified')}")
                                
                                with col2:
                                    priority = deliverable.get('priority', 'medium')
                                    priority_color = {
                                        'high': '🔴',
                                        'medium': '🟡', 
                                        'low': '🟢'
                                    }.get(priority.lower(), '⚪')
                                    
                                    st.write(f"**Priority:** {priority_color} {priority.title()}")
                    else:
                        st.info("No specific deliverables identified. Consider adding clarification questions.")
                    
                    # Timeline & Constraints
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📅 Timeline")
                        timeline = brief_data.get('timeline', {})
                        
                        if timeline.get('deadline'):
                            st.write(f"**Deadline:** {timeline['deadline']}")
                        
                        if timeline.get('urgency'):
                            urgency = timeline['urgency']
                            urgency_color = {
                                'high': '🔴',
                                'medium': '🟡',
                                'low': '🟢'
                            }.get(urgency.lower(), '⚪')
                            st.write(f"**Urgency:** {urgency_color} {urgency.title()}")
                        
                        if timeline.get('milestones'):
                            st.markdown("**Milestones**")
                            for milestone in timeline['milestones']:
                                st.write(f"• {milestone.get('name', 'Milestone')} - {milestone.get('date', 'TBD')}")
                    
                    with col2:
                        st.subheader("⚖️ Constraints")
                        constraints = brief_data.get('constraints', {})
                        
                        if constraints.get('budget'):
                            st.write(f"**Budget:** {constraints['budget']}")
                        
                        if constraints.get('technical'):
                            st.markdown("**Technical Constraints**")
                            for constraint in constraints['technical']:
                                st.write(f"• {constraint}")
                        
                        if constraints.get('design'):
                            st.markdown("**Design Constraints**")
                            for constraint in constraints['design']:
                                st.write(f"• {constraint}")
                    
                    # Target Audience
                    if brief_data.get('target_audience'):
                        st.subheader("👥 Target Audience")
                        audience = brief_data['target_audience']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if audience.get('primary'):
                                st.write(f"**Primary:** {audience['primary']}")
                            if audience.get('demographics'):
                                st.write(f"**Demographics:** {audience['demographics']}")
                        
                        with col2:
                            if audience.get('personas'):
                                st.markdown("**Personas**")
                                for persona in audience['personas']:
                                    st.write(f"• {persona}")
                    
                    # Brand Context
                    if brief_data.get('brand_context'):
                        st.subheader("🎨 Brand Context")
                        brand = brief_data['brand_context']
                        
                        if brand.get('existing_brand'):
                            st.write(f"**Existing Brand:** {brand['existing_brand']}")
                        
                        if brand.get('competitors'):
                            st.markdown("**Competitors**")
                            for competitor in brand['competitors']:
                                st.write(f"• {competitor}")
                        
                        if brand.get('style_preferences'):
                            st.markdown("**Style Preferences**")
                            for style in brand['style_preferences']:
                                st.write(f"• {style}")
                    
                    # Missing Information & Questions
                    if missing_info:
                        st.subheader("❓ Missing Information")
                        
                        st.warning("The following information should be clarified with the client:")
                        
                        for info in missing_info:
                            st.write(f"• {info}")
                    
                    # Project Structure
                    if brief_data.get('suggested_folder_structure'):
                        st.subheader("📁 Suggested Project Structure")
                        
                        structure = brief_data['suggested_folder_structure']
                        
                        with st.expander("View Folder Structure"):
                            st.write(f"**Root Folder:** {structure.get('root_folder', 'project_folder')}")
                            
                            if structure.get('structure'):
                                st.markdown("**Folder Structure:**")
                                for folder, contents in structure['structure'].items():
                                    st.write(f"📁 {folder}")
                                    if isinstance(contents, list):
                                        for item in contents:
                                            st.write(f"   • {item}")
                    
                    # Initial Checklist
                    if brief_data.get('initial_checklist'):
                        st.subheader("✅ Initial Project Checklist")
                        
                        checklist = brief_data['initial_checklist']
                        
                        for category in checklist:
                            with st.expander(f"{category.get('category', 'Tasks')} ({len(category.get('tasks', []))} items)"):
                                for task in category.get('tasks', []):
                                    st.checkbox(task, key=f"task_{hash(task)}")
                    
                    # Contact Information
                    if brief_data.get('contact_information'):
                        st.subheader("📞 Extracted Contact Information")
                        
                        with st.expander("Contact Details"):
                            for contact in brief_data['contact_information']:
                                st.code(contact)
                    
                    # Reference Materials
                    if brief_data.get('reference_materials'):
                        st.subheader("🔗 Reference Materials")
                        
                        with st.expander("Links and References"):
                            for ref in brief_data['reference_materials']:
                                st.write(f"• {ref}")
                    
                    # Save to database
                    try:
                        # Save project
                        project_id = st.session_state.db_manager.save_project({
                            'name': brief_data.get('project_title', 'Untitled Project'),
                            'client_name': brief_data.get('client_name', client_name),
                            'description': brief_data.get('goals', {}).get('primary', 'No description'),
                            'status': 'planning',
                            'metadata': brief_data
                        })
                        
                        # Log the processing
                        st.session_state.db_manager.log_agent_execution({
                            'agent_name': 'creative_brief_parser',
                            'action': 'parse_creative_brief',
                            'input_data': input_data,
                            'output_data': brief_data,
                            'success': True,
                            'execution_time': result.get('execution_time', 0),
                            'project_id': project_id
                        })
                        
                        st.info(f"💾 Brief saved with Project ID: {project_id}")
                    except Exception as e:
                        st.warning(f"Could not save to database: {str(e)}")
                    
                    # Actions Section
                    st.subheader("🚀 Next Actions")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📝 Create Proposal", use_container_width=True):
                            st.info("Redirect to Proposal Generator with this brief")
                    
                    with col2:
                        if st.button("📊 Generate Taskboard", use_container_width=True):
                            st.info("Redirect to Taskboard Generator with this brief")
                    
                    with col3:
                        if st.button("💰 Estimate Costs", use_container_width=True):
                            st.info("Redirect to Analytics Estimator with this brief")
                    
                    # Export Options
                    st.subheader("📤 Export Brief")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Download as JSON
                        st.download_button(
                            label="📄 Download JSON",
                            data=json.dumps(brief_data, indent=2),
                            file_name=f"creative_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Copy structured brief
                        if st.button("📋 Copy Brief Summary"):
                            summary = f"""
# Creative Brief: {brief_data.get('project_title', 'Project')}

**Client:** {brief_data.get('client_name', 'Unknown')}
**Type:** {brief_data.get('project_type', 'General')}
**Clarity Score:** {brief_data.get('clarity_score', 5)}/10

## Primary Goal
{brief_data.get('goals', {}).get('primary', 'Not specified')}

## Deliverables
{len(brief_data.get('deliverables', []))} deliverables identified

## Missing Information
{len(brief_data.get('missing_information', []))} items need clarification
"""
                            st.code(summary, language="markdown")
                
                else:
                    st.error(f"❌ Parsing failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error parsing creative brief: {str(e)}")
    
    # Help Section
    with st.expander("💡 Tips for Better Brief Parsing"):
        st.markdown("""
        **To get the best results from the Creative Brief Parser:**
        
        1. **Include complete client communication**: Paste the entire email thread or conversation
        
        2. **Look for these key elements**:
           - Project goals and objectives
           - Target audience descriptions
           - Budget mentions
           - Timeline requirements
           - Deliverable specifications
           - Design preferences
           - Technical requirements
        
        3. **Common input sources**:
           - Client inquiry emails
           - Discovery call transcripts  
           - RFP documents
           - Chat conversations
           - Initial project discussions
        
        4. **The parser excels at finding**:
           - Contact information (emails, phones)
           - Project requirements
           - Budget ranges
           - Timeline constraints
           - Success criteria
           - Brand preferences
        
        **Example client input:**
        ```
        Subject: Website Redesign Project
        
        Hi [Agency Name],
        
        We're a growing SaaS company looking to redesign our website. 
        Our current site doesn't effectively communicate our value proposition 
        and we're seeing poor conversion rates.
        
        About us: We provide project management software for creative teams.
        Target audience: Creative directors and project managers at agencies
        Budget: $15,000 - $25,000
        Timeline: Want to launch in Q2
        
        Key requirements:
        - Modern, professional design
        - Case studies section
        - Integration with our product demos
        - Mobile-responsive
        - SEO optimized
        
        Questions or need more info? Let me know!
        
        Best,
        Sarah Johnson
        VP Marketing
        CreativeFlow Inc.
        sarah@creativeflow.com
        (555) 123-4567
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
