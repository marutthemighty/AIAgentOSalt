from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio
from utils.ai_client import AIClient

class BaseAgent(ABC):
    """
    Base class for all AI agents providing standard interface and common functionality
    """
    
    def __init__(self, ai_client: AIClient, agent_name: str):
        self.ai_client = ai_client
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.status = "idle"
        self.last_activity = None
        self.memory = {}  # Agent memory for learning preferences
        self.message_handlers = {}
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method that each agent must implement
        
        Args:
            input_data: Dictionary containing the input data for processing
            
        Returns:
            Dictionary containing the processed results
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return agent capabilities and configuration
        
        Returns:
            Dictionary describing agent capabilities
        """
        pass
    
    def health_check(self) -> bool:
        """
        Check if agent is healthy and responsive
        
        Returns:
            Boolean indicating agent health
        """
        try:
            # Basic health check - can be overridden by specific agents
            return self.ai_client.health_check() if self.ai_client else False
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def _safe_execute(self, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Safely execute a function with error handling and logging
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Dictionary with execution results
        """
        start_time = datetime.now()
        self.status = "processing"
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.last_activity = datetime.now()
            self.status = "idle"
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self.status = "error"
            self.logger.error(f"Execution failed: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def update_memory(self, key: str, value: Any):
        """
        Update agent memory for learning and personalization
        
        Args:
            key: Memory key
            value: Value to store
        """
        try:
            self.memory[key] = value
            self.logger.debug(f"Memory updated: {key}")
        except Exception as e:
            self.logger.error(f"Failed to update memory: {str(e)}")
    
    def get_memory(self, key: str, default: Any = None) -> Any:
        """
        Retrieve value from agent memory
        
        Args:
            key: Memory key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.memory.get(key, default)
    
    def receive_message(self, message_data: Dict[str, Any]):
        """
        Handle incoming messages from other agents
        
        Args:
            message_data: Message data from another agent
        """
        try:
            message_type = message_data.get('message', {}).get('type', 'unknown')
            
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                handler(message_data)
            else:
                self.logger.warning(f"No handler for message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
    
    def register_message_handler(self, message_type: str, handler_func):
        """
        Register a handler for specific message types
        
        Args:
            message_type: Type of message to handle
            handler_func: Function to handle the message
        """
        self.message_handlers[message_type] = handler_func
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status
        
        Returns:
            Dictionary with agent status information
        """
        return {
            'name': self.agent_name,
            'status': self.status,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'memory_size': len(self.memory),
            'capabilities': self.get_capabilities()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent performance metrics
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'status': self.status,
            'memory_usage': len(self.memory),
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'uptime': (datetime.now() - self.last_activity).total_seconds() if self.last_activity else 0
        }
    
    async def _generate_ai_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Generate AI response using the configured AI client
        
        Args:
            prompt: The prompt to send to AI
            context: Additional context for the AI
            
        Returns:
            AI-generated response
        """
        try:
            # Add agent context to prompt
            enhanced_prompt = f"""
You are {self.agent_name}, a specialized AI agent for creative workflow automation.

Context: {context if context else 'No additional context provided'}

Task: {prompt}

Please provide a detailed, actionable response that aligns with your role as {self.agent_name}.
"""
            
            response = await self.ai_client.generate_response(enhanced_prompt)
            return response
            
        except Exception as e:
            self.logger.error(f"AI response generation failed: {str(e)}")
            raise
    
    def _validate_input(self, input_data: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate input data has required fields
        
        Args:
            input_data: Input data to validate
            required_fields: List of required field names
            
        Returns:
            Boolean indicating if validation passed
        """
        try:
            for field in required_fields:
                if field not in input_data or input_data[field] is None:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Input validation error: {str(e)}")
            return False
