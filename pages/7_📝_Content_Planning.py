import streamlit as st
import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Content Planning - Creative Workflow AI OS",
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
    st.title("📝 Content Planning")
    st.markdown("### Create comprehensive content plans with blogs, social media calendars, and SEO strategy")
    
    # Get the content plan generator agent
    agent = st.session_state.orchestrator.get_agent('content_plan_generator')
    
    if not agent:
        st.error("Content Plan Generator agent is not available")
        return
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Generate Plan", "📅 Content Calendar", "📊 Content Analytics", "🎯 SEO Strategy"])
    
    with tab1:
        generate_content_plan_tab()
    
    with tab2:
        content_calendar_tab()
    
    with tab3:
        content_analytics_tab()
    
    with tab4:
        seo_strategy_tab()


def generate_content_plan_tab():
    st.subheader("📋 Generate Content Plan")
    
    # Project Information
    st.markdown("**Project & Brand Information**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_name = st.text_input("Brand Name", value="TechFlow Solutions")
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "E-commerce", "Education", 
             "Food & Beverage", "Real Estate", "Professional Services", "Other"]
        )
        content_duration = st.selectbox(
            "Content Plan Duration",
            ["1 Month", "3 Months", "6 Months", "12 Months"]
        )
    
    with col2:
        business_type = st.selectbox(
            "Business Type",
            ["B2B", "B2C", "B2B2C", "Non-profit", "Personal Brand"]
        )
        company_size = st.selectbox(
            "Company Size",
            ["Solo/Freelancer", "Small Team (2-10)", "Medium (11-50)", "Large (50+)"]
        )
        content_budget = st.selectbox(
            "Content Budget Level",
            ["Minimal ($0-1k/month)", "Small ($1k-5k/month)", "Medium ($5k-15k/month)", "Large ($15k+/month)"]
        )
    
    # Brief Input
    st.subheader("📝 Project Brief")
    
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
            "project_title": "Content Marketing Strategy for TechFlow",
            "project_type": "marketing",
            "client_name": brand_name,
            "goals": {
                "primary": "Increase brand awareness and generate 50% more qualified leads through content marketing",
                "secondary": ["Establish thought leadership", "Improve SEO rankings", "Build email subscriber base"]
            },
            "target_audience": {
                "primary": "IT decision makers at mid-size companies (100-500 employees)",
                "demographics": "35-55 years old, tech-savvy, budget-conscious",
                "personas": ["CTO", "IT Director", "Technical Architect"]
            },
            "brand_context": {
                "existing_brand": "B2B SaaS platform for workflow automation",
                "competitors": ["Zapier", "Microsoft Power Automate", "Nintex"],
                "style_preferences": ["Professional", "Technical but accessible", "Data-driven"]
            }
        }
        
        if st.checkbox("Use Sample Brief (TechFlow B2B SaaS)"):
            brief_data = sample_brief
            with st.expander("View Brief Details"):
                st.json(brief_data)
    
    elif input_method == "Manual Input":
        st.markdown("**Content Goals & Strategy**")
        
        primary_goal = st.text_area(
            "Primary Content Goal",
            placeholder="What is the main objective of your content marketing? (e.g., increase brand awareness, generate leads, educate customers)",
            height=80
        )
        
        secondary_goals = st.text_input(
            "Secondary Goals (comma-separated)",
            placeholder="Build email list, improve SEO, establish thought leadership"
        )
        
        target_audience_desc = st.text_area(
            "Target Audience Description",
            placeholder="Describe your ideal audience - demographics, interests, pain points, where they consume content",
            height=100
        )
        
        brand_voice = st.text_input(
            "Brand Voice & Tone",
            placeholder="Professional, Friendly, Technical, Casual, Authoritative, etc."
        )
        
        current_content = st.text_area(
            "Current Content Situation",
            placeholder="Describe your current content efforts, what's working, what's not, existing channels",
            height=80
        )
        
        competitor_content = st.text_area(
            "Competitor Content Analysis",
            placeholder="What type of content are your competitors creating? What gaps do you see?",
            height=80
        )
        
        # Create brief data
        brief_data = {
            "project_title": f"Content Strategy for {brand_name}",
            "project_type": "content_marketing",
            "client_name": brand_name,
            "goals": {
                "primary": primary_goal,
                "secondary": [g.strip() for g in secondary_goals.split(',') if g.strip()]
            },
            "target_audience": {
                "primary": target_audience_desc,
                "demographics": "To be refined based on analysis"
            },
            "brand_context": {
                "existing_brand": current_content,
                "competitors": [c.strip() for c in competitor_content.split(',') if c.strip()],
                "style_preferences": [brand_voice] if brand_voice else ["Professional"]
            }
        }
    
    else:  # Upload Brief
        uploaded_file = st.file_uploader(
            "Upload Content Brief",
            type=['json', 'txt'],
            help="Upload a previously exported brief"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/json":
                    brief_data = json.loads(uploaded_file.read())
                else:
                    text_content = str(uploaded_file.read(), "utf-8")
                    brief_data = {
                        "project_title": f"Content Strategy for {brand_name}",
                        "project_type": "content_marketing",
                        "goals": {"primary": text_content},
                        "brand_context": {"style_preferences": ["Professional"]}
                    }
                
                st.success("Brief loaded successfully!")
                with st.expander("View Loaded Brief"):
                    st.json(brief_data)
            except Exception as e:
                st.error(f"Error loading brief: {str(e)}")
    
    # Content Channels & Types
    st.subheader("📱 Content Channels & Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Content Channels**")
        
        channels = st.multiselect(
            "Select Content Channels",
            ["Blog/Website", "LinkedIn", "Twitter", "Instagram", "Facebook", 
             "YouTube", "Email Newsletter", "Podcast", "Medium", "Industry Publications"],
            default=["Blog/Website", "LinkedIn", "Email Newsletter"]
        )
        
        primary_channel = st.selectbox(
            "Primary Channel",
            channels if channels else ["Blog/Website"]
        )
    
    with col2:
        st.markdown("**Content Types**")
        
        content_types = st.multiselect(
            "Select Content Types",
            ["Blog Posts", "Social Media Posts", "Email Campaigns", "Case Studies",
             "White Papers", "Infographics", "Videos", "Webinars", "Podcasts", "eBooks"],
            default=["Blog Posts", "Social Media Posts", "Email Campaigns"]
        )
        
        content_frequency = st.selectbox(
            "Publishing Frequency",
            ["Daily", "3x per week", "2x per week", "Weekly", "Bi-weekly", "Monthly"]
        )
    
    # Content Preferences
    st.subheader("⚙️ Content Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        seo_focus = st.checkbox("Include SEO optimization", value=True)
        evergreen_content = st.checkbox("Focus on evergreen content", value=True)
        user_generated = st.checkbox("Include user-generated content strategy")
        
        content_mix = st.selectbox(
            "Content Mix Preference",
            ["Educational Heavy (70% educational)", "Balanced Mix (40% educational, 30% promotional, 30% entertainment)",
             "Promotional Heavy (50% promotional)", "Custom Mix"]
        )
    
    with col2:
        repurposing = st.checkbox("Include content repurposing strategy", value=True)
        seasonal_content = st.checkbox("Include seasonal/trending content")
        behind_scenes = st.checkbox("Include behind-the-scenes content")
        
        engagement_priority = st.selectbox(
            "Engagement Priority",
            ["High Engagement", "Lead Generation", "Brand Awareness", "Education", "Community Building"]
        )
    
    # Generate Button
    if st.button("🚀 Generate Content Plan", type="primary", use_container_width=True):
        if not brief_data:
            st.error("Please provide a content brief first")
            return
        
        # Prepare content preferences
        content_prefs = {
            "channels": channels,
            "primary_channel": primary_channel,
            "content_types": content_types,
            "publishing_frequency": content_frequency,
            "seo_focus": seo_focus,
            "evergreen_focus": evergreen_content,
            "include_ugc": user_generated,
            "content_mix": content_mix,
            "repurposing": repurposing,
            "seasonal_content": seasonal_content,
            "behind_scenes": behind_scenes,
            "engagement_priority": engagement_priority,
            "industry": industry,
            "business_type": business_type,
            "budget_level": content_budget
        }
        
        # Prepare timeline
        timeline_mapping = {
            "1 Month": 30,
            "3 Months": 90,
            "6 Months": 180,
            "12 Months": 365
        }
        
        timeline = {
            "duration": content_duration,
            "days": timeline_mapping.get(content_duration, 90),
            "start_date": datetime.now().isoformat()[:10]
        }
        
        input_data = {
            'brief': brief_data,
            'content_preferences': content_prefs,
            'timeline': timeline
        }
        
        with st.spinner("Generating comprehensive content plan with AI..."):
            try:
                # Execute agent processing
                result = asyncio.run(agent.process(input_data))
                
                if result.get('success'):
                    content_plan = result.get('result', {})
                    
                    # Display Results
                    st.success("✅ Content plan generated successfully!")
                    
                    # Content Strategy Overview
                    st.subheader("🎯 Content Strategy")
                    
                    content_strategy = content_plan.get('content_strategy', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if content_strategy.get('objectives'):
                            st.markdown("**Content Objectives**")
                            for obj in content_strategy['objectives']:
                                st.write(f"• {obj}")
                        
                        if content_strategy.get('target_audience'):
                            audience = content_strategy['target_audience']
                            st.markdown("**Target Audience**")
                            st.write(f"**Primary:** {audience.get('primary_persona', 'Not specified')}")
                            
                            if audience.get('preferred_channels'):
                                st.write("**Preferred Channels:** " + ", ".join(audience['preferred_channels']))
                    
                    with col2:
                        if content_strategy.get('brand_voice'):
                            voice = content_strategy['brand_voice']
                            st.markdown("**Brand Voice**")
                            st.write(f"**Tone:** {voice.get('tone', 'Not specified')}")
                            st.write(f"**Style:** {voice.get('style', 'Not specified')}")
                            
                            if voice.get('do_use'):
                                st.write("**Use:** " + ", ".join(voice['do_use'][:3]))
                            if voice.get('dont_use'):
                                st.write("**Avoid:** " + ", ".join(voice['dont_use'][:3]))
                    
                    # Content Pillars
                    if content_strategy.get('content_pillars'):
                        st.subheader("🏛️ Content Pillars")
                        
                        pillars_data = []
                        for pillar in content_strategy['content_pillars']:
                            pillars_data.append({
                                'Pillar': pillar.get('pillar', 'Unknown'),
                                'Description': pillar.get('description', 'No description'),
                                'Percentage': pillar.get('percentage', '0%'),
                                'Content Types': ', '.join(pillar.get('content_types', []))
                            })
                        
                        if pillars_data:
                            df_pillars = pd.DataFrame(pillars_data)
                            st.dataframe(df_pillars, use_container_width=True)
                            
                            # Pillar distribution chart
                            percentages = [int(p.get('percentage', '0%').replace('%', '')) for p in content_strategy['content_pillars']]
                            names = [p.get('pillar', 'Unknown') for p in content_strategy['content_pillars']]
                            
                            if percentages:
                                fig_pillars = px.pie(
                                    values=percentages,
                                    names=names,
                                    title="Content Pillar Distribution"
                                )
                                st.plotly_chart(fig_pillars, use_container_width=True)
                    
                    # Content Calendar Overview
                    st.subheader("📅 Content Calendar")
                    
                    calendar_data = content_plan.get('content_calendar', {})
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Plan Duration", calendar_data.get('duration', 'Not specified'))
                    
                    with col2:
                        st.metric("Start Date", calendar_data.get('start_date', 'Not specified'))
                    
                    with col3:
                        st.metric("End Date", calendar_data.get('end_date', 'Not specified'))
                    
                    # Monthly Themes
                    if calendar_data.get('monthly_themes'):
                        st.markdown("**Monthly Themes**")
                        
                        for theme in calendar_data['monthly_themes']:
                            with st.expander(f"{theme.get('month', 'Month')}: {theme.get('theme', 'Theme')}"):
                                if theme.get('focus_areas'):
                                    st.markdown("**Focus Areas:**")
                                    for area in theme['focus_areas']:
                                        st.write(f"• {area}")
                                
                                if theme.get('content_count'):
                                    counts = theme['content_count']
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Blog Posts", counts.get('blog_posts', 0))
                                    with col2:
                                        st.metric("Social Posts", counts.get('social_posts', 0))
                                    with col3:
                                        st.metric("Other Content", counts.get('other_content', 0))
                    
                    # Content Types & Topics
                    st.subheader("📝 Content Types & Topics")
                    
                    content_types_data = content_plan.get('content_types', [])
                    
                    for content_type in content_types_data:
                        type_name = content_type.get('type', 'Unknown Type')
                        frequency = content_type.get('frequency', 'Not specified')
                        topics = content_type.get('topics', [])
                        
                        with st.expander(f"{type_name.title()} - {frequency}"):
                            if topics:
                                st.markdown("**Content Topics:**")
                                
                                topics_df = pd.DataFrame(topics)
                                if not topics_df.empty:
                                    for _, topic in topics_df.iterrows():
                                        st.markdown(f"**{topic.get('title', 'Untitled')}**")
                                        st.write(f"Description: {topic.get('description', 'No description')}")
                                        
                                        if topic.get('keywords'):
                                            st.write(f"Keywords: {', '.join(topic['keywords'])}")
                                        
                                        if topic.get('call_to_action'):
                                            st.write(f"CTA: {topic['call_to_action']}")
                                        
                                        st.divider()
                            else:
                                st.info("No specific topics generated for this content type")
                    
                    # Social Media Strategy
                    if content_plan.get('social_media_calendar'):
                        st.subheader("📱 Social Media Strategy")
                        
                        social_calendar = content_plan['social_media_calendar']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if social_calendar.get('platforms'):
                                st.markdown("**Platforms**")
                                for platform in social_calendar['platforms']:
                                    st.write(f"• {platform}")
                        
                        with col2:
                            if social_calendar.get('content_mix'):
                                st.markdown("**Content Mix**")
                                mix = social_calendar['content_mix']
                                for content_type, percentage in mix.items():
                                    st.write(f"• {content_type.title()}: {percentage}")
                        
                        # Weekly Posting Schedule
                        if social_calendar.get('posting_schedule'):
                            st.markdown("**Weekly Posting Schedule**")
                            
                            schedule = social_calendar['posting_schedule']
                            schedule_df = pd.DataFrame.from_dict(schedule, orient='index')
                            schedule_df.index.name = 'Day'
                            schedule_df.columns = ['Content Type']
                            
                            st.dataframe(schedule_df, use_container_width=True)
                    
                    # SEO Strategy
                    if content_plan.get('seo_strategy'):
                        st.subheader("🔍 SEO Strategy")
                        
                        seo = content_plan['seo_strategy']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if seo.get('primary_keywords'):
                                st.markdown("**Primary Keywords**")
                                for keyword in seo['primary_keywords']:
                                    st.write(f"• {keyword}")
                        
                        with col2:
                            if seo.get('secondary_keywords'):
                                st.markdown("**Secondary Keywords**")
                                for keyword in seo['secondary_keywords']:
                                    st.write(f"• {keyword}")
                        
                        # Content Clusters
                        if seo.get('content_clusters'):
                            st.markdown("**Content Clusters**")
                            
                            for cluster in seo['content_clusters']:
                                with st.expander(f"Cluster: {cluster.get('topic', 'Topic')}"):
                                    st.write(f"**Pillar Content:** {cluster.get('pillar_content', 'Not specified')}")
                                    
                                    if cluster.get('cluster_content'):
                                        st.markdown("**Supporting Content:**")
                                        for content in cluster['cluster_content']:
                                            st.write(f"• {content}")
                    
                    # Content Templates
                    if content_plan.get('content_templates'):
                        st.subheader("📄 Content Templates")
                        
                        templates = content_plan['content_templates']
                        
                        for template in templates:
                            with st.expander(f"{template.get('template_name', 'Template')} - {template.get('content_type', 'Unknown Type')}"):
                                if template.get('structure'):
                                    st.markdown("**Structure:**")
                                    for section in template['structure']:
                                        st.write(f"• {section}")
                                
                                if template.get('example'):
                                    st.markdown("**Example:**")
                                    st.text_area("", value=template['example'], height=100, key=f"template_{template.get('template_name', 'default')}")
                    
                    # Performance Metrics
                    if content_plan.get('performance_metrics'):
                        st.subheader("📊 Performance Metrics")
                        
                        metrics = content_plan['performance_metrics']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if metrics.get('kpis'):
                                st.markdown("**Key Performance Indicators**")
                                for kpi in metrics['kpis']:
                                    st.write(f"• {kpi}")
                        
                        with col2:
                            if metrics.get('tracking_methods'):
                                st.markdown("**Tracking Methods**")
                                for method in metrics['tracking_methods']:
                                    st.write(f"• {method}")
                        
                        if metrics.get('success_benchmarks'):
                            st.markdown("**Success Benchmarks**")
                            for benchmark in metrics['success_benchmarks']:
                                st.write(f"✅ {benchmark}")
                    
                    # Production Workflow
                    if content_plan.get('production_workflow'):
                        st.subheader("🔄 Production Workflow")
                        
                        workflow = content_plan['production_workflow']
                        
                        if workflow.get('workflow_stages'):
                            for stage in workflow['workflow_stages']:
                                with st.expander(f"{stage.get('stage', 'Stage')} - {stage.get('duration', 'Duration')}"):
                                    if stage.get('activities'):
                                        st.markdown("**Activities:**")
                                        for activity in stage['activities']:
                                            st.write(f"• {activity}")
                                    
                                    if stage.get('stakeholders'):
                                        st.write(f"**Stakeholders:** {', '.join(stage['stakeholders'])}")
                        
                        if workflow.get('quality_checkpoints'):
                            st.markdown("**Quality Checkpoints**")
                            for checkpoint in workflow['quality_checkpoints']:
                                st.write(f"✅ {checkpoint}")
                    
                    # Save to database
                    try:
                        # Log the processing
                        st.session_state.db_manager.log_agent_execution({
                            'agent_name': 'content_plan_generator',
                            'action': 'generate_content_plan',
                            'input_data': input_data,
                            'output_data': content_plan,
                            'success': True,
                            'execution_time': result.get('execution_time', 0)
                        })
                    except Exception as e:
                        st.warning(f"Could not save to database: {str(e)}")
                    
                    # Export Options
                    st.subheader("📤 Export Content Plan")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Download complete plan
                        st.download_button(
                            label="📄 Download Complete Plan",
                            data=json.dumps(content_plan, indent=2),
                            file_name=f"content_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        # Download content calendar
                        if content_plan.get('detailed_calendar'):
                            calendar_data = content_plan['detailed_calendar']
                            st.download_button(
                                label="📅 Download Calendar",
                                data=json.dumps(calendar_data, indent=2),
                                file_name=f"content_calendar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    
                    with col3:
                        # Download SEO strategy
                        if content_plan.get('seo_strategy'):
                            seo_data = content_plan['seo_strategy']
                            st.download_button(
                                label="🔍 Download SEO Strategy",
                                data=json.dumps(seo_data, indent=2),
                                file_name=f"seo_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                
                else:
                    st.error(f"❌ Content plan generation failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error generating content plan: {str(e)}")


def content_calendar_tab():
    st.subheader("📅 Content Calendar View")
    
    # Calendar visualization
    st.info("📅 Interactive content calendar with scheduling and publishing features")
    
    # Sample calendar data
    today = datetime.now()
    calendar_data = []
    
    for i in range(30):
        date = today + timedelta(days=i)
        calendar_data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Day': date.strftime('%A'),
            'Content Type': ['Blog Post', 'Social Media', 'Email', 'Video'][i % 4],
            'Platform': ['Website', 'LinkedIn', 'Instagram', 'YouTube'][i % 4],
            'Status': ['Planned', 'In Progress', 'Ready', 'Published'][i % 4],
            'Topic': f'Content Topic {i+1}'
        })
    
    df_calendar = pd.DataFrame(calendar_data)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        content_filter = st.multiselect(
            "Content Type",
            df_calendar['Content Type'].unique(),
            default=df_calendar['Content Type'].unique()
        )
    
    with col2:
        platform_filter = st.multiselect(
            "Platform",
            df_calendar['Platform'].unique(),
            default=df_calendar['Platform'].unique()
        )
    
    with col3:
        status_filter = st.multiselect(
            "Status",
            df_calendar['Status'].unique(),
            default=df_calendar['Status'].unique()
        )
    
    # Apply filters
    filtered_df = df_calendar[
        (df_calendar['Content Type'].isin(content_filter)) &
        (df_calendar['Platform'].isin(platform_filter)) &
        (df_calendar['Status'].isin(status_filter))
    ]
    
    # Calendar view
    st.dataframe(filtered_df, use_container_width=True)
    
    # Status distribution
    status_counts = filtered_df['Status'].value_counts()
    fig_status = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Content Status Distribution"
    )
    st.plotly_chart(fig_status, use_container_width=True)


def content_analytics_tab():
    st.subheader("📊 Content Performance Analytics")
    
    # Sample analytics data
    content_performance = {
        'Content': ['Blog Post A', 'Social Post B', 'Email C', 'Video D', 'Blog Post E'],
        'Type': ['Blog', 'Social', 'Email', 'Video', 'Blog'],
        'Views': [1500, 850, 400, 2200, 1100],
        'Engagements': [120, 85, 45, 180, 95],
        'Shares': [25, 35, 10, 60, 20],
        'Leads': [15, 5, 25, 8, 12],
        'Date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
    }
    
    df_performance = pd.DataFrame(content_performance)
    df_performance['Date'] = pd.to_datetime(df_performance['Date'])
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_views = df_performance['Views'].sum()
        st.metric("Total Views", f"{total_views:,}")
    
    with col2:
        total_engagements = df_performance['Engagements'].sum()
        st.metric("Total Engagements", total_engagements)
    
    with col3:
        total_shares = df_performance['Shares'].sum()
        st.metric("Total Shares", total_shares)
    
    with col4:
        total_leads = df_performance['Leads'].sum()
        st.metric("Total Leads", total_leads)
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Views by content type
        views_by_type = df_performance.groupby('Type')['Views'].sum()
        fig_views = px.bar(
            x=views_by_type.values,
            y=views_by_type.index,
            orientation='h',
            title="Views by Content Type"
        )
        st.plotly_chart(fig_views, use_container_width=True)
    
    with col2:
        # Engagement rate
        df_performance['Engagement Rate'] = (df_performance['Engagements'] / df_performance['Views'] * 100).round(2)
        fig_engagement = px.scatter(
            df_performance,
            x='Views',
            y='Engagements',
            size='Shares',
            color='Type',
            title="Engagement vs Views",
            hover_data=['Content', 'Engagement Rate']
        )
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Performance table
    st.subheader("📋 Detailed Performance")
    
    # Calculate additional metrics
    df_performance['Engagement Rate'] = (df_performance['Engagements'] / df_performance['Views'] * 100).round(2)
    df_performance['Lead Conversion'] = (df_performance['Leads'] / df_performance['Views'] * 100).round(2)
    
    st.dataframe(df_performance, use_container_width=True)


def seo_strategy_tab():
    st.subheader("🔍 SEO Content Strategy")
    
    # SEO Overview
    st.markdown("**SEO Performance Overview**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Target Keywords", "25", delta="5")
    
    with col2:
        st.metric("Ranking Keywords", "18", delta="3")
    
    with col3:
        st.metric("Avg. Position", "12.5", delta="-2.1")
    
    with col4:
        st.metric("Organic Traffic", "2,450", delta="15%")
    
    # Keyword strategy
    st.subheader("🎯 Keyword Strategy")
    
    keyword_data = {
        'Keyword': ['workflow automation', 'business process management', 'task automation', 
                   'digital transformation', 'productivity software'],
        'Search Volume': [8100, 2900, 4400, 12000, 6600],
        'Difficulty': [65, 45, 55, 80, 70],
        'Current Rank': [15, 8, 12, 25, 18],
        'Content Type': ['Blog', 'Landing Page', 'Blog', 'White Paper', 'Case Study']
    }
    
    df_keywords = pd.DataFrame(keyword_data)
    
    # Keyword opportunity analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Search volume vs difficulty
        fig_keywords = px.scatter(
            df_keywords,
            x='Difficulty',
            y='Search Volume',
            size='Current Rank',
            color='Content Type',
            title="Keyword Opportunity Analysis",
            hover_data=['Keyword']
        )
        st.plotly_chart(fig_keywords, use_container_width=True)
    
    with col2:
        # Ranking distribution
        rank_ranges = pd.cut(df_keywords['Current Rank'], 
                           bins=[0, 10, 20, 50, 100], 
                           labels=['Top 10', '11-20', '21-50', '50+'])
        rank_counts = rank_ranges.value_counts()
        
        fig_ranks = px.pie(
            values=rank_counts.values,
            names=rank_counts.index,
            title="Keyword Ranking Distribution"
        )
        st.plotly_chart(fig_ranks, use_container_width=True)
    
    # Keyword table
    st.dataframe(df_keywords, use_container_width=True)
    
    # Content gap analysis
    st.subheader("📝 Content Gap Analysis")
    
    gap_analysis = {
        'Topic Cluster': ['Automation Tools', 'Integration Guides', 'Industry Solutions', 'Best Practices'],
        'Content Needed': [3, 5, 4, 6],
        'Current Content': [1, 2, 1, 2],
        'Priority': ['High', 'Medium', 'High', 'Medium']
    }
    
    df_gaps = pd.DataFrame(gap_analysis)
    df_gaps['Content Gap'] = df_gaps['Content Needed'] - df_gaps['Current Content']
    
    st.dataframe(df_gaps, use_container_width=True)


if __name__ == "__main__":
    main()
