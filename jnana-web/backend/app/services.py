"""
Jnana Web Service Layer.

This module provides the service layer that integrates the web interface
with the core Jnana system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime


class JnanaWebService:
    """
    Service layer for integrating Jnana core system with web interface.
    
    This service manages the lifecycle of Jnana sessions and provides
    a bridge between the web API and the core Jnana functionality.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the Jnana web service.
        
        Args:
            config_path: Path to Jnana configuration file
        """
        self.config_path = config_path
        self.jnana_systems: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    async def create_session(self, research_goal: str, mode: str = 'interactive') -> Dict[str, Any]:
        """
        Create a new research session.
        
        Args:
            research_goal: The research question or goal
            mode: Session mode ('interactive', 'batch', 'hybrid')
            
        Returns:
            Dictionary containing session information
        """
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.logger.info(f"Created session {session_id} with goal: {research_goal[:100]}...")
            
            return {
                'session_id': session_id,
                'research_goal': research_goal,
                'mode': mode,
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions.
        
        Returns:
            List of session dictionaries
        """
        # For now, return empty list - will be implemented with database
        return []
    
    async def cleanup(self):
        """Clean up all active Jnana systems."""
        for session_id, jnana in self.jnana_systems.items():
            try:
                if hasattr(jnana, 'stop'):
                    await jnana.stop()
            except Exception as e:
                self.logger.error(f"Error stopping session {session_id}: {e}")
        
        self.jnana_systems.clear()
