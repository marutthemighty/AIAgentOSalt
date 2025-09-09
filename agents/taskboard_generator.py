from core.base_agent import BaseAgent
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
import uuid

class TaskboardGenerator(BaseAgent):
    """
    Agent that converts parsed briefs into actionable taskboards
    with tasks, due dates, assignees, and statuses
    """
    
    def __init__(self, ai_client):
        super().__init__(ai_client, "taskboard_generator")
        
        # Task templates based on project types
        self.project_templates = {
            'website': self._website_template,
            'branding': self._branding_template,
            'marketing': self._marketing_template,
            'general': self._general_template
        }
        
        # Standard task categories
        self.task_categories = [
            'Planning', 'Research', 'Design', 'Development', 
            'Content', 'Review', 'Testing', 'Launch', 'Documentation'
        ]
        
        # Priority mapping
        self.priority_weights = {'high': 3, 'medium': 2, 'low': 1}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate taskboard from structured brief
        
        Args:
            input_data: Dictionary containing 'brief', 'team_members', 'preferences'
            
        Returns:
            Dictionary with taskboard structure and tasks
        """
        required_fields = ['brief']
        if not self._validate_input(input_data, required_fields):
            raise ValueError("Missing required fields for taskboard generation")
        
        return await self._safe_execute(self._generate_taskboard, input_data)
    
    async def _generate_taskboard(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to generate taskboard"""
        
        brief = input_data['brief']
        team_members = input_data.get('team_members', [])
        preferences = input_data.get('preferences', {})
        
        # Extract project information
        project_type = brief.get('project_type', 'general').lower()
        deliverables = brief.get('deliverables', [])
        timeline = brief.get('timeline', {})
        
        # Generate base tasks using template
        template_func = self.project_templates.get(project_type, self.project_templates['general'])
        base_tasks = template_func(brief)
        
        # Use AI to enhance and customize tasks
        ai_prompt = f"""
        Based on the following creative brief, enhance and customize the task list:

        Project Type: {project_type}
        Brief Summary: {brief.get('goals', {}).get('primary', 'Not specified')}
        Deliverables: {json.dumps(deliverables, indent=2)}
        Timeline: {json.dumps(timeline, indent=2)}
        Team Members: {', '.join(team_members) if team_members else 'Not specified'}

        Base Tasks Generated:
        {json.dumps(base_tasks, indent=2)}

        Please enhance this task list and provide a JSON response with the following structure:
        {{
            "project_info": {{
                "id": "unique_project_id",
                "name": "project name",
                "description": "brief description",
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "status": "planning"
            }},
            "columns": [
                {{
                    "id": "column_id",
                    "name": "Column Name",
                    "order": 1,
                    "color": "#hex_color"
                }}
            ],
            "tasks": [
                {{
                    "id": "task_id",
                    "title": "Task title",
                    "description": "Detailed description",
                    "category": "task category",
                    "priority": "high/medium/low",
                    "estimated_hours": "number",
                    "assignee": "team member or TBD",
                    "due_date": "YYYY-MM-DD",
                    "dependencies": ["task_ids that must be completed first"],
                    "column_id": "current column",
                    "tags": ["relevant", "tags"],
                    "checklist": ["subtask 1", "subtask 2"],
                    "deliverable_link": "linked deliverable if applicable"
                }}
            ],
            "milestones": [
                {{
                    "id": "milestone_id",
                    "name": "Milestone name",
                    "date": "YYYY-MM-DD",
                    "description": "Milestone description",
                    "linked_tasks": ["task_ids"]
                }}
            ],
            "timeline_view": {{
                "gantt_data": "gantt chart data structure",
                "critical_path": ["task_ids on critical path"]
            }}
        }}
        """
        
        ai_response = await self._generate_ai_response(ai_prompt)
        
        try:
            enhanced_taskboard = json.loads(ai_response)
            
            # Validate and enhance the taskboard
            self._validate_taskboard(enhanced_taskboard)
            self._optimize_task_scheduling(enhanced_taskboard)
            
            # Add integration data
            enhanced_taskboard['integrations'] = self._generate_integration_data(enhanced_taskboard)
            
            # Add metadata
            enhanced_taskboard['generated_at'] = datetime.now().isoformat()
            enhanced_taskboard['generator_version'] = '1.0.0'
            enhanced_taskboard['original_brief'] = brief.get('project_title', 'Unknown Project')
            
            # Learn from generation
            self._learn_from_generation(brief, enhanced_taskboard)
            
            return enhanced_taskboard
            
        except json.JSONDecodeError:
            self.logger.warning("AI response wasn't valid JSON, using fallback generation")
            return self._fallback_generation(brief, team_members, base_tasks)
    
    def _website_template(self, brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate website project template tasks"""
        return [
            {
                'title': 'Project Discovery & Planning',
                'category': 'Planning',
                'estimated_hours': 8,
                'priority': 'high',
                'checklist': [
                    'Review brief and requirements',
                    'Conduct stakeholder interviews',
                    'Define project scope',
                    'Create project timeline'
                ]
            },
            {
                'title': 'User Research & Analysis',
                'category': 'Research',
                'estimated_hours': 12,
                'priority': 'high',
                'checklist': [
                    'Analyze target audience',
                    'Research competitors',
                    'Create user personas',
                    'Define user journeys'
                ]
            },
            {
                'title': 'Information Architecture',
                'category': 'Planning',
                'estimated_hours': 6,
                'priority': 'high',
                'checklist': [
                    'Create site map',
                    'Define navigation structure',
                    'Plan content hierarchy',
                    'Wireframe key pages'
                ]
            },
            {
                'title': 'Visual Design',
                'category': 'Design',
                'estimated_hours': 20,
                'priority': 'medium',
                'checklist': [
                    'Create style guide',
                    'Design homepage',
                    'Design internal pages',
                    'Create responsive layouts'
                ]
            },
            {
                'title': 'Frontend Development',
                'category': 'Development',
                'estimated_hours': 30,
                'priority': 'medium',
                'checklist': [
                    'Set up development environment',
                    'Code HTML/CSS',
                    'Implement responsive design',
                    'Add interactive elements'
                ]
            },
            {
                'title': 'Content Creation',
                'category': 'Content',
                'estimated_hours': 15,
                'priority': 'medium',
                'checklist': [
                    'Write copy for all pages',
                    'Optimize for SEO',
                    'Source/create images',
                    'Review and edit content'
                ]
            },
            {
                'title': 'Testing & Quality Assurance',
                'category': 'Testing',
                'estimated_hours': 8,
                'priority': 'high',
                'checklist': [
                    'Cross-browser testing',
                    'Mobile responsiveness check',
                    'Performance optimization',
                    'Accessibility audit'
                ]
            },
            {
                'title': 'Launch & Deployment',
                'category': 'Launch',
                'estimated_hours': 4,
                'priority': 'high',
                'checklist': [
                    'Set up hosting',
                    'Configure domain',
                    'Deploy website',
                    'Test live site'
                ]
            }
        ]
    
    def _branding_template(self, brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate branding project template tasks"""
        return [
            {
                'title': 'Brand Strategy Development',
                'category': 'Planning',
                'estimated_hours': 10,
                'priority': 'high',
                'checklist': [
                    'Define brand positioning',
                    'Identify target audience',
                    'Analyze competitors',
                    'Create brand strategy document'
                ]
            },
            {
                'title': 'Logo Design & Concepts',
                'category': 'Design',
                'estimated_hours': 16,
                'priority': 'high',
                'checklist': [
                    'Brainstorm concepts',
                    'Create initial sketches',
                    'Develop 3-5 concepts',
                    'Refine selected concept'
                ]
            },
            {
                'title': 'Brand Guidelines Creation',
                'category': 'Documentation',
                'estimated_hours': 12,
                'priority': 'medium',
                'checklist': [
                    'Define color palette',
                    'Select typography',
                    'Create usage guidelines',
                    'Document brand voice'
                ]
            },
            {
                'title': 'Brand Asset Development',
                'category': 'Design',
                'estimated_hours': 8,
                'priority': 'medium',
                'checklist': [
                    'Create business card design',
                    'Design letterhead',
                    'Develop social media templates',
                    'Create brand presentation'
                ]
            }
        ]
    
    def _marketing_template(self, brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate marketing project template tasks"""
        return [
            {
                'title': 'Campaign Strategy & Planning',
                'category': 'Planning',
                'estimated_hours': 8,
                'priority': 'high',
                'checklist': [
                    'Define campaign objectives',
                    'Identify target audience',
                    'Set success metrics',
                    'Create campaign timeline'
                ]
            },
            {
                'title': 'Content Creation',
                'category': 'Content',
                'estimated_hours': 15,
                'priority': 'medium',
                'checklist': [
                    'Write ad copy',
                    'Create visual assets',
                    'Develop landing pages',
                    'Prepare social media content'
                ]
            },
            {
                'title': 'Campaign Launch',
                'category': 'Launch',
                'estimated_hours': 4,
                'priority': 'high',
                'checklist': [
                    'Set up tracking',
                    'Launch campaigns',
                    'Monitor initial performance',
                    'Make optimization adjustments'
                ]
            }
        ]
    
    def _general_template(self, brief: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general project template tasks"""
        return [
            {
                'title': 'Project Setup & Planning',
                'category': 'Planning',
                'estimated_hours': 4,
                'priority': 'high',
                'checklist': [
                    'Review project requirements',
                    'Set up project workspace',
                    'Create initial timeline',
                    'Assign team members'
                ]
            },
            {
                'title': 'Research & Discovery',
                'category': 'Research',
                'estimated_hours': 6,
                'priority': 'medium',
                'checklist': [
                    'Gather requirements',
                    'Research best practices',
                    'Analyze constraints',
                    'Document findings'
                ]
            },
            {
                'title': 'Concept Development',
                'category': 'Design',
                'estimated_hours': 8,
                'priority': 'medium',
                'checklist': [
                    'Brainstorm solutions',
                    'Create initial concepts',
                    'Get stakeholder feedback',
                    'Refine concepts'
                ]
            },
            {
                'title': 'Final Delivery',
                'category': 'Launch',
                'estimated_hours': 4,
                'priority': 'high',
                'checklist': [
                    'Prepare final deliverables',
                    'Quality check',
                    'Package for delivery',
                    'Present to client'
                ]
            }
        ]
    
    def _validate_taskboard(self, taskboard: Dict[str, Any]):
        """Validate taskboard structure and fix issues"""
        
        # Ensure required fields exist
        if 'tasks' not in taskboard:
            taskboard['tasks'] = []
        
        if 'columns' not in taskboard:
            taskboard['columns'] = [
                {'id': 'todo', 'name': 'To Do', 'order': 1, 'color': '#3498db'},
                {'id': 'in_progress', 'name': 'In Progress', 'order': 2, 'color': '#f39c12'},
                {'id': 'review', 'name': 'Review', 'order': 3, 'color': '#9b59b6'},
                {'id': 'done', 'name': 'Done', 'order': 4, 'color': '#27ae60'}
            ]
        
        # Assign unique IDs if missing
        for i, task in enumerate(taskboard['tasks']):
            if 'id' not in task:
                task['id'] = str(uuid.uuid4())[:8]
            if 'column_id' not in task:
                task['column_id'] = 'todo'
    
    def _optimize_task_scheduling(self, taskboard: Dict[str, Any]):
        """Optimize task scheduling based on dependencies and priorities"""
        
        tasks = taskboard.get('tasks', [])
        
        # Sort tasks by priority and dependencies
        def task_sort_key(task):
            priority_weight = self.priority_weights.get(task.get('priority', 'medium'), 2)
            dependency_count = len(task.get('dependencies', []))
            return (-priority_weight, dependency_count)
        
        tasks.sort(key=task_sort_key)
        
        # Assign realistic due dates
        project_start = datetime.now()
        current_date = project_start
        
        for task in tasks:
            estimated_hours = task.get('estimated_hours', 4)
            # Assume 6 working hours per day
            days_needed = max(1, estimated_hours // 6)
            
            # Add buffer for high priority tasks
            if task.get('priority') == 'high':
                days_needed = int(days_needed * 1.2)
            
            current_date += timedelta(days=days_needed)
            task['due_date'] = current_date.strftime('%Y-%m-%d')
    
    def _generate_integration_data(self, taskboard: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data for external integrations"""
        
        return {
            'jira': {
                'epic_name': taskboard.get('project_info', {}).get('name', 'Project'),
                'story_points_total': sum(task.get('estimated_hours', 4) // 2 for task in taskboard.get('tasks', [])),
                'components': list(set(task.get('category', 'General') for task in taskboard.get('tasks', [])))
            },
            'trello': {
                'board_name': taskboard.get('project_info', {}).get('name', 'Project Board'),
                'lists': [col['name'] for col in taskboard.get('columns', [])],
                'labels': list(set(task.get('priority', 'medium') for task in taskboard.get('tasks', [])))
            },
            'notion': {
                'database_name': f"{taskboard.get('project_info', {}).get('name', 'Project')} Tasks",
                'properties': {
                    'title': 'title',
                    'status': 'select',
                    'priority': 'select',
                    'assignee': 'person',
                    'due_date': 'date'
                }
            }
        }
    
    def _learn_from_generation(self, brief: Dict[str, Any], taskboard: Dict[str, Any]):
        """Learn from taskboard generation to improve future results"""
        
        memory_key = f"taskboard_patterns_{datetime.now().strftime('%Y%m')}"
        current_patterns = self.get_memory(memory_key, {
            'average_task_count': 0,
            'common_categories': {},
            'project_type_patterns': {}
        })
        
        # Update task count average
        task_count = len(taskboard.get('tasks', []))
        current_patterns['average_task_count'] = (
            current_patterns['average_task_count'] * 0.8 + task_count * 0.2
        )
        
        # Track category usage
        for task in taskboard.get('tasks', []):
            category = task.get('category', 'General')
            current_patterns['common_categories'][category] = (
                current_patterns['common_categories'].get(category, 0) + 1
            )
        
        # Track project type patterns
        project_type = brief.get('project_type', 'general')
        if project_type not in current_patterns['project_type_patterns']:
            current_patterns['project_type_patterns'][project_type] = {
                'avg_tasks': task_count,
                'common_categories': [],
                'avg_duration': 0
            }
        
        self.update_memory(memory_key, current_patterns)
    
    def _fallback_generation(self, brief: Dict[str, Any], team_members: List[str], base_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback generation when AI response fails"""
        
        project_name = brief.get('project_title', 'New Project')
        
        # Convert base tasks to full task structure
        tasks = []
        for i, task in enumerate(base_tasks):
            task_id = str(uuid.uuid4())[:8]
            tasks.append({
                'id': task_id,
                'title': task['title'],
                'description': f"Task for {project_name}",
                'category': task.get('category', 'General'),
                'priority': task.get('priority', 'medium'),
                'estimated_hours': task.get('estimated_hours', 4),
                'assignee': team_members[i % len(team_members)] if team_members else 'TBD',
                'due_date': (datetime.now() + timedelta(days=(i+1)*2)).strftime('%Y-%m-%d'),
                'dependencies': [],
                'column_id': 'todo',
                'tags': [task.get('category', 'general')],
                'checklist': task.get('checklist', [])
            })
        
        return {
            'project_info': {
                'id': str(uuid.uuid4())[:8],
                'name': project_name,
                'description': brief.get('goals', {}).get('primary', 'Project description'),
                'start_date': datetime.now().strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'status': 'planning'
            },
            'columns': [
                {'id': 'todo', 'name': 'To Do', 'order': 1, 'color': '#3498db'},
                {'id': 'in_progress', 'name': 'In Progress', 'order': 2, 'color': '#f39c12'},
                {'id': 'review', 'name': 'Review', 'order': 3, 'color': '#9b59b6'},
                {'id': 'done', 'name': 'Done', 'order': 4, 'color': '#27ae60'}
            ],
            'tasks': tasks,
            'milestones': [],
            'generated_at': datetime.now().isoformat(),
            'fallback_generation': True
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            'name': 'Taskboard Generator',
            'description': 'Converts creative briefs into actionable taskboards with scheduling',
            'inputs': ['brief', 'team_members', 'preferences'],
            'outputs': ['taskboard', 'timeline', 'milestones'],
            'supported_project_types': ['website', 'branding', 'marketing', 'general'],
            'integrations': ['jira', 'trello', 'notion'],
            'features': ['dependency_management', 'priority_optimization', 'resource_allocation'],
            'version': '1.0.0'
        }
