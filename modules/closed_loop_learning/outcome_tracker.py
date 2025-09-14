"""
Outcome Tracker - Captures real business outcomes for continuous learning
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import text, Table, Column, String, DateTime, Float, Integer, Text, Boolean, MetaData
from core.database import DatabaseManager
    
class OutcomeTracker:
    """Tracks and analyzes project outcomes for continuous learning"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create outcome tracking tables if they don't exist"""
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS project_outcomes (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        proposal_id TEXT,
                        proposal_submitted_at TIMESTAMP,
                        proposal_value REAL,
                        proposal_won BOOLEAN,
                        proposal_feedback TEXT,
                        estimated_hours REAL,
                        actual_hours REAL,
                        estimated_cost REAL,
                        actual_cost REAL,
                        revision_count INTEGER DEFAULT 0,
                        client_satisfaction_score REAL,
                        delivery_delay_days INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        project_metadata TEXT
                    )
                """))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not create outcome tables: {e}")
    
    def track_proposal_submission(self, project_id: str, proposal_value: float, 
                                proposal_id: Optional[str] = None) -> str:
        """Track when a proposal is submitted"""
        outcome_id = str(uuid.uuid4())
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO project_outcomes (id, project_id, proposal_id, proposal_submitted_at, proposal_value)
                    VALUES (:id, :project_id, :proposal_id, :submitted_at, :value)
                """), {
                    'id': outcome_id,
                    'project_id': project_id,
                    'proposal_id': proposal_id,
                    'submitted_at': datetime.utcnow(),
                    'value': proposal_value
                })
                conn.commit()
            return outcome_id
        except Exception as e:
            print(f"Error tracking proposal submission: {e}")
            return outcome_id
    
    def track_proposal_outcome(self, project_id: str, won: bool, feedback: Optional[str] = None):
        """Track proposal win/loss and feedback"""
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE project_outcomes 
                    SET proposal_won = :won, proposal_feedback = :feedback, updated_at = :updated_at
                    WHERE project_id = :project_id
                """), {
                    'won': won,
                    'feedback': feedback,
                    'updated_at': datetime.utcnow(),
                    'project_id': project_id
                })
                conn.commit()
        except Exception as e:
            print(f"Error tracking proposal outcome: {e}")
    
    def track_project_estimates(self, project_id: str, estimated_hours: float, estimated_cost: float):
        """Track initial project estimates"""
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE project_outcomes 
                    SET estimated_hours = :hours, estimated_cost = :cost, updated_at = :updated_at
                    WHERE project_id = :project_id
                """), {
                    'hours': estimated_hours,
                    'cost': estimated_cost,
                    'updated_at': datetime.utcnow(),
                    'project_id': project_id
                })
                conn.commit()
        except Exception as e:
            print(f"Error tracking project estimates: {e}")
    
    def track_project_actuals(self, project_id: str, actual_hours: float, actual_cost: float,
                            revision_count: int = 0, satisfaction_score: Optional[float] = None,
                            delay_days: int = 0):
        """Track actual project metrics"""
        try:
            with self.db_manager.engine.connect() as conn:
                conn.execute(text("""
                    UPDATE project_outcomes 
                    SET actual_hours = :hours, actual_cost = :cost, revision_count = :revisions,
                        client_satisfaction_score = :satisfaction, delivery_delay_days = :delay,
                        updated_at = :updated_at
                    WHERE project_id = :project_id
                """), {
                    'hours': actual_hours,
                    'cost': actual_cost,
                    'revisions': revision_count,
                    'satisfaction': satisfaction_score,
                    'delay': delay_days,
                    'updated_at': datetime.utcnow(),
                    'project_id': project_id
                })
                conn.commit()
        except Exception as e:
            print(f"Error tracking project actuals: {e}")
    
    def get_proposal_win_rate(self, days_back: int = 90) -> float:
        """Calculate proposal win rate over specified period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        try:
            with self.db_manager.engine.connect() as conn:
                total_result = conn.execute(text("""
                    SELECT COUNT(*) as count FROM project_outcomes 
                    WHERE proposal_submitted_at >= :cutoff_date AND proposal_won IS NOT NULL
                """), {'cutoff_date': cutoff_date})
                total_proposals = total_result.fetchone().count
                
                won_result = conn.execute(text("""
                    SELECT COUNT(*) as count FROM project_outcomes 
                    WHERE proposal_submitted_at >= :cutoff_date AND proposal_won = 1
                """), {'cutoff_date': cutoff_date})
                won_proposals = won_result.fetchone().count
                
                return won_proposals / total_proposals if total_proposals > 0 else 0.0
        except Exception as e:
            print(f"Error calculating win rate: {e}")
            return 0.0
    
    def get_estimation_accuracy(self, days_back: int = 90) -> Dict[str, float]:
        """Calculate estimation accuracy metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT estimated_hours, actual_hours, estimated_cost, actual_cost,
                           delivery_delay_days, client_satisfaction_score
                    FROM project_outcomes 
                    WHERE created_at >= :cutoff_date 
                      AND estimated_hours IS NOT NULL 
                      AND actual_hours IS NOT NULL
                """), {'cutoff_date': cutoff_date})
                
                outcomes = result.fetchall()
                
                if not outcomes:
                    return {"hour_accuracy": 0.0, "cost_accuracy": 0.0, "avg_delay_days": 0.0, "avg_satisfaction": 0.0}
                
                hour_errors = []
                cost_errors = []
                delays = []
                satisfactions = []
                
                for outcome in outcomes:
                    if outcome.estimated_hours and outcome.actual_hours:
                        hour_error = abs(outcome.estimated_hours - outcome.actual_hours) / outcome.estimated_hours
                        hour_errors.append(min(hour_error, 1.0))  # Cap at 100% error
                    
                    if outcome.estimated_cost and outcome.actual_cost:
                        cost_error = abs(outcome.estimated_cost - outcome.actual_cost) / outcome.estimated_cost
                        cost_errors.append(min(cost_error, 1.0))
                    
                    delays.append(outcome.delivery_delay_days or 0)
                    satisfactions.append(outcome.client_satisfaction_score or 0)
                
                return {
                    "hour_accuracy": 1.0 - (sum(hour_errors) / len(hour_errors)) if hour_errors else 0.0,
                    "cost_accuracy": 1.0 - (sum(cost_errors) / len(cost_errors)) if cost_errors else 0.0,
                    "avg_delay_days": sum(delays) / len(delays) if delays else 0.0,
                    "avg_satisfaction": sum(satisfactions) / len(satisfactions) if satisfactions else 0.0
                }
        except Exception as e:
            print(f"Error calculating estimation accuracy: {e}")
            return {"hour_accuracy": 0.0, "cost_accuracy": 0.0, "avg_delay_days": 0.0, "avg_satisfaction": 0.0}
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Generate insights for continuous improvement"""
        win_rate = self.get_proposal_win_rate()
        accuracy = self.get_estimation_accuracy()
        
        insights = {
            "proposal_performance": {
                "win_rate": win_rate,
                "recommendation": "Focus on proposal quality" if win_rate < 0.3 else "Maintain current approach"
            },
            "estimation_performance": accuracy,
            "improvement_areas": []
        }
        
        # Generate recommendations
        if accuracy["hour_accuracy"] < 0.7:
            insights["improvement_areas"].append("Hour estimation needs calibration")
        
        if accuracy["avg_delay_days"] > 3:
            insights["improvement_areas"].append("Project timeline management needs attention")
        
        if accuracy["avg_satisfaction"] < 7.0:
            insights["improvement_areas"].append("Client satisfaction requires focus")
        
        return insights