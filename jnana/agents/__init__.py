"""
Agent wrappers and extensions for Jnana system.
"""

from .biomni_agent import BiomniAgent, BiomniConfig, BiomniVerificationResult

# Import other agents if they exist
try:
    from .interactive_agent_wrapper import InteractiveAgentWrapper
    INTERACTIVE_AGENT_AVAILABLE = True
except ImportError:
    INTERACTIVE_AGENT_AVAILABLE = False

try:
    from .agent_factory import AgentFactory
    AGENT_FACTORY_AVAILABLE = True
except ImportError:
    AGENT_FACTORY_AVAILABLE = False

__all__ = [
    "BiomniAgent",
    "BiomniConfig",
    "BiomniVerificationResult"
]

if INTERACTIVE_AGENT_AVAILABLE:
    __all__.append("InteractiveAgentWrapper")

if AGENT_FACTORY_AVAILABLE:
    __all__.append("AgentFactory")
