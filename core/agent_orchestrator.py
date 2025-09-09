import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from utils.ai_client import AIClient
from utils.config import Config

# Import all agents
from agents.meeting_notes_processor import MeetingNotesProcessor
from agents.creative_brief_parser import CreativeBriefParser
from agents.taskboard_generator import TaskboardGenerator
from agents.branding_generator import BrandingGenerator
from agents.proposal_generator import ProposalGenerator
from agents.content_plan_generator import ContentPlanGenerator
from agents.asset_validator import AssetValidator
from agents.client_portal_assistant import ClientPortalAssistant
from agents.deliverables_packager import DeliverablesPackager
from agents.analytics_estimator import AnalyticsEstimator
from agents.workflow_optimizer import WorkflowOptimizer
from agents.sentiment_analyzer import SentimentAnalyzer

class AgentOrchestrator:
    """
    Central orchestrator for managing all AI agents and their interactions
    """
    
    def __init__(self):
        self.config = Config()
        self.ai_client = AIClient()
        self.agents = {}
        self.message_queue = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize all agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all 12 AI agents"""
        try:
            self.agents = {
                'meeting_notes_processor': MeetingNotesProcessor(self.ai_client),
                'creative_brief_parser': CreativeBriefParser(self.ai_client),
                'taskboard_generator': TaskboardGenerator(self.ai_client),
                'branding_generator': BrandingGenerator(self.ai_client),
                'proposal_generator': ProposalGenerator(self.ai_client),
                'content_plan_generator': ContentPlanGenerator(self.ai_client),
                'asset_validator': AssetValidator(self.ai_client),
                'client_portal_assistant': ClientPortalAssistant(self.ai_client),
                'deliverables_packager': DeliverablesPackager(self.ai_client),
                'analytics_estimator': AnalyticsEstimator(self.ai_client),
                'workflow_optimizer': WorkflowOptimizer(self.ai_client),
                'sentiment_analyzer': SentimentAnalyzer(self.ai_client)
            }
            self.logger.info("All agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")
            raise
    
    def get_agent(self, agent_name: str):
        """Get a specific agent by name"""
        return self.agents.get(agent_name)
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        status = {}
        for name, agent in self.agents.items():
            try:
                # Check if agent is responsive
                health = agent.health_check()
                status[name] = "active" if health else "error"
            except Exception:
                status[name] = "error"
        return status
    
    async def execute_agent_task(self, agent_name: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using a specific agent"""
        try:
            agent = self.get_agent(agent_name)
            if not agent:
                raise ValueError(f"Agent '{agent_name}' not found")
            
            # Add metadata to task
            task_data['timestamp'] = datetime.now().isoformat()
            task_data['request_id'] = self._generate_request_id()
            
            # Execute the task
            result = await agent.process(task_data)
            
            # Log the execution
            self._log_agent_execution(agent_name, task_data, result)
            
            return {
                'success': True,
                'agent': agent_name,
                'result': result,
                'timestamp': task_data['timestamp'],
                'request_id': task_data['request_id']
            }
            
        except Exception as e:
            self.logger.error(f"Error executing task for agent {agent_name}: {str(e)}")
            return {
                'success': False,
                'agent': agent_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def route_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """Route messages between agents"""
        try:
            message_data = {
                'from': from_agent,
                'to': to_agent,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'id': self._generate_request_id()
            }
            
            self.message_queue.append(message_data)
            self.logger.info(f"Message routed from {from_agent} to {to_agent}")
            
            # Process message immediately if recipient agent exists
            if to_agent in self.agents:
                recipient_agent = self.agents[to_agent]
                if hasattr(recipient_agent, 'receive_message'):
                    recipient_agent.receive_message(message_data)
            
        except Exception as e:
            self.logger.error(f"Error routing message: {str(e)}")
    
    async def execute_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a multi-agent workflow"""
        try:
            workflow_id = self._generate_request_id()
            results = {}
            
            for step in workflow_definition.get('steps', []):
                agent_name = step.get('agent')
                task_data = step.get('data', {})
                
                # Add previous results to context if specified
                if step.get('use_previous_results'):
                    task_data['previous_results'] = results
                
                # Execute the step
                step_result = await self.execute_agent_task(agent_name, task_data)
                results[agent_name] = step_result
                
                # Check if step failed and handle according to workflow config
                if not step_result.get('success') and workflow_definition.get('stop_on_error', True):
                    break
            
            return {
                'workflow_id': workflow_id,
                'success': True,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing workflow: {str(e)}")
            return {
                'workflow_id': workflow_id,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_ai_service(self) -> bool:
        """Check if AI service is available"""
        try:
            return self.ai_client.health_check()
        except Exception:
            return False
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            metrics = {
                'agents_count': len(self.agents),
                'active_agents': len([a for a in self.get_agent_status().values() if a == 'active']),
                'message_queue_size': len(self.message_queue),
                'ai_service_status': self.check_ai_service(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add agent-specific metrics
            for name, agent in self.agents.items():
                if hasattr(agent, 'get_metrics'):
                    metrics[f'{name}_metrics'] = agent.get_metrics()
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            return {}
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def process_with_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input using specified agent with comprehensive error handling"""
        start_time = datetime.now()
        
        try:
            # Validate agent exists
            if agent_name not in self.agents:
                error_msg = f"Agent '{agent_name}' not found. Available agents: {list(self.agents.keys())}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_type': 'agent_not_found',
                    'agent': agent_name,
                    'suggestions': self._suggest_similar_agents(agent_name)
                }
            
            # Validate input data
            if not input_data:
                self.logger.warning(f"Empty input data provided to agent {agent_name}")
                input_data = {}
            
            agent = self.agents[agent_name]
            
            # Check if agent is healthy/available
            if hasattr(agent, 'is_available') and not agent.is_available():
                error_msg = f"Agent '{agent_name}' is currently unavailable"
                self.logger.warning(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'error_type': 'agent_unavailable',
                    'agent': agent_name,
                    'retry_suggestion': 'Please try again in a few moments'
                }
            
            # Process with the agent
            result = agent.process(input_data)
            
            # Log successful execution
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            try:
                if hasattr(self, 'db_manager'):
                    self.db_manager.log_agent_execution({
                        'agent_name': agent_name,
                        'action': 'process',
                        'input_data': input_data,
                        'output_data': result,
                        'success': True,
                        'execution_time': int(execution_time)
                    })
            except Exception as db_error:
                self.logger.warning(f"Failed to log execution to database: {str(db_error)}")
            
            return {
                'success': True,
                'result': result,
                'agent': agent_name,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            # Log failed execution with detailed error info
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = str(e)
            error_type = type(e).__name__
            
            try:
                if hasattr(self, 'db_manager'):
                    self.db_manager.log_agent_execution({
                        'agent_name': agent_name,
                        'action': 'process',
                        'input_data': input_data,
                        'output_data': None,
                        'success': False,
                        'error_message': error_msg,
                        'execution_time': int(execution_time)
                    })
            except Exception:
                pass  # Don't fail on logging errors
            
            self.logger.error(f"Error in agent {agent_name}: {error_msg}")
            
            # Provide user-friendly error messages
            user_friendly_error = self._get_user_friendly_error(error_type, error_msg)
            
            return {
                'success': False,
                'error': user_friendly_error,
                'error_type': error_type,
                'technical_error': error_msg,
                'agent': agent_name,
                'execution_time': execution_time,
                'suggestions': self._get_error_suggestions(error_type, agent_name)
            }
    
    def _suggest_similar_agents(self, agent_name: str) -> List[str]:
        """Suggest similar agent names in case of typos"""
        available_agents = list(self.agents.keys())
        suggestions = []
        
        # Simple similarity check
        for available in available_agents:
            if agent_name.lower() in available.lower() or available.lower() in agent_name.lower():
                suggestions.append(available)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _get_user_friendly_error(self, error_type: str, error_msg: str) -> str:
        """Convert technical errors to user-friendly messages"""
        error_mappings = {
            'APIError': 'There was an issue with the AI service. Please try again.',
            'ConnectionError': 'Unable to connect to external services. Please check your internet connection.',
            'ValidationError': 'The input provided is not valid. Please check your data and try again.',
            'TimeoutError': 'The operation took too long to complete. Please try again with simpler input.',
            'PermissionError': 'Permission denied. Please check your access rights.',
            'JSONDecodeError': 'Invalid data format received. Please try again.',
            'KeyError': 'Required information is missing from the input.',
        }
        
        for error_pattern, friendly_msg in error_mappings.items():
            if error_pattern in error_type:
                return friendly_msg
        
        # Generic fallback
        return 'An unexpected error occurred. Please try again or contact support if the issue persists.'
    
    def _get_error_suggestions(self, error_type: str, agent_name: str) -> List[str]:
        """Get suggestions for resolving specific errors"""
        suggestions = []
        
        if 'API' in error_type or 'Connection' in error_type:
            suggestions.extend([
                'Check your internet connection',
                'Verify API keys are set correctly',
                'Try again in a few moments'
            ])
        elif 'Validation' in error_type or 'Key' in error_type:
            suggestions.extend([
                'Check that all required fields are filled',
                'Verify the input format is correct',
                'Review the example data format'
            ])
        elif 'Timeout' in error_type:
            suggestions.extend([
                'Try with shorter or simpler input',
                'Break large requests into smaller parts',
                'Check system performance and try again'
            ])
        
        return suggestions

    def _log_agent_execution(self, agent_name: str, task_data: Dict, result: Dict):
        """Log agent execution for monitoring"""
        log_entry = {
            'agent': agent_name,
            'task_type': task_data.get('type', 'unknown'),
            'success': result.get('success', False),
            'timestamp': datetime.now().isoformat(),
            'execution_time': result.get('execution_time', 0)
        }
        
        self.logger.info(f"Agent execution logged: {json.dumps(log_entry)}")
