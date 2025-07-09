"""
Jnana: AI Co-Scientist with Interactive Hypothesis Generation

Jnana integrates Wisteria's interactive capabilities with ProtoGnosis's 
multi-agent system to provide a comprehensive research hypothesis platform.
"""

__version__ = "0.1.0"
__author__ = "ProtoGnosis Team"

from .core.jnana_system import JnanaSystem
from .data.unified_hypothesis import UnifiedHypothesis
from .core.model_manager import UnifiedModelManager

__all__ = [
    "JnanaSystem",
    "UnifiedHypothesis", 
    "UnifiedModelManager"
]
