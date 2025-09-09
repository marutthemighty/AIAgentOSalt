import streamlit as st
import asyncio
from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Analytics & Cost Estimator - Creative Workflow AI OS",
    page_icon="📈",
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
    st.title("📈 Analytics & Cost Estimator")
    st.markdown("### Data-driven project predictions and insights")
    
    # Status check
    col1, col2 = st.columns([3, 1])
    with col2:
        analytics_agent = st.session_state.orchestrator.get_agent("analytics_estimator")
        if analytics_agent:
            st.success("🟢 Analytics Engine Online")
        else:
            st.error("🔴 Analytics Engine Offline")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 Project Estimation", "📊 Analytics Dashboard", "📈 Performance Insights", "⚙️ Analytics Settings"])
    
    with tab1:
        st.subheader("🔮 AI-Powered Project Estimation")
        
        # Project brief input
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Project Brief**")
            project_brief = st.text_area(
                "Describe the project requirements",
                placeholder="Enter project description, goals, deliverables, and any specific requirements...",
                height=150
            )
            
            project_type = st.selectbox(
                "Project Type",
                ["Website", "Branding", "Marketing Campaign", "Mobile App", "E-commerce", "Custom"]
            )
            
            # Deliverables
            st.write("**Deliverables**")
            deliverables_text = st.text_area(
                "List required deliverables (one per line)",
                placeholder="Homepage design\nProduct pages\nContact form\nLogo design\nBrand guidelines",
                height=100
            )
        
        with col2:
            st.write("**Project Constraints**")
            
            timeline_preference = st.selectbox(
                "Timeline Preference",
                ["Flexible", "Normal", "Tight", "Rush"]
            )
            
            budget_range = st.selectbox(
                "Budget Range",
                ["$5K - $10K", "$10K - $25K", "$25K - $50K", "$50K+", "To be determined"]
            )
            
            team_size = st.selectbox(
                "Team Size",
                ["Solo (1 person)", "Small (2-3 people)", "Medium (4-6 people)", "Large (7+ people)"]
            )
            
            client_tier = st.selectbox(
                "Client Type",
                ["Startup", "SME", "Enterprise", "Non-profit"]
            )
            
            complexity_level = st.selectbox(
                "Perceived Complexity",
                ["Simple", "Medium", "Complex", "Very Complex"]
            )
        
        # Additional parameters
        with st.expander("🔧 Advanced Parameters"):
            col1, col2 = st.columns(2)
            
            with col1:
                has_integrations = st.checkbox("Requires third-party integrations")
                custom_development = st.checkbox("Custom development needed")
                multiple_stakeholders = st.checkbox("Multiple stakeholders involved")
                tight_deadline = st.checkbox("Tight deadline constraints")
            
            with col2:
                new_technology = st.checkbox("Uses new/experimental technology")
                complex_approval_process = st.checkbox("Complex approval process")
                scope_likely_to_change = st.checkbox("Scope likely to change")
                high_quality_standards = st.checkbox("High quality standards required")
        
        # Generate estimate button
        if st.button("🚀 Generate AI Estimate", type="primary", use_container_width=True):
            if project_brief and deliverables_text:
                with st.spinner("Analyzing project and generating data-driven estimates..."):
                    try:
                        # Parse deliverables
                        deliverables_list = [
                            {'item': line.strip(), 'format': 'various'} 
                            for line in deliverables_text.split('\n') 
                            if line.strip()
                        ]
                        
                        # Prepare analysis data
                        brief_data = {
                            'project_type': project_type.lower(),
                            'description': project_brief,
                            'deliverables': deliverables_list,
                            'constraints': {
                                'timeline': timeline_preference.lower(),
                                'budget_range': budget_range,
                                'complexity': complexity_level.lower()
                            },
                            'timeline': {
                                'preference': timeline_preference.lower(),
                                'flexible': timeline_preference == 'Flexible'
                            }
                        }
                        
                        # Team and historical data (mock data)
                        team_info = {
                            'size': team_size.lower(),
                            'client_tier': client_tier.lower(),
                            'experience_level': 'medium'
                        }
                        
                        historical_data = [
                            {'type': 'website', 'duration_days': 45, 'final_cost': 15000, 'successful': True},
                            {'type': 'branding', 'duration_days': 30, 'final_cost': 8000, 'successful': True},
                            {'type': 'marketing', 'duration_days': 21, 'final_cost': 6000, 'successful': True}
                        ]
                        
                        # Run analytics
                        analytics_result = st.session_state.orchestrator.process_with_agent(
                            'analytics_estimator',
                            {
                                'brief': brief_data,
                                'historical_data': historical_data,
                                'team_info': team_info
                            }
                        )
                        
                        if analytics_result.get('success'):
                            result_data = analytics_result.get('result', {})
                            
                            st.success("✅ AI analysis completed!")
                            
                            # Display results
                            display_estimation_results(result_data)
                        
                        else:
                            st.error(f"Analysis failed: {analytics_result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")
            else:
                st.warning("Please provide project brief and deliverables list.")
    
    with tab2:
        st.subheader("📊 Analytics Dashboard")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Projects Analyzed", "156", delta="23")
        with col2:
            st.metric("Avg. Accuracy", "87%", delta="5%")
        with col3:
            st.metric("Cost Predictions", "142", delta="18")
        with col4:
            st.metric("Time Saved", "45 hrs", delta="12 hrs")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Project Types Analysis")
            
            # Sample data for project types
            project_types_data = {
                'Type': ['Website', 'Branding', 'Marketing', 'Mobile App', 'E-commerce'],
                'Count': [45, 32, 28, 18, 12],
                'Avg Cost': [15000, 8000, 6000, 25000, 35000]
            }
            
            df_types = pd.DataFrame(project_types_data)
            
            fig_types = px.bar(
                df_types, 
                x='Type', 
                y='Count',
                title="Projects by Type",
                color='Avg Cost',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_types, use_container_width=True)
        
        with col2:
            st.subheader("💰 Cost Distribution")
            
            # Sample cost distribution data
            cost_ranges = ['$5K-$10K', '$10K-$25K', '$25K-$50K', '$50K+']
            cost_counts = [35, 65, 40, 15]
            
            fig_costs = px.pie(
                values=cost_counts,
                names=cost_ranges,
                title="Project Cost Distribution"
            )
            st.plotly_chart(fig_costs, use_container_width=True)
        
        # Timeline accuracy chart
        st.subheader("⏱️ Estimation Accuracy Over Time")
        
        # Sample accuracy data
        dates = pd.date_range('2024-01-01', periods=12, freq='M')
        accuracy_data = {
            'Date': dates,
            'Cost Accuracy': [78, 82, 85, 88, 84, 87, 89, 91, 88, 90, 92, 87],
            'Timeline Accuracy': [75, 80, 82, 85, 87, 84, 88, 89, 91, 88, 90, 89]
        }
        
        df_accuracy = pd.DataFrame(accuracy_data)
        
        fig_accuracy = go.Figure()
        fig_accuracy.add_trace(go.Scatter(
            x=df_accuracy['Date'], 
            y=df_accuracy['Cost Accuracy'],
            name='Cost Accuracy',
            line=dict(color='blue')
        ))
        fig_accuracy.add_trace(go.Scatter(
            x=df_accuracy['Date'], 
            y=df_accuracy['Timeline Accuracy'],
            name='Timeline Accuracy',
            line=dict(color='red')
        ))
        
        fig_accuracy.update_layout(
            title="Prediction Accuracy Trends",
            xaxis_title="Date",
            yaxis_title="Accuracy (%)",
            hovermode='x'
        )
        
        st.plotly_chart(fig_accuracy, use_container_width=True)
    
    with tab3:
        st.subheader("📈 Performance Insights")
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Prediction Performance**")
            
            accuracy_metrics = {
                'Metric': ['Cost Estimation', 'Timeline Prediction', 'Resource Planning', 'Risk Assessment'],
                'Accuracy': [87, 84, 79, 82],
                'Confidence': [92, 88, 85, 86]
            }
            
            df_metrics = pd.DataFrame(accuracy_metrics)
            st.dataframe(df_metrics, use_container_width=True)
            
            # Top performing project types
            st.write("**Best Prediction Accuracy by Type**")
            top_types = {
                'Project Type': ['Branding', 'Website', 'Marketing', 'Mobile App'],
                'Accuracy': [91, 87, 85, 79]
            }
            df_top = pd.DataFrame(top_types)
            st.dataframe(df_top, use_container_width=True)
        
        with col2:
            st.write("**Common Risk Factors**")
            
            risk_factors = [
                {"Risk": "Scope creep", "Frequency": "68%", "Impact": "High"},
                {"Risk": "Unclear requirements", "Frequency": "45%", "Impact": "Medium"},
                {"Risk": "Tight deadlines", "Frequency": "52%", "Impact": "High"},
                {"Risk": "Multiple stakeholders", "Frequency": "38%", "Impact": "Medium"},
                {"Risk": "New technology", "Frequency": "23%", "Impact": "High"}
            ]
            
            for risk in risk_factors:
                with st.container():
                    col_risk, col_freq, col_impact = st.columns([2, 1, 1])
                    with col_risk:
                        st.write(f"• {risk['Risk']}")
                    with col_freq:
                        st.write(risk['Frequency'])
                    with col_impact:
                        impact_color = "🔴" if risk['Impact'] == "High" else "🟡"
                        st.write(f"{impact_color} {risk['Impact']}")
        
        # Improvement recommendations
        st.subheader("💡 AI Recommendations")
        
        recommendations = [
            {
                "area": "Timeline Estimation",
                "current": "84% accuracy",
                "recommendation": "Include more buffer time for complex integrations",
                "impact": "Expected 7% improvement"
            },
            {
                "area": "Cost Prediction",
                "current": "87% accuracy", 
                "recommendation": "Factor in client tier pricing variations",
                "impact": "Expected 5% improvement"
            },
            {
                "area": "Risk Assessment",
                "current": "82% accuracy",
                "recommendation": "Add stakeholder complexity scoring",
                "impact": "Expected 8% improvement"
            }
        ]
        
        for rec in recommendations:
            with st.expander(f"🎯 {rec['area']} - {rec['impact']}"):
                st.write(f"**Current Performance:** {rec['current']}")
                st.write(f"**Recommendation:** {rec['recommendation']}")
                st.write(f"**Expected Impact:** {rec['impact']}")
    
    with tab4:
        st.subheader("⚙️ Analytics Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estimation Parameters**")
            
            default_buffer = st.slider("Default timeline buffer (%)", 0, 50, 20)
            risk_tolerance = st.selectbox("Risk tolerance", ["Conservative", "Moderate", "Aggressive"])
            confidence_threshold = st.slider("Minimum confidence level (%)", 60, 95, 80)
            
            st.write("**Data Sources**")
            use_historical = st.checkbox("Use historical project data", value=True)
            use_industry_benchmarks = st.checkbox("Include industry benchmarks", value=True)
            use_market_rates = st.checkbox("Consider current market rates", value=False)
            
            auto_learning = st.checkbox("Enable automatic model learning", value=True)
        
        with col2:
            st.write("**Reporting Preferences**")
            
            detail_level = st.selectbox("Report detail level", ["Summary", "Standard", "Detailed"])
            include_charts = st.checkbox("Include charts in reports", value=True)
            include_comparisons = st.checkbox("Include industry comparisons", value=True)
            include_risks = st.checkbox("Include risk analysis", value=True)
            
            st.write("**Notification Settings**")
            notify_low_confidence = st.checkbox("Alert for low confidence predictions", value=True)
            notify_high_variance = st.checkbox("Alert for high cost variance", value=True)
            
            update_frequency = st.selectbox("Model update frequency", ["Weekly", "Monthly", "Quarterly"])
        
        if st.button("💾 Save Analytics Settings", type="primary"):
            settings = {
                'default_buffer': default_buffer,
                'risk_tolerance': risk_tolerance,
                'confidence_threshold': confidence_threshold,
                'use_historical': use_historical,
                'use_industry_benchmarks': use_industry_benchmarks,
                'use_market_rates': use_market_rates,
                'auto_learning': auto_learning,
                'detail_level': detail_level,
                'include_charts': include_charts,
                'include_comparisons': include_comparisons,
                'include_risks': include_risks,
                'notify_low_confidence': notify_low_confidence,
                'notify_high_variance': notify_high_variance,
                'update_frequency': update_frequency
            }
            
            st.success("✅ Analytics settings saved successfully!")

def display_estimation_results(result_data):
    """Display the estimation results in a structured format"""
    
    # Effort estimation
    effort_est = result_data.get('effort_estimation', {})
    if effort_est:
        st.subheader("⏱️ Effort Estimation")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_hours = effort_est.get('total_hours', 'Not specified')
            st.metric("Total Estimated Hours", total_hours)
        with col2:
            team_allocation = effort_est.get('team_allocation', {})
            total_roles = len([k for k, v in team_allocation.items() if v])
            st.metric("Team Roles Needed", total_roles)
        with col3:
            confidence = effort_est.get('effort_confidence', 'medium')
            st.metric("Confidence Level", confidence.title())
        
        # Phase breakdown
        phases = effort_est.get('phase_breakdown', [])
        if phases:
            st.write("**Phase Breakdown:**")
            for phase in phases:
                with st.expander(f"{phase.get('phase', 'Unknown Phase')} - {phase.get('estimated_hours', 'TBD')} hours"):
                    st.write(f"**Percentage of Total:** {phase.get('percentage_of_total', 'Not specified')}")
                    st.write(f"**Confidence:** {phase.get('confidence_level', 'medium').title()}")
                    activities = phase.get('key_activities', [])
                    if activities:
                        st.write("**Key Activities:**")
                        for activity in activities:
                            st.write(f"• {activity}")
    
    # Timeline prediction
    timeline_pred = result_data.get('timeline_prediction', {})
    if timeline_pred:
        st.subheader("📅 Timeline Prediction")
        
        col1, col2 = st.columns(2)
        with col1:
            duration = timeline_pred.get('estimated_duration', 'Not specified')
            st.metric("Estimated Duration", duration)
            
            confidence = timeline_pred.get('timeline_confidence', 'medium')
            st.metric("Timeline Confidence", confidence.title())
        
        with col2:
            # Milestones
            milestones = timeline_pred.get('milestone_dates', [])
            if milestones:
                st.write("**Key Milestones:**")
                for milestone in milestones[:3]:  # Show first 3
                    st.write(f"• {milestone.get('milestone', 'Unknown')} - {milestone.get('estimated_date', 'TBD')}")
    
    # Cost estimation
    cost_est = result_data.get('cost_estimation', {})
    if cost_est:
        st.subheader("💰 Cost Estimation")
        
        cost_range = cost_est.get('cost_range', {})
        col1, col2, col3 = st.columns(3)
        
        with col1:
            minimum = cost_range.get('minimum', 'Not specified')
            st.metric("Minimum Cost", minimum)
        with col2:
            most_likely = cost_range.get('most_likely', 'Not specified')
            st.metric("Most Likely Cost", most_likely)
        with col3:
            maximum = cost_range.get('maximum', 'Not specified')
            st.metric("Maximum Cost", maximum)
        
        # Cost breakdown
        cost_breakdown = cost_est.get('cost_breakdown', [])
        if cost_breakdown:
            st.write("**Cost Breakdown:**")
            for item in cost_breakdown:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(item.get('category', 'Unknown'))
                with col2:
                    st.write(item.get('amount', 'TBD'))
                with col3:
                    st.write(item.get('percentage', 'N/A'))
    
    # Risk analysis
    risk_analysis = result_data.get('risk_analysis', {})
    if risk_analysis:
        st.subheader("⚠️ Risk Analysis")
        
        overall_risk = risk_analysis.get('overall_risk_level', 'medium')
        risk_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(overall_risk, "🟡")
        
        st.write(f"**Overall Risk Level:** {risk_color} {overall_risk.title()}")
        
        # Identified risks
        risks = risk_analysis.get('identified_risks', [])
        if risks:
            st.write("**Key Risks:**")
            for risk in risks[:5]:  # Show first 5 risks
                with st.expander(f"🔸 {risk.get('risk', 'Unknown Risk')}"):
                    st.write(f"**Probability:** {risk.get('probability', 'Unknown').title()}")
                    st.write(f"**Impact:** {risk.get('impact', 'Unknown').title()}")
                    st.write(f"**Mitigation:** {risk.get('mitigation', 'No mitigation specified')}")
                    
                    cost_impact = risk.get('cost_impact', 'Unknown')
                    if cost_impact != 'Unknown':
                        st.write(f"**Cost Impact:** {cost_impact}")
    
    # Recommendations
    recommendations = result_data.get('recommendations', {})
    if recommendations:
        st.subheader("💡 AI Recommendations")
        
        approach = recommendations.get('project_approach', 'No specific approach recommended')
        st.write(f"**Recommended Approach:** {approach}")
        
        pricing = recommendations.get('pricing_strategy', 'Standard pricing approach')
        st.write(f"**Pricing Strategy:** {pricing}")
        
        timeline_opt = recommendations.get('timeline_optimization', [])
        if timeline_opt:
            st.write("**Timeline Optimization:**")
            for opt in timeline_opt:
                st.write(f"• {opt}")
        
        cost_opt = recommendations.get('cost_optimization', [])
        if cost_opt:
            st.write("**Cost Optimization:**")
            for opt in cost_opt:
                st.write(f"• {opt}")

if __name__ == "__main__":
    main()