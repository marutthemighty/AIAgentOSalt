import streamlit as st
import asyncio
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import our new learning modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Learning Intelligence - Creative Workflow AI OS",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if 'orchestrator' not in st.session_state:
    from core.agent_orchestrator import AgentOrchestrator
    st.session_state.orchestrator = AgentOrchestrator()

if 'db_manager' not in st.session_state:
    from core.database import DatabaseManager
    st.session_state.db_manager = DatabaseManager()

def initialize_learning_system():
    """Initialize the closed-loop learning system"""
    try:
        from modules.closed_loop_learning.outcome_tracker import OutcomeTracker
        from modules.closed_loop_learning.brand_memory import BrandMemorySystem
        from modules.closed_loop_learning.feedback_collector import FeedbackCollector
        from modules.closed_loop_learning.learning_engine import LearningEngine
        
        if 'learning_system' not in st.session_state:
            st.session_state.learning_system = {
                'outcome_tracker': OutcomeTracker(st.session_state.db_manager),
                'brand_memory': BrandMemorySystem(st.session_state.db_manager),
                'feedback_collector': FeedbackCollector(st.session_state.db_manager),
                'learning_engine': LearningEngine(st.session_state.db_manager)
            }
        return True
    except Exception as e:
        st.error(f"Failed to initialize learning system: {str(e)}")
        return False

def main():
    st.title("🧠 Learning Intelligence")
    st.markdown("### Advanced closed-loop learning system for continuous improvement")
    
    # Initialize learning system
    if not initialize_learning_system():
        st.error("Learning system unavailable")
        return
    
    learning_system = st.session_state.learning_system
    
    # Tabs for different learning functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Performance Analytics", 
        "🧠 Brand Intelligence", 
        "💬 Feedback Insights", 
        "📊 Learning Dashboard",
        "⚙️ System Controls"
    ])
    
    with tab1:
        performance_analytics_tab(learning_system)
    
    with tab2:
        brand_intelligence_tab(learning_system)
    
    with tab3:
        feedback_insights_tab(learning_system)
    
    with tab4:
        learning_dashboard_tab(learning_system)
    
    with tab5:
        system_controls_tab(learning_system)

def performance_analytics_tab(learning_system):
    """Performance analytics and outcome tracking"""
    st.header("🎯 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Proposal Performance")
        
        try:
            outcome_tracker = learning_system['outcome_tracker']
            
            # Get win rate
            win_rate = outcome_tracker.get_proposal_win_rate()
            
            # Create win rate gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = win_rate * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Proposal Win Rate (%)"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgray"},
                        {'range': [25, 50], 'color': "gray"},
                        {'range': [50, 75], 'color': "lightgreen"},
                        {'range': [75, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading proposal performance: {str(e)}")
    
    with col2:
        st.subheader("Estimation Accuracy")
        
        try:
            accuracy_metrics = outcome_tracker.get_estimation_accuracy()
            
            # Create accuracy metrics chart
            metrics_df = pd.DataFrame([
                {"Metric": "Hour Accuracy", "Score": accuracy_metrics.get("hour_accuracy", 0) * 100},
                {"Metric": "Cost Accuracy", "Score": accuracy_metrics.get("cost_accuracy", 0) * 100},
                {"Metric": "Client Satisfaction", "Score": accuracy_metrics.get("avg_satisfaction", 0) * 10}
            ])
            
            fig_bar = px.bar(
                metrics_df, 
                x="Metric", 
                y="Score",
                title="Estimation Accuracy Metrics",
                color="Score",
                color_continuous_scale="viridis",
                range_y=[0, 100]
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Show average delay
            avg_delay = accuracy_metrics.get("avg_delay_days", 0)
            if avg_delay > 0:
                st.warning(f"⏰ Average delivery delay: {avg_delay:.1f} days")
            else:
                st.success("✅ Projects delivered on time")
                
        except Exception as e:
            st.error(f"Error loading estimation accuracy: {str(e)}")
    
    # Learning insights
    st.subheader("📈 Performance Insights")
    
    try:
        insights = outcome_tracker.get_learning_insights()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Performance:**")
            proposal_perf = insights.get("proposal_performance", {})
            st.metric("Win Rate", f"{proposal_perf.get('win_rate', 0):.1%}")
            
            estimation_perf = insights.get("estimation_performance", {})
            st.metric("Hour Accuracy", f"{estimation_perf.get('hour_accuracy', 0):.1%}")
            st.metric("Average Satisfaction", f"{estimation_perf.get('avg_satisfaction', 0):.1f}/10")
        
        with col2:
            st.markdown("**Improvement Areas:**")
            improvement_areas = insights.get("improvement_areas", [])
            if improvement_areas:
                for area in improvement_areas:
                    st.write(f"• {area}")
            else:
                st.success("No critical improvement areas identified!")
                
    except Exception as e:
        st.error(f"Error loading insights: {str(e)}")

def brand_intelligence_tab(learning_system):
    """Brand memory and intelligence features"""
    st.header("🧠 Brand Intelligence")
    
    try:
        brand_memory = learning_system['brand_memory']
        
        # Client selection
        client_id = st.text_input("Client ID", placeholder="Enter client ID to view brand profile")
        
        if client_id:
            brand_profile = brand_memory.get_brand_profile(client_id)
            
            if brand_profile:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Brand Profile")
                    st.write(f"**Client:** {brand_profile['client_name']}")
                    st.write(f"**Confidence Score:** {brand_profile['confidence_score']:.2f}")
                    st.write(f"**Interactions:** {brand_profile['interaction_count']}")
                    st.write(f"**Last Updated:** {brand_profile['last_updated']}")
                
                with col2:
                    st.subheader("Brand Characteristics")
                    
                    # Display brand voice if available
                    brand_voice = brand_profile.get('brand_voice', {})
                    if brand_voice:
                        tone_profile = brand_voice.get('tone_profile', {})
                        if tone_profile:
                            tone_df = pd.DataFrame([
                                {"Characteristic": key.title(), "Score": value}
                                for key, value in tone_profile.items()
                            ])
                            
                            fig_tone = px.radar(
                                tone_df,
                                r='Score',
                                theta='Characteristic',
                                title="Brand Voice Profile",
                                range_r=[0, 1]
                            )
                            st.plotly_chart(fig_tone, use_container_width=True)
                
                # Recommendations
                st.subheader("🎯 Brand Recommendations")
                recommendations = brand_memory.get_recommendations(client_id, "general")
                
                if recommendations and recommendations['confidence'] > 0.3:
                    for rec in recommendations['recommendations']:
                        st.write(f"• {rec}")
                else:
                    st.info("Insufficient data for brand-specific recommendations")
            else:
                st.warning("No brand profile found for this client")
        
        # Add new brand interaction
        st.subheader("➕ Record Brand Interaction")
        
        with st.expander("Add New Interaction"):
            with st.form("brand_interaction"):
                int_client_id = st.text_input("Client ID")
                int_project_id = st.text_input("Project ID")
                int_content_type = st.selectbox("Content Type", 
                    ["proposal", "creative_brief", "content", "branding", "feedback"])
                int_content = st.text_area("Content/Description")
                int_feedback = st.text_area("Client Feedback (optional)")
                int_approval = st.selectbox("Approval Status", 
                    ["", "approved", "rejected", "needs_revision"])
                
                if st.form_submit_button("Record Interaction"):
                    if int_client_id and int_project_id and int_content:
                        content_data = {"content": int_content}
                        
                        interaction_id = brand_memory.record_interaction(
                            int_client_id, int_project_id, int_content_type,
                            content_data, int_feedback if int_feedback else None,
                            int_approval if int_approval else None
                        )
                        
                        st.success(f"Interaction recorded! ID: {interaction_id}")
                        st.rerun()
                    else:
                        st.error("Please fill in required fields")
        
    except Exception as e:
        st.error(f"Error in brand intelligence: {str(e)}")

def feedback_insights_tab(learning_system):
    """Feedback collection and insights"""
    st.header("💬 Feedback Insights")
    
    try:
        feedback_collector = learning_system['feedback_collector']
        
        # Pending feedback checkpoints
        st.subheader("⏳ Pending Feedback")
        
        pending_checkpoints = feedback_collector.get_pending_checkpoints()
        
        if pending_checkpoints:
            for checkpoint in pending_checkpoints[:5]:  # Show top 5
                with st.expander(f"{checkpoint['checkpoint_type'].title()} - {checkpoint['project_id'][:8]}"):
                    st.write(f"**Created:** {checkpoint['created_at']}")
                    st.write(f"**Type:** {checkpoint['checkpoint_type']}")
                    
                    # Show agent output
                    agent_output = checkpoint.get('agent_output', {})
                    if agent_output:
                        st.json(agent_output)
                    
                    # Feedback form
                    with st.form(f"feedback_{checkpoint['id']}"):
                        score = st.slider("Quality Score", 1, 10, 5)
                        feedback_text = st.text_area("Detailed Feedback")
                        improvements = st.text_area("Improvement Suggestions (one per line)")
                        approval = st.selectbox("Approval Status", 
                            ["approved", "rejected", "needs_revision"])
                        
                        if st.form_submit_button("Submit Feedback"):
                            improvement_list = [i.strip() for i in improvements.split('\n') if i.strip()]
                            
                            success = feedback_collector.submit_feedback(
                                checkpoint['id'], score, feedback_text,
                                improvement_list, approval
                            )
                            
                            if success:
                                st.success("Feedback submitted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to submit feedback")
        else:
            st.info("No pending feedback checkpoints")
        
        # Feedback analytics
        st.subheader("📊 Feedback Analytics")
        
        analytics = feedback_collector.get_feedback_analytics()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Score", f"{analytics.get('average_score', 0):.1f}/10")
        
        with col2:
            st.metric("Total Feedback", analytics.get('total_feedback', 0))
        
        with col3:
            st.metric("Approval Rate", f"{analytics.get('approval_rate', 0):.1%}")
        
        # Feedback by type
        feedback_by_type = analytics.get('feedback_by_type', {})
        if feedback_by_type:
            type_df = pd.DataFrame([
                {
                    "Checkpoint Type": type_name.title(),
                    "Average Score": data.get('average_score', 0),
                    "Count": data.get('count', 0),
                    "Approval Rate": data.get('approval_rate', 0)
                }
                for type_name, data in feedback_by_type.items()
            ])
            
            fig_types = px.scatter(
                type_df,
                x="Average Score",
                y="Approval Rate",
                size="Count",
                hover_name="Checkpoint Type",
                title="Feedback Performance by Type"
            )
            
            st.plotly_chart(fig_types, use_container_width=True)
        
        # Learning recommendations
        st.subheader("🎯 Learning Recommendations")
        recommendations = feedback_collector.get_learning_recommendations()
        
        for rec in recommendations:
            st.write(f"• {rec}")
            
    except Exception as e:
        st.error(f"Error in feedback insights: {str(e)}")

def learning_dashboard_tab(learning_system):
    """Comprehensive learning dashboard"""
    st.header("📊 Learning Dashboard")
    
    try:
        learning_engine = learning_system['learning_engine']
        
        # Get comprehensive insights
        insights = learning_engine.get_learning_insights()
        
        # Learning maturity
        st.subheader("🌱 Learning System Maturity")
        
        maturity = insights.get('learning_maturity', {})
        overall_score = maturity.get('overall_score', 0)
        level = maturity.get('level', 'nascent')
        
        # Maturity gauge
        fig_maturity = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = overall_score * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Learning Maturity: {level.title()}"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgray"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "green"}
                ]
            }
        ))
        
        st.plotly_chart(fig_maturity, use_container_width=True)
        
        # Component scores
        component_scores = maturity.get('component_scores', {})
        if component_scores:
            comp_df = pd.DataFrame([
                {"Component": key.replace('_', ' ').title(), "Score": value * 100}
                for key, value in component_scores.items()
            ])
            
            fig_components = px.bar(
                comp_df,
                x="Component",
                y="Score",
                title="Learning Component Maturity",
                color="Score",
                color_continuous_scale="viridis"
            )
            
            st.plotly_chart(fig_components, use_container_width=True)
        
        # Data points
        data_points = maturity.get('data_points', {})
        if data_points:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Tracked Outcomes", data_points.get('outcomes', 0))
            
            with col2:
                st.metric("Brand Interactions", data_points.get('brand_interactions', 0))
            
            with col3:
                st.metric("Feedback Sessions", data_points.get('feedback_sessions', 0))
        
        # Recommendations summary
        st.subheader("🎯 Priority Actions")
        
        recommendations = insights.get('recommendations', {})
        all_recs = []
        
        for category, recs in recommendations.items():
            if isinstance(recs, list):
                all_recs.extend(recs)
        
        if all_recs:
            for i, rec in enumerate(all_recs[:5], 1):
                st.write(f"{i}. {rec}")
        else:
            st.success("No immediate actions required - system performing well!")
            
    except Exception as e:
        st.error(f"Error in learning dashboard: {str(e)}")

def system_controls_tab(learning_system):
    """System controls and configuration"""
    st.header("⚙️ System Controls")
    
    # Manual data entry
    st.subheader("📝 Manual Data Entry")
    
    with st.expander("Track Project Outcome"):
        with st.form("manual_outcome"):
            project_id = st.text_input("Project ID")
            proposal_value = st.number_input("Proposal Value ($)", min_value=0.0)
            won = st.selectbox("Proposal Won?", [None, True, False])
            estimated_hours = st.number_input("Estimated Hours", min_value=0.0)
            actual_hours = st.number_input("Actual Hours", min_value=0.0)
            satisfaction = st.slider("Client Satisfaction", 1, 10, 5)
            
            if st.form_submit_button("Track Outcome"):
                if project_id:
                    try:
                        outcome_tracker = learning_system['outcome_tracker']
                        
                        # Track proposal
                        outcome_id = outcome_tracker.track_proposal_submission(
                            project_id, proposal_value
                        )
                        
                        if won is not None:
                            outcome_tracker.track_proposal_outcome(project_id, won)
                        
                        if estimated_hours > 0:
                            outcome_tracker.track_project_estimates(
                                project_id, estimated_hours, proposal_value
                            )
                        
                        if actual_hours > 0:
                            outcome_tracker.track_project_actuals(
                                project_id, actual_hours, proposal_value,
                                satisfaction_score=satisfaction
                            )
                        
                        st.success(f"Outcome tracked! ID: {outcome_id}")
                        
                    except Exception as e:
                        st.error(f"Error tracking outcome: {str(e)}")
                else:
                    st.error("Project ID is required")
    
    # Create feedback checkpoint
    with st.expander("Create Feedback Checkpoint"):
        with st.form("create_checkpoint"):
            cp_project_id = st.text_input("Project ID")
            cp_type = st.selectbox("Checkpoint Type", 
                ["proposal", "creative_brief", "content", "qa", "delivery"])
            cp_output = st.text_area("Agent Output (JSON format)")
            
            if st.form_submit_button("Create Checkpoint"):
                if cp_project_id and cp_output:
                    try:
                        agent_output = json.loads(cp_output)
                        feedback_collector = learning_system['feedback_collector']
                        
                        checkpoint_id = feedback_collector.create_checkpoint(
                            cp_project_id, cp_type, agent_output
                        )
                        
                        st.success(f"Checkpoint created! ID: {checkpoint_id}")
                        
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format")
                    except Exception as e:
                        st.error(f"Error creating checkpoint: {str(e)}")
                else:
                    st.error("All fields are required")
    
    # System status
    st.subheader("🔍 System Status")
    
    try:
        # Check database connection
        db_status = st.session_state.db_manager.check_connection()
        st.write(f"**Database Connection:** {'✅ Connected' if db_status else '❌ Disconnected'}")
        
        # Check learning system components
        for component_name, component in learning_system.items():
            st.write(f"**{component_name.replace('_', ' ').title()}:** ✅ Initialized")
        
        # Run learning analysis
        if st.button("Run Learning Analysis"):
            with st.spinner("Running comprehensive learning analysis..."):
                try:
                    # This would be async in a real implementation
                    analysis = learning_system['learning_engine'].get_learning_insights()
                    
                    st.success("Analysis completed!")
                    st.json(analysis)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    
    except Exception as e:
        st.error(f"Error checking system status: {str(e)}")

if __name__ == "__main__":
    main()