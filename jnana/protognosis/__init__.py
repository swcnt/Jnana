"""
ProtoGnosis Integration Module for Jnana.

This module provides the complete ProtoGnosis multi-agent system
integrated into the Jnana framework.

ProtoGnosis is a multi-agent AI system for generating and evaluating
novel research hypotheses using specialized agents and tournament-based
evaluation.
"""

__version__ = "1.0.0"

# Core ProtoGnosis components
from .core.coscientist import CoScientist
from .core.agent_core import (
    Agent, SupervisorAgent, Task, ResearchHypothesis, ContextMemory
)
from .core.llm_interface import LLMInterface, create_llm
from .core.multi_llm_config import LLMConfig, AgentLLMConfig

# Specialized agents
from .agents.generation_agent import GenerationAgent
from .agents.reflection_agent import ReflectionAgent
from .agents.ranking_agent import RankingAgent
from .agents.evolution_agent import EvolutionAgent
from .agents.proximity_agent import ProximityAgent
from .agents.meta_review_agent import MetaReviewAgent

# Utilities and adapters
from .utils.jnana_adapter import JnanaProtoGnosisAdapter
from .utils.data_converter import ProtoGnosisDataConverter

__all__ = [
    # Core components
    "CoScientist",
    "Agent",
    "SupervisorAgent", 
    "Task",
    "ResearchHypothesis",
    "ContextMemory",
    "LLMInterface",
    "create_llm",
    "LLMConfig",
    "AgentLLMConfig",
    
    # Specialized agents
    "GenerationAgent",
    "ReflectionAgent", 
    "RankingAgent",
    "EvolutionAgent",
    "ProximityAgent",
    "MetaReviewAgent",
    
    # Utilities
    "JnanaProtoGnosisAdapter",
    "ProtoGnosisDataConverter"
]

# Version and metadata
PROTOGNOSIS_VERSION = __version__
PROTOGNOSIS_DESCRIPTION = """
ProtoGnosis Multi-Agent Research Hypothesis System

A sophisticated AI system that uses multiple specialized agents to:
- Generate novel research hypotheses using various strategies
- Evaluate and refine hypotheses through peer review
- Rank hypotheses using tournament-based competition
- Evolve hypotheses through iterative improvement
- Provide meta-analysis and comprehensive evaluation

Integrated into Jnana for seamless hypothesis generation and evaluation.
"""

def get_protognosis_info():
    """Get information about the ProtoGnosis integration."""
    return {
        "version": PROTOGNOSIS_VERSION,
        "description": PROTOGNOSIS_DESCRIPTION,
        "agents": [
            "GenerationAgent - Generates initial hypotheses",
            "ReflectionAgent - Provides peer review and critique", 
            "RankingAgent - Ranks hypotheses by quality",
            "EvolutionAgent - Evolves and improves hypotheses",
            "ProximityAgent - Analyzes hypothesis relationships",
            "MetaReviewAgent - Provides comprehensive meta-analysis"
        ],
        "strategies": [
            "literature_exploration - Research-based generation",
            "scientific_debate - Contrarian perspective generation", 
            "assumptions_identification - Challenge existing assumptions",
            "research_expansion - Extend current research directions"
        ],
        "features": [
            "Multi-LLM support (OpenAI, Anthropic, Google, Ollama)",
            "Tournament-based evaluation with Elo ratings",
            "Asynchronous processing for scalability",
            "Context memory for coherent conversations",
            "Comprehensive logging and monitoring"
        ]
    }

# Check if ProtoGnosis components are available
try:
    # Test imports to verify integration
    from .core.coscientist import CoScientist
    from .agents.generation_agent import GenerationAgent
    PROTOGNOSIS_AVAILABLE = True
    PROTOGNOSIS_ERROR = None
except ImportError as e:
    PROTOGNOSIS_AVAILABLE = False
    PROTOGNOSIS_ERROR = str(e)

def is_protognosis_available():
    """Check if ProtoGnosis is fully available."""
    return PROTOGNOSIS_AVAILABLE

def get_protognosis_status():
    """Get the status of ProtoGnosis integration."""
    if PROTOGNOSIS_AVAILABLE:
        return {
            "available": True,
            "version": PROTOGNOSIS_VERSION,
            "components": len(__all__),
            "error": None
        }
    else:
        return {
            "available": False,
            "version": None,
            "components": 0,
            "error": PROTOGNOSIS_ERROR
        }
