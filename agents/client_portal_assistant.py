from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime

class ClientPortalAssistant(BaseAgent):
    """
    Agent that provides a chatbot interface for clients to track progress,
    view AI-generated updates, and ask questions about their projects
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "client_portal_assistant")
        
        # Common client query types
        self.query_types = {
            'project_status': 'Questions about project progress and timeline',
            'deliverables': 'Questions about what will be delivered',
            'billing': 'Questions about invoices and payments',
            'revisions': 'Questions about changes and revisions',
            'timeline': 'Questions about deadlines and milestones',
            'general': 'General project questions'
        }
        
        # Response templates for common scenarios
        self.response_templates = {
            'project_update': {
                'greeting': "Hello! Here's the latest update on your project:",
                'sections': ['current_phase', 'completed_tasks', 'next_steps', 'timeline_status'],
                'closing': "Is there anything specific you'd like to know more about?"
            },
            'status_inquiry': {
                'greeting': "I'd be happy to update you on your project status.",
                'data_points': ['progress_percentage', 'current_milestone', 'estimated_completion'],
                'follow_up': "Would you like more details about any particular aspect?"
            }
        }
        
        # Client communication preferences
        self.communication_preferences = {
            'formal': {'tone': 'professional', 'style': 'detailed'},
            'casual': {'tone': 'friendly', 'style': 'conversational'},
            'brief': {'tone': 'efficient', 'style': 'concise'}
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process client inquiries and provide appropriate responses
        
        Args:
            input_data: Dictionary containing 'query', 'client_id', 'project_data', 'context'
            
        Returns:
            Dictionary with response and suggested actions
        """
        required_fields = ['query']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for client portal assistance")
        
        return await self._safe_execute(self._process_client_query, input_data)
    
    async def _process_client_query(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to process client queries"""
        
        query = input_data['query']
        client_id = input_data.get('client_id', 'unknown')
        project_data = input_data.get('project_data', {})
        context = input_data.get('context', {})
        
        # Classify the query type
        query_classification = await self._classify_query(query)
        
        # Get relevant project information
        relevant_info = self._extract_relevant_info(project_data, query_classification)
        
        # Generate contextual response using AI
        ai_prompt = f"""
        You are a helpful AI assistant for a creative agency's client portal. 
        A client has asked a question about their project. Please provide a professional, 
        helpful response that addresses their query directly.

        Client Query: "{query}"
        Query Type: {query_classification['type']}
        Client ID: {client_id}
        
        Relevant Project Information:
        {json.dumps(relevant_info, indent=2)}
        
        Project Context:
        {json.dumps(context, indent=2)}

        Please provide a JSON response with the following structure:
        {{
            "response": {{
                "message": "Your helpful response to the client",
                "tone": "professional/friendly/reassuring",
                "includes_data": true/false,
                "response_type": "informational/action_required/escalation_needed"
            }},
            "data_provided": {{
                "project_status": "Current project status if relevant",
                "timeline_info": "Timeline information if relevant",
                "deliverables_info": "Deliverable information if relevant",
                "next_steps": "What happens next if relevant"
            }},
            "suggested_actions": [
                {{
                    "action": "Action description",
                    "priority": "high/medium/low",
                    "assignee": "Who should handle this",
                    "timeline": "When this should be done"
                }}
            ],
            "follow_up_questions": [
                "Suggested follow-up question 1",
                "Suggested follow-up question 2"
            ],
            "attachments": [
                {{
                    "type": "document/image/link",
                    "title": "Attachment title",
                    "description": "What this attachment contains",
                    "relevance": "Why this is relevant to the query"
                }}
            ],
            "escalation": {{
                "needed": true/false,
                "reason": "Why escalation is needed if applicable",
                "to_whom": "Account manager/Project manager/Designer",
                "urgency": "high/medium/low"
            }},
            "client_satisfaction": {{
                "likely_satisfied": true/false,
                "confidence_level": "high/medium/low",
                "satisfaction_factors": ["What might affect satisfaction"]
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            portal_response = json.loads(ai_response)
            
            # Enhance response with additional context
            portal_response['query_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'client_id': client_id,
                'query_type': query_classification['type'],
                'confidence': query_classification.get('confidence', 'medium'),
                'response_time_ms': 0  # Would be calculated in real implementation
            }
            
            # Add personalization based on client history
            portal_response['personalization'] = self._personalize_response(client_id, query_classification)
            
            # Generate proactive suggestions
            portal_response['proactive_suggestions'] = self._generate_proactive_suggestions(project_data, client_id)
            
            # Log interaction for learning
            self._log_client_interaction(client_id, query, portal_response)
            
            return portal_response
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback response")
            return self._fallback_response(query, project_data, query_classification)
    
    async def _classify_query(self, query: str) -> Dict[str, Any]:
        """Classify the type of client query"""
        
        query_lower = query.lower()
        
        # Simple keyword-based classification (could be enhanced with ML)
        classifications = {
            'project_status': ['status', 'progress', 'how is', 'update', 'where are we'],
            'deliverables': ['deliverable', 'files', 'final', 'receive', 'download'],
            'billing': ['invoice', 'payment', 'cost', 'bill', 'price'],
            'revisions': ['change', 'revision', 'modify', 'edit', 'different'],
            'timeline': ['deadline', 'when', 'timeline', 'schedule', 'date'],
            'general': []  # catch-all
        }
        
        scores = {}
        for query_type, keywords in classifications.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                scores[query_type] = score
        
        if scores:
            best_match = max(scores.keys(), key=lambda k: scores[k])
            confidence = 'high' if scores[best_match] >= 2 else 'medium'
        else:
            best_match = 'general'
            confidence = 'low'
        
        return {
            'type': best_match,
            'confidence': confidence,
            'keywords_found': [k for k, v in scores.items() if v > 0]
        }
    
    def _extract_relevant_info(self, project_data: Dict[str, Any], query_classification: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant project information based on query type"""
        
        query_type = query_classification['type']
        relevant_info = {}
        
        if query_type == 'project_status':
            relevant_info.update({
                'current_status': project_data.get('status', 'In progress'),
                'progress_percentage': project_data.get('progress', 'Not specified'),
                'current_phase': project_data.get('current_phase', 'Not specified'),
                'last_update': project_data.get('last_update', 'Not available')
            })
        
        elif query_type == 'deliverables':
            relevant_info.update({
                'deliverables': project_data.get('deliverables', []),
                'completed_deliverables': project_data.get('completed_deliverables', []),
                'pending_deliverables': project_data.get('pending_deliverables', [])
            })
        
        elif query_type == 'timeline':
            relevant_info.update({
                'start_date': project_data.get('start_date', 'Not specified'),
                'estimated_completion': project_data.get('estimated_completion', 'Not specified'),
                'milestones': project_data.get('milestones', []),
                'current_milestone': project_data.get('current_milestone', 'Not specified')
            })
        
        elif query_type == 'billing':
            relevant_info.update({
                'total_cost': project_data.get('total_cost', 'Not specified'),
                'payments_made': project_data.get('payments_made', []),
                'outstanding_balance': project_data.get('outstanding_balance', 'Not specified'),
                'next_payment_due': project_data.get('next_payment_due', 'Not specified')
            })
        
        else:
            # Include general project information
            relevant_info = {
                'project_name': project_data.get('name', 'Your project'),
                'status': project_data.get('status', 'In progress'),
                'team_contact': project_data.get('account_manager', 'Your account manager')
            }
        
        return relevant_info
    
    def _personalize_response(self, client_id: str, query_classification: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize response based on client history and preferences"""
        
        # Get client preferences from memory
        client_prefs = self.get_memory(f'client_prefs_{client_id}', {
            'communication_style': 'professional',
            'preferred_detail_level': 'medium',
            'frequent_query_types': [],
            'satisfaction_history': []
        })
        
        # Update frequent query types
        query_type = query_classification['type']
        if query_type not in client_prefs['frequent_query_types']:
            client_prefs['frequent_query_types'].append(query_type)
        
        # Save updated preferences
        self.update_memory(f'client_prefs_{client_id}', client_prefs)
        
        return {
            'communication_style': client_prefs['communication_style'],
            'detail_level': client_prefs['preferred_detail_level'],
            'is_frequent_query_type': query_type in client_prefs['frequent_query_types'][:3],
            'personalization_confidence': 'high' if len(client_prefs['frequent_query_types']) > 3 else 'low'
        }
    
    def _generate_proactive_suggestions(self, project_data: Dict[str, Any], client_id: str) -> List[Dict[str, Any]]:
        """Generate proactive suggestions for the client"""
        
        suggestions = []
        
        # Timeline-based suggestions
        if project_data.get('estimated_completion'):
            suggestions.append({
                'type': 'timeline_reminder',
                'message': 'Your project is estimated to complete soon. Would you like to schedule a review meeting?',
                'action': 'Schedule review meeting',
                'priority': 'medium'
            })
        
        # Deliverables-based suggestions
        completed_deliverables = project_data.get('completed_deliverables', [])
        if completed_deliverables:
            suggestions.append({
                'type': 'review_opportunity',
                'message': f'We have {len(completed_deliverables)} deliverables ready for your review.',
                'action': 'Review completed work',
                'priority': 'high'
            })
        
        # Communication suggestions
        last_update = project_data.get('last_update')
        if last_update:
            suggestions.append({
                'type': 'stay_informed',
                'message': 'Would you like to set up regular progress updates?',
                'action': 'Set up regular updates',
                'priority': 'low'
            })
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _log_client_interaction(self, client_id: str, query: str, response: Dict[str, Any]):
        """Log client interaction for learning and improvement"""
        
        interaction_log = {
            'timestamp': datetime.now().isoformat(),
            'client_id': client_id,
            'query_type': response.get('query_metadata', {}).get('query_type', 'unknown'),
            'response_type': response.get('response', {}).get('response_type', 'unknown'),
            'escalation_needed': response.get('escalation', {}).get('needed', False),
            'satisfaction_predicted': response.get('client_satisfaction', {}).get('likely_satisfied', True)
        }
        
        # Store in memory for pattern analysis
        memory_key = f'client_interactions_{client_id}'
        interactions = self.get_memory(memory_key, [])
        interactions.append(interaction_log)
        
        # Keep only last 50 interactions
        if len(interactions) > 50:
            interactions = interactions[-50:]
        
        self.update_memory(memory_key, interactions)
    
    def _fallback_response(self, query: str, project_data: Dict[str, Any], query_classification: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback response when AI response fails"""
        
        project_name = project_data.get('name', 'your project')
        
        return {
            'response': {
                'message': f'Thank you for your question about {project_name}. I understand you\'re asking about {query_classification["type"]}. Let me connect you with your project manager for the most accurate information.',
                'tone': 'professional',
                'includes_data': False,
                'response_type': 'escalation_needed'
            },
            'suggested_actions': [
                {
                    'action': 'Connect client with project manager',
                    'priority': 'high',
                    'assignee': 'Project Manager',
                    'timeline': 'Within 2 hours'
                }
            ],
            'escalation': {
                'needed': True,
                'reason': 'Unable to generate appropriate response',
                'to_whom': 'Project manager',
                'urgency': 'medium'
            },
            'query_metadata': {
                'timestamp': datetime.now().isoformat(),
                'fallback_response': True
            }
        }
    
    async def generate_project_update(self, project_data: Dict[str, Any], client_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate proactive project update for client"""
        
        try:
            preferences = client_preferences or {}
            
            ai_prompt = f"""
            Generate a proactive project update for a client based on the current project status.
            
            Project Data: {json.dumps(project_data, indent=2)}
            Client Preferences: {json.dumps(preferences, indent=2)}
            
            Create a friendly, informative update that includes:
            - Current progress summary
            - Recent accomplishments
            - Upcoming milestones
            - Any items that need client input
            - Next steps
            
            Format as a professional but warm update message.
            """
            
            update_message = await self._generate_ai_response(ai_prompt)
            
            return {
                'success': True,
                'update_message': update_message,
                'timestamp': datetime.now().isoformat(),
                'project_id': project_data.get('id', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Error generating project update: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_message': f'Your project "{project_data.get("name", "project")}" is progressing well. We\'ll have a detailed update for you soon.'
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Client Portal Assistant',
            'description': 'Provides chatbot interface for clients to track progress and ask questions',
            'inputs': ['query', 'client_id', 'project_data', 'context'],
            'outputs': ['response', 'suggested_actions', 'escalation_recommendations'],
            'supported_query_types': list(self.query_types.keys()),
            'features': ['query_classification', 'personalized_responses', 'proactive_suggestions'],
            'integrations': ['project_management', 'client_database', 'notification_system'],
            'version': '1.0.0'
        }
