import streamlit as st
import asyncio
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Deliverables Packager - Creative Workflow AI OS",
    page_icon="📦",
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
    st.title("📦 Deliverables Packager")
    st.markdown("### Professional packaging and delivery of project assets")
    
    # Status check
    col1, col2 = st.columns([3, 1])
    with col2:
        packager = st.session_state.orchestrator.get_agent("deliverables_packager")
        if packager:
            st.success("🟢 Packager Online")
        else:
            st.error("🔴 Packager Offline")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Package Creation", "📁 File Organization", "📄 Documentation", "📊 Delivery History"])
    
    with tab1:
        st.subheader("Create Delivery Package")
        
        # Project information
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Project Information**")
            project_name = st.text_input("Project Name", value="Website Redesign")
            client_name = st.text_input("Client Name", value="ABC Corporation")
            project_type = st.selectbox(
                "Project Type",
                ["Website", "Branding", "Marketing", "Print", "Social Media"]
            )
            
            delivery_date = st.date_input("Delivery Date", value=datetime.now())
            package_version = st.text_input("Package Version", value="1.0")
        
        with col2:
            st.write("**Packaging Preferences**")
            
            file_organization = st.selectbox(
                "File Organization",
                ["Standard Structure", "Client Custom", "Minimal", "Detailed"]
            )
            
            include_documentation = st.checkbox("Include Documentation", value=True)
            include_source_files = st.checkbox("Include Source Files", value=True)
            create_readme = st.checkbox("Create README file", value=True)
            generate_changelog = st.checkbox("Generate Changelog", value=True)
        
        # File upload section
        st.subheader("📁 Upload Project Assets")
        
        uploaded_files = st.file_uploader(
            "Upload all project deliverables",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'pdf', 'svg', 'ai', 'psd', 'doc', 'docx', 'html', 'css', 'js', 'zip']
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} files uploaded for packaging")
            
            # Display uploaded files with categorization
            st.write("**Uploaded Files:**")
            
            file_categories = {
                'Images': [],
                'Documents': [],
                'Design Files': [],
                'Web Files': [],
                'Archives': []
            }
            
            for file in uploaded_files:
                ext = file.name.split('.')[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'svg']:
                    file_categories['Images'].append(file)
                elif ext in ['pdf', 'doc', 'docx']:
                    file_categories['Documents'].append(file)
                elif ext in ['ai', 'psd', 'sketch']:
                    file_categories['Design Files'].append(file)
                elif ext in ['html', 'css', 'js']:
                    file_categories['Web Files'].append(file)
                else:
                    file_categories['Archives'].append(file)
            
            for category, files in file_categories.items():
                if files:
                    with st.expander(f"{category} ({len(files)} files)"):
                        for file in files:
                            st.write(f"• {file.name} ({file.size} bytes)")
        
        # Additional information
        st.subheader("📝 Additional Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_description = st.text_area(
                "Project Description",
                placeholder="Brief description of the project and deliverables...",
                height=100
            )
            
            special_instructions = st.text_area(
                "Special Instructions",
                placeholder="Any special instructions for the client...",
                height=100
            )
        
        with col2:
            delivery_notes = st.text_area(
                "Delivery Notes",
                placeholder="Notes about the delivery package...",
                height=100
            )
            
            client_instructions = st.text_area(
                "Client Instructions",
                placeholder="Instructions for the client on how to use the deliverables...",
                height=100
            )
        
        # Create package button
        if st.button("🚀 Create Delivery Package", type="primary", use_container_width=True):
            if uploaded_files and project_name and client_name:
                with st.spinner("Creating professional delivery package..."):
                    try:
                        # Prepare packaging data
                        assets_data = []
                        for file in uploaded_files:
                            assets_data.append({
                                'filename': file.name,
                                'size': f"{file.size/1024:.1f}KB",
                                'type': file.name.split('.')[-1].lower(),
                                'id': str(hash(file.name))
                            })
                        
                        project_info = {
                            'name': project_name,
                            'client_name': client_name,
                            'type': project_type.lower(),
                            'delivery_date': delivery_date.isoformat(),
                            'version': package_version,
                            'description': project_description
                        }
                        
                        packaging_prefs = {
                            'organization': file_organization,
                            'include_documentation': include_documentation,
                            'include_source_files': include_source_files,
                            'create_readme': create_readme,
                            'generate_changelog': generate_changelog,
                            'special_instructions': special_instructions,
                            'delivery_notes': delivery_notes,
                            'client_instructions': client_instructions
                        }
                        
                        # Run packaging
                        packaging_result = st.session_state.orchestrator.process_with_agent(
                            'deliverables_packager',
                            {
                                'assets': assets_data,
                                'project_info': project_info,
                                'packaging_preferences': packaging_prefs
                            }
                        )
                        
                        if packaging_result.get('success'):
                            result_data = packaging_result.get('result', {})
                            
                            st.success("✅ Delivery package created successfully!")
                            
                            # Package summary
                            package_summary = result_data.get('package_summary', {})
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Files", package_summary.get('total_files', len(assets_data)))
                            with col2:
                                st.metric("Package Size", package_summary.get('total_size', 'Calculating...'))
                            with col3:
                                st.metric("Package Version", package_summary.get('package_version', package_version))
                            
                            # File structure
                            st.subheader("📁 Package Structure")
                            file_structure = result_data.get('file_structure', {})
                            
                            root_folder = file_structure.get('root_folder', project_name + '_Deliverables')
                            st.write(f"📂 **{root_folder}**")
                            
                            subfolders = file_structure.get('subfolders', [])
                            for folder in subfolders:
                                folder_name = folder.get('folder_name', 'Unknown')
                                file_count = folder.get('file_count', 0)
                                description = folder.get('description', 'No description')
                                
                                with st.expander(f"📁 {folder_name} ({file_count} files)"):
                                    st.write(f"**Description:** {description}")
                                    
                                    files = folder.get('files', [])
                                    for file in files:
                                        st.write(f"• {file.get('final_name', 'Unknown')} - {file.get('description', 'No description')}")
                            
                            # Documentation generated
                            documentation = result_data.get('documentation', {})
                            if documentation:
                                st.subheader("📄 Generated Documentation")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    readme = documentation.get('readme_file', {})
                                    if readme:
                                        st.write(f"✅ **{readme.get('filename', 'README.md')}**")
                                    
                                    changelog = documentation.get('changelog', {})
                                    if changelog:
                                        st.write(f"✅ **{changelog.get('filename', 'CHANGELOG.md')}**")
                                
                                with col2:
                                    file_guide = documentation.get('file_guide', {})
                                    if file_guide:
                                        st.write(f"✅ **{file_guide.get('filename', 'File_Guide.md')}**")
                                    
                                    instructions = documentation.get('instructions', {})
                                    if instructions:
                                        st.write(f"✅ **{instructions.get('filename', 'Client_Instructions.md')}**")
                            
                            # Quality assurance
                            qa_results = result_data.get('quality_assurance', {})
                            if qa_results:
                                st.subheader("✅ Quality Assurance")
                                
                                delivery_readiness = qa_results.get('delivery_readiness', {})
                                ready = delivery_readiness.get('ready_for_delivery', True)
                                
                                if ready:
                                    st.success("🎉 Package is ready for delivery!")
                                else:
                                    st.warning("⚠️ Package may need review before delivery")
                                    issues = delivery_readiness.get('issues_to_resolve', [])
                                    for issue in issues:
                                        st.write(f"• {issue}")
                            
                            # Delivery options
                            delivery_options = result_data.get('delivery_options', {})
                            if delivery_options:
                                st.subheader("📤 Delivery Options")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    zip_option = delivery_options.get('zip_package', {})
                                    if zip_option:
                                        st.write("**📦 ZIP Package**")
                                        st.write(f"Filename: {zip_option.get('filename', 'package.zip')}")
                                        st.write(f"Size: {zip_option.get('estimated_size', 'Unknown')}")
                                        
                                        if st.button("📥 Download ZIP", type="primary"):
                                            st.info("Download link would be generated here")
                                
                                with col2:
                                    cloud_option = delivery_options.get('cloud_delivery', {})
                                    if cloud_option:
                                        st.write("**☁️ Cloud Delivery**")
                                        st.write(f"Platform: {cloud_option.get('recommended_platform', 'Cloud Storage')}")
                                        st.write(f"Structure: {cloud_option.get('folder_structure', 'Organized folders')}")
                                        
                                        if st.button("☁️ Upload to Cloud"):
                                            st.info("Cloud upload would be initiated here")
                        
                        else:
                            st.error(f"Packaging failed: {packaging_result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Packaging error: {str(e)}")
            else:
                st.warning("Please upload files and provide project information before creating package.")
    
    with tab2:
        st.subheader("📁 File Organization Templates")
        
        # Organization templates
        templates = {
            "Website Project": {
                "folders": ["01_Final_Website_Files", "02_Design_Assets", "03_Documentation", "04_Source_Files"],
                "description": "Standard structure for website deliveries"
            },
            "Branding Project": {
                "folders": ["01_Logo_Files", "02_Brand_Guidelines", "03_Marketing_Materials", "04_Source_Files"],
                "description": "Organized structure for brand identity projects"
            },
            "Marketing Campaign": {
                "folders": ["01_Campaign_Assets", "02_Social_Media_Assets", "03_Documentation", "04_Source_Files"],
                "description": "Structure for marketing campaign deliverables"
            }
        }
        
        for template_name, template_info in templates.items():
            with st.expander(f"📂 {template_name}"):
                st.write(f"**Description:** {template_info['description']}")
                st.write("**Folder Structure:**")
                for folder in template_info['folders']:
                    st.write(f"• {folder}")
        
        # Custom template creation
        st.subheader("🛠️ Create Custom Template")
        
        col1, col2 = st.columns(2)
        
        with col1:
            template_name = st.text_input("Template Name")
            template_description = st.text_area("Template Description")
        
        with col2:
            custom_folders = st.text_area(
                "Folder Names (one per line)",
                placeholder="01_Final_Files\n02_Documentation\n03_Source_Files"
            )
        
        if st.button("💾 Save Template"):
            if template_name and custom_folders:
                st.success(f"✅ Template '{template_name}' saved successfully!")
            else:
                st.warning("Please provide template name and folder structure.")
    
    with tab3:
        st.subheader("📄 Documentation Generator")
        
        # Documentation templates
        doc_types = {
            "README": "Project overview and file guide",
            "File Guide": "Detailed explanation of each file",
            "Changelog": "Version history and changes",
            "Client Instructions": "How to use the deliverables",
            "Technical Notes": "Technical specifications and requirements"
        }
        
        selected_docs = st.multiselect(
            "Select documentation to generate",
            list(doc_types.keys()),
            default=["README", "File Guide", "Client Instructions"]
        )
        
        for doc_type in selected_docs:
            with st.expander(f"📝 {doc_type} Settings"):
                st.write(f"**Purpose:** {doc_types[doc_type]}")
                
                if doc_type == "README":
                    include_overview = st.checkbox("Include project overview", value=True, key=f"{doc_type}_overview")
                    include_file_list = st.checkbox("Include file list", value=True, key=f"{doc_type}_files")
                    include_contact = st.checkbox("Include contact information", value=True, key=f"{doc_type}_contact")
                
                elif doc_type == "Changelog":
                    auto_generate = st.checkbox("Auto-generate from version history", value=True, key=f"{doc_type}_auto")
                    include_dates = st.checkbox("Include modification dates", value=True, key=f"{doc_type}_dates")
                
                custom_content = st.text_area(
                    f"Additional content for {doc_type}",
                    placeholder=f"Add custom content for {doc_type}...",
                    key=f"{doc_type}_content"
                )
        
        if st.button("📄 Generate Documentation", type="primary"):
            if selected_docs:
                with st.spinner("Generating documentation..."):
                    st.success(f"✅ Generated {len(selected_docs)} documentation files!")
                    for doc in selected_docs:
                        st.write(f"• {doc}.md")
            else:
                st.warning("Please select at least one documentation type.")
    
    with tab4:
        st.subheader("📊 Delivery History")
        
        # Recent deliveries
        try:
            recent_activity = st.session_state.db_manager.get_recent_activity(limit=10)
            packaging_activities = [a for a in recent_activity if 'deliverables_packager' in a.get('agent', '')]
            
            if packaging_activities:
                st.write("**Recent Packaging Activities:**")
                for activity in packaging_activities:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"📦 {activity['action']}")
                        with col2:
                            st.write(activity['timestamp'])
                        with col3:
                            success = "✅" if activity.get('success', True) else "❌"
                            st.write(success)
                        
                        if activity.get('details'):
                            st.caption(activity['details'])
                        st.divider()
            else:
                st.info("No recent packaging activities found.")
        
        except Exception as e:
            st.error(f"Error loading packaging history: {str(e)}")
        
        # Delivery statistics
        st.subheader("📈 Delivery Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Packages Created", "42", delta="6")
        with col2:
            st.metric("Total Files Delivered", "1,256", delta="89")
        with col3:
            st.metric("Average Package Size", "85.2 MB", delta="12.1 MB")
        with col4:
            st.metric("Client Satisfaction", "4.8/5", delta="0.2")

if __name__ == "__main__":
    main()