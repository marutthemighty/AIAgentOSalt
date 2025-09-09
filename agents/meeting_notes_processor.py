from core.base_agent import BaseAgent
from typing import Dict, Any
import re
import json
from datetime import datetime

class MeetingNotesProcessor(BaseAgent):
    """
    Agent that converts meeting notes or transcripts into structured action items,
    integrates with project management tools, and provides status updates
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "meeting_notes_processor")
        
        # Initialize agent-specific configuration
        self.action_item_patterns = [
            r"action item:?\s*(.+)",
            r"todo:?\s*(.+)",
            r"follow up:?\s*(.+)",
            r"next steps?:?\s*(.+)",
        ]
        
        # Register message handlers
        self.register_message_handler('feedback', self._handle_feedback)
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process meeting notes and extract structured information
        
        Args:
            input_data: Dictionary containing 'meeting_notes', 'attendees', 'meeting_date'
            
        Returns:
            Dictionary with structured action items, decisions, and follow-ups
        """
        # Validate input
        required_fields = ['meeting_notes']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for meeting notes processing")
        
        return await self._safe_execute(self._process_meeting_notes, input_data)
    
    async def _process_meeting_notes(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to process meeting notes"""
        
        meeting_notes = input_data['meeting_notes']
        attendees = input_data.get('attendees', [])
        meeting_date = input_data.get('meeting_date', datetime.now().isoformat())
        
        # Extract basic action items using regex patterns
        quick_actions = self._extract_quick_actions(meeting_notes)
        
        # Use AI to generate comprehensive analysis
        ai_prompt = f"""
        Analyze the following meeting notes and extract structured information:

        Meeting Notes:
        {meeting_notes}

        Attendees: {', '.join(attendees) if attendees else 'Not specified'}
        Date: {meeting_date}

        Please provide a JSON response with the following structure:
        {{
            "summary": "Brief meeting summary",
            "key_decisions": ["List of key decisions made"],
            "action_items": [
                {{
                    "task": "Description of task",
                    "assignee": "Person responsible",
                    "due_date": "Estimated due date",
                    "priority": "high/medium/low",
                    "category": "task category"
                }}
            ],
            "follow_ups": ["List of follow-up items"],
            "blockers": ["Any identified blockers or issues"],
            "next_meeting": "Suggested next meeting topics or date"
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            # Parse AI response
            structured_data = json.loads(ai_response)
            
            # Enhance with quick actions found
            if quick_actions:
                existing_tasks = [item['task'] for item in structured_data.get('action_items', [])]
                for action in quick_actions:
                    if action not in existing_tasks:
                        structured_data.setdefault('action_items', []).append({
                            'task': action,
                            'assignee': 'TBD',
                            'due_date': 'TBD',
                            'priority': 'medium',
                            'category': 'general'
                        })
            
            # Add metadata
            structured_data['processed_at'] = datetime.now().isoformat()
            structured_data['attendees'] = attendees
            structured_data['original_meeting_date'] = meeting_date
            
            # Learn from processing for future improvements
            self._learn_from_processing(meeting_notes, structured_data)
            
            return structured_data
            
        except json.JSONDecodeError:
            # Fallback to manual extraction if AI response isn't valid JSON
            self.logger.warning("AI response wasn't valid JSON, using fallback processing")
            return self._fallback_processing(meeting_notes, attendees, meeting_date, quick_actions)
    
    def _extract_quick_actions(self, text: str) -> list:
        """Extract action items using regex patterns"""
        actions = []
        
        for pattern in self.action_item_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            actions.extend([match.strip() for match in matches])
        
        return list(set(actions))  # Remove duplicates
    
    def _fallback_processing(self, notes: str, attendees: list, date: str, quick_actions: list) -> Dict[str, Any]:
        """Fallback processing when AI response fails"""
        
        # Basic text analysis
        sentences = notes.split('.')
        
        return {
            'summary': sentences[0][:200] + "..." if sentences else "Meeting summary not available",
            'key_decisions': [],
            'action_items': [
                {
                    'task': action,
                    'assignee': 'TBD',
                    'due_date': 'TBD',
                    'priority': 'medium',
                    'category': 'general'
                } for action in quick_actions
            ],
            'follow_ups': [],
            'blockers': [],
            'next_meeting': 'To be determined',
            'processed_at': datetime.now().isoformat(),
            'attendees': attendees,
            'original_meeting_date': date,
            'fallback_processing': True
        }
    
    def _learn_from_processing(self, original_notes: str, processed_data: Dict[str, Any]):
        """Learn from processing to improve future results"""
        
        # Store patterns for learning
        memory_key = f"processing_pattern_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {})
        
        # Analyze successful extractions
        action_count = len(processed_data.get('action_items', []))
        decision_count = len(processed_data.get('key_decisions', []))
        
        current_patterns.update({
            'average_actions': current_patterns.get('average_actions', 0) * 0.8 + action_count * 0.2,
            'average_decisions': current_patterns.get('average_decisions', 0) * 0.8 + decision_count * 0.2,
            'last_processed': datetime.now().isoformat()
        })
        
        self.update_memory(memory_key, current_patterns)
    
    def _handle_feedback(self, message_data: Dict[str, Any]):
        """Handle feedback from other agents or users"""
        feedback = message_data.get('message', {}).get('feedback', {})
        
        if feedback.get('type') == 'accuracy':
            # Adjust processing based on accuracy feedback
            accuracy_score = feedback.get('score', 0.5)
            self.update_memory('accuracy_trend', accuracy_score)
            
        elif feedback.get('type') == 'preferences':
            # Learn team preferences
            preferences = feedback.get('data', {})
            self.update_memory('team_preferences', preferences)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Meeting Notes Processor',
            'description': 'Converts meeting notes into structured action items and project updates',
            'inputs': ['meeting_notes', 'attendees', 'meeting_date'],
            'outputs': ['action_items', 'decisions', 'summary', 'follow_ups'],
            'integrations': ['jira', 'slack', 'notion'],
            'learning_features': ['team_preferences', 'accuracy_improvement'],
            'version': '1.0.0'
        }
    
    async def create_jira_tasks(self, action_items: list, project_key: str = None) -> Dict[str, Any]:
        """Create JIRA tasks from action items (integration method)"""
        try:
            # This would integrate with actual JIRA API
            # For now, return structured data for JIRA integration
            
            jira_tasks = []
            for item in action_items:
                task = {
                    'summary': item['task'],
                    'description': f"Generated from meeting notes\nAssignee: {item.get('assignee', 'TBD')}",
                    'priority': item.get('priority', 'medium').title(),
                    'due_date': item.get('due_date'),
                    'labels': ['meeting-generated', item.get('category', 'general')]
                }
                jira_tasks.append(task)
            
            return {
                'success': True,
                'tasks_created': len(jira_tasks),
                'tasks': jira_tasks,
                'project_key': project_key
            }
            
        except Exception as e:
            self.logger.error(f"Error creating JIRA tasks: {str(e)}")
            return {'success': False, 'error': str(e)}
