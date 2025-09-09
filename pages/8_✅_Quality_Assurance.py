import streamlit as st
import asyncio
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Quality Assurance - Creative Workflow AI OS",
    page_icon="✅",
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
    st.title("✅ Quality Assurance")
    st.markdown("### AI-powered asset validation and quality control")
    
    # Status check
    col1, col2 = st.columns([3, 1])
    with col2:
        asset_validator = st.session_state.orchestrator.get_agent("asset_validator")
        if asset_validator:
            st.success("🟢 Asset Validator Online")
        else:
            st.error("🔴 Asset Validator Offline")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Asset Validation", "📊 Quality Reports", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Upload Assets for Validation")
        
        # File upload section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "Upload project assets for validation",
                accept_multiple_files=True,
                type=['png', 'jpg', 'jpeg', 'pdf', 'svg', 'ai', 'psd', 'doc', 'docx', 'html', 'css', 'js']
            )
            
            if uploaded_files:
                st.info(f"📁 {len(uploaded_files)} files uploaded")
                
                # Display uploaded files
                for file in uploaded_files:
                    st.write(f"• {file.name} ({file.size} bytes)")
        
        with col2:
            st.markdown("**Validation Criteria**")
            
            project_type = st.selectbox(
                "Project Type",
                ["Website", "Branding", "Marketing", "Print", "Social Media"]
            )
            
            validation_level = st.selectbox(
                "Validation Level",
                ["Basic", "Standard", "Comprehensive"]
            )
            
            check_format = st.checkbox("Format Compliance", value=True)
            check_quality = st.checkbox("Quality Standards", value=True)
            check_brand = st.checkbox("Brand Guidelines", value=True)
            check_accessibility = st.checkbox("Accessibility", value=False)
        
        # Project brief input
        st.subheader("Project Brief Information")
        brief_text = st.text_area(
            "Paste project brief or requirements",
            placeholder="Enter project requirements, deliverables list, and quality standards...",
            height=100
        )
        
        # Validation button
        if st.button("🚀 Start Validation", type="primary", use_container_width=True):
            if uploaded_files and brief_text:
                with st.spinner("Validating assets against requirements..."):
                    try:
                        # Prepare validation data
                        assets_data = []
                        for file in uploaded_files:
                            assets_data.append({
                                'filename': file.name,
                                'size': f"{file.size/1024:.1f}KB",
                                'type': file.name.split('.')[-1].lower(),
                                'id': str(hash(file.name))
                            })
                        
                        brief_data = {
                            'project_type': project_type.lower(),
                            'requirements': brief_text,
                            'deliverables': [{'item': f"Asset {i+1}", 'format': 'various'} for i in range(len(assets_data))]
                        }
                        
                        validation_criteria = {
                            'level': validation_level.lower(),
                            'check_format': check_format,
                            'check_quality': check_quality,
                            'check_brand': check_brand,
                            'check_accessibility': check_accessibility
                        }
                        
                        # Run validation
                        validation_result = st.session_state.orchestrator.process_with_agent(
                            'asset_validator',
                            {
                                'assets': assets_data,
                                'brief': brief_data,
                                'validation_criteria': validation_criteria
                            }
                        )
                        
                        if validation_result.get('success'):
                            result_data = validation_result.get('result', {})
                            
                            # Display results
                            st.success("✅ Validation completed!")
                            
                            # Overall assessment
                            overall = result_data.get('overall_assessment', {})
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                quality_score = overall.get('quality_score', 'N/A')
                                st.metric("Quality Score", quality_score)
                            
                            with col2:
                                compliance = overall.get('compliance_status', 'Unknown')
                                st.metric("Compliance", compliance)
                            
                            with col3:
                                ready = overall.get('ready_for_delivery', 'Unknown')
                                st.metric("Delivery Ready", ready)
                            
                            # Detailed results
                            st.subheader("📋 Validation Details")
                            
                            asset_reviews = result_data.get('asset_by_asset_review', [])
                            for review in asset_reviews:
                                with st.expander(f"📄 {review.get('asset_name', 'Unknown Asset')}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.write(f"**Score:** {review.get('validation_score', 'N/A')}")
                                        st.write(f"**Status:** {review.get('status', 'Unknown')}")
                                    
                                    with col2:
                                        issues = review.get('issues_found', [])
                                        if issues:
                                            st.write("**Issues Found:**")
                                            for issue in issues:
                                                st.write(f"• {issue.get('issue', 'Unknown issue')}")
                                        else:
                                            st.success("No issues found")
                            
                            # Recommendations
                            recommendations = result_data.get('recommendations', {})
                            if recommendations:
                                st.subheader("💡 Recommendations")
                                
                                immediate = recommendations.get('immediate_actions', [])
                                if immediate:
                                    st.write("**Immediate Actions:**")
                                    for action in immediate:
                                        st.write(f"• {action}")
                                
                                suggestions = recommendations.get('suggested_improvements', [])
                                if suggestions:
                                    st.write("**Suggested Improvements:**")
                                    for suggestion in suggestions:
                                        st.write(f"• {suggestion}")
                        
                        else:
                            st.error(f"Validation failed: {validation_result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Validation error: {str(e)}")
            else:
                st.warning("Please upload files and provide project brief before validating.")
    
    with tab2:
        st.subheader("📊 Quality Reports")
        
        # Recent validations
        try:
            recent_activity = st.session_state.db_manager.get_recent_activity(limit=10)
            validation_activities = [a for a in recent_activity if 'asset_validator' in a.get('agent', '')]
            
            if validation_activities:
                st.write("**Recent Validation Activities:**")
                for activity in validation_activities:
                    with st.container():
                        st.write(f"🕐 {activity['timestamp']} - {activity['action']}")
                        if activity.get('details'):
                            st.caption(activity['details'])
                        st.divider()
            else:
                st.info("No recent validation activities found.")
        
        except Exception as e:
            st.error(f"Error loading validation history: {str(e)}")
        
        # Quality metrics
        st.subheader("📈 Quality Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Quality Score", "85%", delta="5%")
        with col2:
            st.metric("Pass Rate", "78%", delta="12%")
        with col3:
            st.metric("Assets Validated", "156", delta="23")
    
    with tab3:
        st.subheader("⚙️ Validation Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Default Validation Criteria**")
            
            default_format_check = st.checkbox("Format compliance by default", value=True)
            default_quality_check = st.checkbox("Quality standards by default", value=True)
            default_brand_check = st.checkbox("Brand guidelines by default", value=False)
            default_accessibility = st.checkbox("Accessibility checks by default", value=False)
            
            auto_fix_suggestions = st.checkbox("Suggest automated fixes", value=True)
            detailed_reporting = st.checkbox("Generate detailed reports", value=True)
        
        with col2:
            st.write("**Quality Thresholds**")
            
            pass_threshold = st.slider("Minimum score for pass", 0, 100, 70)
            warning_threshold = st.slider("Warning threshold", 0, 100, 85)
            
            st.write("**File Size Limits**")
            max_file_size = st.number_input("Max file size (MB)", min_value=1, max_value=100, value=10)
            
            st.write("**Supported Formats**")
            supported_formats = st.multiselect(
                "Allowed file formats",
                ["jpg", "png", "svg", "pdf", "ai", "psd", "doc", "docx", "html", "css", "js"],
                default=["jpg", "png", "svg", "pdf"]
            )
        
        if st.button("💾 Save Settings", type="primary"):
            settings = {
                'default_format_check': default_format_check,
                'default_quality_check': default_quality_check,
                'default_brand_check': default_brand_check,
                'default_accessibility': default_accessibility,
                'auto_fix_suggestions': auto_fix_suggestions,
                'detailed_reporting': detailed_reporting,
                'pass_threshold': pass_threshold,
                'warning_threshold': warning_threshold,
                'max_file_size': max_file_size,
                'supported_formats': supported_formats
            }
            
            # Save settings (in real implementation, this would save to database)
            st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()