"""
LangSmith integration for observability and monitoring.
Provides tracing, logging, and evaluation capabilities for the agent.
"""

import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from config.settings import settings


logger = logging.getLogger(__name__)


class LangSmithService:
    """
    Service for LangSmith integration.
    Handles tracing, logging, and monitoring of agent interactions.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_name: Optional[str] = None,
        tracing_enabled: bool = True
    ):
        """Initialize LangSmith service."""
        self.api_key = api_key or settings.langsmith_api_key
        self.project_name = project_name or settings.langsmith_project_name
        self.tracing_enabled = tracing_enabled and settings.langsmith_tracing_enabled
        
        if self.api_key and self.tracing_enabled:
            self._setup_langsmith()
        else:
            logger.info("LangSmith not configured or disabled")
    
    def _setup_langsmith(self):
        """Setup LangSmith environment variables and tracing."""
        try:
            if not self.api_key:
                raise ValueError("LangSmith API key is required for tracing")
            # Set environment variables for LangSmith
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.api_key
            os.environ["LANGCHAIN_PROJECT"] = self.project_name
            
            logger.info(f"LangSmith tracing enabled for project: {self.project_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup LangSmith: {e}")
            self.tracing_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled."""
        return self.tracing_enabled and self.api_key is not None
    
    def log_conversation(
        self,
        user_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a conversation turn to LangSmith.
        
        Args:
            user_id: User identifier
            user_message: User's input message
            agent_response: Agent's response
            metadata: Additional metadata for logging
        """
        if not self.is_enabled():
            return
        
        try:
            # Import LangSmith client here to avoid import errors if not available
            from langsmith import Client
            
            client = Client(api_key=self.api_key)
            
            # Create a run for this conversation turn
            run_data = {
                "name": "conversation_turn",
                "inputs": {
                    "user_id": user_id,
                    "user_message": user_message
                },
                "outputs": {
                    "agent_response": agent_response
                },
                "tags": ["kavak-agent", "conversation"],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    **(metadata or {})
                }
            }
            
            # Log to LangSmith
            client.create_run(**run_data)
            
            logger.debug(f"Logged conversation to LangSmith for user {user_id}")
            
        except ImportError:
            logger.warning("LangSmith client not available")
        except Exception as e:
            logger.error(f"Error logging to LangSmith: {e}")
    
    def log_tool_usage(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        user_id: str,
        execution_time: Optional[float] = None
    ):
        """
        Log tool usage to LangSmith.
        
        Args:
            tool_name: Name of the tool used
            inputs: Tool input parameters
            outputs: Tool outputs
            user_id: User identifier
            execution_time: Tool execution time in seconds
        """
        if not self.is_enabled():
            return
        
        try:
            from langsmith import Client
            
            client = Client(api_key=self.api_key)
            
            run_data = {
                "name": f"tool_usage_{tool_name}",
                "inputs": inputs,
                "outputs": outputs,
                "tags": ["kavak-agent", "tool-usage", tool_name],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    "tool_name": tool_name,
                    "execution_time": execution_time
                }
            }
            
            client.create_run(**run_data)
            
            logger.debug(f"Logged tool usage to LangSmith: {tool_name}")
            
        except Exception as e:
            logger.error(f"Error logging tool usage to LangSmith: {e}")
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log errors to LangSmith.
        
        Args:
            error_type: Type of error
            error_message: Error message
            user_id: User identifier
            context: Additional context information
        """
        if not self.is_enabled():
            return
        
        try:
            from langsmith import Client
            
            client = Client(api_key=self.api_key)
            
            run_data = {
                "name": "error_log",
                "inputs": {
                    "error_type": error_type,
                    "user_id": user_id
                },
                "outputs": {
                    "error_message": error_message
                },
                "tags": ["kavak-agent", "error", error_type],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    "error_type": error_type,
                    **(context or {})
                }
            }
            
            client.create_run(**run_data)
            
            logger.debug(f"Logged error to LangSmith: {error_type}")
            
        except Exception as e:
            logger.error(f"Error logging error to LangSmith: {e}")
    
    def create_dataset(
        self,
        dataset_name: str,
        description: str,
        examples: List[Dict[str, Any]]
    ):
        """
        Create a dataset for evaluation.
        
        Args:
            dataset_name: Name of the dataset
            description: Dataset description
            examples: List of example data
        """
        if not self.is_enabled():
            logger.warning("Cannot create dataset - LangSmith not enabled")
            return
        
        try:
            from langsmith import Client
            
            client = Client(api_key=self.api_key)
            
            # Create dataset
            dataset = client.create_dataset(
                dataset_name=dataset_name,
                description=description
            )
            
            # Add examples to dataset
            for example in examples:
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=example.get("inputs", {}),
                    outputs=example.get("outputs", {}),
                    metadata=example.get("metadata", {})
                )
            
            logger.info(f"Created LangSmith dataset: {dataset_name}")
            return dataset
            
        except Exception as e:
            logger.error(f"Error creating LangSmith dataset: {e}")
    
    def get_project_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current project.
        
        Returns:
            Dictionary with project statistics
        """
        if not self.is_enabled():
            return {"error": "LangSmith not enabled"}
        
        try:
            from langsmith import Client
            
            client = Client(api_key=self.api_key)
            
            # Get runs for the project
            runs = list(client.list_runs(project_name=self.project_name, limit=100))
            
            stats = {
                "total_runs": len(runs),
                "project_name": self.project_name,
                "recent_runs": len([r for r in runs if r.start_time and 
                                 (datetime.now() - r.start_time).days < 7])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting project stats: {e}")
            return {"error": str(e)}


# Global LangSmith service instance
langsmith_service = LangSmithService()