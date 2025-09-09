import streamlit as st
import asyncio
from datetime import datetime
import json
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Branding Generator - Creative Workflow AI OS",
    page_icon="🎨",
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
    st.title("🎨 Branding Generator")
    st.markdown("### Generate comprehensive brand kits, tone guides, and messaging templates")
    
    # Get the branding generator agent
    agent = st.session_state.orchestrator.get_agent('branding_generator')
    
    if not agent:
        st.error("Branding Generator agent is not available")
        return
    
    # Input Section
    st.subheader("📋 Brand Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_name = st.text_input(
            "Brand Name",
            placeholder="Enter the brand/company name"
        )
        
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "Retail", "Education", "Consulting", 
             "Creative Agency", "Non-profit", "Food & Beverage", "Real Estate", "Other"]
        )
        
        brand_stage = st.selectbox(
            "Brand Stage",
            ["New Brand", "Rebranding", "Brand Refresh", "Brand Extension"]
        )
    
    with col2:
        company_size = st.selectbox(
            "Company Size",
            ["Startup (1-10 employees)", "Small (11-50 employees)", 
             "Medium (51-200 employees)", "Large (200+ employees)"]
        )
        
        budget_range = st.selectbox(
            "Budget Range",
            ["Under $5,000", "$5,000 - $15,000", "$15,000 - $50,000", 
             "$50,000 - $100,000", "Over $100,000"]
        )
        
        timeline = st.selectbox(
            "Timeline",
            ["Rush (1-2 weeks)", "Normal (3-6 weeks)", "Flexible (2-3 months)"]
        )
    
    # Brand Brief Input
    st.subheader("📝 Brand Brief")
    
    input_method = st.radio(
        "Input Method",
        ["Use Existing Brief", "Manual Input", "Upload Brief"],
        horizontal=True
    )
    
    brief_data = {}
    
    if input_method == "Use Existing Brief":
        st.info("💡 Select from previously parsed creative briefs")
        
        # Sample brief for demo
        sample_brief = {
            "project_title": "TechFlow Brand Identity",
            "client_name": brand_name or "TechFlow Inc.",
            "project_type": "branding",
            "goals": {
                "primary": "Create a modern, trustworthy brand identity for a B2B SaaS company",
                "secondary": ["Differentiate from competitors", "Appeal to enterprise clients"]
            },
            "target_audience": {
                "primary": "IT directors and CTOs at mid-size companies",
                "demographics": "35-50 years old, technology-focused, budget-conscious"
            },
            "brand_context": {
                "existing_brand": "Outdated logo and inconsistent messaging",
                "competitors": ["Salesforce", "HubSpot", "Microsoft"],
                "style_preferences": ["Modern", "Professional", "Trustworthy", "Innovative"]
            }
        }
        
        if st.checkbox("Use Sample Brief (TechFlow SaaS Company)"):
            brief_data = sample_brief
            with st.expander("View Brief Details"):
                st.json(brief_data)
    
    elif input_method == "Manual Input":
        st.markdown("**Brand Strategy Information**")
        
        brand_mission = st.text_area(
            "Brand Mission/Purpose",
            placeholder="What is the core purpose of this brand? What problem does it solve?",
            height=100
        )
        
        brand_values = st.text_input(
            "Core Values (comma-separated)",
            placeholder="Innovation, Trust, Excellence, Sustainability"
        )
        
        target_audience_desc = st.text_area(
            "Target Audience Description",
            placeholder="Describe your ideal customers - demographics, psychographics, behavior",
            height=100
        )
        
        brand_personality = st.text_input(
            "Brand Personality",
            placeholder="Professional, Friendly, Innovative, Trustworthy, etc."
        )
        
        competitive_landscape = st.text_area(
            "Competitive Landscape",
            placeholder="Who are your main competitors? What makes you different?",
            height=80
        )
        
        style_preferences = st.text_area(
            "Style Preferences & Inspiration",
            placeholder="Describe visual styles you like, colors, fonts, or reference brands",
            height=80
        )
        
        # Create brief data
        brief_data = {
            "project_title": f"{brand_name} Brand Identity" if brand_name else "Brand Identity Project",
            "client_name": brand_name or "Client",
            "project_type": "branding",
            "goals": {
                "primary": brand_mission,
                "secondary": [v.strip() for v in brand_values.split(',') if v.strip()]
            },
            "target_audience": {
                "primary": target_audience_desc,
                "demographics": "To be refined"
            },
            "brand_context": {
                "existing_brand": f"Current stage: {brand_stage}",
                "competitors": [c.strip() for c in competitive_landscape.split(',') if c.strip()],
                "style_preferences": [s.strip() for s in style_preferences.split(',') if s.strip()],
                "personality": brand_personality
            }
        }
    
    else:  # Upload Brief
        uploaded_file = st.file_uploader(
            "Upload Brand Brief",
            type=['json', 'txt'],
            help="Upload a previously exported brief or text document"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/json":
                    brief_data = json.loads(uploaded_file.read())
                else:
                    # Text file - create basic brief
                    text_content = str(uploaded_file.read(), "utf-8")
                    brief_data = {
                        "project_title": f"{brand_name} Brand Identity" if brand_name else "Brand Identity Project",
                        "client_name": brand_name or "Client",
                        "project_type": "branding",
                        "goals": {"primary": text_content},
                        "brand_context": {"style_preferences": ["Modern", "Professional"]}
                    }
                
                st.success("Brief loaded successfully!")
                with st.expander("View Loaded Brief"):
                    st.json(brief_data)
                    
            except Exception as e:
                st.error(f"Error loading brief: {str(e)}")
    
    # Brand Preferences
    st.subheader("🎨 Brand Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Visual Preferences**")
        
        color_preferences = st.multiselect(
            "Preferred Color Categories",
            ["Blue (Trust, Professional)", "Green (Growth, Nature)", "Red (Energy, Passion)",
             "Purple (Luxury, Creative)", "Orange (Friendly, Bold)", "Gray (Sophisticated, Neutral)",
             "Black (Premium, Modern)", "Bright Colors", "Pastels", "Earth Tones"]
        )
        
        style_direction = st.selectbox(
            "Visual Style Direction",
            ["Modern & Minimalist", "Classic & Traditional", "Bold & Creative", 
             "Elegant & Luxury", "Friendly & Approachable", "Technical & Professional"]
        )
    
    with col2:
        st.markdown("**Brand Archetype**")
        
        brand_archetype = st.selectbox(
            "Brand Archetype (Optional)",
            ["Auto-detect", "The Hero", "The Magician", "The Outlaw", "The Lover",
             "The Jester", "The Everyman", "The Caregiver", "The Ruler", 
             "The Creator", "The Innocent", "The Sage", "The Explorer"]
        )
        
        tone_of_voice = st.multiselect(
            "Tone of Voice",
            ["Professional", "Friendly", "Authoritative", "Casual", "Formal",
             "Playful", "Serious", "Warm", "Technical", "Conversational"]
        )
    
    # Generate Button
    generate_button = st.button(
        "🚀 Generate Brand Kit",
        type="primary",
        use_container_width=True,
        disabled=not brief_data
    )
    
    if generate_button and brief_data:
        # Prepare input data
        brand_preferences = {
            "color_preferences": color_preferences,
            "style_direction": style_direction,
            "brand_archetype": brand_archetype if brand_archetype != "Auto-detect" else None,
            "tone_of_voice": tone_of_voice,
            "industry": industry,
            "company_size": company_size,
            "budget_range": budget_range,
            "timeline": timeline
        }
        
        input_data = {
            'brief': brief_data,
            'brand_preferences': brand_preferences,
            'target_audience': brief_data.get('target_audience', {})
        }
        
        with st.spinner("Generating comprehensive brand kit with AI..."):
            try:
                # Execute agent processing
                result = asyncio.run(agent.process(input_data))
                
                if result.get('success'):
                    brand_kit = result.get('result', {})
                    
                    # Display Results
                    st.success("✅ Brand kit generated successfully!")
                    
                    # Brand Identity Overview
                    st.subheader("🎯 Brand Identity")
                    
                    brand_identity = brand_kit.get('brand_identity', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Core Identity**")
                        st.write(f"**Brand Name:** {brand_identity.get('brand_name', 'N/A')}")
                        st.write(f"**Tagline:** {brand_identity.get('tagline', 'N/A')}")
                        st.write(f"**Archetype:** {brand_identity.get('brand_archetype', 'N/A')}")
                        
                        if brand_identity.get('brand_personality'):
                            st.markdown("**Personality Traits**")
                            for trait in brand_identity['brand_personality']:
                                st.write(f"• {trait}")
                    
                    with col2:
                        st.markdown("**Mission & Vision**")
                        if brand_identity.get('mission_statement'):
                            st.markdown("**Mission:**")
                            st.write(brand_identity['mission_statement'])
                        
                        if brand_identity.get('vision_statement'):
                            st.markdown("**Vision:**")
                            st.write(brand_identity['vision_statement'])
                        
                        if brand_identity.get('core_values'):
                            st.markdown("**Core Values:**")
                            for value in brand_identity['core_values']:
                                st.write(f"• {value}")
                    
                    # Visual Identity
                    st.subheader("🎨 Visual Identity")
                    
                    visual_identity = brand_kit.get('visual_identity', {})
                    
                    # Color Palette
                    if visual_identity.get('color_palette'):
                        st.markdown("**Color Palette**")
                        
                        color_palette = visual_identity['color_palette']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if color_palette.get('primary'):
                                primary = color_palette['primary']
                                st.markdown("**Primary Color**")
                                st.markdown(f"""
                                <div style="background-color: {primary.get('hex', '#000000')}; 
                                            padding: 20px; border-radius: 8px; color: white; text-align: center;">
                                    {primary.get('color', 'Primary')}
                                    <br>{primary.get('hex', '#000000')}
                                </div>
                                """, unsafe_allow_html=True)
                                st.write(f"**Usage:** {primary.get('usage', 'Primary brand applications')}")
                        
                        with col2:
                            if color_palette.get('secondary'):
                                st.markdown("**Secondary Colors**")
                                for secondary in color_palette['secondary'][:2]:
                                    st.markdown(f"""
                                    <div style="background-color: {secondary.get('hex', '#666666')}; 
                                                padding: 15px; border-radius: 8px; color: white; text-align: center; margin: 5px 0;">
                                        {secondary.get('color', 'Secondary')}
                                        <br>{secondary.get('hex', '#666666')}
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        with col3:
                            if color_palette.get('accent'):
                                st.markdown("**Accent Colors**")
                                for accent in color_palette['accent'][:2]:
                                    st.markdown(f"""
                                    <div style="background-color: {accent.get('hex', '#999999')}; 
                                                padding: 15px; border-radius: 8px; color: white; text-align: center; margin: 5px 0;">
                                        {accent.get('color', 'Accent')}
                                        <br>{accent.get('hex', '#999999')}
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    # Typography
                    if visual_identity.get('typography'):
                        st.markdown("**Typography**")
                        
                        typography = visual_identity['typography']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if typography.get('primary_font'):
                                primary_font = typography['primary_font']
                                st.markdown("**Primary Font (Headlines)**")
                                st.write(f"**Font:** {primary_font.get('name', 'N/A')}")
                                st.write(f"**Category:** {primary_font.get('category', 'N/A')}")
                                st.write(f"**Usage:** {primary_font.get('usage', 'N/A')}")
                                
                                if primary_font.get('alternatives'):
                                    st.write("**Web-safe alternatives:**")
                                    for alt in primary_font['alternatives']:
                                        st.write(f"• {alt}")
                        
                        with col2:
                            if typography.get('secondary_font'):
                                secondary_font = typography['secondary_font']
                                st.markdown("**Secondary Font (Body Text)**")
                                st.write(f"**Font:** {secondary_font.get('name', 'N/A')}")
                                st.write(f"**Category:** {secondary_font.get('category', 'N/A')}")
                                st.write(f"**Usage:** {secondary_font.get('usage', 'N/A')}")
                                
                                if secondary_font.get('alternatives'):
                                    st.write("**Web-safe alternatives:**")
                                    for alt in secondary_font['alternatives']:
                                        st.write(f"• {alt}")
                    
                    # Logo Concepts
                    if visual_identity.get('logo_concepts'):
                        st.markdown("**Logo Concepts**")
                        
                        for i, concept in enumerate(visual_identity['logo_concepts']):
                            with st.expander(f"Concept {i+1}: {concept.get('concept', 'Logo Concept')}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Style:** {concept.get('style', 'N/A')}")
                                    st.write(f"**Description:** {concept.get('description', 'N/A')}")
                                
                                with col2:
                                    if concept.get('elements'):
                                        st.markdown("**Design Elements:**")
                                        for element in concept['elements']:
                                            st.write(f"• {element}")
                    
                    # Brand Voice & Messaging
                    st.subheader("💬 Brand Voice & Messaging")
                    
                    brand_voice = brand_kit.get('brand_voice', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Tone of Voice**")
                        st.write(f"**Overall Tone:** {brand_voice.get('tone_of_voice', 'N/A')}")
                        st.write(f"**Communication Style:** {brand_voice.get('communication_style', 'N/A')}")
                        
                        if brand_voice.get('vocabulary'):
                            vocabulary = brand_voice['vocabulary']
                            if vocabulary.get('use'):
                                st.markdown("**Words to Use:**")
                                st.write(", ".join(vocabulary['use']))
                            
                            if vocabulary.get('avoid'):
                                st.markdown("**Words to Avoid:**")
                                st.write(", ".join(vocabulary['avoid']))
                    
                    with col2:
                        if brand_voice.get('brand_story'):
                            st.markdown("**Brand Story**")
                            st.write(brand_voice['brand_story'])
                    
                    # Messaging Pillars
                    if brand_voice.get('messaging_pillars'):
                        st.markdown("**Messaging Pillars**")
                        
                        for pillar in brand_voice['messaging_pillars']:
                            with st.expander(f"Pillar: {pillar.get('pillar', 'Message Theme')}"):
                                st.write(f"**Description:** {pillar.get('description', 'N/A')}")
                                
                                if pillar.get('example_messages'):
                                    st.markdown("**Example Messages:**")
                                    for msg in pillar['example_messages']:
                                        st.write(f"• {msg}")
                    
                    # Brand Applications
                    st.subheader("📱 Brand Applications")
                    
                    applications = brand_kit.get('applications', {})
                    
                    # Business Materials
                    if applications.get('business_materials'):
                        st.markdown("**Business Materials**")
                        
                        for material in applications['business_materials']:
                            with st.expander(f"{material.get('item', 'Business Material')}"):
                                st.write(f"**Specifications:** {material.get('specifications', 'N/A')}")
                                st.write(f"**Design Notes:** {material.get('design_notes', 'N/A')}")
                    
                    # Digital Applications
                    if applications.get('digital_applications'):
                        st.markdown("**Digital Applications**")
                        
                        for app in applications['digital_applications']:
                            with st.expander(f"{app.get('platform', 'Digital Platform')}"):
                                st.write(f"**Specifications:** {app.get('specifications', 'N/A')}")
                                st.write(f"**Design Notes:** {app.get('design_notes', 'N/A')}")
                    
                    # Social Media Kit
                    if brand_kit.get('social_media_kit'):
                        st.subheader("📱 Social Media Kit")
                        
                        social_kit = brand_kit['social_media_kit']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if social_kit.get('profile_setup'):
                                profile = social_kit['profile_setup']
                                st.markdown("**Profile Setup**")
                                st.write(f"**Bio Template:** {profile.get('bio_template', 'N/A')}")
                                st.write(f"**Posting Tone:** {profile.get('posting_tone', 'N/A')}")
                                
                                if profile.get('hashtag_strategy'):
                                    st.write(f"**Hashtags:** {', '.join(profile['hashtag_strategy'])}")
                        
                        with col2:
                            if social_kit.get('content_pillars'):
                                st.markdown("**Content Strategy**")
                                for pillar in social_kit['content_pillars']:
                                    st.write(f"**{pillar.get('pillar', 'Content Type')}:** {pillar.get('percentage', '0')}%")
                    
                    # Usage Guidelines
                    if brand_kit.get('usage_guidelines'):
                        st.subheader("📏 Usage Guidelines")
                        
                        guidelines = brand_kit['usage_guidelines']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if guidelines.get('logo_usage'):
                                logo_usage = guidelines['logo_usage']
                                st.markdown("**Logo Usage**")
                                st.write(f"**Minimum Size:** {logo_usage.get('minimum_size', 'N/A')}")
                                st.write(f"**Clear Space:** {logo_usage.get('clear_space', 'N/A')}")
                                
                                if logo_usage.get('acceptable_variations'):
                                    st.write("**Acceptable Variations:**")
                                    for var in logo_usage['acceptable_variations']:
                                        st.write(f"• {var}")
                                
                                if logo_usage.get('prohibited_uses'):
                                    st.write("**Prohibited Uses:**")
                                    for use in logo_usage['prohibited_uses']:
                                        st.write(f"• {use}")
                        
                        with col2:
                            if guidelines.get('color_usage'):
                                color_usage = guidelines['color_usage']
                                st.markdown("**Color Usage**")
                                st.write(f"**Primary Applications:** {color_usage.get('primary_applications', 'N/A')}")
                                st.write(f"**Accessibility:** {color_usage.get('accessibility', 'N/A')}")
                                st.write(f"**Print Considerations:** {color_usage.get('print_considerations', 'N/A')}")
                    
                    # Brand Audit Checklist
                    if brand_kit.get('brand_audit_checklist'):
                        st.subheader("✅ Brand Audit Checklist")
                        
                        checklist = brand_kit['brand_audit_checklist']
                        
                        for category in checklist:
                            with st.expander(f"{category.get('category', 'Audit Category')}"):
                                for item in category.get('items', []):
                                    st.checkbox(item, key=f"audit_{hash(item)}")
                    
                    # Save to database
                    try:
                        # Log the processing
                        st.session_state.db_manager.log_agent_execution({
                            'agent_name': 'branding_generator',
                            'action': 'generate_brand_kit',
                            'input_data': input_data,
                            'output_data': brand_kit,
                            'success': True,
                            'execution_time': result.get('execution_time', 0)
                        })
                    except Exception as e:
                        st.warning(f"Could not save to database: {str(e)}")
                    
                    # Export Options
                    st.subheader("📤 Export Brand Kit")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Download complete brand kit
                        st.download_button(
                            label="📄 Download Complete Kit",
                            data=json.dumps(brand_kit, indent=2),
                            file_name=f"brand_kit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Download color palette
                        if visual_identity.get('color_palette'):
                            color_data = visual_identity['color_palette']
                            st.download_button(
                                label="🎨 Download Colors",
                                data=json.dumps(color_data, indent=2),
                                file_name=f"color_palette_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    
                    with col3:
                        # Download brand guidelines
                        if brand_kit.get('usage_guidelines'):
                            guidelines_data = brand_kit['usage_guidelines']
                            st.download_button(
                                label="📏 Download Guidelines",
                                data=json.dumps(guidelines_data, indent=2),
                                file_name=f"brand_guidelines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                
                else:
                    st.error(f"❌ Brand kit generation failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error generating brand kit: {str(e)}")
    
    # Help Section
    with st.expander("💡 Branding Best Practices"):
        st.markdown("""
        **To create effective brand identities:**
        
        1. **Start with Strategy**: Define mission, vision, values before visual design
        
        2. **Know Your Audience**: Understand who you're designing for
        
        3. **Research Competitors**: Understand the competitive landscape
        
        4. **Choose Colors Wisely**: Colors evoke emotions and associations
           - Blue: Trust, professionalism, stability
           - Green: Growth, nature, harmony
           - Red: Energy, passion, urgency
           - Purple: Luxury, creativity, sophistication
        
        5. **Typography Matters**: Choose fonts that reflect personality
           - Serif: Traditional, reliable, academic
           - Sans-serif: Modern, clean, approachable
           - Script: Elegant, personal, creative
        
        6. **Consistency is Key**: Apply brand elements consistently across all touchpoints
        
        7. **Plan for Scalability**: Ensure brand works across different sizes and mediums
        
        8. **Consider Accessibility**: Ensure sufficient color contrast and readability
        
        **Brand Archetype Guide:**
        - **Hero**: Nike, FedEx - courage, determination
        - **Magician**: Disney, Tesla - transformation, vision
        - **Sage**: Google, Harvard - wisdom, intelligence
        - **Innocent**: Coca-Cola, Dove - optimism, purity
        - **Explorer**: The North Face, Jeep - adventure, freedom
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
