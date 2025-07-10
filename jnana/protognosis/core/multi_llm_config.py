"""
Configuration class for managing multiple LLM providers in the AI Co-scientist system.
"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""
    provider: str  # "anthropic", "gemini", "openai", "ollama", "llm_studio", "cerebras"
    model: Optional[str] = None  # Specific model to use, or None for default
    api_key: Optional[str] = None  # API key, or None to use environment variable
    base_url: Optional[str] = None  # Base URL for local LLM providers
    temperature: float = 0.7  # Default temperature
    max_tokens: int = 1024  # Default max tokens
    model_adapter: Optional[Dict[str, Any]] = None  # Configuration for model adaptation

    def __post_init__(self):
        """Validate and normalize the config."""
        self.provider = self.provider.lower()

        # Set default models based on provider
        if self.model is None:
            if self.provider == "anthropic":
                self.model = "claude-3-7-sonnet-20250219"  # Updated to latest model
            elif self.provider == "gemini":
                self.model = "gemini-1.5-pro"
            elif self.provider == "openai":
                self.model = "gpt-4o"
            elif self.provider == "ollama":
                self.model = "llama3"
            elif self.provider == "llm_studio":
                self.model = "default"
            elif self.provider == "cerebras":
                self.model = "cerebras_api_keyllama-4-scout-17b-16e-instruct"

@dataclass
class AgentLLMConfig:
    """Configuration for LLM providers by agent type."""
    # Default LLM for any agent type not specifically configured
    default: LLMConfig

    # LLM configs for specific agent types
    supervisor: Optional[LLMConfig] = None
    generation: Optional[LLMConfig] = None
    reflection: Optional[LLMConfig] = None
    ranking: Optional[LLMConfig] = None
    evolution: Optional[LLMConfig] = None
    proximity: Optional[LLMConfig] = None
    meta_review: Optional[LLMConfig] = None

    # Additional configs for specific agent instances (by id)
    specific_agents: Dict[str, LLMConfig] = field(default_factory=dict)

    def get_config_for_agent(self, agent_type: str, agent_id: Optional[str] = None) -> LLMConfig:
        """
        Get the LLM configuration for a specific agent.

        Args:
            agent_type: Type of agent ("supervisor", "generation", etc.)
            agent_id: Optional specific agent ID

        Returns:
            LLM configuration to use for this agent
        """
        # First check if there's a specific config for this agent ID
        if agent_id and agent_id in self.specific_agents:
            return self.specific_agents[agent_id]

        # Next check if there's a config for this agent type
        agent_type = agent_type.lower()
        if agent_type == "supervisor" and self.supervisor:
            return self.supervisor
        elif agent_type == "generation" and self.generation:
            return self.generation
        elif agent_type == "reflection" and self.reflection:
            return self.reflection
        elif agent_type == "ranking" and self.ranking:
            return self.ranking
        elif agent_type == "evolution" and self.evolution:
            return self.evolution
        elif agent_type == "proximity" and self.proximity:
            return self.proximity
        elif agent_type == "meta-review" and self.meta_review:
            return self.meta_review

        # Otherwise use the default
        return self.default
