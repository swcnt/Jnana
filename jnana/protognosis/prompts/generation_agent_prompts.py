"""
Prompt templates for the Generation Agent.
These can be customized by the end user.
"""

def create_scientific_debate_prompt(research_goal, plan_config):
    """Create a prompt for scientific debate-based hypothesis generation."""
    constraints = ', '.join(plan_config.get('constraints', []))
    preferences = ', '.join(plan_config.get('preferences', []))
    
    return (
        f"You are an AI co-scientist specializing in generating novel research hypotheses through simulated scientific debates.\n\n"
        f"Research goal:\n{research_goal}\n\n"
        f"Your task is to simulate a scientific debate among experts with different perspectives to "
        f"generate a novel research hypothesis that addresses this goal.\n\n"
        f"Follow these steps:\n"
        f"1. Create 3-5 expert personas with different backgrounds and perspectives relevant to this research area\n"
        f"2. Simulate a scientific debate where each expert proposes initial ideas and critiques others' proposals\n"
        f"3. Allow the debate to evolve through multiple rounds, refining ideas and addressing criticisms\n"
        f"4. Synthesize the most promising ideas from the debate into a coherent hypothesis\n"
        f"5. Ensure the final hypothesis is specific, testable, and explains its significance\n\n"
        f"Constraints to consider:\n{constraints}\n\n"
        f"Preferences to incorporate:\n{preferences}\n\n"
        f"The final hypothesis should represent a consensus emerging from diverse scientific perspectives, "
        f"addressing potential criticisms and limitations while maintaining novelty and testability."
    )

def create_literature_exploration_prompt(research_goal, plan_config):
    """Create a prompt for literature exploration-based hypothesis generation."""
    constraints = ', '.join(plan_config.get('constraints', []))
    preferences = ', '.join(plan_config.get('preferences', []))
    
    return (
        f"You are an AI co-scientist specializing in generating novel research hypotheses based on literature exploration.\n\n"
        f"Research goal:\n{research_goal}\n\n"
        f"Your task is to generate a novel research hypothesis that addresses this goal.\n\n"
        f"Follow these steps:\n"
        f"1. Imagine you have conducted a thorough literature review in this research area\n"
        f"2. Identify key findings, methods, and theories from the literature\n"
        f"3. Look for gaps, contradictions, or unexplored connections in existing research\n"
        f"4. Develop a novel hypothesis that addresses these gaps or connects disparate findings\n"
        f"5. Ensure the hypothesis is specific, testable, and explain its significance\n\n"
        f"Constraints to consider:\n{constraints}\n\n"
        f"Preferences to incorporate:\n{preferences}\n\n"
        f"The final hypothesis should be well-grounded in existing literature while proposing "
        f"a novel direction that advances understanding in this research area."
    )

def create_assumptions_identification_prompt(research_goal, plan_config):
    """Create a prompt for assumptions identification-based hypothesis generation."""
    constraints = ', '.join(plan_config.get('constraints', []))
    preferences = ', '.join(plan_config.get('preferences', []))
    
    return (
        f"You are an AI co-scientist specializing in generating novel research hypotheses through identification of key assumptions.\n\n"
        f"Research goal:\n{research_goal}\n\n"
        f"Your task is to generate a novel research hypothesis by identifying and challenging key assumptions "
        f"in the current understanding of this research area.\n\n"
        f"Follow these steps:\n"
        f"1. Identify 3-5 key assumptions that underlie current thinking in this research area\n"
        f"2. For each assumption, analyze its validity and evidence supporting or contradicting it\n"
        f"3. Select one or more assumptions that could be productively challenged\n"
        f"4. Develop a novel hypothesis that challenges or reframes these assumptions\n"
        f"5. Ensure the hypothesis is specific, testable, and explain its significance\n\n"
        f"Constraints to consider:\n{constraints}\n\n"
        f"Preferences to incorporate:\n{preferences}\n\n"
        f"The final hypothesis should represent a meaningful challenge to existing assumptions, "
        f"opening new avenues for research while remaining scientifically plausible."
    )

def create_research_expansion_prompt(research_goal, plan_config, top_summaries):
    """Create a prompt for research expansion-based hypothesis generation."""
    constraints = ', '.join(plan_config.get('constraints', []))
    preferences = ', '.join(plan_config.get('preferences', []))
    
    return (
        f"You are an AI co-scientist specializing in generating novel research hypotheses by building upon existing ideas.\n\n"
        f"Research goal:\n{research_goal}\n\n"
        f"Your task is to generate a novel research hypothesis that builds upon or expands existing ideas in this area.\n\n"
        f"Top-ranked existing hypotheses:\n{top_summaries}\n\n"
        f"Follow these steps:\n"
        f"1. Analyze the research goal and existing hypotheses\n"
        f"2. Identify unexplored aspects, extensions, or combinations of these ideas\n"
        f"3. Develop a novel hypothesis that builds upon these foundations in an original way\n"
        f"4. Ensure the hypothesis goes beyond incremental improvements to propose substantively new ideas\n"
        f"5. Make the hypothesis specific, testable, and explain its significance\n\n"
        f"Constraints to consider:\n{constraints}\n\n"
        f"Preferences to incorporate:\n{preferences}\n\n"
        f"The final hypothesis should represent a meaningful advancement beyond existing ideas, "
        f"while maintaining a clear connection to the research goal and prior work."
    )
