import streamlit as st
import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Proposal Generator - Creative Workflow AI OS",
    page_icon="📄",
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
    st.title("📄 Proposal Generator")
    st.markdown("### Convert creative briefs into professional proposals and contracts")
    
    # Get the proposal generator agent
    agent = st.session_state.orchestrator.get_agent('proposal_generator')
    
    if not agent:
        st.error("Proposal Generator agent is not available")
        return
    
    # Tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📝 Generate Proposal", "📋 Proposal Templates", "📊 Proposal Analytics"])
    
    with tab1:
        generate_proposal_tab()
    
    with tab2:
        proposal_templates_tab()
    
    with tab3:
        proposal_analytics_tab()


def generate_proposal_tab():
    st.subheader("📝 Generate New Proposal")
    
    # Brief Input Section
    st.markdown("**Project Brief**")
    
    input_method = st.radio(
        "Input Method",
        ["Use Existing Brief", "Quick Input", "Upload Brief"],
        horizontal=True
    )
    
    brief_data = {}
    
    if input_method == "Use Existing Brief":
        st.info("💡 Select from previously parsed creative briefs")
        
        # Sample brief for demo
        sample_brief = {
            "project_title": "E-commerce Website Development",
            "client_name": "Fashion Forward Inc.",
            "project_type": "website",
            "goals": {
                "primary": "Create a modern e-commerce platform to increase online sales by 150%",
                "secondary": ["Improve user experience", "Mobile optimization", "SEO optimization"]
            },
            "deliverables": [
                {
                    "item": "Custom e-commerce website",
                    "description": "Full-featured online store with payment processing",
                    "format": "Website",
                    "priority": "high"
                },
                {
                    "item": "Mobile app",
                    "description": "iOS and Android shopping app",
                    "format": "Mobile App",
                    "priority": "medium"
                },
                {
                    "item": "Admin dashboard",
                    "description": "Inventory and order management system",
                    "format": "Web Dashboard",
                    "priority": "high"
                }
            ],
            "timeline": {
                "deadline": "2024-06-01",
                "urgency": "medium"
            },
            "constraints": {
                "budget": "$25,000 - $35,000"
            }
        }
        
        if st.checkbox("Use Sample Brief (Fashion Forward E-commerce)"):
            brief_data = sample_brief
            with st.expander("View Brief Details"):
                st.json(brief_data)
    
    elif input_method == "Quick Input":
        st.markdown("**Project Information**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_title = st.text_input("Project Title", value="Website Development Project")
            client_name = st.text_input("Client Name", value="Acme Corporation")
            project_type = st.selectbox("Project Type", ["website", "branding", "marketing", "general"])
        
        with col2:
            project_goal = st.text_area("Project Goal", height=100, 
                                      placeholder="Describe the main objective of this project")
            budget_range = st.text_input("Budget Range", placeholder="$10,000 - $15,000")
            timeline = st.date_input("Deadline", value=datetime.now().date() + timedelta(days=60))
        
        # Quick deliverables
        st.markdown("**Key Deliverables**")
        deliverable_input = st.text_area(
            "Deliverables (one per line)",
            placeholder="Website design\nResponsive development\nContent management system\nSEO optimization",
            height=100
        )
        
        deliverables = []
        if deliverable_input:
            for line in deliverable_input.split('\n'):
                if line.strip():
                    deliverables.append({
                        "item": line.strip(),
                        "description": f"Professional {line.strip().lower()}",
                        "priority": "medium"
                    })
        
        # Create brief data
        brief_data = {
            "project_title": project_title,
            "client_name": client_name,
            "project_type": project_type,
            "goals": {"primary": project_goal},
            "deliverables": deliverables,
            "timeline": {"deadline": timeline.isoformat()},
            "constraints": {"budget": budget_range}
        }
    
    else:  # Upload Brief
        uploaded_file = st.file_uploader(
            "Upload Brief",
            type=['json'],
            help="Upload a previously exported creative brief"
        )
        
        if uploaded_file is not None:
            try:
                brief_data = json.loads(uploaded_file.read())
                st.success("Brief loaded successfully!")
                with st.expander("View Loaded Brief"):
                    st.json(brief_data)
            except Exception as e:
                st.error(f"Error loading brief: {str(e)}")
    
    # Company Information
    st.subheader("🏢 Company Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Your Company Name", value="Creative Agency Inc.")
        contact_person = st.text_input("Contact Person", value="John Smith")
        company_email = st.text_input("Email", value="john@creativeagency.com")
        company_phone = st.text_input("Phone", value="+1 (555) 123-4567")
    
    with col2:
        company_address = st.text_area("Address", height=100, 
                                     value="123 Creative St\nDesign City, DC 12345")
        company_website = st.text_input("Website", value="www.creativeagency.com")
        tax_id = st.text_input("Tax ID (Optional)", placeholder="12-3456789")
    
    # Pricing Configuration
    st.subheader("💰 Pricing Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pricing_model = st.selectbox(
            "Pricing Model",
            ["Fixed Price", "Hourly Rate", "Milestone-based", "Retainer", "Value-based"]
        )
        
        if pricing_model == "Hourly Rate":
            hourly_rate = st.number_input("Hourly Rate ($)", min_value=50, max_value=500, value=150)
            estimated_hours = st.number_input("Estimated Hours", min_value=10, max_value=1000, value=80)
        elif pricing_model == "Fixed Price":
            fixed_price = st.number_input("Fixed Price ($)", min_value=1000, max_value=100000, value=15000)
        else:
            base_price = st.number_input("Base Price ($)", min_value=1000, max_value=100000, value=15000)
    
    with col2:
        payment_terms = st.selectbox(
            "Payment Terms",
            ["Net 30", "Net 15", "Due on Receipt", "50% upfront, 50% on completion", 
             "25% upfront, 75% on milestones", "Custom"]
        )
        
        if payment_terms == "Custom":
            custom_terms = st.text_area("Custom Payment Terms", height=80)
        
        include_expenses = st.checkbox("Include Expense Reimbursement Clause")
        rush_fee = st.checkbox("Include Rush Fee for Tight Deadlines")
    
    # Additional Options
    st.subheader("⚙️ Proposal Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_portfolio = st.checkbox("Include Portfolio Examples", value=True)
        include_testimonials = st.checkbox("Include Client Testimonials", value=True)
        include_team_bios = st.checkbox("Include Team Member Bios")
    
    with col2:
        include_risk_analysis = st.checkbox("Include Risk Assessment", value=True)
        include_alternatives = st.checkbox("Include Alternative Options")
        digital_signature = st.checkbox("Include Digital Signature Section", value=True)
    
    # Generate Button
    if st.button("🚀 Generate Proposal", type="primary", use_container_width=True):
        if not brief_data:
            st.error("Please provide a project brief first")
            return
        
        # Prepare company info
        company_info = {
            "name": company_name,
            "contact_person": contact_person,
            "email": company_email,
            "phone": company_phone,
            "address": company_address,
            "website": company_website,
            "tax_id": tax_id
        }
        
        # Prepare pricing preferences
        pricing_prefs = {
            "model": pricing_model,
            "payment_terms": payment_terms,
            "include_expenses": include_expenses,
            "rush_fee": rush_fee
        }
        
        if pricing_model == "Hourly Rate":
            pricing_prefs.update({
                "hourly_rate": hourly_rate,
                "estimated_hours": estimated_hours
            })
        elif pricing_model == "Fixed Price":
            pricing_prefs["fixed_price"] = fixed_price
        else:
            pricing_prefs["base_price"] = base_price
        
        # Prepare input data
        input_data = {
            'brief': brief_data,
            'pricing_preferences': pricing_prefs,
            'company_info': company_info
        }
        
        with st.spinner("Generating professional proposal with AI..."):
            try:
                # Execute agent processing
                agent = st.session_state.orchestrator.get_agent('proposal_generator')
                result = asyncio.run(agent.process(input_data))
                
                if result.get('success'):
                    proposal_data = result.get('result', {})
                    
                    # Display Results
                    st.success("✅ Proposal generated successfully!")
                    
                    # Proposal Header
                    st.subheader("📋 Proposal Overview")
                    
                    proposal_header = proposal_data.get('proposal_header', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Proposal #", proposal_header.get('proposal_number', 'PROP-001'))
                    
                    with col2:
                        st.metric("Date", proposal_header.get('date', datetime.now().strftime('%Y-%m-%d')))
                    
                    with col3:
                        st.metric("Valid Until", proposal_header.get('valid_until', 'TBD'))
                    
                    with col4:
                        st.metric("Client", proposal_header.get('client_name', 'Unknown'))
                    
                    # Executive Summary
                    st.subheader("📊 Executive Summary")
                    
                    exec_summary = proposal_data.get('executive_summary', {})
                    
                    if exec_summary.get('overview'):
                        st.markdown("**Project Overview**")
                        st.write(exec_summary['overview'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if exec_summary.get('key_benefits'):
                            st.markdown("**Key Benefits**")
                            for benefit in exec_summary['key_benefits']:
                                st.write(f"• {benefit}")
                    
                    with col2:
                        if exec_summary.get('success_metrics'):
                            st.markdown("**Success Metrics**")
                            for metric in exec_summary['success_metrics']:
                                st.write(f"• {metric}")
                    
                    if exec_summary.get('timeline_summary'):
                        st.info(f"**Timeline:** {exec_summary['timeline_summary']}")
                    
                    # Project Scope
                    st.subheader("🎯 Project Scope")
                    
                    project_scope = proposal_data.get('project_scope', {})
                    
                    if project_scope.get('objectives'):
                        st.markdown("**Objectives**")
                        for objective in project_scope['objectives']:
                            st.write(f"• {objective}")
                    
                    # Deliverables
                    if project_scope.get('deliverables'):
                        st.markdown("**Deliverables**")
                        
                        for i, deliverable in enumerate(project_scope['deliverables']):
                            with st.expander(f"Deliverable {i+1}: {deliverable.get('item', 'Item')}"):
                                st.write(f"**Description:** {deliverable.get('description', 'N/A')}")
                                st.write(f"**Specifications:** {deliverable.get('specifications', 'N/A')}")
                                st.write(f"**Acceptance Criteria:** {deliverable.get('acceptance_criteria', 'N/A')}")
                    
                    # Out of Scope
                    if project_scope.get('out_of_scope'):
                        st.markdown("**Out of Scope**")
                        st.warning("The following items are NOT included in this proposal:")
                        for item in project_scope['out_of_scope']:
                            st.write(f"• {item}")
                    
                    # Methodology
                    st.subheader("🔄 Methodology & Approach")
                    
                    methodology = proposal_data.get('methodology', {})
                    
                    if methodology.get('approach'):
                        st.write(methodology['approach'])
                    
                    if methodology.get('phases'):
                        st.markdown("**Project Phases**")
                        
                        for phase in methodology['phases']:
                            with st.expander(f"{phase.get('name', 'Phase')} - {phase.get('duration', 'TBD')}"):
                                st.write(f"**Description:** {phase.get('description', 'N/A')}")
                                
                                if phase.get('deliverables'):
                                    st.markdown("**Phase Deliverables:**")
                                    for deliverable in phase['deliverables']:
                                        st.write(f"• {deliverable}")
                                
                                if phase.get('milestones'):
                                    st.markdown("**Milestones:**")
                                    for milestone in phase['milestones']:
                                        st.write(f"• {milestone}")
                    
                    # Timeline
                    st.subheader("📅 Project Timeline")
                    
                    timeline_data = proposal_data.get('timeline', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Project Duration:** {timeline_data.get('project_duration', 'TBD')}")
                        st.write(f"**Start Date:** {timeline_data.get('start_date', 'TBD')}")
                        st.write(f"**End Date:** {timeline_data.get('end_date', 'TBD')}")
                    
                    with col2:
                        if timeline_data.get('buffer_time'):
                            st.info(f"**Buffer Time:** {timeline_data['buffer_time']}")
                    
                    if timeline_data.get('key_milestones'):
                        st.markdown("**Key Milestones**")
                        
                        milestone_df = pd.DataFrame(timeline_data['key_milestones'])
                        if not milestone_df.empty:
                            st.dataframe(milestone_df, use_container_width=True)
                    
                    # Investment & Pricing
                    st.subheader("💰 Investment & Pricing")
                    
                    investment = proposal_data.get('investment', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Pricing Information**")
                        st.write(f"**Pricing Model:** {investment.get('pricing_model', 'TBD')}")
                        st.write(f"**Total Investment:** {investment.get('total_investment', 'TBD')}")
                        st.write(f"**Payment Terms:** {investment.get('payment_terms', 'TBD')}")
                    
                    with col2:
                        if investment.get('payment_schedule'):
                            st.markdown("**Payment Schedule**")
                            for payment in investment['payment_schedule']:
                                st.write(f"• {payment.get('milestone', 'Payment')}: {payment.get('amount', 'TBD')} - Due: {payment.get('due_date', 'TBD')}")
                    
                    if investment.get('included_services'):
                        st.markdown("**Included Services**")
                        for service in investment['included_services']:
                            st.write(f"✅ {service}")
                    
                    if investment.get('additional_costs'):
                        st.markdown("**Potential Additional Costs**")
                        for cost in investment['additional_costs']:
                            st.write(f"⚠️ {cost}")
                    
                    # Team & Expertise
                    if proposal_data.get('team_and_expertise'):
                        st.subheader("👥 Team & Expertise")
                        
                        team_info = proposal_data['team_and_expertise']
                        
                        if team_info.get('team_overview'):
                            st.write(team_info['team_overview'])
                        
                        if team_info.get('key_team_members'):
                            st.markdown("**Key Team Members**")
                            
                            for member in team_info['key_team_members']:
                                with st.expander(f"{member.get('name', 'Team Member')} - {member.get('role', 'Role')}"):
                                    st.write(f"**Experience:** {member.get('experience', 'N/A')}")
                    
                    # Terms & Conditions
                    st.subheader("📜 Terms & Conditions")
                    
                    terms = proposal_data.get('terms_and_conditions', {})
                    
                    if terms.get('project_terms'):
                        st.markdown("**Project Terms**")
                        for term in terms['project_terms']:
                            st.write(f"• {term}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if terms.get('intellectual_property'):
                            st.markdown("**Intellectual Property**")
                            st.write(terms['intellectual_property'])
                        
                        if terms.get('revision_policy'):
                            st.markdown("**Revision Policy**")
                            st.write(terms['revision_policy'])
                    
                    with col2:
                        if terms.get('cancellation_policy'):
                            st.markdown("**Cancellation Policy**")
                            st.write(terms['cancellation_policy'])
                        
                        if terms.get('liability_limitation'):
                            st.markdown("**Liability Limitation**")
                            st.write(terms['liability_limitation'])
                    
                    # Next Steps
                    if proposal_data.get('next_steps'):
                        st.subheader("🚀 Next Steps")
                        
                        next_steps = proposal_data['next_steps']
                        
                        if next_steps.get('proposal_approval'):
                            st.info(f"**Approval Process:** {next_steps['proposal_approval']}")
                        
                        if next_steps.get('project_kickoff'):
                            st.info(f"**Project Kickoff:** {next_steps['project_kickoff']}")
                        
                        if next_steps.get('contact_information'):
                            st.info(f"**Contact Information:** {next_steps['contact_information']}")
                    
                    # Risk Assessment
                    if proposal_data.get('risk_mitigation'):
                        st.subheader("⚠️ Risk Assessment")
                        
                        with st.expander("View Risk Analysis"):
                            risks = proposal_data['risk_mitigation']
                            for risk_category, risk_info in risks.items():
                                if isinstance(risk_info, dict):
                                    st.markdown(f"**{risk_category.replace('_', ' ').title()}**")
                                    st.write(f"Description: {risk_info.get('description', 'N/A')}")
                                    st.write(f"Mitigation: {risk_info.get('mitigation', 'N/A')}")
                                    st.divider()
                    
                    # Actions
                    st.subheader("🎯 Actions")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📄 Generate Contract", use_container_width=True):
                            with st.spinner("Generating contract..."):
                                try:
                                    contract_result = asyncio.run(agent.generate_contract(proposal_data))
                                    
                                    if contract_result.get('success'):
                                        st.success("✅ Contract generated!")
                                        st.json(contract_result['contract'])
                                    else:
                                        st.error(f"❌ Contract generation failed: {contract_result.get('error')}")
                                
                                except Exception as e:
                                    st.error(f"❌ Error generating contract: {str(e)}")
                    
                    with col2:
                        if st.button("📧 Email Proposal", use_container_width=True):
                            st.info("Email integration would be implemented here")
                    
                    with col3:
                        if st.button("🔄 Create Revision", use_container_width=True):
                            st.info("Would create a new version for editing")
                    
                    # Export Options
                    st.subheader("📤 Export Proposal")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Download as JSON
                        st.download_button(
                            label="📄 Download JSON",
                            data=json.dumps(proposal_data, indent=2),
                            file_name=f"proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Generate PDF would be implemented with a PDF library
                        if st.button("📑 Generate PDF", use_container_width=True):
                            st.info("PDF generation would be implemented with reportlab or similar")
                    
                    # Save to database
                    try:
                        # Log the processing
                        st.session_state.db_manager.log_agent_execution({
                            'agent_name': 'proposal_generator',
                            'action': 'generate_proposal',
                            'input_data': input_data,
                            'output_data': proposal_data,
                            'success': True,
                            'execution_time': result.get('execution_time', 0)
                        })
                    except Exception as e:
                        st.warning(f"Could not save to database: {str(e)}")
                
                else:
                    st.error(f"❌ Proposal generation failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error generating proposal: {str(e)}")


def proposal_templates_tab():
    st.subheader("📋 Proposal Templates")
    
    # Template categories
    template_categories = {
        "Website Development": {
            "description": "Templates for web development projects",
            "templates": ["Basic Website", "E-commerce Site", "Custom Web App"]
        },
        "Branding & Design": {
            "description": "Templates for brand identity projects", 
            "templates": ["Logo Design", "Complete Brand Identity", "Brand Refresh"]
        },
        "Marketing Campaigns": {
            "description": "Templates for marketing and advertising projects",
            "templates": ["Social Media Campaign", "Content Marketing", "PPC Campaign"]
        },
        "Consulting": {
            "description": "Templates for consulting and strategy projects",
            "templates": ["Strategy Consultation", "Process Optimization", "Training Program"]
        }
    }
    
    st.info("📝 Pre-built proposal templates to speed up your workflow")
    
    for category, info in template_categories.items():
        with st.expander(f"{category} - {info['description']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                for template in info['templates']:
                    st.write(f"• {template}")
            
            with col2:
                if st.button(f"Use Template", key=f"template_{category}"):
                    st.info(f"Would load {category} template")


def proposal_analytics_tab():
    st.subheader("📊 Proposal Analytics")
    
    # Sample analytics data
    proposals_data = {
        'Proposal': ['Website A', 'Brand B', 'Marketing C', 'Website D', 'Consulting E'],
        'Status': ['Accepted', 'Pending', 'Accepted', 'Declined', 'Pending'],
        'Value': [15000, 8000, 12000, 20000, 25000],
        'Date Sent': ['2024-01-15', '2024-01-20', '2024-01-25', '2024-02-01', '2024-02-05'],
        'Response Time (days)': [7, 0, 3, 14, 0],
        'Client Type': ['SMB', 'Startup', 'Enterprise', 'SMB', 'Enterprise']
    }
    
    df = pd.DataFrame(proposals_data)
    df['Date Sent'] = pd.to_datetime(df['Date Sent'])
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_value = df['Value'].sum()
        st.metric("Total Proposal Value", f"${total_value:,}")
    
    with col2:
        accepted = len(df[df['Status'] == 'Accepted'])
        total = len(df)
        win_rate = (accepted / total) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col3:
        accepted_value = df[df['Status'] == 'Accepted']['Value'].sum()
        st.metric("Won Value", f"${accepted_value:,}")
    
    with col4:
        avg_response = df[df['Response Time (days)'] > 0]['Response Time (days)'].mean()
        st.metric("Avg Response Time", f"{avg_response:.1f} days")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = df['Status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Proposal Status Distribution"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Value by client type
        value_by_type = df.groupby('Client Type')['Value'].mean()
        fig_value = px.bar(
            x=value_by_type.index,
            y=value_by_type.values,
            title="Average Proposal Value by Client Type"
        )
        st.plotly_chart(fig_value, use_container_width=True)
    
    # Proposal performance table
    st.subheader("📋 Recent Proposals")
    st.dataframe(df, use_container_width=True)


if __name__ == "__main__":
    main()
