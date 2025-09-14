"""
Learning Engine - Orchestrates closed-loop learning across all components
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .outcome_tracker import OutcomeTracker
from .brand_memory import BrandMemorySystem
from .feedback_collector import FeedbackCollector
from core.database import DatabaseManager

class LearningEngine:
    """Main orchestrator for closed-loop learning system"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.outcome_tracker = OutcomeTracker(db_manager)
        self.brand_memory = BrandMemorySystem(db_manager)
        self.feedback_collector = FeedbackCollector(db_manager)
        
        # Register feedback callbacks for learning
        self._setup_feedback_callbacks()
    
    def _setup_feedback_callbacks(self):
        """Setup callbacks to trigger learning when feedback is received"""
        
        def on_proposal_feedback(feedback_data: Dict[str, Any]):
            """Handle feedback on proposals"""
            project_id = feedback_data["project_id"]
            score = feedback_data["score"]
            approval = feedback_data["approval"]
            
            # Update outcome tracking
            if approval == "approved":
                self.outcome_tracker.track_proposal_outcome(project_id, won=True)
            elif approval == "rejected":
                self.outcome_tracker.track_proposal_outcome(project_id, won=False, 
                                                          feedback=feedback_data["feedback"])
        
        def on_content_feedback(feedback_data: Dict[str, Any]):
            """Handle feedback on content creation"""
            # This could trigger brand memory updates
            pass
        
        self.feedback_collector.register_feedback_callback("proposal", on_proposal_feedback)
        self.feedback_collector.register_feedback_callback("content", on_content_feedback)
        self.feedback_collector.register_feedback_callback("creative_brief", on_content_feedback)
    
    def start_project_learning(self, project_id: str, client_id: str, 
                             initial_data: Dict[str, Any]) -> Dict[str, str]:
        """Initialize learning for a new project"""
        
        # Create initial tracking entries
        outcome_id = None
        if "proposal_value" in initial_data:
            outcome_id = self.outcome_tracker.track_proposal_submission(
                project_id, initial_data["proposal_value"]
            )
        
        # Record initial brand interaction
        brand_interaction_id = None
        if "content" in initial_data:
            brand_interaction_id = self.brand_memory.record_interaction(
                client_id, project_id, "project_start", initial_data
            )
        
        return {
            "outcome_id": outcome_id,
            "brand_interaction_id": brand_interaction_id,
            "status": "learning_initialized"
        }
    
    def create_feedback_checkpoint(self, project_id: str, checkpoint_type: str,
                                 agent_output: Dict[str, Any]) -> str:
        """Create a checkpoint for human feedback"""
        return self.feedback_collector.create_checkpoint(
            project_id, checkpoint_type, agent_output
        )
    
    def get_learning_insights(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive learning insights"""
        
        # Overall outcome insights
        outcome_insights = self.outcome_tracker.get_learning_insights()
        
        # Feedback insights
        feedback_analytics = self.feedback_collector.get_feedback_analytics()
        feedback_recommendations = self.feedback_collector.get_learning_recommendations()
        
        # Brand-specific insights
        brand_insights = {}
        if client_id:
            brand_profile = self.brand_memory.get_brand_profile(client_id)
            if brand_profile:
                brand_insights = {
                    "brand_profile": brand_profile,
                    "recommendations": self.brand_memory.get_recommendations(client_id, "general")
                }
        
        # Combine insights
        combined_insights = {
            "outcome_performance": outcome_insights,
            "feedback_quality": feedback_analytics,
            "recommendations": {
                "outcome_based": outcome_insights.get("improvement_areas", []),
                "feedback_based": feedback_recommendations,
                "brand_based": brand_insights.get("recommendations", {}).get("recommendations", [])
            },
            "learning_maturity": self._calculate_learning_maturity(),
            "next_actions": self._generate_next_actions(outcome_insights, feedback_analytics)
        }
        
        if brand_insights:
            combined_insights["brand_intelligence"] = brand_insights
        
        return combined_insights
    
    def _calculate_learning_maturity(self) -> Dict[str, Any]:
        """Calculate how mature the learning system is"""
        
        # Get data counts using raw SQL
        try:
            with self.db_manager.engine.connect() as conn:
                from sqlalchemy import text
                
                # Count project outcomes
                result = conn.execute(text("SELECT COUNT(*) FROM project_outcomes"))
                outcome_count = result.scalar() or 0
                
                # Count brand interactions
                result = conn.execute(text("SELECT COUNT(*) FROM brand_interactions"))
                interaction_count = result.scalar() or 0
                
                # Count completed feedback
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM feedback_checkpoints 
                    WHERE feedback_given_at IS NOT NULL
                """))
                feedback_count = result.scalar() or 0
                
        except Exception as e:
            print(f"Error calculating learning maturity: {e}")
            outcome_count = interaction_count = feedback_count = 0
        
        # Calculate maturity scores (0-1)
        outcome_maturity = min(1.0, outcome_count / 50)  # Mature at 50 outcomes
        brand_maturity = min(1.0, interaction_count / 100)  # Mature at 100 interactions
        feedback_maturity = min(1.0, feedback_count / 30)  # Mature at 30 feedback sessions
        
        overall_maturity = (outcome_maturity + brand_maturity + feedback_maturity) / 3
        
        maturity_level = "nascent"
        if overall_maturity > 0.7:
            maturity_level = "mature"
        elif overall_maturity > 0.4:
            maturity_level = "developing"
        elif overall_maturity > 0.1:
            maturity_level = "emerging"
        
        return {
            "overall_score": overall_maturity,
            "level": maturity_level,
            "component_scores": {
                "outcome_tracking": outcome_maturity,
                "brand_learning": brand_maturity,
                "feedback_processing": feedback_maturity
            },
            "data_points": {
                "outcomes": outcome_count,
                "brand_interactions": interaction_count,
                "feedback_sessions": feedback_count
            }
        }
    
    def _generate_next_actions(self, outcome_insights: Dict[str, Any], 
                              feedback_analytics: Dict[str, Any]) -> List[str]:
        """Generate prioritized next actions for improvement"""
        actions = []
        
        # Based on outcome performance
        win_rate = outcome_insights.get("proposal_performance", {}).get("win_rate", 0)
        if win_rate < 0.3:
            actions.append("URGENT: Improve proposal quality - win rate is critically low")
        elif win_rate < 0.5:
            actions.append("Focus on proposal improvement strategies")
        
        # Based on estimation accuracy
        estimation = outcome_insights.get("estimation_performance", {})
        if estimation.get("hour_accuracy", 0) < 0.6:
            actions.append("Calibrate hour estimation algorithms")
        
        if estimation.get("avg_delay_days", 0) > 5:
            actions.append("Improve project timeline management")
        
        # Based on feedback quality
        avg_score = feedback_analytics.get("average_score", 0)
        if avg_score < 5.0:
            actions.append("URGENT: Overall output quality requires immediate attention")
        elif avg_score < 7.0:
            actions.append("Focus on improving output quality")
        
        approval_rate = feedback_analytics.get("approval_rate", 0)
        if approval_rate < 0.6:
            actions.append("Review and update quality standards")
        
        # Add learning system development actions
        maturity = self._calculate_learning_maturity()
        if maturity["overall_score"] < 0.3:
            actions.append("Increase data collection for better learning insights")
        
        return actions[:5]  # Return top 5 priorities
    
    def get_agent_performance_suggestions(self, agent_name: str) -> List[str]:
        """Get performance improvement suggestions for a specific agent"""
        suggestions = []
        
        # Get feedback specific to this agent's outputs
        feedback_analytics = self.feedback_collector.get_feedback_analytics()
        feedback_by_type = feedback_analytics.get("feedback_by_type", {})
        
        # Map agent names to checkpoint types
        agent_checkpoint_map = {
            "proposal_generator": "proposal",
            "creative_brief_parser": "creative_brief",
            "content_planner": "content",
            "quality_assurance": "qa",
            "deliverables_packager": "delivery"
        }
        
        checkpoint_type = agent_checkpoint_map.get(agent_name)
        if checkpoint_type and checkpoint_type in feedback_by_type:
            data = feedback_by_type[checkpoint_type]
            
            if data["average_score"] < 6.0:
                suggestions.append(f"Improve {agent_name} output quality (current score: {data['average_score']:.1f})")
            
            if data["approval_rate"] < 0.7:
                suggestions.append(f"Increase {agent_name} approval rate (current: {data['approval_rate']:.1%})")
        
        # Get overall system recommendations that might apply
        general_recommendations = self.feedback_collector.get_learning_recommendations()
        for rec in general_recommendations:
            if agent_name.replace("_", " ") in rec.lower():
                suggestions.append(rec)
        
        if not suggestions:
            suggestions.append(f"No specific issues identified for {agent_name}")
        
        return suggestions
    
    async def run_learning_analysis(self) -> Dict[str, Any]:
        """Run comprehensive learning analysis asynchronously"""
        
        try:
            # Run analysis tasks concurrently
            outcome_insights = self.outcome_tracker.get_learning_insights()
            feedback_analytics = self.feedback_collector.get_feedback_analytics()
            
            # Calculate improvement opportunities
            improvements = []
            
            # Proposal improvements
            win_rate = outcome_insights.get("proposal_performance", {}).get("win_rate", 0)
            if win_rate < 0.5:
                improvements.append({
                    "area": "Proposal Quality",
                    "current_performance": f"{win_rate:.1%} win rate",
                    "target": "70% win rate",
                    "priority": "high" if win_rate < 0.3 else "medium"
                })
            
            # Estimation improvements
            estimation = outcome_insights.get("estimation_performance", {})
            hour_accuracy = estimation.get("hour_accuracy", 0)
            if hour_accuracy < 0.8:
                improvements.append({
                    "area": "Time Estimation",
                    "current_performance": f"{hour_accuracy:.1%} accuracy",
                    "target": "90% accuracy",
                    "priority": "medium"
                })
            
            # Quality improvements
            avg_score = feedback_analytics.get("average_score", 0)
            if avg_score < 8.0:
                improvements.append({
                    "area": "Output Quality",
                    "current_performance": f"{avg_score:.1f}/10 average score",
                    "target": "8.5/10 average score",
                    "priority": "high" if avg_score < 6.0 else "medium"
                })
            
            return {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "learning_insights": self.get_learning_insights(),
                "improvement_opportunities": improvements,
                "system_health": {
                    "learning_maturity": self._calculate_learning_maturity(),
                    "data_quality": "good" if len(improvements) < 3 else "needs_attention"
                }
            }
            
        except Exception as e:
            return {
                "error": f"Learning analysis failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }