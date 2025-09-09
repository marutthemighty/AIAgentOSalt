from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import re

class SentimentAnalyzer(BaseAgent):
    """
    Agent that uses sentiment classification to detect client satisfaction 
    from emails/Slack and suggests proactive adjustments
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "sentiment_analyzer")
        
        # Sentiment scoring scale
        self.sentiment_scale = {
            'very_positive': {'score': 100, 'range': (80, 100), 'description': 'Highly satisfied and enthusiastic'},
            'positive': {'score': 75, 'range': (60, 79), 'description': 'Satisfied and pleased'},
            'neutral': {'score': 50, 'range': (40, 59), 'description': 'Neither positive nor negative'},
            'negative': {'score': 25, 'range': (20, 39), 'description': 'Dissatisfied or concerned'},
            'very_negative': {'score': 0, 'range': (0, 19), 'description': 'Highly dissatisfied or angry'}
        }
        
        # Communication channels and their characteristics
        self.communication_channels = {
            'email': {'formality': 'high', 'emotion_expression': 'moderate'},
            'slack': {'formality': 'low', 'emotion_expression': 'high'},
            'meeting_notes': {'formality': 'medium', 'emotion_expression': 'low'},
            'chat': {'formality': 'low', 'emotion_expression': 'high'},
            'feedback_form': {'formality': 'medium', 'emotion_expression': 'moderate'}
        }
        
        # Sentiment indicators
        self.positive_indicators = [
            'excellent', 'amazing', 'perfect', 'love', 'great', 'fantastic', 'wonderful',
            'impressed', 'exceeded expectations', 'thrilled', 'delighted', 'outstanding'
        ]
        
        self.negative_indicators = [
            'disappointed', 'frustrated', 'concerned', 'worried', 'unhappy', 'dissatisfied',
            'poor', 'terrible', 'awful', 'unacceptable', 'failed', 'missed deadline'
        ]
        
        # Urgency keywords
        self.urgency_indicators = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency', 'rush',
            'deadline', 'late', 'overdue', 'behind schedule'
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment from client communications
        
        Args:
            input_data: Dictionary containing 'communications', 'client_id', 'context'
            
        Returns:
            Dictionary with sentiment analysis and recommended actions
        """
        required_fields = ['communications']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for sentiment analysis")
        
        return await self._safe_execute(self._analyze_client_sentiment, input_data)
    
    async def _analyze_client_sentiment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to analyze client sentiment"""
        
        communications = input_data['communications']
        client_id = input_data.get('client_id', 'unknown')
        context = input_data.get('context', {})
        
        # Process each communication
        analyzed_communications = []
        
        for comm in communications:
            comm_analysis = await self._analyze_single_communication(comm, client_id, context)
            analyzed_communications.append(comm_analysis)
        
        # Generate comprehensive sentiment report using AI
        ai_prompt = f"""
        Analyze the following client communications for sentiment patterns and provide actionable insights:

        Client ID: {client_id}
        Communication Context: {json.dumps(context, indent=2)}
        
        Individual Communication Analysis:
        {json.dumps(analyzed_communications, indent=2)}

        Please provide a JSON response with the following sentiment analysis structure:
        {{
            "overall_sentiment": {{
                "sentiment_score": "Overall score from 0-100",
                "sentiment_label": "very_positive/positive/neutral/negative/very_negative",
                "confidence_level": "high/medium/low",
                "trend": "improving/stable/declining",
                "summary": "Brief summary of overall client sentiment"
            }},
            "communication_breakdown": [
                {{
                    "communication_id": "Communication identifier",
                    "channel": "email/slack/meeting/chat",
                    "sentiment_score": "Score from 0-100",
                    "sentiment_label": "Sentiment classification",
                    "key_emotions": ["Primary emotions detected"],
                    "urgency_level": "high/medium/low",
                    "concerns_identified": ["Specific concerns mentioned"],
                    "positive_feedback": ["Positive points mentioned"],
                    "action_items_mentioned": ["Any actions requested by client"]
                }}
            ],
            "sentiment_patterns": {{
                "recurring_themes": ["Common themes across communications"],
                "emotional_triggers": ["What causes positive/negative reactions"],
                "communication_preferences": ["Client's preferred communication style"],
                "satisfaction_drivers": ["What makes this client most satisfied"],
                "concern_areas": ["Areas that consistently cause concern"]
            }},
            "risk_assessment": {{
                "churn_risk": "high/medium/low",
                "escalation_risk": "high/medium/low",
                "satisfaction_trajectory": "improving/stable/declining",
                "early_warning_signals": ["Signs that indicate potential issues"],
                "relationship_health": "excellent/good/concerning/poor"
            }},
            "proactive_recommendations": {{
                "immediate_actions": [
                    {{
                        "action": "Specific action to take",
                        "priority": "high/medium/low",
                        "timeline": "When to take this action",
                        "responsible_party": "Who should handle this",
                        "expected_outcome": "What this should achieve"
                    }}
                ],
                "communication_adjustments": [
                    {{
                        "adjustment": "How to modify communication approach",
                        "rationale": "Why this adjustment is needed",
                        "implementation": "How to implement this change"
                    }}
                ],
                "relationship_building": [
                    {{
                        "strategy": "Relationship building strategy",
                        "approach": "How to implement this strategy",
                        "success_metrics": "How to measure success"
                    }}
                ]
            }},
            "sentiment_monitoring": {{
                "key_metrics_to_track": ["Important sentiment metrics"],
                "monitoring_frequency": "How often to check sentiment",
                "alert_thresholds": {{
                    "negative_sentiment_threshold": "Score that triggers alert",
                    "rapid_decline_threshold": "Change rate that triggers alert",
                    "escalation_keywords": ["Words that trigger immediate attention"]
                }},
                "reporting_cadence": "How often to report sentiment trends"
            }},
            "client_journey_insights": {{
                "current_stage": "Where client is in their journey",
                "satisfaction_evolution": "How satisfaction has changed over time",
                "critical_moments": ["Key moments that affected sentiment"],
                "success_celebrations": ["Achievements to acknowledge"],
                "improvement_opportunities": ["Areas to focus on for better experience"]
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            sentiment_report = json.loads(ai_response)
            
            # Enhance with additional analysis
            sentiment_report['historical_comparison'] = self._compare_with_historical_sentiment(client_id, sentiment_report)
            sentiment_report['predictive_insights'] = self._generate_predictive_insights(analyzed_communications)
            sentiment_report['automated_alerts'] = self._generate_automated_alerts(sentiment_report)
            
            # Add metadata
            sentiment_report['analysis_timestamp'] = datetime.now().isoformat()
            sentiment_report['analyzer_version'] = '1.0.0'
            sentiment_report['communications_analyzed'] = len(communications)
            sentiment_report['client_id'] = client_id
            
            # Learn from sentiment analysis
            self._learn_from_sentiment_analysis(client_id, sentiment_report)
            
            return sentiment_report
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback analysis")
            return self._fallback_sentiment_analysis(analyzed_communications, client_id)
    
    async def _analyze_single_communication(self, communication: Dict[str, Any], client_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of a single communication"""
        
        message = communication.get('message', '')
        channel = communication.get('channel', 'email')
        timestamp = communication.get('timestamp', datetime.now().isoformat())
        
        # Basic sentiment indicators
        sentiment_analysis = {
            'communication_id': communication.get('id', 'unknown'),
            'channel': channel,
            'timestamp': timestamp,
            'message_length': len(message),
            'sentiment_indicators': {}
        }
        
        # Check for positive indicators
        positive_count = sum(1 for indicator in self.positive_indicators if indicator.lower() in message.lower())
        negative_count = sum(1 for indicator in self.negative_indicators if indicator.lower() in message.lower())
        urgency_count = sum(1 for indicator in self.urgency_indicators if indicator.lower() in message.lower())
        
        sentiment_analysis['sentiment_indicators'] = {
            'positive_signals': positive_count,
            'negative_signals': negative_count,
            'urgency_signals': urgency_count
        }
        
        # Calculate basic sentiment score
        base_score = 50  # Neutral baseline
        base_score += positive_count * 10
        base_score -= negative_count * 15
        base_score -= urgency_count * 5  # Urgency slightly negative
        
        # Clamp score between 0 and 100
        sentiment_score = max(0, min(100, base_score))
        sentiment_analysis['preliminary_sentiment_score'] = sentiment_score
        
        # Determine sentiment label
        for label, data in self.sentiment_scale.items():
            if data['range'][0] <= sentiment_score <= data['range'][1]:
                sentiment_analysis['preliminary_sentiment_label'] = label
                break
        
        # Extract specific concerns and praises
        sentiment_analysis['extracted_concerns'] = self._extract_concerns(message)
        sentiment_analysis['extracted_praises'] = self._extract_praises(message)
        
        return sentiment_analysis
    
    def _extract_concerns(self, message: str) -> List[str]:
        """Extract specific concerns from message"""
        
        concern_patterns = [
            r"(?:worried|concerned|disappointed|frustrated) (?:about|with) ([^.!?]*)",
            r"(?:issue|problem|difficulty) (?:with|regarding) ([^.!?]*)",
            r"(?:not happy|dissatisfied) (?:with|about) ([^.!?]*)",
            r"(?:behind schedule|running late|delayed) ([^.!?]*)"
        ]
        
        concerns = []
        for pattern in concern_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            concerns.extend([match.strip() for match in matches if match.strip()])
        
        return concerns[:5]  # Limit to 5 concerns
    
    def _extract_praises(self, message: str) -> List[str]:
        """Extract specific praises from message"""
        
        praise_patterns = [
            r"(?:love|really like|impressed with|happy with) ([^.!?]*)",
            r"(?:excellent|great|amazing|fantastic) ([^.!?]*)",
            r"(?:exceeded expectations|better than expected) ([^.!?]*)",
            r"(?:thrilled|delighted) (?:with|about) ([^.!?]*)"
        ]
        
        praises = []
        for pattern in praise_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            praises.extend([match.strip() for match in matches if match.strip()])
        
        return praises[:5]  # Limit to 5 praises
    
    def _compare_with_historical_sentiment(self, client_id: str, current_report: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current sentiment with historical patterns"""
        
        # Get historical sentiment data from memory
        historical_key = f"sentiment_history_{client_id}"
        historical_data = self.get_memory(historical_key, [])
        
        comparison = {
            'historical_data_points': len(historical_data),
            'trend_analysis': 'stable',
            'significant_changes': []
        }
        
        if historical_data:
            # Get recent sentiment scores
            recent_scores = [entry.get('sentiment_score', 50) for entry in historical_data[-5:]]
            current_score = current_report.get('overall_sentiment', {}).get('sentiment_score', 50)
            
            try:
                current_score_num = float(str(current_score).replace('%', ''))
                recent_avg = sum(float(str(score).replace('%', '')) for score in recent_scores) / len(recent_scores)
                
                # Determine trend
                if current_score_num > recent_avg + 10:
                    comparison['trend_analysis'] = 'improving'
                elif current_score_num < recent_avg - 10:
                    comparison['trend_analysis'] = 'declining'
                else:
                    comparison['trend_analysis'] = 'stable'
                
                comparison['sentiment_change'] = current_score_num - recent_avg
                comparison['average_historical_sentiment'] = recent_avg
                
            except:
                comparison['trend_analysis'] = 'unable_to_calculate'
        
        # Store current sentiment for future comparisons
        current_entry = {
            'timestamp': datetime.now().isoformat(),
            'sentiment_score': current_report.get('overall_sentiment', {}).get('sentiment_score', 50),
            'sentiment_label': current_report.get('overall_sentiment', {}).get('sentiment_label', 'neutral')
        }
        
        historical_data.append(current_entry)
        
        # Keep only last 20 entries
        if len(historical_data) > 20:
            historical_data = historical_data[-20:]
        
        self.update_memory(historical_key, historical_data)
        
        return comparison
    
    def _generate_predictive_insights(self, analyzed_communications: List[Dict]) -> Dict[str, Any]:
        """Generate predictive insights based on communication patterns"""
        
        insights = {
            'satisfaction_prediction': 'stable',
            'risk_indicators': [],
            'positive_momentum': [],
            'recommended_focus_areas': []
        }
        
        if not analyzed_communications:
            return insights
        
        # Analyze communication frequency and sentiment trends
        recent_comms = analyzed_communications[-3:]  # Last 3 communications
        
        sentiment_scores = []
        urgency_levels = []
        
        for comm in recent_comms:
            score = comm.get('preliminary_sentiment_score', 50)
            sentiment_scores.append(score)
            
            urgency = comm.get('sentiment_indicators', {}).get('urgency_signals', 0)
            urgency_levels.append(urgency)
        
        # Predict satisfaction trajectory
        if len(sentiment_scores) >= 2:
            if sentiment_scores[-1] > sentiment_scores[0] + 10:
                insights['satisfaction_prediction'] = 'improving'
                insights['positive_momentum'].append('Sentiment scores trending upward')
            elif sentiment_scores[-1] < sentiment_scores[0] - 10:
                insights['satisfaction_prediction'] = 'declining'
                insights['risk_indicators'].append('Sentiment scores trending downward')
        
        # Check for risk patterns
        high_urgency_count = sum(1 for level in urgency_levels if level > 2)
        if high_urgency_count >= 2:
            insights['risk_indicators'].append('Multiple urgent communications indicate stress')
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 50
        if avg_sentiment < 40:
            insights['risk_indicators'].append('Consistently low sentiment scores')
        
        # Generate focus area recommendations
        if avg_sentiment < 60:
            insights['recommended_focus_areas'].append('Improve communication frequency')
            insights['recommended_focus_areas'].append('Address specific concerns proactively')
        
        if high_urgency_count > 0:
            insights['recommended_focus_areas'].append('Reduce client stress through better project updates')
        
        return insights
    
    def _generate_automated_alerts(self, sentiment_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated alerts based on sentiment analysis"""
        
        alerts = {
            'active_alerts': [],
            'monitoring_rules': [],
            'escalation_triggers': []
        }
        
        current_sentiment = sentiment_report.get('overall_sentiment', {})
        sentiment_score = current_sentiment.get('sentiment_score', 50)
        
        try:
            score_num = float(str(sentiment_score).replace('%', ''))
        except:
            score_num = 50
        
        # Generate alerts based on sentiment thresholds
        if score_num < 30:
            alerts['active_alerts'].append({
                'level': 'high',
                'message': 'Critical: Very low client sentiment detected',
                'action_required': 'Immediate escalation to account manager',
                'timeline': 'Within 2 hours'
            })
        elif score_num < 50:
            alerts['active_alerts'].append({
                'level': 'medium',
                'message': 'Warning: Below-average client sentiment',
                'action_required': 'Schedule check-in call with client',
                'timeline': 'Within 24 hours'
            })
        
        # Check for risk indicators
        risk_assessment = sentiment_report.get('risk_assessment', {})
        if risk_assessment.get('churn_risk') == 'high':
            alerts['active_alerts'].append({
                'level': 'high',
                'message': 'High churn risk detected',
                'action_required': 'Account manager intervention needed',
                'timeline': 'Immediate'
            })
        
        # Set up monitoring rules
        alerts['monitoring_rules'] = [
            {
                'rule': 'Sentiment drops below 40',
                'action': 'Trigger medium alert',
                'frequency': 'Real-time'
            },
            {
                'rule': 'Three consecutive negative communications',
                'action': 'Trigger high alert',
                'frequency': 'Per communication'
            },
            {
                'rule': 'Sentiment decline of 20+ points',
                'action': 'Trigger escalation',
                'frequency': 'Daily review'
            }
        ]
        
        return alerts
    
    def _learn_from_sentiment_analysis(self, client_id: str, sentiment_report: Dict[str, Any]):
        """Learn from sentiment analysis to improve future predictions"""
        
        memory_key = f"sentiment_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'sentiment_trends': {},
            'successful_interventions': [],
            'communication_preferences': {}
        })
        
        # Track sentiment patterns by client
        overall_sentiment = sentiment_report.get('overall_sentiment', {})
        sentiment_label = overall_sentiment.get('sentiment_label', 'neutral')
        
        if client_id not in current_patterns['sentiment_trends']:
            current_patterns['sentiment_trends'][client_id] = []
        
        current_patterns['sentiment_trends'][client_id].append({
            'date': datetime.now().isoformat(),
            'sentiment': sentiment_label,
            'score': overall_sentiment.get('sentiment_score', 50)
        })
        
        # Keep only last 10 entries per client
        if len(current_patterns['sentiment_trends'][client_id]) > 10:
            current_patterns['sentiment_trends'][client_id] = (
                current_patterns['sentiment_trends'][client_id][-10:]
            )
        
        # Track communication preferences
        communication_breakdown = sentiment_report.get('communication_breakdown', [])
        for comm in communication_breakdown:
            channel = comm.get('channel', 'unknown')
            sentiment_score = comm.get('sentiment_score', 50)
            
            if client_id not in current_patterns['communication_preferences']:
                current_patterns['communication_preferences'][client_id] = {}
            
            if channel not in current_patterns['communication_preferences'][client_id]:
                current_patterns['communication_preferences'][client_id][channel] = []
            
            current_patterns['communication_preferences'][client_id][channel].append(sentiment_score)
            
            # Keep only last 5 scores per channel
            if len(current_patterns['communication_preferences'][client_id][channel]) > 5:
                current_patterns['communication_preferences'][client_id][channel] = (
                    current_patterns['communication_preferences'][client_id][channel][-5:]
                )
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_sentiment_analysis(self, analyzed_communications: List[Dict], client_id: str) -> Dict[str, Any]:
        """Fallback sentiment analysis when AI response fails"""
        
        if not analyzed_communications:
            return {
                'overall_sentiment': {
                    'sentiment_score': 50,
                    'sentiment_label': 'neutral',
                    'confidence_level': 'low',
                    'summary': 'No communications to analyze'
                },
                'analysis_timestamp': datetime.now().isoformat(),
                'fallback_analysis': True
            }
        
        # Calculate average sentiment from preliminary scores
        scores = [comm.get('preliminary_sentiment_score', 50) for comm in analyzed_communications]
        avg_score = sum(scores) / len(scores)
        
        # Determine sentiment label
        sentiment_label = 'neutral'
        for label, data in self.sentiment_scale.items():
            if data['range'][0] <= avg_score <= data['range'][1]:
                sentiment_label = label
                break
        
        # Basic risk assessment
        negative_comms = sum(1 for score in scores if score < 40)
        churn_risk = 'high' if negative_comms > len(scores) * 0.6 else 'medium' if negative_comms > 0 else 'low'
        
        return {
            'overall_sentiment': {
                'sentiment_score': f"{avg_score:.0f}",
                'sentiment_label': sentiment_label,
                'confidence_level': 'medium',
                'trend': 'stable',
                'summary': f'Analysis of {len(analyzed_communications)} communications shows {sentiment_label} sentiment'
            },
            'communication_breakdown': [
                {
                    'communication_id': comm.get('communication_id', f'comm_{i}'),
                    'channel': comm.get('channel', 'unknown'),
                    'sentiment_score': f"{comm.get('preliminary_sentiment_score', 50):.0f}",
                    'sentiment_label': comm.get('preliminary_sentiment_label', 'neutral'),
                    'urgency_level': 'high' if comm.get('sentiment_indicators', {}).get('urgency_signals', 0) > 2 else 'medium' if comm.get('sentiment_indicators', {}).get('urgency_signals', 0) > 0 else 'low'
                } for i, comm in enumerate(analyzed_communications)
            ],
            'risk_assessment': {
                'churn_risk': churn_risk,
                'escalation_risk': 'medium' if avg_score < 40 else 'low',
                'relationship_health': 'good' if avg_score >= 60 else 'concerning' if avg_score >= 40 else 'poor'
            },
            'proactive_recommendations': {
                'immediate_actions': [
                    {
                        'action': 'Review client communications for specific concerns',
                        'priority': 'medium',
                        'timeline': 'Within 24 hours',
                        'responsible_party': 'Account manager'
                    }
                ] if avg_score < 60 else []
            },
            'analysis_timestamp': datetime.now().isoformat(),
            'fallback_analysis': True,
            'communications_analyzed': len(analyzed_communications),
            'client_id': client_id
        }
    
    async def monitor_sentiment_trends(self, client_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Monitor sentiment trends for a specific client over time"""
        
        try:
            # Get historical sentiment data
            historical_key = f"sentiment_history_{client_id}"
            historical_data = self.get_memory(historical_key, [])
            
            # Filter data for specified time period
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_data = [
                entry for entry in historical_data 
                if datetime.fromisoformat(entry.get('timestamp', cutoff_date.isoformat())) >= cutoff_date
            ]
            
            if not recent_data:
                return {
                    'success': False,
                    'message': 'No sentiment data available for specified period'
                }
            
            # Calculate trend metrics
            scores = [float(str(entry.get('sentiment_score', 50)).replace('%', '')) for entry in recent_data]
            
            trend_analysis = {
                'average_sentiment': sum(scores) / len(scores),
                'sentiment_range': {'min': min(scores), 'max': max(scores)},
                'volatility': max(scores) - min(scores),
                'data_points': len(recent_data),
                'trend_direction': 'stable'
            }
            
            # Determine trend direction
            if len(scores) >= 2:
                first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
                second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
                
                if second_half_avg > first_half_avg + 5:
                    trend_analysis['trend_direction'] = 'improving'
                elif second_half_avg < first_half_avg - 5:
                    trend_analysis['trend_direction'] = 'declining'
            
            return {
                'success': True,
                'client_id': client_id,
                'monitoring_period': f'{days_back} days',
                'trend_analysis': trend_analysis,
                'recent_data': recent_data
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring sentiment trends: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Sentiment Analyzer',
            'description': 'Analyzes client communications for sentiment and suggests proactive relationship management',
            'inputs': ['communications', 'client_id', 'context'],
            'outputs': ['sentiment_analysis', 'risk_assessment', 'proactive_recommendations'],
            'supported_channels': list(self.communication_channels.keys()),
            'sentiment_scale': list(self.sentiment_scale.keys()),
            'features': ['trend_monitoring', 'automated_alerts', 'predictive_insights'],
            'analysis_types': ['individual_communication', 'aggregate_sentiment', 'historical_comparison'],
            'version': '1.0.0'
        }
