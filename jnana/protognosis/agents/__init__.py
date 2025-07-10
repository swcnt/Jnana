"""
ProtoGnosis Specialized Agents.

This module contains all the specialized agents used in the ProtoGnosis system:
- GenerationAgent: Generates initial research hypotheses
- ReflectionAgent: Provides peer review and critique
- RankingAgent: Ranks hypotheses by quality
- EvolutionAgent: Evolves and improves hypotheses
- ProximityAgent: Analyzes hypothesis relationships
- MetaReviewAgent: Provides comprehensive meta-analysis
"""

from .generation_agent import GenerationAgent
from .reflection_agent import ReflectionAgent
from .ranking_agent import RankingAgent
from .evolution_agent import EvolutionAgent
from .proximity_agent import ProximityAgent
from .meta_review_agent import MetaReviewAgent

__all__ = [
    "GenerationAgent",
    "ReflectionAgent",
    "RankingAgent", 
    "EvolutionAgent",
    "ProximityAgent",
    "MetaReviewAgent"
]
