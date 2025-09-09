import os
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
import json

class AIClient:
    """
    Centralized AI client for interacting with Gemini API
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            self.logger.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.client = genai
                self.logger.info("Gemini AI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client: {str(e)}")
                self.client = None
        
        # Default model configuration
        self.default_model = "gemini-2.5-flash"
        self.fallback_model = "gemini-2.5-pro"
        
        # Request settings
        self.max_retries = 3
        self.timeout = 30
    
    def generate_response(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        Generate AI response for given prompt
        
        Args:
            prompt: The input prompt
            model: Model to use (defaults to default_model)
            **kwargs: Additional parameters
            
        Returns:
            Generated response as string
        """
        if not self.client:
            raise Exception("AI client not initialized. Check GEMINI_API_KEY.")
        
        model_name = model or self.default_model
        
        try:
            model = self.client.GenerativeModel(model_name)
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get('temperature', 0.7),
                max_output_tokens=kwargs.get('max_tokens', 4000),
                top_p=kwargs.get('top_p', 0.95)
            )
            response = model.generate_content(prompt, generation_config=generation_config)
            
            if response and response.text:
                return response.text
            else:
                raise Exception("Empty response from AI model")
                
        except Exception as e:
            self.logger.error(f"Error generating AI response: {str(e)}")
            
            # Try fallback model if primary fails
            if model_name != self.fallback_model:
                self.logger.info(f"Retrying with fallback model: {self.fallback_model}")
                try:
                    return self.generate_response(prompt, self.fallback_model, **kwargs)
                except Exception as fallback_error:
                    self.logger.error(f"Fallback model also failed: {str(fallback_error)}")
            
            raise Exception(f"AI response generation failed: {str(e)}")
    
    def generate_structured_response(self, prompt: str, response_schema = None, model: str = None) -> Dict[str, Any]:
        """
        Generate structured JSON response
        
        Args:
            prompt: The input prompt
            response_schema: Pydantic model for response validation
            model: Model to use
            
        Returns:
            Parsed JSON response
        """
        if not self.client:
            raise Exception("AI client not initialized. Check GEMINI_API_KEY.")
        
        model_name = model or self.default_model
        
        try:
            model = self.client.GenerativeModel(model_name)
            generation_config = genai.types.GenerationConfig(
                temperature=0.3  # Lower temperature for structured output
            )
            
            # Add JSON instruction to prompt
            json_prompt = f"{prompt}\n\nPlease respond with valid JSON format."
            response = model.generate_content(json_prompt, generation_config=generation_config)
            
            if response and response.text:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON response: {str(e)}")
                    # Try to extract JSON from response
                    return self._extract_json_from_text(response.text)
            else:
                raise Exception("Empty response from AI model")
                
        except Exception as e:
            self.logger.error(f"Error generating structured AI response: {str(e)}")
            raise Exception(f"Structured AI response generation failed: {str(e)}")
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Attempt to extract JSON from text response
        """
        try:
            # Look for JSON-like patterns
            import re
            
            # Find content between { and }
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback: return text in error format
            return {"error": "Could not parse JSON", "raw_response": text}
            
        except Exception as e:
            self.logger.error(f"Failed to extract JSON from text: {str(e)}")
            return {"error": "JSON extraction failed", "raw_response": text}
    
    def analyze_image(self, image_path: str, prompt: str = None) -> str:
        """
        Analyze image with AI
        
        Args:
            image_path: Path to image file
            prompt: Optional analysis prompt
            
        Returns:
            Analysis result
        """
        if not self.client:
            raise Exception("AI client not initialized. Check GEMINI_API_KEY.")
        
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                
            analysis_prompt = prompt or "Analyze this image in detail and describe its key elements, context, and any notable aspects."
            
            # Create PIL Image for Gemini
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_bytes))
            
            model = self.client.GenerativeModel("gemini-1.5-pro")  # Use pro model for image analysis
            response = model.generate_content([analysis_prompt, image])
            
            return response.text if response.text else "No analysis available"
            
        except Exception as e:
            self.logger.error(f"Error analyzing image: {str(e)}")
            raise Exception(f"Image analysis failed: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Check if AI service is available
        
        Returns:
            True if service is healthy, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Simple test request
            model = self.client.GenerativeModel(self.default_model)
            response = model.generate_content("Hello")
            return bool(response and response.text)
            
        except Exception as e:
            self.logger.error(f"AI health check failed: {str(e)}")
            return False
    
    def get_available_models(self) -> list:
        """
        Get list of available models
        
        Returns:
            List of available model names
        """
        try:
            if not self.client:
                return []
            
            # For Gemini, return known available models
            return [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting available models: {str(e)}")
            return []
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4
    
    def get_model_limits(self, model: str = None) -> Dict[str, Any]:
        """
        Get model limitations and capabilities
        
        Args:
            model: Model name
            
        Returns:
            Dictionary with model limits
        """
        model_name = model or self.default_model
        
        # Known limits for Gemini models
        limits = {
            "gemini-2.5-flash": {
                "max_input_tokens": 1000000,
                "max_output_tokens": 8192,
                "rate_limit_rpm": 15,
                "rate_limit_tpm": 1000000,
                "rate_limit_rpd": 1500
            },
            "gemini-2.5-pro": {
                "max_input_tokens": 2000000,
                "max_output_tokens": 8192,
                "rate_limit_rpm": 2,
                "rate_limit_tpm": 32000,
                "rate_limit_rpd": 50
            },
            "gemini-1.5-flash": {
                "max_input_tokens": 1000000,
                "max_output_tokens": 8192,
                "rate_limit_rpm": 15,
                "rate_limit_tpm": 1000000,
                "rate_limit_rpd": 1500
            },
            "gemini-1.5-pro": {
                "max_input_tokens": 2000000,
                "max_output_tokens": 8192,
                "rate_limit_rpm": 2,
                "rate_limit_tpm": 32000,
                "rate_limit_rpd": 50
            }
        }
        
        return limits.get(model_name, limits["gemini-2.5-flash"])
    
    def batch_generate(self, prompts: list, model: str = None, **kwargs) -> list:
        """
        Generate responses for multiple prompts
        
        Args:
            prompts: List of prompts
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            List of responses
        """
        responses = []
        
        for prompt in prompts:
            try:
                response = self.generate_response(prompt, model, **kwargs)
                responses.append(response)
            except Exception as e:
                self.logger.error(f"Error in batch generation for prompt: {str(e)}")
                responses.append(f"Error: {str(e)}")
        
        return responses
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics (placeholder for future implementation)
        
        Returns:
            Dictionary with usage stats
        """
        return {
            "requests_made": "Not available",
            "tokens_used": "Not available",
            "rate_limit_remaining": "Not available",
            "last_request_time": "Not available"
        }
