"""
Prompt templates for the Reflection Agent.
These can be customized by the end user.
"""

def create_initial_review_prompt(hypothesis_content):
    """Create a prompt for initial hypothesis review."""
    return (
        f"You are conducting an initial review of a scientific hypothesis.\n\n"
        f"Hypothesis:\n{hypothesis_content}\n\n"
        f"Please provide a brief assessment of this hypothesis, focusing on:\n"
        f"1. Overall scientific merit\n"
        f"2. Key strengths\n"
        f"3. Primary concerns or limitations\n"
        f"4. Whether it merits further investigation\n\n"
        f"Your goal is to provide a quick initial assessment to determine if this hypothesis "
        f"deserves more detailed review and development."
    )

def create_deep_verification_prompt(hypothesis_content):
    """Create a prompt for deep verification review."""
    return (
        f"You are conducting a deep verification review of a scientific hypothesis.\n\n"
        f"Hypothesis:\n{hypothesis_content}\n\n"
        f"Please analyze this hypothesis in depth, focusing on:\n"
        f"1. Identifying all underlying assumptions\n"
        f"2. Evaluating the logical structure and reasoning\n"
        f"3. Checking for internal contradictions or inconsistencies\n"
        f"4. Assessing overall validity\n\n"
        f"Your goal is to determine if this hypothesis is logically sound and internally consistent."
    )

def create_observation_review_prompt(hypothesis_content, observations):
    """Create a prompt for observation review."""
    return (
        f"You are reviewing whether a research hypothesis can account for existing observations in the literature.\n\n"
        f"Hypothesis:\n{hypothesis_content}\n\n"
        f"Key observations from the literature:\n{observations}\n\n"
        f"For each observation, please:\n"
        f"1. Analyze whether the hypothesis can explain it\n"
        f"2. Compare how well the hypothesis explains it versus existing theories\n"
        f"3. Identify any observations that the hypothesis cannot explain\n"
        f"4. Suggest potential modifications to the hypothesis that could address any inconsistencies\n\n"
        f"Provide a comprehensive assessment of how well the hypothesis accounts for these observations."
    )

def create_debate_comparison_prompt(research_goal, hypothesis1_content, hypothesis2_content, criteria):
    """Create a prompt for debate comparison."""
    criteria_str = ', '.join(criteria)
    
    return (
        f"You are judging a scientific debate between two competing research hypotheses.\n\n"
        f"Research goal:\n{research_goal}\n\n"
        f"Hypothesis A:\n{hypothesis1_content}\n\n"
        f"Hypothesis B:\n{hypothesis2_content}\n\n"
        f"Please evaluate these hypotheses on the following criteria:\n{criteria_str}\n\n"
        f"For each criterion, provide:\n"
        f"1. A detailed comparison of how each hypothesis performs\n"
        f"2. Specific strengths and weaknesses of each hypothesis\n"
        f"3. Your judgment on which hypothesis is stronger on this criterion\n\n"
        f"Then provide an overall assessment of which hypothesis better addresses the research goal, "
        f"explaining your reasoning in detail."
    )