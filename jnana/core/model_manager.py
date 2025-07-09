"""
Unified Model Manager for Jnana system.

This module provides a unified interface for managing LLM configurations
from both Wisteria and ProtoGnosis systems, enabling seamless model selection
and configuration across different use cases.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

# Import ProtoGnosis configuration classes
try:
    from multi_llm_config import LLMConfig, AgentLLMConfig
    PROTOGNOSIS_AVAILABLE = True
except ImportError:
    PROTOGNOSIS_AVAILABLE = False
    # Create placeholder classes if ProtoGnosis is not available
    class LLMConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class AgentLLMConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


class UnifiedModelManager:
    """
    Unified model configuration manager that bridges Wisteria and ProtoGnosis
    model configuration systems.
    """
    
    def __init__(self, config_path: Union[str, Path]):
        """
        Initialize the unified model manager.
        
        Args:
            config_path: Path to the Jnana model configuration file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Create ProtoGnosis-compatible configuration
        self.agent_llm_config = self._create_agent_llm_config()
        
        # Create Wisteria-compatible configuration
        self.wisteria_config = self._create_wisteria_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the Jnana configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Expand environment variables
            config = self._expand_env_vars(config)
            
            return config
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand environment variables in configuration."""
        if isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)  # Return original if env var not found
        else:
            return obj
    
    def _create_llm_config(self, config_dict: Dict[str, Any]) -> LLMConfig:
        """Create an LLMConfig object from configuration dictionary."""
        return LLMConfig(
            provider=config_dict.get("provider", "openai"),
            model=config_dict.get("model"),
            api_key=config_dict.get("api_key"),
            base_url=config_dict.get("base_url"),
            temperature=config_dict.get("temperature", 0.7),
            max_tokens=config_dict.get("max_tokens", 2048),
            model_adapter=config_dict.get("model_adapter")
        )
    
    def _create_agent_llm_config(self) -> AgentLLMConfig:
        """Create ProtoGnosis-compatible AgentLLMConfig."""
        # Get default configuration
        default_config = self.config.get("default", {})
        default_llm = self._create_llm_config(default_config)
        
        # Get agent-specific configurations
        agents_config = self.config.get("agents", {})
        
        agent_llm_config = AgentLLMConfig(
            default=default_llm,
            supervisor=self._create_llm_config(agents_config.get("supervisor", default_config)),
            generation=self._create_llm_config(agents_config.get("generation", default_config)),
            reflection=self._create_llm_config(agents_config.get("reflection", default_config)),
            ranking=self._create_llm_config(agents_config.get("ranking", default_config)),
            evolution=self._create_llm_config(agents_config.get("evolution", default_config)),
            proximity=self._create_llm_config(agents_config.get("proximity", default_config)),
            meta_review=self._create_llm_config(agents_config.get("meta_review", default_config))
        )
        
        return agent_llm_config
    
    def _create_wisteria_config(self) -> Dict[str, Any]:
        """Create Wisteria-compatible configuration."""
        wisteria_servers = {"servers": []}
        
        # Add interactive configurations
        interactive_config = self.config.get("interactive", {})
        for name, config in interactive_config.items():
            server_config = {
                "server": config.get("base_url", "api.openai.com").replace("https://", "").replace("http://", ""),
                "shortname": f"interactive_{name}",
                "openai_api_key": config.get("api_key", "${OPENAI_API_KEY}"),
                "openai_api_base": config.get("base_url", "https://api.openai.com/v1"),
                "openai_model": config.get("model", "gpt-4o")
            }
            wisteria_servers["servers"].append(server_config)
        
        # Add local configurations
        local_config = self.config.get("local", {})
        for name, config in local_config.items():
            if config.get("provider") == "ollama":
                server_config = {
                    "server": config.get("base_url", "localhost:11434").replace("http://", ""),
                    "shortname": f"local_{name}",
                    "openai_api_key": config.get("api_key", "${OLLAMA_API_KEY}"),
                    "openai_api_base": config.get("base_url", "http://localhost:11434/v1"),
                    "openai_model": config.get("model", "llama3")
                }
                wisteria_servers["servers"].append(server_config)
        
        return wisteria_servers
    
    def get_model_for_agent(self, agent_type: str, agent_id: Optional[str] = None) -> LLMConfig:
        """
        Get LLM configuration for a specific agent type.

        Args:
            agent_type: Type of agent ("supervisor", "generation", etc.)
            agent_id: Optional specific agent ID

        Returns:
            LLMConfig for the agent
        """
        # Get agent-specific configuration or fall back to default
        agents_config = self.config.get("agents", {})
        if agent_type in agents_config:
            config_dict = agents_config[agent_type]
        else:
            config_dict = self.config.get("default", {})

        return self._create_llm_config(config_dict)
    
    def get_interactive_model(self, preference: Optional[str] = None) -> LLMConfig:
        """
        Get model configuration for interactive use (Wisteria-style).
        
        Args:
            preference: Optional model preference ("primary", "alternative", or specific model name)
            
        Returns:
            LLMConfig for interactive use
        """
        interactive_config = self.config.get("interactive", {})
        
        if preference and preference in interactive_config:
            config_dict = interactive_config[preference]
        elif "primary" in interactive_config:
            config_dict = interactive_config["primary"]
        else:
            # Fall back to default
            config_dict = self.config.get("default", {})
        
        return self._create_llm_config(config_dict)
    
    def get_task_model(self, task_type: str) -> LLMConfig:
        """
        Get model configuration for a specific task type.
        
        Args:
            task_type: Type of task ("hypothesis_generation", "refinement", etc.)
            
        Returns:
            LLMConfig for the task
        """
        tasks_config = self.config.get("tasks", {})
        
        if task_type in tasks_config:
            config_dict = tasks_config[task_type]
        else:
            # Fall back to default
            config_dict = self.config.get("default", {})
        
        return self._create_llm_config(config_dict)
    
    def get_wisteria_config_path(self) -> Path:
        """Get path for Wisteria-compatible configuration file."""
        wisteria_path = self.config_path.parent / "wisteria_models.yaml"
        
        # Write Wisteria configuration if it doesn't exist or is outdated
        if not wisteria_path.exists() or wisteria_path.stat().st_mtime < self.config_path.stat().st_mtime:
            with open(wisteria_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.wisteria_config, f, default_flow_style=False)
        
        return wisteria_path
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List all available models by category."""
        models = {
            "agents": [],
            "interactive": [],
            "local": [],
            "tasks": []
        }
        
        # Agent models
        agents_config = self.config.get("agents", {})
        for agent_type, config in agents_config.items():
            model_name = f"{config.get('provider', 'unknown')}:{config.get('model', 'unknown')}"
            models["agents"].append(f"{agent_type} -> {model_name}")
        
        # Interactive models
        interactive_config = self.config.get("interactive", {})
        for name, config in interactive_config.items():
            model_name = f"{config.get('provider', 'unknown')}:{config.get('model', 'unknown')}"
            models["interactive"].append(f"{name} -> {model_name}")
        
        # Local models
        local_config = self.config.get("local", {})
        for name, config in local_config.items():
            model_name = f"{config.get('provider', 'unknown')}:{config.get('model', 'unknown')}"
            models["local"].append(f"{name} -> {model_name}")
        
        # Task models
        tasks_config = self.config.get("tasks", {})
        for task_type, config in tasks_config.items():
            model_name = f"{config.get('provider', 'unknown')}:{config.get('model', 'unknown')}"
            models["tasks"].append(f"{task_type} -> {model_name}")
        
        return models
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the configuration and return any issues found.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check required sections
        required_sections = ["default"]
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required section: {section}")
        
        # Validate default configuration
        default_config = self.config.get("default", {})
        if not default_config.get("provider"):
            errors.append("Default configuration missing 'provider'")
        
        # Check API keys for cloud providers
        cloud_providers = ["openai", "anthropic", "gemini"]
        
        def check_api_key(config_dict: Dict[str, Any], context: str):
            provider = config_dict.get("provider", "")
            if provider in cloud_providers:
                api_key = config_dict.get("api_key", "")
                if not api_key or api_key.startswith("${"):
                    # Check if environment variable exists
                    if api_key.startswith("${") and api_key.endswith("}"):
                        env_var = api_key[2:-1]
                        if not os.getenv(env_var):
                            errors.append(f"{context}: Environment variable {env_var} not set")
                    else:
                        errors.append(f"{context}: API key required for {provider}")
        
        # Check default config
        check_api_key(default_config, "Default configuration")
        
        # Check agent configurations
        agents_config = self.config.get("agents", {})
        for agent_type, config in agents_config.items():
            check_api_key(config, f"Agent '{agent_type}' configuration")
        
        # Check interactive configurations
        interactive_config = self.config.get("interactive", {})
        for name, config in interactive_config.items():
            check_api_key(config, f"Interactive '{name}' configuration")
        
        return errors
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance and scaling settings."""
        return self.config.get("performance", {
            "max_concurrent_requests": 10,
            "request_timeout": 60,
            "retry_attempts": 3,
            "rate_limit_delay": 1.0
        })
    
    def get_ui_settings(self) -> Dict[str, Any]:
        """Get UI and interaction settings."""
        return self.config.get("ui", {
            "default_mode": "interactive",
            "auto_save_interval": 300,
            "max_hypothesis_display": 100,
            "enable_real_time_updates": True
        })
