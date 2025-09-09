import streamlit as st
import asyncio
from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Workflow Optimizer - Creative Workflow AI OS",
    page_icon="⚡",
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
    st.title("⚡ Workflow Optimizer")
    st.markdown("### AI-powered workflow analysis and optimization recommendations")
    
    # Status check
    col1, col2 = st.columns([3, 1])
    with col2:
        optimizer = st.session_state.orchestrator.get_agent("workflow_optimizer")
        if optimizer:
            st.success("🟢 Optimizer Online")
        else:
            st.error("🔴 Optimizer Offline")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Workflow Analysis", "📊 Performance Dashboard", "💡 Optimization Recommendations", "⚙️ Settings"])
    
    with tab1:
        st.subheader("🔍 Workflow Analysis")
        
        # Data input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Project Data for Analysis**")
            
            # Project selection
            analysis_period = st.selectbox(
                "Analysis Period",
                ["Last 30 days", "Last 3 months", "Last 6 months", "Last year", "All time"]
            )
            
            project_types = st.multiselect(
                "Project Types to Include",
                ["Website", "Branding", "Marketing", "Mobile App", "E-commerce"],
                default=["Website", "Branding", "Marketing"]
            )
            
            team_members = st.multiselect(
                "Team Members to Analyze",
                ["Sarah (PM)", "Mike (Designer)", "Alex (Developer)", "Emma (Content)", "David (Strategy)"],
                default=["Sarah (PM)", "Mike (Designer)", "Alex (Developer)"]
            )
            
            # Upload workflow data
            st.write("**Upload Workflow Data (Optional)**")
            uploaded_data = st.file_uploader(
                "Upload CSV with project/task data",
                type=['csv'],
                help="Upload project data, task completion times, or team performance metrics"
            )
            
            if uploaded_data:
                try:
                    df = pd.read_csv(uploaded_data)
                    st.success(f"✅ Loaded {len(df)} records from uploaded data")
                    st.dataframe(df.head(), use_container_width=True)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        with col2:
            st.write("**Analysis Configuration**")
            
            focus_areas = st.multiselect(
                "Focus Areas",
                ["Task Completion Time", "Bottlenecks", "Team Utilization", "Communication", "Quality"],
                default=["Bottlenecks", "Team Utilization"]
            )
            
            analysis_depth = st.selectbox(
                "Analysis Depth",
                ["Quick Overview", "Standard Analysis", "Deep Dive"]
            )
            
            include_recommendations = st.checkbox("Include optimization recommendations", value=True)
            include_benchmarks = st.checkbox("Compare against industry benchmarks", value=True)
            
            # Analysis triggers
            analyze_efficiency = st.checkbox("Analyze task efficiency", value=True)
            detect_bottlenecks = st.checkbox("Detect workflow bottlenecks", value=True)
            team_performance = st.checkbox("Analyze team performance", value=True)
            resource_utilization = st.checkbox("Check resource utilization", value=True)
        
        # Run analysis button
        if st.button("🚀 Analyze Workflow", type="primary", use_container_width=True):
            with st.spinner("Analyzing workflow patterns and team performance..."):
                try:
                    # Prepare mock project data for analysis
                    project_data = {
                        'projects': [
                            {
                                'id': 'proj_001',
                                'name': 'Website Redesign',
                                'type': 'website',
                                'duration_days': 45,
                                'status': 'completed',
                                'team_size': 4,
                                'parallel_tasks': 3,
                                'revision_cycles': 2
                            },
                            {
                                'id': 'proj_002', 
                                'name': 'Brand Identity',
                                'type': 'branding',
                                'duration_days': 30,
                                'status': 'in_progress',
                                'team_size': 3,
                                'parallel_tasks': 2,
                                'revision_cycles': 1
                            }
                        ]
                    }
                    
                    # Mock team metrics
                    team_metrics = {
                        'overall_efficiency': 78,
                        'individual_metrics': [
                            {
                                'name': 'Sarah',
                                'role': 'Project Manager',
                                'productivity_score': 88,
                                'workload_level': 'balanced',
                                'collaboration_rating': 92
                            },
                            {
                                'name': 'Mike',
                                'role': 'Designer',
                                'productivity_score': 85,
                                'workload_level': 'high',
                                'collaboration_rating': 87
                            },
                            {
                                'name': 'Alex',
                                'role': 'Developer',
                                'productivity_score': 82,
                                'workload_level': 'balanced',
                                'collaboration_rating': 90
                            }
                        ]
                    }
                    
                    # Mock workflow history
                    workflow_history = [
                        {
                            'date': '2024-01-15',
                            'tasks': [
                                {
                                    'name': 'Design Review',
                                    'status': 'delayed',
                                    'delay_days': 2,
                                    'delay_reason': 'Client feedback delay',
                                    'phase': 'Design'
                                },
                                {
                                    'name': 'Development Setup',
                                    'status': 'completed',
                                    'phase': 'Development'
                                }
                            ]
                        }
                    ]
                    
                    # Run workflow optimization
                    optimization_result = st.session_state.orchestrator.process_with_agent(
                        'workflow_optimizer',
                        {
                            'project_data': project_data,
                            'team_metrics': team_metrics,
                            'workflow_history': workflow_history
                        }
                    )
                    
                    if optimization_result.get('success'):
                        result_data = optimization_result.get('result', {})
                        
                        st.success("✅ Workflow analysis completed!")
                        
                        # Display results
                        display_workflow_analysis(result_data)
                    
                    else:
                        st.error(f"Analysis failed: {optimization_result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")
    
    with tab2:
        st.subheader("📊 Performance Dashboard")
        
        # Key performance indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Workflow Efficiency", "78%", delta="5%")
        with col2:
            st.metric("Task Completion Rate", "92%", delta="3%")
        with col3:
            st.metric("Average Cycle Time", "5.2 days", delta="-0.8 days")
        with col4:
            st.metric("Team Utilization", "85%", delta="7%")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Efficiency Trends")
            
            # Sample efficiency data
            dates = pd.date_range('2024-01-01', periods=30, freq='D')
            efficiency_data = {
                'Date': dates,
                'Efficiency': [75 + (i % 10) + (i // 10) for i in range(30)],
                'Target': [85] * 30
            }
            
            df_efficiency = pd.DataFrame(efficiency_data)
            
            fig_efficiency = go.Figure()
            fig_efficiency.add_trace(go.Scatter(
                x=df_efficiency['Date'],
                y=df_efficiency['Efficiency'],
                name='Actual Efficiency',
                line=dict(color='blue')
            ))
            fig_efficiency.add_trace(go.Scatter(
                x=df_efficiency['Date'],
                y=df_efficiency['Target'],
                name='Target',
                line=dict(color='red', dash='dash')
            ))
            
            fig_efficiency.update_layout(
                title="Workflow Efficiency Over Time",
                xaxis_title="Date",
                yaxis_title="Efficiency (%)"
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Team Performance")
            
            # Team performance data
            team_data = {
                'Member': ['Sarah', 'Mike', 'Alex', 'Emma', 'David'],
                'Productivity': [88, 85, 82, 79, 83],
                'Collaboration': [92, 87, 90, 85, 88]
            }
            
            df_team = pd.DataFrame(team_data)
            
            fig_team = go.Figure()
            fig_team.add_trace(go.Bar(
                x=df_team['Member'],
                y=df_team['Productivity'],
                name='Productivity',
                marker_color='lightblue'
            ))
            fig_team.add_trace(go.Bar(
                x=df_team['Member'],
                y=df_team['Collaboration'],
                name='Collaboration',
                marker_color='lightgreen'
            ))
            
            fig_team.update_layout(
                title="Individual Performance Scores",
                xaxis_title="Team Member",
                yaxis_title="Score",
                barmode='group'
            )
            
            st.plotly_chart(fig_team, use_container_width=True)
        
        # Bottleneck analysis
        st.subheader("🚫 Bottleneck Analysis")
        
        bottleneck_data = {
            'Phase': ['Client Review', 'Design Approval', 'Development Testing', 'Content Creation', 'Final QA'],
            'Frequency': [15, 12, 8, 6, 4],
            'Avg Delay (days)': [3.2, 2.1, 1.8, 2.5, 1.2]
        }
        
        df_bottlenecks = pd.DataFrame(bottleneck_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_freq = px.bar(
                df_bottlenecks,
                x='Phase',
                y='Frequency',
                title="Bottleneck Frequency by Phase",
                color='Frequency',
                color_continuous_scale='reds'
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        
        with col2:
            fig_delay = px.bar(
                df_bottlenecks,
                x='Phase',
                y='Avg Delay (days)',
                title="Average Delay by Phase",
                color='Avg Delay (days)',
                color_continuous_scale='oranges'
            )
            st.plotly_chart(fig_delay, use_container_width=True)
        
        # Resource utilization
        st.subheader("📊 Resource Utilization")
        
        utilization_data = {
            'Resource': ['Project Managers', 'Designers', 'Developers', 'Content Writers', 'QA Testers'],
            'Current Utilization': [95, 88, 85, 72, 68],
            'Optimal Range': ['80-90%', '75-85%', '80-90%', '70-80%', '60-75%']
        }
        
        df_util = pd.DataFrame(utilization_data)
        st.dataframe(df_util, use_container_width=True)
    
    with tab3:
        st.subheader("💡 AI-Generated Optimization Recommendations")
        
        # Immediate actions
        st.write("**🚨 Immediate Actions (High Priority)**")
        
        immediate_actions = [
            {
                "action": "Implement client feedback buffer",
                "impact": "Reduce review delays by 40%",
                "effort": "Low",
                "timeline": "1 week"
            },
            {
                "action": "Standardize design review process", 
                "impact": "Improve approval speed by 25%",
                "effort": "Medium",
                "timeline": "2 weeks"
            },
            {
                "action": "Add parallel development tracks",
                "impact": "Reduce overall timeline by 15%", 
                "effort": "Medium",
                "timeline": "1 month"
            }
        ]
        
        for i, action in enumerate(immediate_actions):
            with st.expander(f"🎯 {action['action']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Expected Impact:** {action['impact']}")
                with col2:
                    st.write(f"**Implementation Effort:** {action['effort']}")
                with col3:
                    st.write(f"**Timeline:** {action['timeline']}")
        
        # Process improvements
        st.write("**🔧 Process Improvements (Medium Priority)**")
        
        process_improvements = [
            {
                "improvement": "Automated task assignment",
                "current": "Manual assignment based on availability",
                "improved": "AI-driven assignment based on skills and workload",
                "benefits": ["Better resource utilization", "Faster task distribution", "Improved quality matching"]
            },
            {
                "improvement": "Real-time progress tracking",
                "current": "Weekly status meetings",
                "improved": "Automated progress updates with dashboard",
                "benefits": ["Instant visibility", "Early issue detection", "Reduced meeting overhead"]
            }
        ]
        
        for improvement in process_improvements:
            with st.expander(f"⚙️ {improvement['improvement']}"):
                st.write(f"**Current Process:** {improvement['current']}")
                st.write(f"**Improved Process:** {improvement['improved']}")
                st.write("**Benefits:**")
                for benefit in improvement['benefits']:
                    st.write(f"• {benefit}")
        
        # Automation opportunities
        st.write("**🤖 Automation Opportunities**")
        
        automation_opps = [
            {
                "task": "File organization and naming",
                "time_saved": "2 hours per project",
                "complexity": "Low",
                "roi": "High"
            },
            {
                "task": "Client status report generation",
                "time_saved": "1 hour per week",
                "complexity": "Medium", 
                "roi": "Medium"
            },
            {
                "task": "Quality checklist validation",
                "time_saved": "30 minutes per deliverable",
                "complexity": "Medium",
                "roi": "High"
            }
        ]
        
        for opp in automation_opps:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"🤖 {opp['task']}")
            with col2:
                st.write(f"⏱️ {opp['time_saved']}")
            with col3:
                complexity_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}[opp['complexity']]
                st.write(f"{complexity_icon} {opp['complexity']}")
            with col4:
                roi_icon = {"Low": "📉", "Medium": "📊", "High": "📈"}[opp['roi']]
                st.write(f"{roi_icon} {opp['roi']}")
        
        # Implementation roadmap
        st.subheader("🗺️ Implementation Roadmap")
        
        roadmap_phases = {
            "Phase 1 (Weeks 1-2)": [
                "Implement client feedback buffer",
                "Standardize design review process", 
                "Set up automated file organization"
            ],
            "Phase 2 (Weeks 3-6)": [
                "Add parallel development tracks",
                "Implement real-time progress tracking",
                "Automate status report generation"
            ],
            "Phase 3 (Weeks 7-12)": [
                "Deploy AI-driven task assignment",
                "Implement quality checklist automation",
                "Full workflow optimization integration"
            ]
        }
        
        for phase, tasks in roadmap_phases.items():
            with st.expander(phase):
                for task in tasks:
                    st.write(f"✅ {task}")
        
        # Expected results
        st.subheader("📈 Expected Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Efficiency Gains**")
            st.metric("Workflow Efficiency", "78% → 92%", delta="14%")
            st.metric("Task Completion Rate", "92% → 97%", delta="5%")
        
        with col2:
            st.write("**Time Savings**") 
            st.metric("Average Cycle Time", "5.2 → 3.8 days", delta="-1.4 days")
            st.metric("Project Timeline", "15% reduction", delta="-15%")
        
        with col3:
            st.write("**Resource Optimization**")
            st.metric("Team Utilization", "85% → 90%", delta="5%")
            st.metric("Bottleneck Reduction", "60% fewer delays", delta="-60%")
    
    with tab4:
        st.subheader("⚙️ Workflow Optimizer Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Analysis Configuration**")
            
            analysis_frequency = st.selectbox(
                "Automatic analysis frequency",
                ["Daily", "Weekly", "Bi-weekly", "Monthly"]
            )
            
            efficiency_threshold = st.slider("Efficiency alert threshold (%)", 60, 95, 75)
            bottleneck_sensitivity = st.selectbox("Bottleneck detection sensitivity", ["Low", "Medium", "High"])
            
            st.write("**Data Sources**")
            include_project_data = st.checkbox("Include project completion data", value=True)
            include_time_tracking = st.checkbox("Include time tracking data", value=True)
            include_team_feedback = st.checkbox("Include team feedback surveys", value=False)
            include_client_feedback = st.checkbox("Include client satisfaction data", value=True)
        
        with col2:
            st.write("**Recommendation Engine**")
            
            recommendation_style = st.selectbox(
                "Recommendation style",
                ["Conservative", "Balanced", "Aggressive"]
            )
            
            focus_on_quick_wins = st.checkbox("Prioritize quick wins", value=True)
            consider_team_capacity = st.checkbox("Consider team capacity for changes", value=True)
            include_cost_analysis = st.checkbox("Include cost-benefit analysis", value=True)
            
            st.write("**Notifications**")
            alert_efficiency_drops = st.checkbox("Alert on efficiency drops", value=True)
            alert_new_bottlenecks = st.checkbox("Alert on new bottlenecks", value=True)
            weekly_summary = st.checkbox("Send weekly optimization summary", value=True)
        
        if st.button("💾 Save Optimizer Settings", type="primary"):
            st.success("✅ Workflow optimizer settings saved successfully!")

def display_workflow_analysis(result_data):
    """Display workflow analysis results"""
    
    # Workflow assessment
    assessment = result_data.get('workflow_assessment', {})
    if assessment:
        st.subheader("🔍 Workflow Assessment")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            efficiency_score = assessment.get('current_efficiency_score', 'Not specified')
            st.metric("Current Efficiency", efficiency_score)
        with col2:
            workflow_pattern = assessment.get('workflow_pattern', 'Unknown')
            st.metric("Workflow Pattern", workflow_pattern.title())
        with col3:
            overall_assessment = assessment.get('overall_assessment', 'No assessment available')
            st.write("**Overall Assessment:**")
            st.write(overall_assessment)
        
        # Strengths and weaknesses
        col1, col2 = st.columns(2)
        with col1:
            strengths = assessment.get('strengths', [])
            if strengths:
                st.write("**Strengths:**")
                for strength in strengths:
                    st.write(f"✅ {strength}")
        
        with col2:
            weaknesses = assessment.get('weaknesses', [])
            if weaknesses:
                st.write("**Areas for Improvement:**")
                for weakness in weaknesses:
                    st.write(f"⚠️ {weakness}")
    
    # Bottleneck analysis
    bottleneck_analysis = result_data.get('bottleneck_analysis', {})
    if bottleneck_analysis:
        st.subheader("🚫 Bottleneck Analysis")
        
        primary_bottlenecks = bottleneck_analysis.get('primary_bottlenecks', [])
        if primary_bottlenecks:
            for bottleneck in primary_bottlenecks:
                severity = bottleneck.get('impact_severity', 'medium')
                severity_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(severity, "🟡")
                
                with st.expander(f"{severity_color} {bottleneck.get('bottleneck', 'Unknown Bottleneck')}"):
                    st.write(f"**Location:** {bottleneck.get('location', 'Not specified')}")
                    st.write(f"**Frequency:** {bottleneck.get('frequency', 'Unknown')}")
                    st.write(f"**Estimated Delay:** {bottleneck.get('estimated_delay', 'Unknown')}")
                    st.write(f"**Root Cause:** {bottleneck.get('root_cause', 'Not identified')}")
                    
                    affected_members = bottleneck.get('affected_team_members', [])
                    if affected_members:
                        st.write(f"**Affected Team Members:** {', '.join(affected_members)}")
    
    # Team efficiency analysis
    team_analysis = result_data.get('team_efficiency_analysis', {})
    if team_analysis:
        st.subheader("👥 Team Efficiency Analysis")
        
        individual_performance = team_analysis.get('individual_performance', [])
        if individual_performance:
            st.write("**Individual Performance:**")
            
            for member in individual_performance:
                name = member.get('team_member', 'Unknown')
                efficiency = member.get('efficiency_score', 'Not specified')
                workload = member.get('workload_balance', 'Unknown')
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{name}**")
                with col2:
                    st.write(f"Efficiency: {efficiency}")
                with col3:
                    workload_color = {"underutilized": "🟡", "balanced": "🟢", "overloaded": "🔴"}.get(workload, "⚪")
                    st.write(f"{workload_color} {workload.title()}")
        
        # Team dynamics
        team_dynamics = team_analysis.get('team_dynamics', {})
        if team_dynamics:
            st.write("**Team Dynamics:**")
            col1, col2 = st.columns(2)
            
            with col1:
                comm_effectiveness = team_dynamics.get('communication_effectiveness', 'Not specified')
                st.write(f"Communication Effectiveness: {comm_effectiveness}")
                
                collab_quality = team_dynamics.get('collaboration_quality', 'Unknown')
                st.write(f"Collaboration Quality: {collab_quality.title()}")
            
            with col2:
                knowledge_sharing = team_dynamics.get('knowledge_sharing', 'Not specified')
                st.write(f"Knowledge Sharing: {knowledge_sharing}")
                
                decision_speed = team_dynamics.get('decision_making_speed', 'Unknown')
                st.write(f"Decision Making: {decision_speed.title()}")
    
    # Optimization recommendations
    recommendations = result_data.get('optimization_recommendations', {})
    if recommendations:
        st.subheader("💡 Optimization Recommendations")
        
        immediate_actions = recommendations.get('immediate_actions', [])
        if immediate_actions:
            st.write("**Immediate Actions:**")
            for action in immediate_actions:
                impact = action.get('expected_impact', 'medium')
                impact_color = {"low": "🟡", "medium": "🟠", "high": "🔴"}.get(impact, "🟡")
                
                with st.expander(f"{impact_color} {action.get('action', 'Unknown Action')}"):
                    st.write(f"**Implementation Effort:** {action.get('implementation_effort', 'Unknown')}")
                    st.write(f"**Timeline:** {action.get('timeline', 'Not specified')}")
                    st.write(f"**Responsible Party:** {action.get('responsible_party', 'Not assigned')}")
                    
                    success_metrics = action.get('success_metrics', [])
                    if success_metrics:
                        st.write("**Success Metrics:**")
                        for metric in success_metrics:
                            st.write(f"• {metric}")

if __name__ == "__main__":
    main()