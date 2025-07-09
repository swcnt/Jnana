"""
Validation utilities for Jnana system.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from ..data.unified_hypothesis import UnifiedHypothesis


def validate_hypothesis(hypothesis: UnifiedHypothesis) -> Tuple[bool, List[str]]:
    """
    Validate a hypothesis for completeness and quality.
    
    Args:
        hypothesis: Hypothesis to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields
    if not hypothesis.title or not hypothesis.title.strip():
        errors.append("Hypothesis title is required")
    
    if not hypothesis.content and not hypothesis.description:
        errors.append("Hypothesis content or description is required")
    
    # Check title length and format
    if hypothesis.title:
        if len(hypothesis.title) < 10:
            errors.append("Hypothesis title should be at least 10 characters")
        if len(hypothesis.title) > 200:
            errors.append("Hypothesis title should be less than 200 characters")
    
    # Check content length
    content = hypothesis.content or hypothesis.description
    if content:
        if len(content) < 50:
            errors.append("Hypothesis content should be at least 50 characters")
        if len(content) > 10000:
            errors.append("Hypothesis content should be less than 10,000 characters")
    
    # Check experimental validation
    if hypothesis.experimental_validation:
        if len(hypothesis.experimental_validation) < 20:
            errors.append("Experimental validation should be more detailed (at least 20 characters)")
    
    # Validate references
    for i, ref in enumerate(hypothesis.references):
        if not ref.citation or not ref.citation.strip():
            errors.append(f"Reference {i+1} is missing citation")
    
    # Check for basic scientific language
    if content:
        content_lower = content.lower()
        scientific_indicators = [
            'hypothesis', 'theory', 'experiment', 'data', 'analysis',
            'research', 'study', 'evidence', 'method', 'result'
        ]
        
        if not any(indicator in content_lower for indicator in scientific_indicators):
            errors.append("Content should include scientific terminology")
    
    return len(errors) == 0, errors


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate Jnana configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required sections
    required_sections = ["default"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required configuration section: {section}")
    
    # Validate default configuration
    if "default" in config:
        default_config = config["default"]
        
        if "provider" not in default_config:
            errors.append("Default configuration missing 'provider'")
        
        if "model" not in default_config:
            errors.append("Default configuration missing 'model'")
    
    # Validate agent configurations
    if "agents" in config:
        agents_config = config["agents"]
        valid_agent_types = [
            "supervisor", "generation", "reflection", "ranking",
            "evolution", "proximity", "meta_review"
        ]
        
        for agent_type, agent_config in agents_config.items():
            if agent_type not in valid_agent_types:
                errors.append(f"Unknown agent type: {agent_type}")
            
            if not isinstance(agent_config, dict):
                errors.append(f"Agent configuration for {agent_type} must be a dictionary")
                continue
            
            if "provider" not in agent_config:
                errors.append(f"Agent {agent_type} missing 'provider'")
    
    # Validate performance settings
    if "performance" in config:
        perf_config = config["performance"]
        
        if "max_concurrent_requests" in perf_config:
            max_requests = perf_config["max_concurrent_requests"]
            if not isinstance(max_requests, int) or max_requests < 1:
                errors.append("max_concurrent_requests must be a positive integer")
        
        if "request_timeout" in perf_config:
            timeout = perf_config["request_timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                errors.append("request_timeout must be a positive number")
    
    return len(errors) == 0, errors


def validate_research_goal(research_goal: str) -> Tuple[bool, List[str]]:
    """
    Validate a research goal for clarity and appropriateness.
    
    Args:
        research_goal: Research goal string
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not research_goal or not research_goal.strip():
        errors.append("Research goal cannot be empty")
        return False, errors
    
    goal = research_goal.strip()
    
    # Check length
    if len(goal) < 10:
        errors.append("Research goal should be at least 10 characters")
    
    if len(goal) > 1000:
        errors.append("Research goal should be less than 1000 characters")
    
    # Check for question format (optional but recommended)
    question_indicators = ['?', 'how', 'what', 'why', 'when', 'where', 'which']
    if not any(indicator in goal.lower() for indicator in question_indicators):
        # This is a warning, not an error
        pass
    
    # Check for scientific context
    scientific_terms = [
        'research', 'study', 'analysis', 'investigation', 'experiment',
        'hypothesis', 'theory', 'method', 'approach', 'strategy'
    ]
    
    if not any(term in goal.lower() for term in scientific_terms):
        errors.append("Research goal should include scientific context or terminology")
    
    # Check for inappropriate content
    inappropriate_patterns = [
        r'\b(hack|crack|illegal|unethical)\b',
        r'\b(personal|private|confidential)\s+information\b'
    ]
    
    for pattern in inappropriate_patterns:
        if re.search(pattern, goal.lower()):
            errors.append("Research goal contains inappropriate content")
            break
    
    return len(errors) == 0, errors


def validate_feedback(feedback: str) -> Tuple[bool, List[str]]:
    """
    Validate user feedback for hypothesis refinement.
    
    Args:
        feedback: User feedback string
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not feedback or not feedback.strip():
        errors.append("Feedback cannot be empty")
        return False, errors
    
    feedback = feedback.strip()
    
    # Check length
    if len(feedback) < 5:
        errors.append("Feedback should be at least 5 characters")
    
    if len(feedback) > 5000:
        errors.append("Feedback should be less than 5000 characters")
    
    # Check for constructive content
    constructive_indicators = [
        'improve', 'enhance', 'clarify', 'expand', 'specify',
        'consider', 'suggest', 'recommend', 'add', 'remove',
        'modify', 'change', 'better', 'more', 'less'
    ]
    
    if not any(indicator in feedback.lower() for indicator in constructive_indicators):
        # This is a warning, not an error
        pass
    
    return len(errors) == 0, errors


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    return sanitized.strip()


def validate_model_config(model_config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate individual model configuration.
    
    Args:
        model_config: Model configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if "provider" not in model_config:
        errors.append("Model configuration missing 'provider'")
    
    # Validate provider-specific requirements
    provider = model_config.get("provider", "").lower()
    
    if provider in ["openai", "anthropic", "gemini"]:
        if "api_key" not in model_config:
            errors.append(f"Provider {provider} requires 'api_key'")
    
    if provider in ["ollama", "llm_studio"]:
        if "base_url" not in model_config:
            errors.append(f"Provider {provider} requires 'base_url'")
    
    # Validate numeric parameters
    if "temperature" in model_config:
        temp = model_config["temperature"]
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
            errors.append("Temperature must be a number between 0 and 2")
    
    if "max_tokens" in model_config:
        max_tokens = model_config["max_tokens"]
        if not isinstance(max_tokens, int) or max_tokens < 1:
            errors.append("max_tokens must be a positive integer")
    
    return len(errors) == 0, errors
