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
