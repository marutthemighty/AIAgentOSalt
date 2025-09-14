"""
Brand Memory System - Persistent learning of client preferences and brand patterns
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import text
from core.database import DatabaseManager

class BrandMemorySystem:
    """Learns and remembers brand preferences and patterns for each client"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create brand memory tables if they don't exist"""
        try:
            with self.db_manager.engine.connect() as conn:
                # Create brand_profiles table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS brand_profiles (
                        id TEXT PRIMARY KEY,
                        client_id TEXT NOT NULL UNIQUE,
                        client_name TEXT NOT NULL,
                        brand_voice TEXT,
                        visual_preferences TEXT,
                        content_guidelines TEXT,
                        approval_patterns TEXT,
                        interaction_count REAL DEFAULT 0,
                        confidence_score REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create brand_interactions table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS brand_interactions (
                        id TEXT PRIMARY KEY,
                        client_id TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        content_type TEXT NOT NULL,
                        content_data TEXT NOT NULL,
                        feedback TEXT,
                        approval_status TEXT,
                        tone_features TEXT,
                        visual_features TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not create brand memory tables: {e}")
    
    def record_interaction(self, client_id: str, project_id: str, content_type: str,
                          content_data: Dict[str, Any], feedback: Optional[str] = None,
                          approval_status: Optional[str] = None) -> str:
        """Record a brand interaction for learning"""
        
        # Extract features from content
        tone_features = self._extract_tone_features(content_data)
        visual_features = self._extract_visual_features(content_data)
        
        interaction_id = str(uuid.uuid4())
        
        try:
            with self.db_manager.engine.connect() as conn:
                # Insert brand interaction
                conn.execute(text("""
                    INSERT INTO brand_interactions 
                    (id, client_id, project_id, content_type, content_data, feedback, 
                     approval_status, tone_features, visual_features, created_at)
                    VALUES (:id, :client_id, :project_id, :content_type, :content_data, 
                            :feedback, :approval_status, :tone_features, :visual_features, :created_at)
                """), {
                    'id': interaction_id,
                    'client_id': client_id,
                    'project_id': project_id,
                    'content_type': content_type,
                    'content_data': json.dumps(content_data),
                    'feedback': feedback,
                    'approval_status': approval_status,
                    'tone_features': json.dumps(tone_features),
                    'visual_features': json.dumps(visual_features),
                    'created_at': datetime.utcnow()
                })
                conn.commit()
                
                # Update brand profile
                self._update_brand_profile(client_id)
                
                return interaction_id
                
        except Exception as e:
            print(f"Error recording brand interaction: {e}")
            return ""
    
    def _extract_tone_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tone and voice characteristics from content"""
        features = {
            "formality": 0.5,  # 0 = casual, 1 = formal
            "enthusiasm": 0.5,  # 0 = reserved, 1 = enthusiastic
            "technicality": 0.5,  # 0 = simple, 1 = technical
            "urgency": 0.5,  # 0 = relaxed, 1 = urgent
        }
        
        # Simple heuristic analysis (could be enhanced with NLP)
        text_content = str(content_data.get('content', ''))
        
        # Formality indicators
        formal_words = ['therefore', 'furthermore', 'consequently', 'professional', 'expertise']
        casual_words = ['awesome', 'cool', 'hey', 'totally', 'definitely']
        
        formal_count = sum(1 for word in formal_words if word in text_content.lower())
        casual_count = sum(1 for word in casual_words if word in text_content.lower())
        
        if formal_count + casual_count > 0:
            features["formality"] = formal_count / (formal_count + casual_count)
        
        # Enthusiasm indicators
        enthusiasm_words = ['excited', 'amazing', 'fantastic', 'excellent', 'outstanding']
        features["enthusiasm"] = min(1.0, sum(1 for word in enthusiasm_words if word in text_content.lower()) / 10)
        
        return features
    
    def _extract_visual_features(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract visual preferences from content"""
        features = {
            "color_preferences": [],
            "style_keywords": [],
            "layout_preferences": {}
        }
        
        # Extract colors mentioned
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'black', 'white', 'gray']
        text_content = str(content_data.get('content', ''))
        
        for color in colors:
            if color in text_content.lower():
                features["color_preferences"].append(color)
        
        # Extract style keywords
        style_words = ['modern', 'classic', 'minimalist', 'bold', 'elegant', 'playful', 'professional']
        for style in style_words:
            if style in text_content.lower():
                features["style_keywords"].append(style)
        
        return features
    
    def _update_brand_profile(self, client_id: str):
        """Update brand profile based on accumulated interactions"""
        try:
            with self.db_manager.engine.connect() as conn:
                # Check if profile exists
                result = conn.execute(text("""
                    SELECT id FROM brand_profiles WHERE client_id = :client_id
                """), {'client_id': client_id})
                
                profile_exists = result.fetchone() is not None
                
                if not profile_exists:
                    # Create new profile
                    profile_id = str(uuid.uuid4())
                    conn.execute(text("""
                        INSERT INTO brand_profiles (id, client_id, client_name, created_at)
                        VALUES (:id, :client_id, :client_name, :created_at)
                    """), {
                        'id': profile_id,
                        'client_id': client_id,
                        'client_name': f"Client_{client_id[:8]}",
                        'created_at': datetime.utcnow()
                    })
                
                # Get all interactions for this client
                interactions = conn.execute(text("""
                    SELECT tone_features, visual_features, approval_status
                    FROM brand_interactions 
                    WHERE client_id = :client_id
                """), {'client_id': client_id}).fetchall()
                
                if not interactions:
                    conn.commit()
                    return
                
                # Aggregate tone features
                tone_data = []
                for interaction in interactions:
                    if interaction.tone_features:
                        try:
                            tone_features = json.loads(interaction.tone_features)
                            tone_data.append(tone_features)
                        except:
                            continue
                
                brand_voice_data = {}
                if tone_data:
                    # Average tone characteristics
                    avg_tone = {}
                    for key in tone_data[0].keys():
                        avg_tone[key] = sum(d.get(key, 0) for d in tone_data) / len(tone_data)
                    
                    brand_voice_data = {
                        "tone_profile": avg_tone,
                        "consistency_score": self._calculate_consistency(tone_data)
                    }
                
                # Aggregate visual features
                visual_data = []
                for interaction in interactions:
                    if interaction.visual_features:
                        try:
                            visual_features = json.loads(interaction.visual_features)
                            visual_data.append(visual_features)
                        except:
                            continue
                
                visual_preferences_data = {}
                if visual_data:
                    # Combine visual preferences
                    all_colors = []
                    all_styles = []
                    for data in visual_data:
                        all_colors.extend(data.get("color_preferences", []))
                        all_styles.extend(data.get("style_keywords", []))
                    
                    # Count frequency
                    color_counts = {}
                    for color in all_colors:
                        color_counts[color] = color_counts.get(color, 0) + 1
                    
                    style_counts = {}
                    for style in all_styles:
                        style_counts[style] = style_counts.get(style, 0) + 1
                    
                    visual_preferences_data = {
                        "preferred_colors": color_counts,
                        "preferred_styles": style_counts
                    }
                
                # Calculate approval patterns
                approval_data = {}
                approved_count = sum(1 for i in interactions if i.approval_status == "approved")
                total_count = len([i for i in interactions if i.approval_status is not None])
                
                if total_count > 0:
                    approval_data = {
                        "approval_rate": approved_count / total_count,
                        "total_evaluations": total_count
                    }
                
                # Update profile
                interaction_count = len(interactions)
                confidence_score = min(1.0, interaction_count / 10)  # Max confidence at 10 interactions
                
                conn.execute(text("""
                    UPDATE brand_profiles 
                    SET brand_voice = :brand_voice,
                        visual_preferences = :visual_preferences,
                        approval_patterns = :approval_patterns,
                        interaction_count = :interaction_count,
                        confidence_score = :confidence_score,
                        updated_at = :updated_at
                    WHERE client_id = :client_id
                """), {
                    'brand_voice': json.dumps(brand_voice_data),
                    'visual_preferences': json.dumps(visual_preferences_data),
                    'approval_patterns': json.dumps(approval_data),
                    'interaction_count': interaction_count,
                    'confidence_score': confidence_score,
                    'updated_at': datetime.utcnow(),
                    'client_id': client_id
                })
                
                conn.commit()
                
        except Exception as e:
            print(f"Error updating brand profile: {e}")
    
    def _calculate_consistency(self, tone_data: List[Dict[str, float]]) -> float:
        """Calculate consistency score for tone data"""
        if len(tone_data) < 2:
            return 1.0
        
        consistency_scores = []
        for key in tone_data[0].keys():
            values = [d.get(key, 0) for d in tone_data]
            # Calculate standard deviation
            mean_val = sum(values) / len(values)
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            # Convert to consistency score (1 - normalized std_dev)
            consistency_scores.append(max(0, 1 - (std_dev * 2)))  # *2 to normalize
        
        return sum(consistency_scores) / len(consistency_scores)
    
    def get_brand_profile(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get brand profile for a client"""
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM brand_profiles WHERE client_id = :client_id
                """), {'client_id': client_id})
                
                row = result.fetchone()
                if not row:
                    return None
                
                profile = {
                    'id': row.id,
                    'client_id': row.client_id,
                    'client_name': row.client_name,
                    'interaction_count': row.interaction_count,
                    'confidence_score': row.confidence_score,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at
                }
                
                # Parse JSON fields
                if row.brand_voice:
                    try:
                        profile['brand_voice'] = json.loads(row.brand_voice)
                    except:
                        profile['brand_voice'] = {}
                
                if row.visual_preferences:
                    try:
                        profile['visual_preferences'] = json.loads(row.visual_preferences)
                    except:
                        profile['visual_preferences'] = {}
                
                if row.approval_patterns:
                    try:
                        profile['approval_patterns'] = json.loads(row.approval_patterns)
                    except:
                        profile['approval_patterns'] = {}
                
                return profile
                
        except Exception as e:
            print(f"Error getting brand profile: {e}")
            return None
    
    def get_client_interactions(self, client_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent interactions for a client"""
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM brand_interactions 
                    WHERE client_id = :client_id 
                    ORDER BY created_at DESC 
                    LIMIT :limit
                """), {'client_id': client_id, 'limit': limit})
                
                interactions = []
                for row in result:
                    interaction = {
                        'id': row.id,
                        'client_id': row.client_id,
                        'project_id': row.project_id,
                        'content_type': row.content_type,
                        'feedback': row.feedback,
                        'approval_status': row.approval_status,
                        'created_at': row.created_at
                    }
                    
                    # Parse JSON fields
                    if row.content_data:
                        try:
                            interaction['content_data'] = json.loads(row.content_data)
                        except:
                            interaction['content_data'] = {}
                    
                    if row.tone_features:
                        try:
                            interaction['tone_features'] = json.loads(row.tone_features)
                        except:
                            interaction['tone_features'] = {}
                    
                    if row.visual_features:
                        try:
                            interaction['visual_features'] = json.loads(row.visual_features)
                        except:
                            interaction['visual_features'] = {}
                    
                    interactions.append(interaction)
                
                return interactions
                
        except Exception as e:
            print(f"Error getting client interactions: {e}")
            return []
    
    def get_brand_recommendations(self, client_id: str) -> Dict[str, Any]:
        """Get AI recommendations based on brand profile"""
        profile = self.get_brand_profile(client_id)
        if not profile:
            return {"error": "No brand profile found for client"}
        
        recommendations = {
            "confidence_level": profile.get('confidence_score', 0),
            "tone_recommendations": {},
            "visual_recommendations": {},
            "content_guidelines": []
        }
        
        # Tone recommendations
        brand_voice = profile.get('brand_voice', {})
        tone_profile = brand_voice.get('tone_profile', {})
        
        if tone_profile:
            for aspect, score in tone_profile.items():
                if score > 0.7:
                    recommendations["tone_recommendations"][aspect] = f"Maintain high {aspect}"
                elif score < 0.3:
                    recommendations["tone_recommendations"][aspect] = f"Keep low {aspect}"
                else:
                    recommendations["tone_recommendations"][aspect] = f"Moderate {aspect}"
        
        # Visual recommendations
        visual_prefs = profile.get('visual_preferences', {})
        preferred_colors = visual_prefs.get('preferred_colors', {})
        preferred_styles = visual_prefs.get('preferred_styles', {})
        
        if preferred_colors:
            top_colors = sorted(preferred_colors.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations["visual_recommendations"]["colors"] = [color for color, _ in top_colors]
        
        if preferred_styles:
            top_styles = sorted(preferred_styles.items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations["visual_recommendations"]["styles"] = [style for style, _ in top_styles]
        
        # Approval patterns
        approval_patterns = profile.get('approval_patterns', {})
        approval_rate = approval_patterns.get('approval_rate', 0)
        
        if approval_rate > 0.8:
            recommendations["content_guidelines"].append("Current approach is highly successful")
        elif approval_rate < 0.5:
            recommendations["content_guidelines"].append("Consider adjusting content strategy")
        
        return recommendations
    
    def get_recommendations(self, client_id: str, context: str = "general") -> Dict[str, Any]:
        """Get comprehensive recommendations for a specific client and context"""
        try:
            base_recommendations = self.get_brand_recommendations(client_id)
            
            # Add context-specific recommendations
            profile = self.get_brand_profile(client_id)
            if not profile:
                return {
                    "recommendations": ["No brand profile available - start collecting brand interactions"],
                    "confidence": 0.0,
                    "context": context
                }
            
            confidence = profile.get('confidence_score', 0)
            recommendations = base_recommendations.get("content_guidelines", [])
            
            # Add context-specific guidance
            if context == "proposal":
                brand_voice = profile.get('brand_voice', {})
                tone_profile = brand_voice.get('tone_profile', {})
                
                if tone_profile.get('formality', 0.5) > 0.7:
                    recommendations.append("Use formal, professional language in proposals")
                elif tone_profile.get('formality', 0.5) < 0.3:
                    recommendations.append("Maintain casual, approachable tone in proposals")
                
                if tone_profile.get('enthusiasm', 0.5) > 0.7:
                    recommendations.append("Include enthusiastic language and positive energy")
                
            elif context == "content":
                visual_prefs = profile.get('visual_preferences', {})
                preferred_styles = visual_prefs.get('preferred_styles', {})
                
                if preferred_styles:
                    top_style = max(preferred_styles.items(), key=lambda x: x[1])[0]
                    recommendations.append(f"Align content with {top_style} style preferences")
            
            elif context == "creative_brief":
                approval_patterns = profile.get('approval_patterns', {})
                approval_rate = approval_patterns.get('approval_rate', 0)
                
                if approval_rate > 0.8:
                    recommendations.append("Continue with current creative brief approach - high success rate")
                elif approval_rate < 0.5:
                    recommendations.append("Review and adjust creative brief format and content")
            
            return {
                "recommendations": recommendations,
                "confidence": confidence,
                "context": context,
                "profile_maturity": "high" if confidence > 0.7 else "medium" if confidence > 0.3 else "low"
            }
            
        except Exception as e:
            print(f"Error getting brand recommendations: {e}")
            return {
                "recommendations": ["Unable to generate recommendations due to data access issues"],
                "confidence": 0.0,
                "context": context
            }