"""
Jnana-ProtoGnosis Adapter.

This module provides the main adapter class for integrating ProtoGnosis
functionality into the Jnana system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from ..core.coscientist import CoScientist
from ..core.multi_llm_config import LLMConfig, AgentLLMConfig
from .data_converter import ProtoGnosisDataConverter
from ...data.unified_hypothesis import UnifiedHypothesis
from ...core.model_manager import UnifiedModelManager


class JnanaProtoGnosisAdapter:
    """
    Adapter class for integrating ProtoGnosis with Jnana.
    
    This class provides a bridge between the Jnana system and ProtoGnosis,
    handling data conversion, configuration mapping, and workflow coordination.
    """
    
    def __init__(self, model_manager: UnifiedModelManager, 
                 storage_path: Optional[str] = None,
                 max_workers: int = 4):
        """
        Initialize the Jnana-ProtoGnosis adapter.
        
        Args:
            model_manager: Jnana unified model manager
            storage_path: Path for ProtoGnosis storage
            max_workers: Maximum number of worker threads
        """
        self.model_manager = model_manager
        self.storage_path = storage_path
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # ProtoGnosis instance
        self.coscientist: Optional[CoScientist] = None
        self.is_initialized = False
        
        # Data converter
        self.converter = ProtoGnosisDataConverter()
    
    async def initialize(self) -> bool:
        """
        Initialize the ProtoGnosis system with Jnana configuration.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing ProtoGnosis with Jnana configuration...")
            
            # Convert Jnana model configuration to ProtoGnosis format
            protognosis_config = self._convert_model_config()
            
            # Initialize CoScientist
            self.coscientist = CoScientist(
                llm_config=protognosis_config,
                storage_path=self.storage_path,
                max_workers=self.max_workers
            )

            # Start the CoScientist system (this starts the worker threads!)
            self.coscientist.start()

            self.is_initialized = True
            self.logger.info("ProtoGnosis initialized and started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ProtoGnosis: {e}")
            self.is_initialized = False
            return False

    async def shutdown(self) -> None:
        """
        Shutdown the ProtoGnosis system and clean up resources.
        """
        if self.coscientist and self.is_initialized:
            try:
                self.logger.info("Shutting down ProtoGnosis system...")
                self.coscientist.stop()
                self.is_initialized = False
                self.logger.info("ProtoGnosis system stopped successfully")
            except Exception as e:
                self.logger.error(f"Error shutting down ProtoGnosis: {e}")
    
    async def generate_hypotheses(self, research_goal: str, count: int = 5,
                                 strategies: Optional[List[str]] = None) -> List[UnifiedHypothesis]:
        """
        Generate hypotheses using ProtoGnosis and convert to Jnana format.
        
        Args:
            research_goal: The research goal/question
            count: Number of hypotheses to generate
            strategies: Generation strategies to use
            
        Returns:
            List of UnifiedHypothesis objects
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.coscientist:
            raise RuntimeError("ProtoGnosis not initialized")
        
        try:
            self.logger.info(f"Generating {count} hypotheses for: {research_goal[:100]}...")
            
            # Set research goal in ProtoGnosis
            self.coscientist.set_research_goal(research_goal)
            
            # Generate hypotheses
            hypothesis_ids = self.coscientist.generate_hypotheses(
                count=count,
                strategies=strategies or ["literature_exploration", "scientific_debate"]
            )
            
            # Wait for completion
            self.coscientist.wait_for_completion()
            
            # Get generated hypotheses
            pg_hypotheses = self.coscientist.get_all_hypotheses()
            
            # Convert to Jnana format
            unified_hypotheses = self.converter.batch_protognosis_to_unified(pg_hypotheses)
            
            self.logger.info(f"Successfully generated and converted {len(unified_hypotheses)} hypotheses")
            return unified_hypotheses
            
        except Exception as e:
            self.logger.error(f"Error generating hypotheses: {e}")
            return []
    
    async def run_tournament(self, hypotheses: List[UnifiedHypothesis], 
                           match_count: int = 25) -> List[UnifiedHypothesis]:
        """
        Run tournament evaluation on hypotheses using ProtoGnosis.
        
        Args:
            hypotheses: List of hypotheses to evaluate
            match_count: Number of tournament matches
            
        Returns:
            List of hypotheses with updated tournament records
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.coscientist:
            raise RuntimeError("ProtoGnosis not initialized")
        
        try:
            self.logger.info(f"Running tournament with {match_count} matches on {len(hypotheses)} hypotheses")
            
            # Convert hypotheses to ProtoGnosis format
            pg_hypotheses = self.converter.batch_unified_to_protognosis(hypotheses)
            
            # Add hypotheses to ProtoGnosis memory
            for pg_hyp in pg_hypotheses:
                self.coscientist.memory.add_hypothesis(pg_hyp)
            
            # Run tournament
            self.coscientist.run_tournament(match_count=match_count)
            self.coscientist.wait_for_completion()
            
            # Get updated hypotheses
            updated_pg_hypotheses = self.coscientist.get_all_hypotheses()
            
            # Convert back to Jnana format
            updated_unified_hypotheses = self.converter.batch_protognosis_to_unified(updated_pg_hypotheses)
            
            self.logger.info(f"Tournament completed successfully")
            return updated_unified_hypotheses
            
        except Exception as e:
            self.logger.error(f"Error running tournament: {e}")
            return hypotheses  # Return original hypotheses if tournament fails
    
    async def evolve_hypothesis(self, hypothesis: UnifiedHypothesis, 
                               feedback: str = "") -> UnifiedHypothesis:
        """
        Evolve a hypothesis using ProtoGnosis evolution agent.
        
        Args:
            hypothesis: Hypothesis to evolve
            feedback: Feedback for evolution
            
        Returns:
            Evolved hypothesis
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not self.coscientist:
            raise RuntimeError("ProtoGnosis not initialized")
        
        try:
            # Convert to ProtoGnosis format
            pg_hypothesis = self.converter.unified_to_protognosis(hypothesis)
            
            # Add to ProtoGnosis memory
            self.coscientist.memory.add_hypothesis(pg_hypothesis)
            
            # Evolve hypothesis
            evolution_result = self.coscientist.evolve_hypothesis(
                pg_hypothesis.hypothesis_id, feedback
            )

            try:
                evolved_hypothesis_id = evolution_result.get('evolved_hypothesis_id')
            except:
                self.logger.info("ERROR: evolved hypothesis not found")

            try:
                evolved_pg_hypothesis = self.coscientist.memory.get_hypothesis(evolved_hypothesis_id)
            except:
                self.logger.info("Evolved hypothesis not found in memory")

            """
            # Get the evolved hypothesis from memory
            evolved_pg_hypothesis = self.coscientist.memory.get_hypothesis(
                evolution_result.get("evolved_hypothesis_id", pg_hypothesis.hypothesis_id)
            ) or pg_hypothesis
            """
            # Convert back to Jnana format
            evolved_unified_hypothesis = self.converter.protognosis_to_unified(evolved_pg_hypothesis)
            
            return evolved_unified_hypothesis
            
        except Exception as e:
            self.logger.error(f"Error evolving hypothesis: {e}")
            return hypothesis  # Return original if evolution fails
    
    def _convert_model_config(self) -> AgentLLMConfig:
        """
        Convert Jnana model configuration to ProtoGnosis format.
        
        Returns:
            AgentLLMConfig for ProtoGnosis
        """
        try:
            # Get default model configuration
            default_config = self.model_manager.get_default_config()
            
            # Create default LLM config
            default_llm_config = LLMConfig(
                provider=default_config.get("provider", "ollama"),
                model=default_config.get("model", "deepseek-r1:8b"),
                api_key=default_config.get("api_key"),
                temperature=default_config.get("temperature", 0.7),
                max_tokens=default_config.get("max_tokens", 4096)
            )
            
            # Create agent-specific configs if available
            agent_configs = {}
            
            # Try to get agent-specific configurations
            for agent_type in ["generation", "reflection", "ranking", "evolution", "proximity", "meta_review"]:
                try:
                    agent_config = self.model_manager.get_model_for_agent(agent_type)
                    if agent_config:
                        agent_configs[agent_type] = LLMConfig(
                            provider=agent_config.get("provider", default_llm_config.provider),
                            model=agent_config.get("model", default_llm_config.model),
                            api_key=agent_config.get("api_key", default_llm_config.api_key),
                            temperature=agent_config.get("temperature", default_llm_config.temperature),
                            max_tokens=agent_config.get("max_tokens", default_llm_config.max_tokens)
                        )
                except:
                    # Use default config if agent-specific config not available
                    pass
            
            # Create AgentLLMConfig
            return AgentLLMConfig(
                default=default_llm_config,
                **agent_configs
            )
            
        except Exception as e:
            self.logger.warning(f"Error converting model config, using defaults: {e}")
            # Return basic default configuration
            return AgentLLMConfig(
                    default=LLMConfig(provider="ollama", model="deepseek-r1:8b")
            )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the status of the ProtoGnosis integration.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "initialized": self.is_initialized,
            "coscientist_available": self.coscientist is not None,
            "storage_path": self.storage_path,
            "max_workers": self.max_workers,
            "timestamp": datetime.now().isoformat()
        }
