"""
ProtoGnosis Core Components.

This module contains the core components of the ProtoGnosis system:
- CoScientist: Main orchestrator class
- Agent framework: Base classes for all agents
- LLM Interface: Unified interface for different LLM providers
- Configuration: Multi-LLM configuration management
"""

from .coscientist import CoScientist
from .agent_core import (
    Agent, SupervisorAgent, Task, ResearchHypothesis, ContextMemory
)
from .llm_interface import LLMInterface, create_llm
from .multi_llm_config import LLMConfig, AgentLLMConfig

__all__ = [
    "CoScientist",
    "Agent",
    "SupervisorAgent",
    "Task", 
    "ResearchHypothesis",
    "ContextMemory",
    "LLMInterface",
    "create_llm",
    "LLMConfig",
    "AgentLLMConfig"
]
