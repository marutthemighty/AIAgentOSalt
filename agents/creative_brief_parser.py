from core.base_agent import BaseAgent
from typing import Dict, Any
import json
from datetime import datetime
import re

class CreativeBriefParser(BaseAgent):
    """
    Agent that parses unstructured client inputs into structured briefs
    with goals, deliverables, timelines, and constraints
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "creative_brief_parser")
        
        # Common brief patterns and keywords
        self.goal_keywords = ['goal', 'objective', 'aim', 'target', 'achieve', 'want', 'need']
        self.deliverable_keywords = ['deliver', 'create', 'design', 'build', 'develop', 'produce']
        self.timeline_keywords = ['deadline', 'due', 'timeline', 'schedule', 'urgent', 'asap']
        self.constraint_keywords = ['budget', 'limitation', 'constraint', 'requirement', 'must not']
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse client input into structured creative brief
        
        Args:
            input_data: Dictionary containing 'client_input', 'client_name', 'input_type'
            
        Returns:
            Dictionary with structured brief information
        """
        required_fields = ['client_input']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for brief parsing")
        
        return await self._safe_execute(self._parse_creative_brief, input_data)
    
    async def _parse_creative_brief(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to parse creative brief"""
        
        client_input = input_data['client_input']
        client_name = input_data.get('client_name', 'Unknown Client')
        input_type = input_data.get('input_type', 'text')  # email, chat, call_transcript, text
        
        # Pre-process the input to extract obvious elements
        quick_analysis = self._quick_analysis(client_input)
        
        # Generate comprehensive analysis using AI
        ai_prompt = f"""
        Parse the following client communication into a structured creative brief:

        Client: {client_name}
        Communication Type: {input_type}
        
        Client Input:
        {client_input}

        Please analyze this and provide a JSON response with the following structure:
        {{
            "project_title": "Suggested project title",
            "client_name": "{client_name}",
            "project_type": "Type of project (website, branding, marketing, etc.)",
            "goals": {{
                "primary": "Main project goal",
                "secondary": ["Secondary goals"],
                "success_metrics": ["How success will be measured"]
            }},
            "deliverables": [
                {{
                    "item": "Deliverable name",
                    "description": "Detailed description",
                    "format": "File format or type",
                    "priority": "high/medium/low"
                }}
            ],
            "timeline": {{
                "deadline": "Final deadline if mentioned",
                "milestones": [
                    {{
                        "name": "Milestone name",
                        "date": "Estimated date",
                        "deliverables": ["Associated deliverables"]
                    }}
                ],
                "urgency": "high/medium/low"
            }},
            "constraints": {{
                "budget": "Budget information if mentioned",
                "technical": ["Technical constraints"],
                "design": ["Design constraints"],
                "content": ["Content constraints"]
            }},
            "target_audience": {{
                "primary": "Primary audience description",
                "demographics": "Age, location, interests if mentioned",
                "personas": ["User personas if identifiable"]
            }},
            "brand_context": {{
                "existing_brand": "Information about existing brand",
                "competitors": ["Mentioned competitors"],
                "style_preferences": ["Design/style preferences mentioned"]
            }},
            "additional_notes": "Any other important information",
            "clarity_score": "1-10 rating of how clear the brief is",
            "missing_information": ["Key information that should be clarified with client"]
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            structured_brief = json.loads(ai_response)
            
            # Enhance with quick analysis findings
            self._merge_quick_analysis(structured_brief, quick_analysis)
            
            # Add metadata
            structured_brief['parsed_at'] = datetime.now().isoformat()
            structured_brief['input_type'] = input_type
            structured_brief['parser_version'] = '1.0.0'
            
            # Generate project folder structure
            structured_brief['suggested_folder_structure'] = self._generate_folder_structure(structured_brief)
            
            # Create initial checklist
            structured_brief['initial_checklist'] = self._generate_initial_checklist(structured_brief)
            
            # Learn from this parsing
            self._learn_from_parsing(client_input, structured_brief)
            
            return structured_brief
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback parsing")
            return self._fallback_parsing(client_input, client_name, input_type, quick_analysis)
    
    def _quick_analysis(self, text: str) -> Dict[str, Any]:
        """Quick analysis using regex patterns"""
        
        analysis = {
            'goals_found': [],
            'deliverables_found': [],
            'timelines_found': [],
            'constraints_found': [],
            'contact_info': [],
            'urls_found': []
        }
        
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        analysis['contact_info'].extend(emails)
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        analysis['urls_found'].extend(urls)
        
        # Extract phone numbers
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        analysis['contact_info'].extend(phones)
        
        # Find sentences containing goal keywords
        sentences = text.split('.')
        for sentence in sentences:
            lower_sentence = sentence.lower()
            if any(keyword in lower_sentence for keyword in self.goal_keywords):
                analysis['goals_found'].append(sentence.strip())
            if any(keyword in lower_sentence for keyword in self.deliverable_keywords):
                analysis['deliverables_found'].append(sentence.strip())
            if any(keyword in lower_sentence for keyword in self.timeline_keywords):
                analysis['timelines_found'].append(sentence.strip())
            if any(keyword in lower_sentence for keyword in self.constraint_keywords):
                analysis['constraints_found'].append(sentence.strip())
        
        return analysis
    
    def _merge_quick_analysis(self, structured_brief: Dict[str, Any], quick_analysis: Dict[str, Any]):
        """Merge quick analysis results into structured brief"""
        
        # Add found contact information
        if quick_analysis['contact_info']:
            structured_brief['contact_information'] = quick_analysis['contact_info']
        
        # Add found URLs as reference materials
        if quick_analysis['urls_found']:
            structured_brief['reference_materials'] = quick_analysis['urls_found']
        
        # Enhance goals with found goal statements
        if quick_analysis['goals_found']:
            existing_goals = structured_brief.get('goals', {}).get('secondary', [])
            structured_brief.setdefault('goals', {}).setdefault('additional_context', []).extend(quick_analysis['goals_found'])
    
    def _generate_folder_structure(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Generate suggested project folder structure"""
        
        project_type = brief.get('project_type', 'general').lower()
        client_name = brief.get('client_name', 'client').replace(' ', '_').lower()
        
        base_structure = {
            '01_project_brief': ['brief.md', 'requirements.txt', 'timeline.md'],
            '02_research': ['competitor_analysis', 'target_audience', 'references'],
            '03_concepts': ['wireframes', 'mockups', 'prototypes'],
            '04_assets': ['images', 'fonts', 'icons', 'logos'],
            '05_final_deliverables': ['exports', 'source_files', 'documentation'],
            '06_communication': ['client_feedback', 'meeting_notes', 'approvals']
        }
        
        # Customize based on project type
        if 'website' in project_type or 'web' in project_type:
            base_structure['03_concepts'].extend(['site_map', 'user_flows'])
            base_structure['04_assets'].extend(['graphics', 'videos'])
            
        elif 'branding' in project_type or 'logo' in project_type:
            base_structure['03_concepts'] = ['logo_concepts', 'brand_guidelines', 'color_palettes']
            base_structure['04_assets'] = ['logo_files', 'brand_assets', 'templates']
            
        elif 'marketing' in project_type:
            base_structure['03_concepts'] = ['campaign_concepts', 'ad_designs', 'content_plans']
            base_structure['04_assets'] = ['ad_materials', 'social_media', 'print_materials']
        
        return {
            'root_folder': f"{client_name}_{brief.get('project_title', 'project').replace(' ', '_').lower()}",
            'structure': base_structure,
            'naming_convention': 'lowercase_with_underscores',
            'file_versioning': 'v1, v2, v3...'
        }
    
    def _generate_initial_checklist(self, brief: Dict[str, Any]) -> list:
        """Generate initial project checklist based on brief"""
        
        checklist = [
            {
                'category': 'Project Setup',
                'tasks': [
                    'Create project folder structure',
                    'Set up project management board',
                    'Schedule kick-off meeting',
                    'Clarify missing information with client'
                ]
            },
            {
                'category': 'Research Phase',
                'tasks': [
                    'Analyze target audience',
                    'Research competitors',
                    'Gather reference materials',
                    'Define success metrics'
                ]
            }
        ]
        
        # Add deliverable-specific tasks
        deliverables = brief.get('deliverables', [])
        if deliverables:
            deliverable_tasks = {
                'category': 'Deliverables',
                'tasks': [f"Create {item.get('item', 'deliverable')}" for item in deliverables[:5]]
            }
            checklist.append(deliverable_tasks)
        
        # Add timeline-specific tasks
        timeline = brief.get('timeline', {})
        if timeline.get('deadline'):
            timeline_tasks = {
                'category': 'Timeline Management',
                'tasks': [
                    f"Work backwards from deadline: {timeline['deadline']}",
                    'Set internal milestones',
                    'Buffer time for revisions',
                    'Schedule client review points'
                ]
            }
            checklist.append(timeline_tasks)
        
        return checklist
    
    def _learn_from_parsing(self, original_input: str, parsed_brief: Dict[str, Any]):
        """Learn from parsing to improve future results"""
        
        # Store patterns for learning
        memory_key = f"parsing_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'common_project_types': {},
            'clarity_scores': [],
            'missing_info_patterns': []
        })
        
        # Update project type frequency
        project_type = parsed_brief.get('project_type', 'unknown')
        current_patterns['common_project_types'][project_type] = (
            current_patterns['common_project_types'].get(project_type, 0) + 1
        )
        
        # Track clarity scores
        clarity_score = parsed_brief.get('clarity_score', 5)
        current_patterns['clarity_scores'].append(clarity_score)
        if len(current_patterns['clarity_scores']) > 50:
            current_patterns['clarity_scores'] = current_patterns['clarity_scores'][-50:]
        
        # Track common missing information
        missing_info = parsed_brief.get('missing_information', [])
        current_patterns['missing_info_patterns'].extend(missing_info)
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_parsing(self, client_input: str, client_name: str, input_type: str, quick_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback parsing when AI response fails"""
        
        return {
            'project_title': f'Project for {client_name}',
            'client_name': client_name,
            'project_type': 'general',
            'goals': {
                'primary': 'To be clarified with client',
                'secondary': quick_analysis.get('goals_found', []),
                'success_metrics': []
            },
            'deliverables': [
                {
                    'item': goal,
                    'description': 'Extracted from client input',
                    'format': 'TBD',
                    'priority': 'medium'
                } for goal in quick_analysis.get('deliverables_found', [])[:3]
            ],
            'timeline': {
                'deadline': 'TBD',
                'milestones': [],
                'urgency': 'medium'
            },
            'constraints': {
                'budget': 'Not specified',
                'technical': quick_analysis.get('constraints_found', []),
                'design': [],
                'content': []
            },
            'parsed_at': datetime.now().isoformat(),
            'input_type': input_type,
            'fallback_parsing': True,
            'contact_information': quick_analysis.get('contact_info', []),
            'reference_materials': quick_analysis.get('urls_found', []),
            'clarity_score': 3,
            'missing_information': [
                'Project scope and objectives',
                'Budget and timeline',
                'Target audience details',
                'Technical requirements',
                'Brand guidelines'
            ]
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Creative Brief Parser',
            'description': 'Parses unstructured client inputs into structured creative briefs',
            'inputs': ['client_input', 'client_name', 'input_type'],
            'outputs': ['structured_brief', 'project_checklist', 'folder_structure'],
            'supported_input_types': ['email', 'chat', 'call_transcript', 'text'],
            'integrations': ['project_management', 'file_system'],
            'learning_features': ['project_type_recognition', 'clarity_improvement'],
            'version': '1.0.0'
        }
