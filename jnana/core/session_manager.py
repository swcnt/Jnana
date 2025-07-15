"""
Session management for Jnana system.

This module handles session lifecycle, persistence, and state management
for research sessions that may span multiple interactions.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging
import uuid

from ..data.unified_hypothesis import UnifiedHypothesis
from ..data.storage import JnanaStorage
from ..data.data_migration import DataMigration
from .event_manager import EventManager, EventType


class SessionState:
    """Represents the current state of a research session."""
    
    def __init__(self, session_id: str = None):
        """Initialize session state."""
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = time.time()
        self.updated_at = time.time()
        self.research_goal = ""
        self.current_mode = "interactive"  # "interactive", "batch", "hybrid"
        self.active_hypothesis_id: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        self.settings: Dict[str, Any] = {}
        
        # Session statistics
        self.stats = {
            "hypotheses_generated": 0,
            "feedback_entries": 0,
            "tournament_matches": 0,
            "agent_interactions": 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session state to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "research_goal": self.research_goal,
            "current_mode": self.current_mode,
            "active_hypothesis_id": self.active_hypothesis_id,
            "metadata": self.metadata,
            "settings": self.settings,
            "stats": self.stats
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Create session state from dictionary."""
        state = cls(data.get("session_id"))
        state.created_at = data.get("created_at", time.time())
        state.updated_at = data.get("updated_at", time.time())
        state.research_goal = data.get("research_goal", "")
        state.current_mode = data.get("current_mode", "interactive")
        state.active_hypothesis_id = data.get("active_hypothesis_id")
        state.metadata = data.get("metadata", {})
        state.settings = data.get("settings", {})
        state.stats = data.get("stats", {
            "hypotheses_generated": 0,
            "feedback_entries": 0,
            "tournament_matches": 0,
            "agent_interactions": 0
        })
        return state


class SessionManager:
    """
    Manages research sessions in the Jnana system.
    
    Handles session creation, persistence, restoration, and state management.
    """
    
    def __init__(self, storage: JnanaStorage, event_manager: EventManager):
        """
        Initialize session manager.
        
        Args:
            storage: Storage backend for persistence
            event_manager: Event manager for notifications
        """
        self.storage = storage
        self.event_manager = event_manager
        self.logger = logging.getLogger(__name__)
        
        # Current session state
        self.current_session: Optional[SessionState] = None
        self.hypotheses: List[UnifiedHypothesis] = []
        
        # Auto-save settings
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5 minutes
        self._last_save_time = time.time()
    
    async def create_session(self, research_goal: str, mode: str = "interactive",
                           settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new research session.
        
        Args:
            research_goal: The research question or goal
            mode: Session mode ("interactive", "batch", "hybrid")
            settings: Optional session settings
            
        Returns:
            Session ID
        """
        self.current_session = SessionState()
        self.current_session.research_goal = research_goal
        self.current_session.current_mode = mode
        self.current_session.settings = settings or {}
        
        self.hypotheses = []
        
        # Publish session started event
        await self.event_manager.publish(
            EventType.SESSION_STARTED,
            source="session_manager",
            data={
                "session_id": self.current_session.session_id,
                "research_goal": research_goal,
                "mode": mode
            }
        )
        
        self.logger.info(f"Created new session: {self.current_session.session_id}")
        return self.current_session.session_id
    
    async def load_session(self, session_path: Union[str, Path]) -> str:
        """
        Load a session from file.
        
        Args:
            session_path: Path to session file
            
        Returns:
            Session ID
        """
        session_path = Path(session_path)

        self.logger.info(f"Attempting to read session from filepath {session_path}") 
        
        if not session_path.exists():
            raise FileNotFoundError(f"Session file not found: {session_path}")
        
        # Determine file format and load accordingly
        if session_path.suffix == '.json':
            await self._load_json_session(session_path)
        else:
            raise ValueError(f"Unsupported session file format: {session_path.suffix}")
        
        # Publish session loaded event
        await self.event_manager.publish(
            EventType.SESSION_LOADED,
            source="session_manager",
            data={
                "session_id": self.current_session.session_id,
                "session_path": str(session_path),
                "hypotheses_count": len(self.hypotheses)
            }
        )
        
        self.logger.info(f"Loaded session: {self.current_session.session_id}")
        return self.current_session.session_id
    
    async def _load_json_session(self, session_path: Path):
        """Load session from JSON file."""
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Check if it's a Jnana session or needs migration
        format_version = session_data.get("format_version", "unknown")
        
        if format_version.startswith("jnana"):
            # Native Jnana format
            self.current_session = SessionState.from_dict(session_data.get("session_state", {}))
            hypotheses_data = session_data.get("hypotheses", [])
            self.hypotheses = [UnifiedHypothesis.from_dict(h) for h in hypotheses_data]
        
        elif "hypotheses" in session_data and isinstance(session_data["hypotheses"], list):
            # Try to detect format and migrate
            if self._looks_like_wisteria(session_data):
                self.hypotheses = DataMigration.load_wisteria_session(session_path)
            elif self._looks_like_protognosis(session_data):
                self.hypotheses = DataMigration.load_protognosis_session(session_path)
            else:
                raise ValueError("Unknown session format")
            
            # Create new session state
            self.current_session = SessionState()
            self.current_session.research_goal = session_data.get("metadata", {}).get("research_goal", "")
            
        else:
            raise ValueError("Invalid session file format")
    
    def _looks_like_wisteria(self, session_data: Dict[str, Any]) -> bool:
        """Check if session data looks like Wisteria format."""
        hypotheses = session_data.get("hypotheses", [])
        if not hypotheses:
            return False
        
        first_hyp = hypotheses[0]
        return (isinstance(first_hyp, dict) and 
                "title" in first_hyp and 
                "description" in first_hyp and
                "hallmarks" in first_hyp)
    
    def _looks_like_protognosis(self, session_data: Dict[str, Any]) -> bool:
        """Check if session data looks like ProtoGnosis format."""
        hypotheses = session_data.get("hypotheses", [])
        if not hypotheses:
            return False
        
        first_hyp = hypotheses[0]
        return (isinstance(first_hyp, dict) and 
                "hypothesis_id" in first_hyp and 
                "content" in first_hyp and
                "tournament_record" in first_hyp)
    
    async def save_session(self, output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Save the current session.
        
        Args:
            output_path: Optional path to save to
            
        Returns:
            Path where session was saved
        """
        if not self.current_session:
            raise ValueError("No active session to save")
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jnana_session_{timestamp}.json"
            output_path = Path("sessions") / filename
        else:
            output_path = Path(output_path)
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update session state
        self.current_session.updated_at = time.time()
        self.current_session.stats["hypotheses_generated"] = len(self.hypotheses)
        
        # Prepare session data
        session_data = {
            "format_version": "jnana-1.0",
            "saved_at": datetime.now().isoformat(),
            "session_state": self.current_session.to_dict(),
            "hypotheses": [h.to_dict() for h in self.hypotheses]
        }
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        self._last_save_time = time.time()
        
        # Publish session saved event
        await self.event_manager.publish(
            EventType.SESSION_SAVED,
            source="session_manager",
            data={
                "session_id": self.current_session.session_id,
                "output_path": str(output_path),
                "hypotheses_count": len(self.hypotheses)
            }
        )
        
        self.logger.info(f"Saved session to: {output_path}")
        return output_path
    
    async def add_hypothesis(self, hypothesis: UnifiedHypothesis):
        """Add a hypothesis to the current session."""
        if not self.current_session:
            raise ValueError("No active session")
        
        self.hypotheses.append(hypothesis)
        self.current_session.updated_at = time.time()
        
        # Update statistics
        self.current_session.stats["hypotheses_generated"] = len(self.hypotheses)
        
        # Auto-save if enabled
        if self.auto_save_enabled:
            await self._check_auto_save()
    
    async def update_hypothesis(self, hypothesis: UnifiedHypothesis):
        """Update an existing hypothesis in the session."""
        if not self.current_session:
            raise ValueError("No active session")
        
        # Find and update the hypothesis
        for i, existing in enumerate(self.hypotheses):
            if existing.hypothesis_id == hypothesis.hypothesis_id:
                self.hypotheses[i] = hypothesis
                self.current_session.updated_at = time.time()
                break
        else:
            # Hypothesis not found, add it
            await self.add_hypothesis(hypothesis)
        
        # Auto-save if enabled
        if self.auto_save_enabled:
            await self._check_auto_save()
    
    async def remove_hypothesis(self, hypothesis_id: str) -> bool:
        """Remove a hypothesis from the session."""
        if not self.current_session:
            raise ValueError("No active session")
        
        original_count = len(self.hypotheses)
        self.hypotheses = [h for h in self.hypotheses if h.hypothesis_id != hypothesis_id]
        
        if len(self.hypotheses) < original_count:
            self.current_session.updated_at = time.time()
            self.current_session.stats["hypotheses_generated"] = len(self.hypotheses)
            
            # Auto-save if enabled
            if self.auto_save_enabled:
                await self._check_auto_save()
            
            return True
        
        return False
    
    def get_hypothesis(self, hypothesis_id: str) -> Optional[UnifiedHypothesis]:
        """Get a specific hypothesis by ID."""
        for hypothesis in self.hypotheses:
            if hypothesis.hypothesis_id == hypothesis_id:
                return hypothesis
        return None
    
    def get_all_hypotheses(self) -> List[UnifiedHypothesis]:
        """Get all hypotheses in the current session."""
        return self.hypotheses.copy()
    
    def set_active_hypothesis(self, hypothesis_id: str):
        """Set the currently active hypothesis."""
        if self.current_session:
            self.current_session.active_hypothesis_id = hypothesis_id
            self.current_session.updated_at = time.time()
    
    def get_active_hypothesis(self) -> Optional[UnifiedHypothesis]:
        """Get the currently active hypothesis."""
        if not self.current_session or not self.current_session.active_hypothesis_id:
            return None
        
        return self.get_hypothesis(self.current_session.active_hypothesis_id)
    
    async def _check_auto_save(self):
        """Check if auto-save should be triggered."""
        current_time = time.time()
        if current_time - self._last_save_time >= self.auto_save_interval:
            try:
                await self.save_session()
            except Exception as e:
                self.logger.error(f"Auto-save failed: {e}")
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current session."""
        if not self.current_session:
            return None
        
        return {
            "session_id": self.current_session.session_id,
            "research_goal": self.current_session.research_goal,
            "mode": self.current_session.current_mode,
            "created_at": datetime.fromtimestamp(self.current_session.created_at).isoformat(),
            "updated_at": datetime.fromtimestamp(self.current_session.updated_at).isoformat(),
            "hypotheses_count": len(self.hypotheses),
            "active_hypothesis_id": self.current_session.active_hypothesis_id,
            "stats": self.current_session.stats
        }
