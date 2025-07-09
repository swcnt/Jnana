"""
Main Jnana system class.

This module provides the core Jnana system that integrates Wisteria's
interactive capabilities with ProtoGnosis's multi-agent processing.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .model_manager import UnifiedModelManager
from .session_manager import SessionManager
from .event_manager import EventManager, EventType
from ..data.storage import JnanaStorage
from ..data.unified_hypothesis import UnifiedHypothesis
from ..ui.interactive_interface import InteractiveInterface

# Import ProtoGnosis components if available
try:
    from coscientist import CoScientist
    PROTOGNOSIS_AVAILABLE = True
except ImportError:
    PROTOGNOSIS_AVAILABLE = False
    CoScientist = None


class JnanaSystem:
    """
    Main Jnana system that integrates interactive hypothesis generation
    with scalable multi-agent processing.
    """
    
    def __init__(self, config_path: Union[str, Path] = "config/models.yaml",
                 storage_path: Union[str, Path] = "data/jnana.db",
                 storage_type: str = "json",
                 max_workers: int = 4,
                 output_path: Optional[Union[str, Path]] = None,
                 enable_ui: bool = True):
        """
        Initialize the Jnana system.
        
        Args:
            config_path: Path to model configuration file
            storage_path: Path to storage location
            storage_type: Type of storage ("json", "sqlite")
            max_workers: Maximum number of concurrent workers
            output_path: Optional output path for session files
            enable_ui: Whether to enable the interactive UI
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.model_manager = UnifiedModelManager(config_path)
        self.event_manager = EventManager()
        self.storage = JnanaStorage(storage_path, storage_type)
        self.session_manager = SessionManager(self.storage, self.event_manager)
        
        # Configuration
        self.max_workers = max_workers
        self.output_path = Path(output_path) if output_path else None
        self.enable_ui = enable_ui
        
        # System state
        self.running = False
        self.current_mode = "interactive"
        
        # UI component
        self.ui: Optional[InteractiveInterface] = None
        if enable_ui:
            self.ui = InteractiveInterface(self.event_manager, self.session_manager)
        
        # ProtoGnosis integration
        self.coscientist: Optional[CoScientist] = None
        if PROTOGNOSIS_AVAILABLE:
            self._initialize_protognosis()
        
        self.logger.info("Jnana system initialized")
    
    def _initialize_protognosis(self):
        """Initialize ProtoGnosis CoScientist if available."""
        try:
            self.coscientist = CoScientist(
                llm_config=self.model_manager.agent_llm_config,
                storage_path=str(self.storage.storage_path),
                max_workers=self.max_workers
            )
            self.logger.info("ProtoGnosis integration initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize ProtoGnosis: {e}")
            self.coscientist = None
    
    async def start(self):
        """Start the Jnana system."""
        if self.running:
            return
        
        self.running = True
        
        # Start event manager
        await self.event_manager.start()
        
        # Start ProtoGnosis if available
        if self.coscientist:
            self.coscientist.start()
        
        self.logger.info("Jnana system started")
    
    async def stop(self):
        """Stop the Jnana system."""
        if not self.running:
            return
        
        self.running = False
        
        # Stop event manager
        await self.event_manager.stop()
        
        # Stop ProtoGnosis if running
        if self.coscientist:
            self.coscientist.stop()
        
        self.logger.info("Jnana system stopped")
    
    async def set_research_goal(self, research_goal: str) -> str:
        """
        Set the research goal and create a new session.
        
        Args:
            research_goal: The research question or goal
            
        Returns:
            Session ID
        """
        session_id = await self.session_manager.create_session(
            research_goal=research_goal,
            mode=self.current_mode
        )
        
        # Set research goal in ProtoGnosis if available
        if self.coscientist:
            self.coscientist.set_research_goal(research_goal)
        
        self.logger.info(f"Research goal set: {research_goal[:100]}...")
        return session_id
    
    async def resume_session(self, session_path: Union[str, Path]) -> str:
        """
        Resume a previous session.
        
        Args:
            session_path: Path to session file
            
        Returns:
            Session ID
        """
        session_id = await self.session_manager.load_session(session_path)
        
        # Get session info and set research goal in ProtoGnosis
        session_info = self.session_manager.get_session_info()
        if session_info and self.coscientist:
            research_goal = session_info.get("research_goal", "")
            if research_goal:
                self.coscientist.set_research_goal(research_goal)
        
        self.logger.info(f"Session resumed: {session_id}")
        return session_id
    
    async def run_interactive_mode(self, model_override: Optional[str] = None):
        """
        Run in interactive mode with real-time user interaction.
        
        Args:
            model_override: Optional model to use instead of default
        """
        if not self.ui:
            raise ValueError("UI not enabled for interactive mode")
        
        self.current_mode = "interactive"
        
        # Get model configuration
        if model_override:
            # TODO: Handle model override
            pass
        
        model_config = self.model_manager.get_interactive_model()
        
        # Start the interactive interface
        await self.ui.start_interactive_session(model_config)
    
    async def run_batch_mode(self, hypothesis_count: int = 5,
                           strategies: Optional[List[str]] = None,
                           tournament_matches: int = 25):
        """
        Run in batch mode for large-scale hypothesis generation.
        
        Args:
            hypothesis_count: Number of hypotheses to generate
            strategies: Generation strategies to use
            tournament_matches: Number of tournament matches for ranking
        """
        if not self.coscientist:
            raise ValueError("ProtoGnosis not available for batch mode")
        
        self.current_mode = "batch"
        
        # Generate hypotheses
        self.logger.info(f"Generating {hypothesis_count} hypotheses...")
        hypothesis_ids = self.coscientist.generate_hypotheses(
            count=hypothesis_count,
            strategies=strategies
        )
        
        # Wait for completion
        self.coscientist.wait_for_completion()
        
        # Run tournament evaluation
        self.logger.info(f"Running tournament with {tournament_matches} matches...")
        self.coscientist.run_tournament(match_count=tournament_matches)
        self.coscientist.wait_for_completion()
        
        # Convert and store results
        await self._import_protognosis_results()
        
        # Save session
        if self.output_path:
            await self.session_manager.save_session(self.output_path)
        else:
            await self.session_manager.save_session()
    
    async def run_hybrid_mode(self, hypothesis_count: int = 5,
                            strategies: Optional[List[str]] = None,
                            interactive_refinement: bool = True,
                            tournament_matches: int = 25):
        """
        Run in hybrid mode combining batch generation with interactive refinement.
        
        Args:
            hypothesis_count: Number of initial hypotheses to generate
            strategies: Generation strategies to use
            interactive_refinement: Whether to allow interactive refinement
            tournament_matches: Number of tournament matches for ranking
        """
        if not self.coscientist:
            raise ValueError("ProtoGnosis not available for hybrid mode")
        
        if not self.ui:
            raise ValueError("UI not enabled for hybrid mode")
        
        self.current_mode = "hybrid"
        
        # Phase 1: Batch generation
        self.logger.info("Phase 1: Batch hypothesis generation")
        hypothesis_ids = self.coscientist.generate_hypotheses(
            count=hypothesis_count,
            strategies=strategies
        )
        self.coscientist.wait_for_completion()
        
        # Import initial results
        await self._import_protognosis_results()
        
        # Phase 2: Interactive refinement (if enabled)
        if interactive_refinement:
            self.logger.info("Phase 2: Interactive refinement")
            await self.ui.start_refinement_session()
        
        # Phase 3: Final tournament
        self.logger.info("Phase 3: Final tournament evaluation")
        self.coscientist.run_tournament(match_count=tournament_matches)
        self.coscientist.wait_for_completion()
        
        # Import final results
        await self._import_protognosis_results()
        
        # Save session
        if self.output_path:
            await self.session_manager.save_session(self.output_path)
        else:
            await self.session_manager.save_session()
    
    async def _import_protognosis_results(self):
        """Import results from ProtoGnosis into the session."""
        if not self.coscientist:
            return
        
        # Get hypotheses from ProtoGnosis
        protognosis_hypotheses = self.coscientist.get_all_hypotheses()
        
        # Convert to unified format and add to session
        for pg_hypothesis in protognosis_hypotheses:
            unified_hypothesis = self._convert_protognosis_hypothesis(pg_hypothesis)
            await self.session_manager.update_hypothesis(unified_hypothesis)
    
    def _convert_protognosis_hypothesis(self, pg_hypothesis) -> UnifiedHypothesis:
        """Convert ProtoGnosis hypothesis to unified format."""
        # This would use the DataMigration class
        from ..data.data_migration import DataMigration
        
        if hasattr(pg_hypothesis, 'to_dict'):
            pg_dict = pg_hypothesis.to_dict()
        else:
            pg_dict = pg_hypothesis
        
        return DataMigration.from_protognosis(pg_dict)
    
    async def generate_single_hypothesis(self, strategy: str = "literature_exploration") -> UnifiedHypothesis:
        """
        Generate a single hypothesis using the specified strategy.
        
        Args:
            strategy: Generation strategy to use
            
        Returns:
            Generated hypothesis
        """
        if self.coscientist:
            # Use ProtoGnosis for generation
            hypothesis_ids = self.coscientist.generate_hypotheses(count=1, strategies=[strategy])
            self.coscientist.wait_for_completion()
            
            # Get the generated hypothesis
            hypotheses = self.coscientist.get_all_hypotheses()
            if hypotheses:
                return self._convert_protognosis_hypothesis(hypotheses[-1])
        
        # Fallback: create a basic hypothesis
        # This would be replaced with actual generation logic
        hypothesis = UnifiedHypothesis(
            title="Generated Hypothesis",
            description="This is a placeholder hypothesis generated by Jnana.",
            generation_strategy=strategy
        )
        
        return hypothesis
    
    async def refine_hypothesis(self, hypothesis: UnifiedHypothesis, 
                              feedback: str) -> UnifiedHypothesis:
        """
        Refine a hypothesis based on user feedback.
        
        Args:
            hypothesis: Hypothesis to refine
            feedback: User feedback
            
        Returns:
            Refined hypothesis
        """
        # Add feedback to hypothesis
        hypothesis.add_feedback(feedback)
        
        # Use ProtoGnosis reflection agent if available
        if self.coscientist:
            # This would use the reflection agent to improve the hypothesis
            pass
        
        # Update in session
        await self.session_manager.update_hypothesis(hypothesis)
        
        return hypothesis
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        session_info = self.session_manager.get_session_info()
        
        return {
            "running": self.running,
            "mode": self.current_mode,
            "protognosis_available": PROTOGNOSIS_AVAILABLE,
            "ui_enabled": self.enable_ui,
            "session": session_info,
            "storage_stats": self.storage.get_statistics(),
            "event_stats": self.event_manager.get_statistics()
        }
