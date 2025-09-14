"""
Feedback Collector - Human-in-the-loop feedback collection system
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from sqlalchemy import text
from core.database import DatabaseManager

class FeedbackCollector:
    """Collects and processes human feedback at key workflow checkpoints"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._ensure_tables()
        self.feedback_callbacks: Dict[str, List[Callable]] = {}
    
    def _ensure_tables(self):
        """Create feedback tables if they don't exist"""
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS feedback_checkpoints (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        checkpoint_type TEXT NOT NULL,
                        agent_output TEXT NOT NULL,
                        feedback_score REAL,
                        feedback_text TEXT,
                        improvement_suggestions TEXT,
                        approved TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        feedback_given_at TIMESTAMP,
                        user_id TEXT
                    )
                """))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not create feedback tables: {e}")
    
    def create_checkpoint(self, project_id: str, checkpoint_type: str, 
                         agent_output: Dict[str, Any]) -> str:
        """Create a feedback checkpoint for human review"""
        checkpoint_id = str(uuid.uuid4())
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO feedback_checkpoints 
                    (id, project_id, checkpoint_type, agent_output, created_at)
                    VALUES (:id, :project_id, :checkpoint_type, :agent_output, :created_at)
                """), {
                    'id': checkpoint_id,
                    'project_id': project_id,
                    'checkpoint_type': checkpoint_type,
                    'agent_output': json.dumps(agent_output),
                    'created_at': datetime.utcnow()
                })
                conn.commit()
                return checkpoint_id
        except Exception as e:
            print(f"Error creating checkpoint: {e}")
            return ""
    
    def submit_feedback(self, checkpoint_id: str, score: float, feedback_text: str,
                       improvements: List[str], approval_status: str,
                       user_id: Optional[str] = None) -> bool:
        """Submit human feedback for a checkpoint"""
        try:
            with self.db_manager.engine.connect() as conn:
                # Check if checkpoint exists
                result = conn.execute(text("""
                    SELECT id, project_id, checkpoint_type FROM feedback_checkpoints 
                    WHERE id = :checkpoint_id
                """), {'checkpoint_id': checkpoint_id})
                
                checkpoint_data = result.fetchone()
                if not checkpoint_data:
                    return False
                
                # Update checkpoint with feedback
                conn.execute(text("""
                    UPDATE feedback_checkpoints 
                    SET feedback_score = :score,
                        feedback_text = :feedback_text,
                        improvement_suggestions = :improvements,
                        approved = :approval_status,
                        feedback_given_at = :feedback_given_at,
                        user_id = :user_id
                    WHERE id = :checkpoint_id
                """), {
                    'score': score,
                    'feedback_text': feedback_text,
                    'improvements': json.dumps(improvements),
                    'approval_status': approval_status,
                    'feedback_given_at': datetime.utcnow(),
                    'user_id': user_id,
                    'checkpoint_id': checkpoint_id
                })
                
                conn.commit()
                
                # Trigger feedback callbacks
                self._trigger_callbacks(checkpoint_data.checkpoint_type, {
                    "checkpoint_id": checkpoint_id,
                    "project_id": checkpoint_data.project_id,
                    "score": score,
                    "feedback": feedback_text,
                    "improvements": improvements,
                    "approval": approval_status
                })
                
                return True
        except Exception as e:
            print(f"Error submitting feedback: {e}")
            return False
    
    def register_feedback_callback(self, checkpoint_type: str, callback: Callable):
        """Register a callback to be triggered when feedback is received"""
        if checkpoint_type not in self.feedback_callbacks:
            self.feedback_callbacks[checkpoint_type] = []
        self.feedback_callbacks[checkpoint_type].append(callback)
    
    def _trigger_callbacks(self, checkpoint_type: str, feedback_data: Dict[str, Any]):
        """Trigger registered callbacks for feedback"""
        callbacks = self.feedback_callbacks.get(checkpoint_type, [])
        for callback in callbacks:
            try:
                callback(feedback_data)
            except Exception as e:
                print(f"Error in feedback callback: {e}")
    
    def get_pending_checkpoints(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get checkpoints waiting for feedback"""
        try:
            with self.db_manager.engine.connect() as conn:
                if user_id:
                    result = conn.execute(text("""
                        SELECT * FROM feedback_checkpoints 
                        WHERE feedback_given_at IS NULL AND user_id = :user_id
                        ORDER BY created_at DESC
                    """), {'user_id': user_id})
                else:
                    result = conn.execute(text("""
                        SELECT * FROM feedback_checkpoints 
                        WHERE feedback_given_at IS NULL
                        ORDER BY created_at DESC
                    """))
                
                checkpoints = []
                for row in result:
                    try:
                        agent_output = json.loads(row.agent_output) if row.agent_output else {}
                    except:
                        agent_output = {}
                    
                    checkpoints.append({
                        "id": row.id,
                        "project_id": row.project_id,
                        "checkpoint_type": row.checkpoint_type,
                        "agent_output": agent_output,
                        "created_at": row.created_at.isoformat() if row.created_at else None
                    })
                
                return checkpoints
        except Exception as e:
            print(f"Error getting pending checkpoints: {e}")
            return []
    
    def get_feedback_analytics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get analytics on feedback patterns"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM feedback_checkpoints 
                    WHERE feedback_given_at >= :cutoff_date 
                    AND feedback_score IS NOT NULL
                """), {'cutoff_date': cutoff_date})
                
                feedbacks = list(result)
                
                if not feedbacks:
                    return {"average_score": 0, "total_feedback": 0, "approval_rate": 0}
                
                scores = [f.feedback_score for f in feedbacks if f.feedback_score]
                approvals = [f for f in feedbacks if f.approved == "approved"]
                
                # Analyze improvement suggestions
                all_improvements = []
                for feedback in feedbacks:
                    if feedback.improvement_suggestions:
                        try:
                            improvements = json.loads(feedback.improvement_suggestions)
                            all_improvements.extend(improvements)
                        except:
                            continue
                
                # Count common improvement themes
                improvement_themes = {}
                for improvement in all_improvements:
                    # Simple keyword extraction (could be enhanced with NLP)
                    keywords = improvement.lower().split()
                    for keyword in keywords:
                        if len(keyword) > 3:  # Filter short words
                            improvement_themes[keyword] = improvement_themes.get(keyword, 0) + 1
                
                # Get top themes
                top_themes = sorted(improvement_themes.items(), key=lambda x: x[1], reverse=True)[:5]
                
                return {
                    "average_score": sum(scores) / len(scores) if scores else 0,
                    "total_feedback": len(feedbacks),
                    "approval_rate": len(approvals) / len(feedbacks) if feedbacks else 0,
                    "feedback_by_type": self._get_feedback_by_type(feedbacks),
                    "top_improvement_themes": top_themes,
                    "trend_analysis": self._analyze_trends(feedbacks)
                }
        except Exception as e:
            print(f"Error getting feedback analytics: {e}")
            return {"average_score": 0, "total_feedback": 0, "approval_rate": 0}
    
    def _get_feedback_by_type(self, feedbacks: List) -> Dict[str, Dict]:
        """Analyze feedback patterns by checkpoint type"""
        by_type = {}
        
        for feedback in feedbacks:
            checkpoint_type = feedback.checkpoint_type
            if checkpoint_type not in by_type:
                by_type[checkpoint_type] = {
                    "count": 0,
                    "scores": [],
                    "approvals": 0
                }
            
            by_type[checkpoint_type]["count"] += 1
            if feedback.feedback_score:
                by_type[checkpoint_type]["scores"].append(feedback.feedback_score)
            if feedback.approved == "approved":
                by_type[checkpoint_type]["approvals"] += 1
        
        # Calculate averages
        for checkpoint_type, data in by_type.items():
            if data["scores"]:
                data["average_score"] = sum(data["scores"]) / len(data["scores"])
            else:
                data["average_score"] = 0
            
            data["approval_rate"] = data["approvals"] / data["count"] if data["count"] > 0 else 0
        
        return by_type
    
    def _analyze_trends(self, feedbacks: List) -> Dict[str, Any]:
        """Analyze feedback trends over time"""
        if len(feedbacks) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by date
        sorted_feedbacks = sorted(feedbacks, key=lambda f: f.feedback_given_at or f.created_at)
        
        # Calculate trend in scores
        scores = [f.feedback_score for f in sorted_feedbacks if f.feedback_score]
        if len(scores) < 2:
            return {"trend": "insufficient_score_data"}
        
        # Simple linear trend calculation
        n = len(scores)
        x_values = list(range(n))
        
        # Calculate linear regression slope
        x_mean = sum(x_values) / n
        y_mean = sum(scores) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, scores))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        trend_direction = "improving" if slope > 0.1 else "declining" if slope < -0.1 else "stable"
        
        return {
            "trend": trend_direction,
            "slope": slope,
            "recent_average": sum(scores[-5:]) / min(5, len(scores)),
            "overall_average": y_mean
        }
    
    def get_checkpoint_details(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific checkpoint"""
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM feedback_checkpoints WHERE id = :checkpoint_id
                """), {'checkpoint_id': checkpoint_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                checkpoint = {
                    'id': row.id,
                    'project_id': row.project_id,
                    'checkpoint_type': row.checkpoint_type,
                    'feedback_score': row.feedback_score,
                    'feedback_text': row.feedback_text,
                    'approved': row.approved,
                    'created_at': row.created_at,
                    'feedback_given_at': row.feedback_given_at,
                    'user_id': row.user_id
                }
                
                # Parse JSON fields
                if row.agent_output:
                    try:
                        checkpoint['agent_output'] = json.loads(row.agent_output)
                    except:
                        checkpoint['agent_output'] = {}
                
                if row.improvement_suggestions:
                    try:
                        checkpoint['improvement_suggestions'] = json.loads(row.improvement_suggestions)
                    except:
                        checkpoint['improvement_suggestions'] = []
                
                return checkpoint
                
        except Exception as e:
            print(f"Error getting checkpoint details: {e}")
            return None
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a feedback checkpoint"""
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    DELETE FROM feedback_checkpoints WHERE id = :checkpoint_id
                """), {'checkpoint_id': checkpoint_id})
                conn.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error deleting checkpoint: {e}")
            return False
    
    def get_project_feedback_summary(self, project_id: str) -> Dict[str, Any]:
        """Get feedback summary for a specific project"""
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM feedback_checkpoints 
                    WHERE project_id = :project_id
                    ORDER BY created_at DESC
                """), {'project_id': project_id})
                
                feedbacks = list(result)
                
                if not feedbacks:
                    return {"total_checkpoints": 0, "pending_feedback": 0}
                
                pending = sum(1 for f in feedbacks if f.feedback_given_at is None)
                completed = len(feedbacks) - pending
                
                scores = [f.feedback_score for f in feedbacks if f.feedback_score is not None]
                approvals = [f for f in feedbacks if f.approved == "approved"]
                
                summary = {
                    "total_checkpoints": len(feedbacks),
                    "pending_feedback": pending,
                    "completed_feedback": completed,
                    "average_score": sum(scores) / len(scores) if scores else 0,
                    "approval_rate": len(approvals) / completed if completed > 0 else 0
                }
                
                # Group by checkpoint type
                by_type = {}
                for feedback in feedbacks:
                    checkpoint_type = feedback.checkpoint_type
                    if checkpoint_type not in by_type:
                        by_type[checkpoint_type] = 0
                    by_type[checkpoint_type] += 1
                
                summary["checkpoints_by_type"] = by_type
                
                return summary
                
        except Exception as e:
            print(f"Error getting project feedback summary: {e}")
            return {"total_checkpoints": 0, "pending_feedback": 0}
    
    def get_learning_recommendations(self) -> List[str]:
        """Get AI-generated recommendations based on feedback patterns"""
        try:
            analytics = self.get_feedback_analytics(days_back=60)
            recommendations = []
            
            avg_score = analytics.get("average_score", 0)
            approval_rate = analytics.get("approval_rate", 0)
            top_themes = analytics.get("top_improvement_themes", [])
            
            # Score-based recommendations
            if avg_score < 5.0:
                recommendations.append("CRITICAL: Overall output quality requires immediate attention")
            elif avg_score < 7.0:
                recommendations.append("Focus on improving overall output quality standards")
            elif avg_score > 8.5:
                recommendations.append("Excellent quality maintained - consider optimizing efficiency")
            
            # Approval rate recommendations  
            if approval_rate < 0.4:
                recommendations.append("URGENT: Review and overhaul quality assurance processes")
            elif approval_rate < 0.7:
                recommendations.append("Implement stricter pre-delivery quality checks")
            elif approval_rate > 0.9:
                recommendations.append("High approval rate achieved - focus on speed optimization")
            
            # Theme-based recommendations
            if top_themes:
                for theme, count in top_themes[:3]:
                    if theme in ['clarity', 'clear', 'clearer']:
                        recommendations.append("Improve output clarity and communication")
                    elif theme in ['detail', 'detailed', 'specificity']:
                        recommendations.append("Provide more detailed and specific deliverables")
                    elif theme in ['speed', 'faster', 'time', 'timing']:
                        recommendations.append("Focus on delivery speed optimization")
                    elif theme in ['format', 'formatting', 'structure']:
                        recommendations.append("Standardize output formatting and structure")
            
            # Trend-based recommendations
            trend_data = analytics.get("trend_analysis", {})
            trend = trend_data.get("trend", "stable")
            if trend == "declining":
                recommendations.append("Quality trend is declining - implement immediate improvements")
            elif trend == "improving":
                recommendations.append("Positive trend detected - maintain current improvement trajectory")
            
            # Default if no specific recommendations
            if not recommendations:
                recommendations.append("Continue monitoring feedback patterns for optimization opportunities")
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            print(f"Error generating learning recommendations: {e}")
            return ["Unable to generate recommendations due to data access issues"]