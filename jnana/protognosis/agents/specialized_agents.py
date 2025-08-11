"""
Implementation of the specialized agents in the AI Co-scientist system.
This includes the Generation, Reflection, Ranking, Evolution, Proximity, and Meta-review agents.
"""
import json
import time
import asyncio
import random
from typing import Dict, List, Optional, Any, Union
import logging
import os

from ..core.agent_core import Agent, Task, ResearchHypothesis, ContextMemory
from ..core.llm_interface import LLMInterface
DEBUG = True

# Import prompt templates
try:
    from ..prompts.generation_agent_prompts import (
        create_scientific_debate_prompt,
        create_literature_exploration_prompt,
        create_assumptions_identification_prompt,
        create_research_expansion_prompt
    )
    from ..prompts.reflection_agent_prompts import (
        create_initial_review_prompt,
        create_deep_verification_prompt,
        create_observation_review_prompt,
        create_debate_comparison_prompt
    )
    EXTERNAL_PROMPTS = True
except ImportError:
    EXTERNAL_PROMPTS = False
    logging.warning("External prompt templates not found. Using built-in templates.")

class GenerationAgent(Agent):
    """
    Agent responsible for generating initial research hypotheses.
    
    This agent uses various strategies to generate novel hypotheses:
    - Literature exploration via web search
    - Simulated scientific debates
    - Iterative assumptions identification
    - Research expansion
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the generation agent."""
        super().__init__(agent_id, "generation", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute a task to generate a hypothesis."""
        task_type = task.task_type
        
        if task_type == "generate_hypothesis":
            return await self._generate_hypothesis(task)
        elif task_type == "simulate_debate":
            return await self._simulate_debate(task)
        else:
            raise ValueError(f"Unsupported task type for GenerationAgent: {task_type}")
    
    async def _generate_hypothesis(self, task: Task) -> Dict:
        """Generate a new research hypothesis."""
        self.logger.info(f"Generating hypothesis for task {task.task_id}")
        
        # Get research goal from memory
        research_goal = self.memory.metadata.get("research_goal", "")
        plan_config = self.memory.metadata.get("research_plan_config", {})
        
        if not research_goal:
            raise ValueError("No research goal found in memory")
        
        # Determine generation strategy based on task parameters or randomly select one
        strategy = task.params.get("strategy")
        if not strategy:
            strategies = ["literature_exploration", "scientific_debate", "assumptions_identification", "research_expansion"]
            strategy = random.choice(strategies)
        
        # Use the appropriate prompt template based on the strategy
        if EXTERNAL_PROMPTS:
            if strategy == "literature_exploration":
                prompt = create_literature_exploration_prompt(research_goal, plan_config)
            elif strategy == "scientific_debate":
                prompt = create_scientific_debate_prompt(research_goal, plan_config)
            elif strategy == "assumptions_identification":
                prompt = create_assumptions_identification_prompt(research_goal, plan_config)
            elif strategy == "research_expansion":
                # Get top-ranked hypotheses to build upon
                top_hypotheses = self.memory.get_top_hypotheses(3)
                top_summaries = "\n".join([f"- {h.summary}" for h in top_hypotheses]) if top_hypotheses else "No existing hypotheses yet."
                prompt = create_research_expansion_prompt(research_goal, plan_config, top_summaries)
            else:
                raise ValueError(f"Unknown generation strategy: {strategy}")
        else:
            # Use built-in prompt templates
            if strategy == "literature_exploration":
                prompt = self._create_literature_exploration_prompt(research_goal, plan_config)
            elif strategy == "scientific_debate":
                prompt = self._create_scientific_debate_prompt(research_goal, plan_config)
            elif strategy == "assumptions_identification":
                prompt = self._create_assumptions_identification_prompt(research_goal, plan_config)
            elif strategy == "research_expansion":
                # Get top-ranked hypotheses to build upon
                top_hypotheses = self.memory.get_top_hypotheses(3)
                top_summaries = "\n".join([f"- {h.summary}" for h in top_hypotheses]) if top_hypotheses else "No existing hypotheses yet."
                prompt = self._create_research_expansion_prompt(research_goal, plan_config, top_summaries)
            else:
                raise ValueError(f"Unknown generation strategy: {strategy}")
        
        # Generate hypothesis using the LLM
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="generation",
                                                role="generate novel research hypotheses")
        if DEBUG:
            self.logger.info(f"System prompt: {system_prompt}")
        
    # Define the expected output schema
        schema = {
             "hypothesis": {
                 "title": "string",
                 "content": "string",
                 "summary": "string",
                 "key_novelty_aspects": ["string"],
                 "testable_predictions": ["string"]
             },
             "explanation": "string",
             "generation_strategy": "string"
         }
        
        try:
            # Generate the hypothesis with the LLM
            response_data = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            if DEBUG:
                self.logger.info(f"Raw LLM output : {response_data}")

            # Unpack the response data
            if isinstance(response_data, tuple) and len(response_data) == 3:
                response, prompt_tokens, completion_tokens = response_data
                
                # Update token counts
                self.total_calls += 1
                self.total_prompt_tokens += int(prompt_tokens)
                self.total_completion_tokens += int(completion_tokens)
            else:
                # Handle the case where the response is not a tuple
                response = response_data
                self.total_calls += 1
            
            # Create a new hypothesis object
            hypothesis = ResearchHypothesis(
                content=response["hypothesis"]["content"],
                summary=response["hypothesis"]["summary"],
                agent_id=self.agent_id,
                metadata={
                    "title": response["hypothesis"]["title"],
                    "key_novelty_aspects": response["hypothesis"]["key_novelty_aspects"],
                    "testable_predictions": response["hypothesis"]["testable_predictions"],
                    "generation_strategy": response["generation_strategy"],
                    "explanation": response["explanation"]
                }
            )
            
            # Add the hypothesis to memory
            self.memory.add_hypothesis(hypothesis)

            # Update agent state
            try:
                self.logger.info(f"Updating agent state for {self.agent_id}")
                agent_state = self.memory.get_agent_state(self.agent_id) or {}
                self.logger.info(f"Current agent state: {agent_state}")
                agent_state.update({
                    "last_activity": time.time(),
                    "hypotheses_generated": agent_state.get("hypotheses_generated", 0) + 1,
                    "last_strategy": strategy,
                    "last_hypothesis_id": hypothesis.hypothesis_id,
                    "total_tasks_completed": agent_state.get("total_tasks_completed", 0) + 1
                })
                self.logger.info(f"Updated agent state: {agent_state}")
                self.memory.set_agent_state(self.agent_id, agent_state)
                self.logger.info(f"Agent state saved for {self.agent_id}")
            except Exception as e:
                self.logger.error(f"Error updating agent state: {e}")
                # Don't raise - this shouldn't fail the task

            # Create dataset for this generation task
            try:
                self.logger.info(f"Creating dataset for task {task.task_id}")
                dataset = {
                    "task_id": task.task_id,
                    "agent_id": self.agent_id,
                    "strategy": strategy,
                    "research_goal": research_goal,
                    "hypothesis_generated": hypothesis.hypothesis_id,
                    "generation_time": time.time(),
                    "input_parameters": task.params,
                    "output_quality_metrics": {
                        "content_length": len(hypothesis.content),
                        "summary_length": len(hypothesis.summary),
                        "strategy_alignment": 1.0,  # Could be computed based on strategy adherence
                        "novelty_aspects_count": len(response["hypothesis"].get("key_novelty_aspects", [])),
                        "testable_predictions_count": len(response["hypothesis"].get("testable_predictions", []))
                    }
                }
                self.memory.set_dataset(task.task_id, dataset)
                self.logger.info(f"Dataset created and saved for task {task.task_id}")
            except Exception as e:
                self.logger.error(f"Error creating dataset: {e}")
                # Don't raise - this shouldn't fail the task

            return {
                "hypothesis_id": hypothesis.hypothesis_id,
                "summary": hypothesis.summary,
                "strategy": strategy
            }
            
        except Exception as e:
            self.logger.error(f"Error generating hypothesis: {str(e)}")
            raise
    
    async def _simulate_debate(self, task: Task) -> Dict:
        """Simulate a scientific debate to refine a hypothesis."""
        self.logger.info(f"Simulating debate for task {task.task_id}")
        
        # Get research goal and hypothesis
        research_goal = self.memory.metadata.get("research_goal", "")
        hypothesis_id = task.params.get("hypothesis_id")
        
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for debate task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # Create debate prompt
        prompt = f"""
        You are simulating a scientific debate among experts to refine and improve a research hypothesis.
        
        Research goal: {research_goal}
        
        Original hypothesis:
        {hypothesis.content}
        
        Please simulate a debate among multiple scientific experts (at least 3) with diverse perspectives 
        on this hypothesis. Each expert should provide constructive criticism, suggest improvements, 
        and identify potential flaws or limitations.
        
        After the debate, synthesize the key insights and generate an improved version of the hypothesis 
        that addresses the main concerns raised.
        """
        
        system_prompt = "You are an AI co-scientist that specializes in simulating scientific debates to improve research hypotheses."
        
        schema = {
            "debate": {
                "participants": [{"name": "string", "expertise": "string", "perspective": "string"}],
                "rounds": [{"speaker": "string", "argument": "string"}]
            },
            "key_insights": ["string"],
            "improved_hypothesis": {
                "content": "string",
                "summary": "string"
            }
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens

            # Create a new hypothesis based on the improved version
            improved_hypothesis = ResearchHypothesis(
                content=response["improved_hypothesis"]["content"],
                summary=response["improved_hypothesis"]["summary"],
                agent_id=self.agent_id,
                metadata={
                    "original_hypothesis_id": hypothesis_id,
                    "debate": response["debate"],
                    "key_insights": response["key_insights"],
                    "generation_strategy": "scientific_debate"
                }
            )
            
            # Add the improved hypothesis to memory
            self.memory.add_hypothesis(improved_hypothesis)
            
            return {
                "original_hypothesis_id": hypothesis_id,
                "improved_hypothesis_id": improved_hypothesis.hypothesis_id,
                "key_insights": response["key_insights"]
            }
            
        except Exception as e:
            self.logger.error(f"Error simulating debate: {str(e)}")
            raise
    
    def _create_literature_exploration_prompt(self, research_goal: str, plan_config: Dict) -> str:
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
    
    def _create_scientific_debate_prompt(self, research_goal: str, plan_config: Dict) -> str:
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
    
    def _create_assumptions_identification_prompt(self, research_goal: str, plan_config: Dict) -> str:
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
    
    def _create_research_expansion_prompt(self, research_goal: str, plan_config: Dict, top_summaries: str = "") -> str:
        """Create a prompt for research expansion-based hypothesis generation."""
        # If top_summaries is not provided, get top-ranked hypotheses to build upon
        if not top_summaries:
            top_hypotheses = self.memory.get_top_hypotheses(3)
            top_summaries = "\n".join([f"- {h.summary}" for h in top_hypotheses]) if top_hypotheses else "No existing hypotheses yet."
        
        constraints = ', '.join(plan_config.get('constraints', []))
        preferences = ', '.join(plan_config.get('preferences', []))
        
        prompt = f"""
        You are generating a new research hypothesis that builds upon and expands existing research directions.
        
        Research goal:
        {research_goal}
        
        Top existing hypotheses:
        {top_summaries}
        
        Research constraints:
        {constraints}
        
        Research preferences:
        {preferences}
        
        Please generate a novel research hypothesis that builds upon the existing hypotheses while addressing the research goal.
        Your hypothesis should be specific, testable, and expand the research in a promising direction.
        """
        
        return prompt


class ProteinAgent(Agent):

    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the protein analysis agent."""
        super().__init__(agent_id, "protein", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        task_type = task.task_type
        
        if task_type == "generate-protein-report":
            return await self._generate_protein_report(task)
        else:
            raise ValueError(f"Unsupported task type for ProteinAgent: {task_type}")
    
    async def _generate_protein_report(self, task: Task) -> Dict:
        self.logger.info(f"Generating Protein Report  for task {task.task_id}")
        
        # Get hypothesis
        hypothesis_id = task.params.get("hypothesis_id")
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        schema = {
            "protein_A": {
                "name": "string",
                "residue_connect": "string",
            },
            "protein_B": {
                "name": "string",
                "residue_connect": "string",
            },
        }

        prompt = f"""You are an agent that must respond according to the specified schema.
        Please analyze this hypothesis: {hypothesis.content}.
        It should contain a scientific inquiry corresponding to a protein-protein interaction.
        For these two proteins, provide their names and important residue for interaction in the appropriate fields of the json schema.
        Enclose property names in double quotes.
        """
        
        try:
            # Generate the hypothesis with the LLM
            if DEBUG:
                self.logger.info(f"Generating with prompt: {prompt}")
            response_data = self.llm.generate_with_json_output(prompt, schema)
            
            if DEBUG:
                self.logger.info(f"Protein Analysis Output : {response_data}")

            # Unpack the response data
            if isinstance(response_data, tuple) and len(response_data) == 3:
                response, prompt_tokens, completion_tokens = response_data
                
                # Update token counts
                self.total_calls += 1
                self.total_prompt_tokens += int(prompt_tokens)
                self.total_completion_tokens += int(completion_tokens)
            else:
                # Handle the case where the response is not a tuple
                response = response_data
                self.total_calls += 1
            
            return 
            # TODO
            
        except Exception as e:
            self.logger.error(f"Error generating hypothesis: {str(e)}")
            raise
    


class ReflectionAgent(Agent):
    """
    Agent responsible for critically reviewing hypotheses for correctness, quality, and novelty.
    
    This agent performs several types of reviews:
    - Initial review
    - Full review with web search
    - Deep verification review
    - Observation review
    - Simulation review
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the reflection agent."""
        super().__init__(agent_id, "reflection", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute a task to review a hypothesis."""
        task_type = task.task_type
        
        if task_type == "initial_review":
            return await self._perform_initial_review(task)
        elif task_type == "deep_verification":
            return await self._perform_deep_verification(task)
        elif task_type == "observation_review":
            return await self._perform_observation_review(task)
        elif task_type == "debate_comparison":
            return await self._perform_debate_comparison(task)
        else:
            raise ValueError(f"Unsupported task type for ReflectionAgent: {task_type}")
    
    async def _perform_initial_review(self, task: Task) -> Dict:
        """Perform an initial review of a hypothesis."""
        self.logger.info(f"Performing initial review for task {task.task_id}")
        
        # Get hypothesis
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for review task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # Create review prompt
        if EXTERNAL_PROMPTS:
            prompt = create_initial_review_prompt(hypothesis.content)
        else:
            prompt = f"""
        You are performing an initial review of a research hypothesis. This is a quick assessment 
        to determine if the hypothesis has any obvious flaws or merits further investigation.
        
        Research goal:
        {research_goal}
        
        Hypothesis:
        {hypothesis.content}
        
        Please evaluate this hypothesis on the following criteria:
        1. Relevance - How well does it address the research goal?
        2. Correctness - Are there any obvious scientific errors or inconsistencies?
        3. Novelty - Does it appear to present new ideas?
        4. Testability - Can it be empirically validated?
        5. Safety - Does it raise any ethical concerns?
        
        Provide a brief assessment for each criterion and an overall recommendation on whether
        this hypothesis merits further review.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="reflection",
                                                role="critically review research hypotheses")
        
        schema = {
            "assessment": {
                "relevance": {"score": "number", "rationale": "string"},
                "correctness": {"score": "number", "rationale": "string"},
                "novelty": {"score": "number", "rationale": "string"},
                "testability": {"score": "number", "rationale": "string"},
                "safety": {"score": "number", "rationale": "string"}
            },
            "overall_recommendation": "string",
            "merits_further_review": "boolean",
            "primary_concerns": ["string"],
            "primary_strengths": ["string"]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens

            # Add the review to the hypothesis
            review = {
                "review_id": str(time.time()),
                "review_type": "initial",
                "reviewer_id": self.agent_id,
                "assessment": response["assessment"],
                "overall_recommendation": response["overall_recommendation"],
                "merits_further_review": response["merits_further_review"],
                "primary_concerns": response["primary_concerns"],
                "primary_strengths": response["primary_strengths"]
            }
            
            hypothesis.add_review(review)
            self.memory.update_hypothesis(hypothesis)
            
            return {
                "hypothesis_id": hypothesis_id,
                "review_id": review["review_id"],
                "merits_further_review": response["merits_further_review"]
            }
            
        except Exception as e:
            self.logger.error(f"Error performing initial review: {str(e)}")
            raise
    
    async def _full_review(self, task: Task) -> Dict:
        """Perform a full review of a hypothesis with web search."""
        self.logger.info(f"Performing full review for task {task.task_id}")
        
        # Get the hypothesis to review
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for review task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # Get research goal from memory
        research_goal = self.memory.metadata.get("research_goal", "")
        plan_config = self.memory.metadata.get("research_plan_config", {})
        
        # Create review prompt
        prompt = f"""
        You are performing a comprehensive review of a research hypothesis. This is an in-depth assessment 
        that considers the scientific merit, novelty, and feasibility of the hypothesis.
        
        Research goal:
        {research_goal}
        
        Hypothesis:
        {hypothesis.content}
        
        Please conduct a thorough evaluation of this hypothesis addressing:
        
        1. Scientific validity:
           - Is the hypothesis consistent with established scientific principles?
           - Are there any logical flaws or inconsistencies in the reasoning?
           - Is it compatible with existing empirical evidence?
        
        2. Novelty:
           - How does this hypothesis differ from existing theories or models?
           - Does it introduce genuinely new concepts or merely reframe existing ideas?
           - Has this hypothesis (or a very similar one) been proposed before?
        
        3. Testability:
           - Can the hypothesis be empirically tested?
           - What specific experiments or observations would be needed to validate it?
           - Are these tests feasible with current technology and methods?
        
        4. Potential impact:
           - If correct, how would this hypothesis advance the field?
           - What new questions or research directions might it open?
           - Could it have practical applications or implications?
        
        5. Limitations:
           - What are the key assumptions underlying this hypothesis?
           - Under what conditions might the hypothesis not hold?
           - What are the boundaries of its explanatory power?
        
        Provide a detailed assessment with specific references to the hypothesis content.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="reflection",
                                                role="conduct comprehensive scientific reviews of research hypotheses")
        
        schema = {
            "scientific_validity": {
                "assessment": "string",
                "score": "number",
                "strengths": ["string"],
                "weaknesses": ["string"]
            },
            "novelty": {
                "assessment": "string",
                "score": "number",
                "comparison_to_existing_work": "string"
            },
            "testability": {
                "assessment": "string",
                "score": "number",
                "proposed_experiments": ["string"]
            },
            "potential_impact": {
                "assessment": "string",
                "score": "number",
                "potential_applications": ["string"]
            },
            "limitations": {
                "assessment": "string",
                "key_assumptions": ["string"],
                "boundary_conditions": ["string"]
            },
            "overall_assessment": "string",
            "overall_score": "number",
            "recommendation": "string"
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens

            # Add the review to the hypothesis
            review = {
                "review_id": str(time.time()),
                "review_type": "full",
                "reviewer_id": self.agent_id,
                "scientific_validity": response["scientific_validity"],
                "novelty": response["novelty"],
                "testability": response["testability"],
                "potential_impact": response["potential_impact"],
                "limitations": response["limitations"],
                "overall_assessment": response["overall_assessment"],
                "overall_score": response["overall_score"],
                "recommendation": response["recommendation"]
            }
            
            hypothesis.add_review(review)
            self.memory.update_hypothesis(hypothesis)
            
            return {
                "hypothesis_id": hypothesis_id,
                "review_id": review["review_id"],
                "overall_score": response["overall_score"],
                "recommendation": response["recommendation"]
            }
            
        except Exception as e:
            self.logger.error(f"Error performing full review: {str(e)}")
            raise
    
    async def _deep_verification(self, task: Task) -> Dict:
        """Perform a deep verification review by breaking down assumptions."""
        self.logger.info(f"Performing deep verification for task {task.task_id}")
        
        # Get the hypothesis to review
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for verification task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # Create verification prompt
        prompt = f"""
        You are performing a deep verification review of a research hypothesis. Your task is to 
        break down the hypothesis into its constituent assumptions and verify each one independently.
        
        Hypothesis:
        {hypothesis.content}
        
        Please follow these steps:
        
        1. Decompose the hypothesis into its fundamental assumptions and claims
        2. For each assumption:
           - State it clearly and precisely
           - Assess its plausibility based on current scientific knowledge
           - Identify any evidence that supports or contradicts it
           - Determine if it's a fundamental assumption (if false, invalidates the hypothesis) or auxiliary
        
        3. Identify any logical dependencies between assumptions
        
        4. Assess the overall logical structure of the hypothesis:
           - Is it internally consistent?
           - Does the conclusion follow from the premises?
           - Are there any logical fallacies or reasoning errors?
        
        5. Provide an overall assessment of the hypothesis's validity
        
        Be thorough and rigorous in your analysis. Your goal is to determine if there are any fundamental 
        flaws that would invalidate the hypothesis.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="reflection",
                                                role="conduct deep verification of scientific hypotheses by analyzing their assumptions")
        
        schema = {
            "assumptions": [
                {
                    "statement": "string",
                    "plausibility": "string",
                    "supporting_evidence": "string",
                    "contradicting_evidence": "string",
                    "is_fundamental": "boolean"
                }
            ],
            "logical_structure": {
                "dependencies": "string",
                "consistency": "string",
                "reasoning_quality": "string",
                "identified_fallacies": ["string"]
            },
            "overall_assessment": "string",
            "invalidating_flaws": ["string"],
            "validity_score": "number"
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens

            # Add the verification to the hypothesis
            verification = {
                "review_id": str(time.time()),
                "review_type": "deep_verification",
                "reviewer_id": self.agent_id,
                "assumptions": response["assumptions"],
                "logical_structure": response["logical_structure"],
                "overall_assessment": response["overall_assessment"],
                "invalidating_flaws": response["invalidating_flaws"],
                "validity_score": response["validity_score"]
            }
            
            hypothesis.add_review(verification)
            self.memory.update_hypothesis(hypothesis)
            
            return {
                "hypothesis_id": hypothesis_id,
                "review_id": verification["review_id"],
                "validity_score": response["validity_score"],
                "has_invalidating_flaws": len(response["invalidating_flaws"]) > 0
            }
            
        except Exception as e:
            self.logger.error(f"Error performing deep verification: {str(e)}")
            raise
    
    async def _observation_review(self, task: Task) -> Dict:
        """Review if the hypothesis can account for existing observations."""
        self.logger.info(f"Performing observation review for task {task.task_id}")
        
        # Get the hypothesis to review
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for observation review task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # For this example, we'll use simulated observations
        # In a real implementation, these would come from literature search or databases
        observations = task.params.get("observations", [
            "Observation 1: Description of the first relevant observation from literature",
            "Observation 2: Description of the second relevant observation from literature",
            "Observation 3: Description of the third relevant observation from literature"
        ])
        
        # Create observation review prompt
        prompt = f"""
        You are reviewing whether a research hypothesis can account for existing observations in the literature.
        
        Hypothesis:
        {hypothesis.content}
        
        Key observations from the literature:
        {observations}
        
        For each observation, please:
        1. Analyze whether the hypothesis can explain it
        2. Compare how well the hypothesis explains it versus existing theories
        3. Identify any observations that the hypothesis cannot explain
        4. Suggest potential modifications to the hypothesis that could address any inconsistencies
        
        Provide a comprehensive assessment of how well the hypothesis accounts for these observations.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="reflection",
                                                role="evaluate how well hypotheses explain existing observations")
        
        schema = {
            "explanatory_power": [
                {
                    "observation": "string",
                    "can_explain": "boolean",
                    "explanation_quality": "string",
                    "comparison_to_existing_theories": "string"
                }
            ],
            "unexplained_observations": ["string"],
            "suggested_modifications": ["string"],
            "overall_assessment": "string",
            "explanatory_score": "number"
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Add the observation review to the hypothesis
            review = {
                "review_id": str(time.time()),
                "review_type": "observation",
                "reviewer_id": self.agent_id,
                "explanatory_power": response["explanatory_power"],
                "unexplained_observations": response["unexplained_observations"],
                "suggested_modifications": response["suggested_modifications"],
                "overall_assessment": response["overall_assessment"],
                "explanatory_score": response["explanatory_score"]
            }
            
            hypothesis.add_review(review)
            self.memory.update_hypothesis(hypothesis)
            
            return {
                "hypothesis_id": hypothesis_id,
                "review_id": review["review_id"],
                "explanatory_score": response["explanatory_score"]
            }
            
        except Exception as e:
            self.logger.error(f"Error performing observation review: {str(e)}")
            raise
    
    async def _simulation_review(self, task: Task) -> Dict:
        """Review a hypothesis by simulating its mechanism of action."""
        self.logger.info(f"Performing simulation review for task {task.task_id}")
        
        # Get the hypothesis to review
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for simulation review task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # Create simulation prompt
        prompt = f"""
        You are simulating the mechanism of action described in a research hypothesis to evaluate its plausibility.
        
        Hypothesis:
        {hypothesis.content}
        
        Please simulate the mechanism step by step:
        
        1. Break down the key processes or interactions described in the hypothesis
        2. For each step in the mechanism:
           - Describe what happens at a detailed level
           - Assess whether this step is consistent with established scientific principles
           - Identify any potential bottlenecks, rate-limiting factors, or failures that could occur
        
        3. Simulate how the mechanism would operate under different conditions:
           - Normal/optimal conditions
           - Edge cases or extreme conditions
           - In the presence of potential confounding factors
        
        4. Predict what observable outcomes would result if this mechanism is correct
        
        5. Identify potential failure scenarios and their consequences
        
        Provide a detailed simulation and assessment of the mechanism's plausibility.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="reflection",
                                                role="simulate and evaluate the mechanisms described in research hypotheses")
        
        schema = {
            "mechanism_steps": [
                {
                    "step_description": "string",
                    "scientific_consistency": "string",
                    "potential_issues": ["string"]
                }
            ],
            "simulation_outcomes": {
                "normal_conditions": "string",
                "edge_cases": "string",
                "with_confounders": "string"
            },
            "predicted_observables": ["string"],
            "failure_scenarios": [
                {
                    "scenario": "string",
                    "likelihood": "string",
                    "consequences": "string"
                }
            ],
            "overall_plausibility": "string",
            "plausibility_score": "number"
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Add the simulation review to the hypothesis
            review = {
                "review_id": str(time.time()),
                "review_type": "simulation",
                "reviewer_id": self.agent_id,
                "mechanism_steps": response["mechanism_steps"],
                "simulation_outcomes": response["simulation_outcomes"],
                "predicted_observables": response["predicted_observables"],
                "failure_scenarios": response["failure_scenarios"],
                "overall_plausibility": response["overall_plausibility"],
                "plausibility_score": response["plausibility_score"]
            }
            
            hypothesis.add_review(review)
            self.memory.update_hypothesis(hypothesis)
            
            return {
                "hypothesis_id": hypothesis_id,
                "review_id": review["review_id"],
                "plausibility_score": response["plausibility_score"]
            }
            
        except Exception as e:
            self.logger.error(f"Error performing simulation review: {str(e)}")
            raise


class RankingAgent(Agent):
    """
    Agent responsible for comparing and ranking hypotheses in tournaments using Elo ratings.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the ranking agent."""
        super().__init__(agent_id, "ranking", llm, memory)
        
        # Elo rating parameters
        self.k_factor = 32  # How quickly ratings change (higher = faster changes)
        self.default_rating = 1200  # Default rating for new hypotheses
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute a ranking task."""
        task_type = task.task_type
        
        if task_type == "tournament_match":
            return await self._tournament_match(task)
        elif task_type == "update_rankings":
            return await self._update_rankings(task)
        else:
            raise ValueError(f"Unsupported task type for RankingAgent: {task_type}")
    
    async def _tournament_match(self, task: Task) -> Dict:
        """Conduct a tournament match between two hypotheses."""
        self.logger.info(f"Conducting tournament match for task {task.task_id}")
        
        # Get the hypotheses to compare
        hypothesis1_id = task.params.get("hypothesis1_id")
        hypothesis2_id = task.params.get("hypothesis2_id")
        
        if not hypothesis1_id or not hypothesis2_id:
            raise ValueError("Both hypothesis1_id and hypothesis2_id must be provided")
        
        hypothesis1 = self.memory.get_hypothesis(hypothesis1_id)
        hypothesis2 = self.memory.get_hypothesis(hypothesis2_id)
        
        if not hypothesis1 or not hypothesis2:
            raise ValueError(f"One or both hypotheses not found in memory")
        
        # Get research goal from memory
        research_goal = self.memory.metadata.get("research_goal", "")
        plan_config = self.memory.metadata.get("research_plan_config", {})
        
        # Get evaluation criteria from the research plan
        criteria = plan_config.get("evaluation_criteria", ["novelty", "plausibility", "testability"])
        
        # Create debate prompt
        prompt = f"""
        You are judging a scientific debate between two competing research hypotheses.
        
        Research goal:
        {research_goal}
        
        Hypothesis A:
        {hypothesis1.content}
        
        Hypothesis B:
        {hypothesis2.content}
        
        Please evaluate these hypotheses on the following criteria:
        {', '.join(criteria)}
        
        For each criterion, compare the two hypotheses and determine which one is stronger.
        Then, provide an overall judgment of which hypothesis is better overall, explaining your reasoning.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="ranking",
                                                role="compare and rank research hypotheses")
        
        schema = {
            "criteria_comparison": [
                {
                    "criterion": "string",
                    "hypothesis_a_strengths": "string",
                    "hypothesis_b_strengths": "string",
                    "winner": "string"  # "A", "B", or "tie"
                }
            ],
            "overall_winner": "string",  # "A", "B", or "tie"
            "reasoning": "string",
            "winner_key_advantages": ["string"],
            "loser_key_weaknesses": ["string"]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Determine the winner and update Elo ratings
            winner_id = None
            loser_id = None
            
            if "A" in response["overall_winner"]:
                winner_id = hypothesis1_id
                loser_id = hypothesis2_id
            elif "B" in response["overall_winner"]:
                winner_id = hypothesis2_id
                loser_id = hypothesis1_id
            
            # Only update Elo if there's a clear winner
            if winner_id and loser_id:
                winner = self.memory.get_hypothesis(winner_id)
                loser = self.memory.get_hypothesis(loser_id)
                
                # Calculate new Elo ratings
                expected_winner = self._calculate_expected_score(winner.elo_rating, loser.elo_rating)
                expected_loser = self._calculate_expected_score(loser.elo_rating, winner.elo_rating)
                
                # Update ratings
                winner.elo_rating += self.k_factor * (1 - expected_winner)
                loser.elo_rating += self.k_factor * (0 - expected_loser)
                
                # Update hypotheses in memory
                self.memory.update_hypothesis(winner)
                self.memory.update_hypothesis(loser)
            
            # Record the match result
            match_result = {
                "match_id": str(time.time()),
                "hypothesis1_id": hypothesis1_id,
                "hypothesis2_id": hypothesis2_id,
                "criteria_comparison": response["criteria_comparison"],
                "overall_winner": response["overall_winner"],
                "reasoning": response["reasoning"],
                "winner_key_advantages": response["winner_key_advantages"],
                "loser_key_weaknesses": response["loser_key_weaknesses"]
            }
            
            # Add the match result to both hypotheses
            hypothesis1.add_tournament_match(match_result)
            hypothesis2.add_tournament_match(match_result)
            
            # Update hypotheses in memory
            self.memory.update_hypothesis(hypothesis1)
            self.memory.update_hypothesis(hypothesis2)
            
            # Add match to tournament state
            tournament_state = self.memory.tournament_state
            tournament_state["matches"].append(match_result)
            self.memory.update_tournament_state(tournament_state)
            
            return {
                "match_id": match_result["match_id"],
                "hypothesis1_id": hypothesis1_id,
                "hypothesis2_id": hypothesis2_id,
                "winner": response["overall_winner"],
                "hypothesis1_new_rating": hypothesis1.elo_rating,
                "hypothesis2_new_rating": hypothesis2.elo_rating
            }
            
        except Exception as e:
            self.logger.error(f"Error conducting tournament match: {str(e)}")
            raise
    
    async def _update_rankings(self, task: Task) -> Dict:
        """Update the overall rankings based on Elo ratings."""
        self.logger.info(f"Updating rankings for task {task.task_id}")
        
        # Get all hypotheses
        hypotheses = self.memory.get_all_hypotheses()
        
        # Sort by Elo rating
        ranked_hypotheses = sorted(hypotheses, key=lambda h: h.elo_rating, reverse=True)
        
        # Create rankings
        rankings = [
            {
                "rank": i + 1,
                "hypothesis_id": h.hypothesis_id,
                "elo_rating": h.elo_rating,
                "summary": h.summary
            }
            for i, h in enumerate(ranked_hypotheses)
        ]
        
        # Update tournament state
        tournament_state = self.memory.tournament_state
        tournament_state["rankings"] = rankings
        
        # Calculate statistics
        match_count = len(tournament_state["matches"])
        avg_rating = sum(h.elo_rating for h in hypotheses) / max(1, len(hypotheses))
        rating_std = (sum((h.elo_rating - avg_rating) ** 2 for h in hypotheses) / max(1, len(hypotheses))) ** 0.5
        
        statistics = {
            "match_count": match_count,
            "hypothesis_count": len(hypotheses),
            "avg_rating": avg_rating,
            "rating_std": rating_std,
            "timestamp": time.time()
        }
        
        tournament_state["statistics"] = statistics
        self.memory.update_tournament_state(tournament_state)
        
        return {
            "rankings": rankings[:10],  # Return top 10
            "statistics": statistics
        }
    
    def _calculate_expected_score(self, rating_a: float, rating_b: float) -> float:
        """Calculate the expected score for a player with rating_a against rating_b."""
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


class EvolutionAgent(Agent):
    """
    Agent responsible for improving hypotheses through various evolution strategies.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the evolution agent."""
        super().__init__(agent_id, "evolution", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute an evolution task."""
        task_type = task.task_type
        
        if task_type == "improve_hypothesis":
            return await self._improve_hypothesis(task)
        elif task_type == "evolve_hypothesis":
            return await self._improve_hypothesis(task)  # Use same method for evolution
        elif task_type == "combine_hypotheses":
            return await self._combine_hypotheses(task)
        elif task_type == "simplify_hypothesis":
            return await self._simplify_hypothesis(task)
        elif task_type == "out_of_box_thinking":
            return await self._out_of_box_thinking(task)
        else:
            raise ValueError(f"Unsupported task type for EvolutionAgent: {task_type}")
    
    async def _improve_hypothesis(self, task: Task) -> Dict:
        """Improve a hypothesis by addressing its weaknesses."""
        self.logger.info(f"Improving hypothesis for task {task.task_id}")
        
        # Get the hypothesis to improve
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for improvement task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # Get reviews to identify weaknesses
        reviews = hypothesis.reviews
        if not reviews:
            self.logger.warning(f"No reviews found for hypothesis {hypothesis_id}")
        
        # Extract weaknesses from reviews
        weaknesses = []
        for review in reviews:
            if review.get("review_type") == "full":
                if "scientific_validity" in review:
                    weaknesses.extend(review["scientific_validity"].get("weaknesses", []))
                if "limitations" in review:
                    weaknesses.extend(review["limitations"].get("key_assumptions", []))
            elif review.get("review_type") == "deep_verification":
                weaknesses.extend(review.get("invalidating_flaws", []))
            elif review.get("review_type") == "initial":
                weaknesses.extend(review.get("primary_concerns", []))
        
        # Get research goal from memory
        research_goal = self.memory.metadata.get("research_goal", "")
        
        # Create improvement prompt
        prompt = f"""
        You are improving a research hypothesis by addressing its identified weaknesses.
        
        Research goal:
        {research_goal}
        
        Original hypothesis:
        {hypothesis.content}
        
        Identified weaknesses:
        {weaknesses}
        
        Please create an improved version of this hypothesis that:
        1. Addresses the identified weaknesses
        2. Maintains or enhances the strengths of the original hypothesis
        3. Remains focused on the original research goal
        4. Is more robust, precise, and testable
        
        Explain the specific improvements you've made and how they address each weakness.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="evolution",
                                                role="improve research hypotheses by addressing their weaknesses")
        
        schema = {
            "improved_hypothesis": {
                "content": "string",
                "summary": "string"
            },
            "improvements": [
                {
                    "original_weakness": "string",
                    "improvement_made": "string",
                    "rationale": "string"
                }
            ],
            "additional_enhancements": ["string"],
            "evolution_approach": "string"
        }
        
        try:
            result = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)

            # Handle different return types from different LLM implementations
            if isinstance(result, tuple):
                response, prompt_tokens, completion_tokens = result
                self.total_calls += 1
                self.total_prompt_tokens += prompt_tokens
                self.total_completion_tokens += completion_tokens
            else:
                response = result
                self.total_calls += 1
            
            # Create a new hypothesis based on the improved version
            improved_hypothesis = ResearchHypothesis(
                content=response["improved_hypothesis"]["content"],
                summary=response["improved_hypothesis"]["summary"],
                agent_id=self.agent_id,
                #hypothesis_id= field(default_factory=lambda: str(uuid.uuid4()))
                metadata={
                    "original_hypothesis_id": hypothesis_id,
                    "improvements": response["improvements"],
                    "additional_enhancements": response["additional_enhancements"],
                    "evolution_approach": response["evolution_approach"],
                    "evolution_type": "improve"
                }
            )
            self.logger.info(f"Improved hypothesis: \n {improved_hypothesis.to_dict()}")
            # Add the improved hypothesis to memory
            self.memory.add_hypothesis(improved_hypothesis)
            self.memory.save()
            
            return {
                "original_hypothesis_id": hypothesis_id,
                "improved_hypothesis_id": improved_hypothesis.hypothesis_id,
                "improvements": response["improvements"],
                "improved_hypothesis": improved_hypothesis
            }
            
        except Exception as e:
            self.logger.error(f"Error improving hypothesis: {str(e)}")
            raise
    
    async def _combine_hypotheses(self, task: Task) -> Dict:
        """Combine multiple hypotheses into a new, synthesized hypothesis."""
        self.logger.info(f"Combining hypotheses for task {task.task_id}")
        
        # Get the hypotheses to combine
        hypothesis_ids = task.params.get("hypothesis_ids", [])
        if not hypothesis_ids or len(hypothesis_ids) < 2:
            raise ValueError("At least two hypothesis_ids must be provided for combination task")
        
        hypotheses = []
        for h_id in hypothesis_ids:
            h = self.memory.get_hypothesis(h_id)
            if not h:
                raise ValueError(f"Hypothesis {h_id} not found in memory")
            hypotheses.append(h)
        
        # Get research goal from memory
        research_goal = self.memory.metadata.get("research_goal", "")
        
        # Create hypotheses summaries
        hypotheses_content = "\n\n".join([
            f"Hypothesis {i+1}:\n{h.content}"
            for i, h in enumerate(hypotheses)
        ])
        
        # Create combination prompt
        prompt = f"""
        You are combining multiple research hypotheses into a new, synthesized hypothesis.
        
        Research goal:
        {research_goal}
        
        Hypotheses to combine:
        {hypotheses_content}
        
        Please create a new hypothesis that:
        1. Integrates the key insights and strengths from each input hypothesis
        2. Resolves any contradictions or inconsistencies between them
        3. Creates a more comprehensive and powerful explanation than any individual hypothesis
        4. Addresses the research goal more effectively
        
        Explain how you've combined elements from each hypothesis and why this synthesis is superior.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="evolution",
                                                role="synthesize multiple research hypotheses into new, integrated hypotheses")
        
        schema = {
            "combined_hypothesis": {
                "content": "string",
                "summary": "string"
            },
            "integration_approach": "string",
            "elements_from_each": [
                {
                    "hypothesis_number": "number",
                    "elements_incorporated": ["string"],
                    "rationale": "string"
                }
            ],
            "resolved_contradictions": [
                {
                    "contradiction": "string",
                    "resolution": "string"
                }
            ],
            "advantages_of_synthesis": ["string"]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create a new hypothesis based on the combined version
            combined_hypothesis = ResearchHypothesis(
                content=response["combined_hypothesis"]["content"],
                summary=response["combined_hypothesis"]["summary"],
                agent_id=self.agent_id,
                metadata={
                    "original_hypothesis_ids": hypothesis_ids,
                    "integration_approach": response["integration_approach"],
                    "elements_from_each": response["elements_from_each"],
                    "resolved_contradictions": response["resolved_contradictions"],
                    "advantages_of_synthesis": response["advantages_of_synthesis"],
                    "evolution_type": "combine"
                }
            )
            
            # Add the combined hypothesis to memory
            self.memory.add_hypothesis(combined_hypothesis)
            
            return {
                "original_hypothesis_ids": hypothesis_ids,
                "combined_hypothesis_id": combined_hypothesis.hypothesis_id,
                "advantages_of_synthesis": response["advantages_of_synthesis"]
            }
            
        except Exception as e:
            self.logger.error(f"Error combining hypotheses: {str(e)}")
            raise
    
    async def _simplify_hypothesis(self, task: Task) -> Dict:
        """Simplify a complex hypothesis for easier verification and testing."""
        self.logger.info(f"Simplifying hypothesis for task {task.task_id}")
        
        # Get the hypothesis to simplify
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis_id provided for simplification task")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in memory")
        
        # Create simplification prompt
        prompt = f"""
        You are simplifying a complex research hypothesis for easier verification and testing.
        
        Original hypothesis:
        {hypothesis.content}
        
        Please create a simplified version of this hypothesis that:
        1. Preserves the core idea and key insights
        2. Reduces complexity and unnecessary details
        3. Is more clearly testable with specific experiments
        4. Uses more precise and concise language
        
        Focus on making the hypothesis more accessible and easier to validate while maintaining its scientific value.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="evolution",
                                                role="simplify complex hypotheses while preserving their core insights")
        
        schema = {
            "simplified_hypothesis": {
                "content": "string",
                "summary": "string"
            },
            "simplification_approach": "string",
            "preserved_elements": ["string"],
            "removed_elements": ["string"],
            "improved_testability": "string",
            "proposed_experiments": ["string"]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create a new hypothesis based on the simplified version
            simplified_hypothesis = ResearchHypothesis(
                content=response["simplified_hypothesis"]["content"],
                summary=response["simplified_hypothesis"]["summary"],
                agent_id=self.agent_id,
                metadata={
                    "original_hypothesis_id": hypothesis_id,
                    "simplification_approach": response["simplification_approach"],
                    "preserved_elements": response["preserved_elements"],
                    "removed_elements": response["removed_elements"],
                    "improved_testability": response["improved_testability"],
                    "proposed_experiments": response["proposed_experiments"],
                    "evolution_type": "simplify"
                }
            )
            
            # Add the simplified hypothesis to memory
            self.memory.add_hypothesis(simplified_hypothesis)
            
            return {
                "original_hypothesis_id": hypothesis_id,
                "simplified_hypothesis_id": simplified_hypothesis.hypothesis_id,
                "improved_testability": response["improved_testability"]
            }
            
        except Exception as e:
            self.logger.error(f"Error simplifying hypothesis: {str(e)}")
            raise
    
    async def _out_of_box_thinking(self, task: Task) -> Dict:
        """Generate a novel hypothesis using out-of-the-box thinking."""
        self.logger.info(f"Generating out-of-box hypothesis for task {task.task_id}")
        
        # Get research goal from memory
        research_goal = self.memory.metadata.get("research_goal", "")
        plan_config = self.memory.metadata.get("research_plan_config", {})
        
        # Get existing hypotheses for context
        hypotheses = self.memory.get_all_hypotheses()
        top_hypotheses = sorted(hypotheses, key=lambda h: h.elo_rating, reverse=True)[:3]
        
        # Extract current trends
        trends = []
        for h in top_hypotheses:
            for review in h.reviews:
                if "novelty" in review and isinstance(review["novelty"], dict):
                    if "comparison_to_existing_work" in review["novelty"]:
                        trends.append(review["novelty"]["comparison_to_existing_work"])
        
        trends_text = "\n".join(trends) if trends else "No specific trends identified."
        
        # Create out-of-box thinking prompt
        prompt = f"""
        You are generating a novel research hypothesis using out-of-the-box thinking.
        
        Research goal:
        {research_goal}
        
        Current trends in existing hypotheses:
        {trends_text}
        
        Your task is to create a highly original hypothesis that:
        1. Takes a radically different approach from existing hypotheses
        2. Challenges conventional assumptions in the field
        3. Draws inspiration from other scientific domains or paradigms
        4. Offers a fresh perspective on the research goal
        5. Remains scientifically plausible despite its originality
        
        Be bold and creative while ensuring the hypothesis is testable and grounded in scientific principles.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="evolution",
                                                role="generate highly original research hypotheses using out-of-the-box thinking")
        
        schema = {
            "novel_hypothesis": {
                "content": "string",
                "summary": "string"
            },
            "key_innovations": ["string"],
            "challenged_assumptions": ["string"],
            "cross_domain_inspirations": ["string"],
            "potential_impact": "string",
            "testability_approach": "string"
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create a new hypothesis
            novel_hypothesis = ResearchHypothesis(
                content=response["novel_hypothesis"]["content"],
                summary=response["novel_hypothesis"]["summary"],
                agent_id=self.agent_id,
                metadata={
                    "key_innovations": response["key_innovations"],
                    "challenged_assumptions": response["challenged_assumptions"],
                    "cross_domain_inspirations": response["cross_domain_inspirations"],
                    "potential_impact": response["potential_impact"],
                    "testability_approach": response["testability_approach"],
                    "evolution_type": "out_of_box"
                }
            )
            
            # Add the novel hypothesis to memory
            self.memory.add_hypothesis(novel_hypothesis)
            
            return {
                "novel_hypothesis_id": novel_hypothesis.hypothesis_id,
                "key_innovations": response["key_innovations"],
                "cross_domain_inspirations": response["cross_domain_inspirations"]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating out-of-box hypothesis: {str(e)}")
            raise


class ProximityAgent(Agent):
    """
    Agent responsible for calculating similarity between hypotheses and building a proximity graph.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the proximity agent."""
        super().__init__(agent_id, "proximity", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute a proximity task."""
        task_type = task.task_type
        
        if task_type == "calculate_similarity":
            return await self._calculate_similarity(task)
        elif task_type == "build_proximity_graph":
            return await self._build_proximity_graph(task)
        else:
            raise ValueError(f"Unsupported task type for ProximityAgent: {task_type}")
    
    async def _calculate_similarity(self, task: Task) -> Dict:
        """Calculate similarity between two hypotheses."""
        self.logger.info(f"Calculating similarity for task {task.task_id}")
        
        # Get the hypotheses to compare
        hypothesis1_id = task.params.get("hypothesis1_id")
        hypothesis2_id = task.params.get("hypothesis2_id")
        
        if not hypothesis1_id or not hypothesis2_id:
            raise ValueError("Both hypothesis1_id and hypothesis2_id must be provided")
        
        hypothesis1 = self.memory.get_hypothesis(hypothesis1_id)
        hypothesis2 = self.memory.get_hypothesis(hypothesis2_id)
        
        if not hypothesis1 or not hypothesis2:
            raise ValueError(f"One or both hypotheses not found in memory")
        
        # Create similarity prompt
        prompt = f"""
        You are calculating the similarity between two research hypotheses.
        
        Hypothesis 1:
        {hypothesis1.content}
        
        Hypothesis 2:
        {hypothesis2.content}
        
        Please analyze these hypotheses and determine their similarity across multiple dimensions:
        
        1. Conceptual similarity - Do they propose similar concepts or mechanisms?
        2. Methodological similarity - Do they suggest similar experimental approaches?
        3. Domain overlap - Do they address similar aspects of the research domain?
        4. Predictive similarity - Would they make similar predictions or have similar implications?
        
        Provide a detailed analysis and a numerical similarity score from 0 (completely different) to 1 (nearly identical).
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="proximity",
                                                role="analyze similarity between research hypotheses")
        
        schema = {
            "similarity_dimensions": {
                "conceptual": {"score": "number", "explanation": "string"},
                "methodological": {"score": "number", "explanation": "string"},
                "domain": {"score": "number", "explanation": "string"},
                "predictive": {"score": "number", "explanation": "string"}
            },
            "shared_elements": ["string"],
            "key_differences": ["string"],
            "overall_similarity_score": "number",
            "detailed_explanation": "string"
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Record the similarity result
            similarity = {
                "hypothesis1_id": hypothesis1_id,
                "hypothesis2_id": hypothesis2_id,
                "similarity_dimensions": response["similarity_dimensions"],
                "shared_elements": response["shared_elements"],
                "key_differences": response["key_differences"],
                "overall_similarity_score": response["overall_similarity_score"],
                "detailed_explanation": response["detailed_explanation"]
            }
            
            # Get or create agent state
            agent_state = self.memory.get_agent_state(self.agent_id) or {
                "similarity_cache": {}
            }
            
            # Cache the similarity result
            if "similarity_cache" not in agent_state:
                agent_state["similarity_cache"] = {}
            
            # Use a consistent key format regardless of order
            key_pair = tuple(sorted([hypothesis1_id, hypothesis2_id]))
            agent_state["similarity_cache"][str(key_pair)] = similarity
            
            # Update agent state in memory
            self.memory.set_agent_state(self.agent_id, agent_state)
            
            return {
                "hypothesis1_id": hypothesis1_id,
                "hypothesis2_id": hypothesis2_id,
                "overall_similarity_score": response["overall_similarity_score"]
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            raise
    
    async def _build_proximity_graph(self, task: Task) -> Dict:
        """Build a proximity graph of all hypotheses."""
        self.logger.info(f"Building proximity graph for task {task.task_id}")
        
        # Get all hypotheses
        hypotheses = self.memory.get_all_hypotheses()
        hypothesis_ids = [h.hypothesis_id for h in hypotheses]
        
        # Get existing similarity cache
        agent_state = self.memory.get_agent_state(self.agent_id) or {
            "similarity_cache": {}
        }
        similarity_cache = agent_state.get("similarity_cache", {})
        
        # Build graph structure
        graph = {
            "nodes": [
                {
                    "id": h.hypothesis_id,
                    "summary": h.summary,
                    "elo_rating": h.elo_rating
                }
                for h in hypotheses
            ],
            "edges": []
        }
        
        # Add edges from cache
        for key, similarity in similarity_cache.items():
            h1_id, h2_id = eval(key)  # Convert string representation of tuple back to tuple
            
            if h1_id in hypothesis_ids and h2_id in hypothesis_ids:
                # Only include hypotheses that still exist
                graph["edges"].append({
                    "source": h1_id,
                    "target": h2_id,
                    "similarity": similarity["overall_similarity_score"]
                })
        
        # Calculate cluster statistics
        # This is a simple implementation - in a real system, you might use more sophisticated clustering algorithms
        clusters = self._identify_clusters(graph)
        
        # Update agent state with the graph
        agent_state["proximity_graph"] = graph
        agent_state["clusters"] = clusters
        
        # Update agent state in memory
        self.memory.set_agent_state(self.agent_id, agent_state)
        
        return {
            "graph": graph,
            "clusters": clusters,
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"])
        }
    
    def _identify_clusters(self, graph: Dict) -> List[Dict]:
        """
        Identify clusters in the proximity graph.
        This is a simple implementation that identifies connected components based on a similarity threshold.
        """
        # Create an adjacency list representation
        adjacency = {}
        for node in graph["nodes"]:
            adjacency[node["id"]] = []
        
        # Add edges with similarity above threshold
        threshold = 0.7  # Similarity threshold for clustering
        for edge in graph["edges"]:
            if edge["similarity"] >= threshold:
                adjacency[edge["source"]].append(edge["target"])
                adjacency[edge["target"]].append(edge["source"])
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        
        for node_id in adjacency:
            if node_id not in visited:
                # BFS to find all nodes in this cluster
                cluster = []
                queue = [node_id]
                visited.add(node_id)
                
                while queue:
                    current = queue.pop(0)
                    cluster.append(current)
                    
                    for neighbor in adjacency[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                clusters.append({
                    "cluster_id": len(clusters),
                    "node_ids": cluster,
                    "size": len(cluster)
                })
        
        return clusters


class ExperimentAgent(Agent):
    """
    Agent responsible for designing and analyzing experiments to test hypotheses.
    
    This agent performs several types of tasks:
    - Experimental design
    - Implementation planning
    - Result analysis
    - Refinement recommendations
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the experiment agent."""
        super().__init__(agent_id, "experiment", llm, memory)
    
    async def process_task(self, task: Task) -> Dict:
        """Process a task assigned to this agent."""
        if task.task_type == "design_experiment":
            return await self._design_experiment(task)
        elif task.task_type == "analyze_results":
            return await self._analyze_results(task)
        elif task.task_type == "recommend_refinements":
            return await self._recommend_refinements(task)
        else:
            raise ValueError(f"Unknown task type for experiment agent: {task.task_type}")
    
    async def _design_experiment(self, task: Task) -> Dict:
        """Design an experiment to test a hypothesis."""
        self.logger.info(f"Designing experiment for task {task.task_id}")
        
        # Get hypothesis to test
        hypothesis_id = task.params.get("hypothesis_id")
        if not hypothesis_id:
            raise ValueError("No hypothesis ID provided for experiment design")
        
        hypothesis = self.memory.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        
        # Create experiment design prompt
        prompt = f"""
        You are designing an experiment to test a scientific hypothesis.
        
        Hypothesis:
        {hypothesis.content}
        
        Please design a comprehensive experiment that will effectively test this hypothesis.
        Include the following:
        
        1. Experimental setup and methodology
        2. Required materials, equipment, or computational resources
        3. Key variables to measure and control
        4. Expected outcomes if the hypothesis is true
        5. Expected outcomes if the hypothesis is false
        6. Potential confounding factors and how to address them
        7. Statistical analysis methods to evaluate results
        8. Estimated time and resource requirements
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="experiment",
                                                role="design rigorous experiments to test scientific hypotheses")
        
        schema = {
            "experiment_design": {
                "title": "string",
                "summary": "string",
                "methodology": "string",
                "required_resources": ["string"],
                "variables": {
                    "independent": ["string"],
                    "dependent": ["string"],
                    "controlled": ["string"]
                },
                "expected_outcomes": {
                    "if_true": ["string"],
                    "if_false": ["string"]
                },
                "confounding_factors": ["string"],
                "analysis_methods": ["string"],
                "estimated_requirements": {
                    "time": "string",
                    "resources": "string",
                    "expertise": "string"
                }
            },
            "feasibility_assessment": {
                "score": "number",
                "rationale": "string",
                "challenges": ["string"]
            }
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create experiment object
            experiment = {
                "experiment_id": str(time.time()),
                "hypothesis_id": hypothesis_id,
                "designer_id": self.agent_id,
                "design": response["experiment_design"],
                "feasibility": response["feasibility_assessment"],
                "status": "designed",
                "results": None
            }
            
            # Store experiment in memory
            self.memory.add_experiment(experiment)
            
            return {
                "experiment_id": experiment["experiment_id"],
                "hypothesis_id": hypothesis_id,
                "feasibility_score": response["feasibility_assessment"]["score"]
            }
            
        except Exception as e:
            self.logger.error(f"Error designing experiment: {str(e)}")
            raise
    
    async def _analyze_results(self, task: Task) -> Dict:
        """Analyze experimental results."""
        self.logger.info(f"Analyzing results for task {task.task_id}")
        
        # Get experiment ID and results
        experiment_id = task.params.get("experiment_id")
        results_data = task.params.get("results_data")
        
        if not experiment_id:
            raise ValueError("No experiment ID provided for results analysis")
        
        if not results_data:
            raise ValueError("No results data provided for analysis")
        
        # Get experiment from memory
        experiment = self.memory.get_experiment(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found in memory")
        
        # Get associated hypothesis
        hypothesis = self.memory.get_hypothesis(experiment["hypothesis_id"])
        if not hypothesis:
            raise ValueError(f"Hypothesis {experiment['hypothesis_id']} not found")
        
        # Create analysis prompt
        prompt = (
            f"You are analyzing the results of a scientific experiment designed to test a hypothesis.\n\n"
            f"Hypothesis:\n{hypothesis.content}\n\n"
            f"Experiment design:\n{json.dumps(experiment['design'], indent=2)}\n\n"
            f"Experimental results:\n{results_data}\n\n"
            f"Please analyze these results to determine if they support or refute the hypothesis.\n"
            f"Provide a detailed analysis, including:\n"
            f"1. Summary of the results\n"
            f"2. Comparison to expected outcomes\n"
            f"3. Discussion of potential confounding factors\n"
            f"4. Statistical analysis of the results\n"
            f"5. Interpretation of the results in the context of the hypothesis\n"
            f"6. Recommendations for future research\n\n"
            f"Your analysis should be clear, concise, and scientifically rigorous."
        )
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="experiment",
                                                role="analyze experimental results to test scientific hypotheses")
        
        schema = {
            "analysis": {
                "summary": "string",
                "comparison_to_expected": "string",
                "confounding_factors_discussion": "string",
                "statistical_analysis": "string",
                "interpretation": "string",
                "future_research_recommendations": ["string"]
            },
            "support_for_hypothesis": {
                "supported": "boolean",
                "confidence_level": "string",
                "reasoning": "string"
            }
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create analysis object
            analysis = {
                "analysis_id": str(time.time()),
                "experiment_id": experiment_id,
                "analyzer_id": self.agent_id,
                "analysis": response["analysis"],
                "support_for_hypothesis": response["support_for_hypothesis"]
            }
            
            # Store analysis in memory
            self.memory.add_analysis(analysis)
            
            return {
                "analysis_id": analysis["analysis_id"],
                "experiment_id": experiment_id,
                "hypothesis_id": hypothesis.hypothesis_id,
                "supported": response["support_for_hypothesis"]["supported"],
                "confidence_level": response["support_for_hypothesis"]["confidence_level"],
                "summary": response["analysis"]["summary"]
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing results: {str(e)}")
            raise


class MetaReviewAgent(Agent):
    """
    Agent responsible for generating meta-reviews of the research process.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the meta-review agent."""
        super().__init__(agent_id, "meta-review", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute a meta-review task."""
        task_type = task.task_type
        
        if task_type == "generate_meta_review":
            return await self._generate_meta_review(task)
        else:
            raise ValueError(f"Unsupported task type for MetaReviewAgent: {task_type}")
    
    async def _generate_meta_review(self, task: Task) -> Dict:
        """Generate a meta-review of all hypotheses and reviews."""
        self.logger.info(f"Generating meta-review for task {task.task_id}")
        
        # Get all hypotheses and their reviews
        hypotheses = self.memory.get_all_hypotheses()
        if not hypotheses:
            raise ValueError("No hypotheses found in memory")
        
        # Extract all reviews
        all_reviews = []
        for hypothesis in hypotheses:
            all_reviews.extend(hypothesis.reviews)
        
        # Get tournament matches
        matches = self.memory.get_all_matches()
        
        # Create meta-review prompt
        prompt = f"""
        You are conducting a meta-review of a scientific research process.
        
        You have access to {len(hypotheses)} hypotheses, {len(all_reviews)} reviews, and {len(matches)} comparison matches.
        
        Please analyze this data to identify:
        1. Common strengths and weaknesses across hypotheses
        2. Patterns in what makes hypotheses successful in tournaments
        3. Gaps in the current research exploration
        4. Patterns in how hypotheses are evaluated
        5. Recommendations for future research directions
        
        Your goal is to synthesize insights from the entire research process.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="meta-review",
                                                role="synthesize insights from multiple research hypotheses and reviews")
        
        schema = {
            "common_strengths": {
                "patterns": ["string"],
                "examples": ["string"],
                "implications": "string"
            },
            "common_weaknesses": {
                "patterns": ["string"],
                "examples": ["string"],
                "implications": "string"
            },
            "success_factors": {
                "tournament_patterns": ["string"],
                "winning_characteristics": ["string"],
                "losing_characteristics": ["string"]
            },
            "research_gaps": ["string"],
            "evaluation_patterns": {
                "common_criteria": ["string"],
                "overlooked_dimensions": ["string"]
            },
            "recommendations": {
                "for_hypothesis_generation": ["string"],
                "for_hypothesis_evaluation": ["string"],
                "for_future_research_directions": ["string"]
            }
        }
        
        try:
            # Generate the meta-review with the LLM
            response_data = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            # Unpack the response data
            if isinstance(response_data, tuple) and len(response_data) == 3:
                response, prompt_tokens, completion_tokens = response_data
                
                # Update token counts
                self.total_calls += 1
                self.total_prompt_tokens += int(prompt_tokens)
                self.total_completion_tokens += int(completion_tokens)
            else:
                # Handle the case where the response is not a tuple
                response = response_data
                self.total_calls += 1

            # Create meta-review
            meta_review = {
                "meta_review_id": str(time.time()),
                "common_strengths": response["common_strengths"],
                "common_weaknesses": response["common_weaknesses"],
                "success_factors": response["success_factors"],
                "research_gaps": response["research_gaps"],
                "evaluation_patterns": response["evaluation_patterns"],
                "recommendations": response["recommendations"],
                "review_count": len(all_reviews),
                "match_count": len(matches),
                "hypothesis_count": len(hypotheses)
            }
            
            # Store meta-review in memory
            self.memory.add_meta_review(meta_review)
            
            return {
                "meta_review_id": meta_review["meta_review_id"],
                "research_gaps": response["research_gaps"],
                "recommendations": response["recommendations"]["for_future_research_directions"]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating meta-review: {str(e)}")
            raise
    
    async def _recommend_refinements(self, task: Task) -> Dict:
        """Recommend refinements to a hypothesis based on experimental results."""
        self.logger.info(f"Recommending refinements for task {task.task_id}")
        
        # Get experiment ID
        experiment_id = task.params.get("experiment_id")
        
        if not experiment_id:
            raise ValueError("No experiment ID provided for refinement recommendations")
        
        # Get experiment from memory
        experiment = self.memory.get_experiment(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Check if experiment has been analyzed
        if experiment["status"] != "analyzed" or not experiment.get("analysis"):
            raise ValueError(f"Experiment {experiment_id} has not been analyzed yet")
        
        # Get associated hypothesis
        hypothesis = self.memory.get_hypothesis(experiment["hypothesis_id"])
        if not hypothesis:
            raise ValueError(f"Hypothesis {experiment['hypothesis_id']} not found")
        
        # Create refinement prompt
        prompt = f"""
        You are recommending refinements to a scientific hypothesis based on experimental results.
        
        Original hypothesis:
        {hypothesis.content}
        
        Experiment design:
        {json.dumps(experiment["design"], indent=2)}
        
        Experimental results and analysis:
        {json.dumps(experiment["analysis"], indent=2)}
        
        Based on these results, please recommend:
        
        1. Specific refinements to the original hypothesis to better align with the experimental findings
        2. Modifications to the experimental approach for future testing
        3. New hypotheses that might emerge from unexpected findings
        4. Next steps in the research process
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="experiment",
                                                role="recommend hypothesis refinements based on experimental evidence")
        
        schema = {
            "hypothesis_refinements": {
                "refined_hypothesis": {
                    "content": "string",
                    "summary": "string"
                },
                "key_changes": ["string"],
                "rationale": "string"
            },
            "experimental_modifications": ["string"],
            "new_hypotheses": [
                {
                    "content": "string",
                    "rationale": "string"
                }
            ],
            "next_steps": ["string"]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create a new refined hypothesis
            refined_hypothesis = ResearchHypothesis(
                content=response["hypothesis_refinements"]["refined_hypothesis"]["content"],
                summary=response["hypothesis_refinements"]["refined_hypothesis"]["summary"],
                agent_id=self.agent_id,
                metadata={
                    "original_hypothesis_id": hypothesis.hypothesis_id,
                    "experiment_id": experiment_id,
                    "refinement_rationale": response["hypothesis_refinements"]["rationale"],
                    "key_changes": response["hypothesis_refinements"]["key_changes"],
                    "refinement_type": "experiment_based"
                }
            )
            
            # Add the refined hypothesis to memory
            self.memory.add_hypothesis(refined_hypothesis)
            
            # Create new hypotheses from unexpected findings
            new_hypothesis_ids = []
            for new_hyp in response["new_hypotheses"]:
                new_hypothesis = ResearchHypothesis(
                    content=new_hyp["content"],
                    summary=new_hyp["content"][:100] + "...",  # Simple summary
                    agent_id=self.agent_id,
                    metadata={
                        "parent_hypothesis_id": hypothesis.hypothesis_id,
                        "experiment_id": experiment_id,
                        "generation_rationale": new_hyp["rationale"],
                        "generation_type": "experiment_derived"
                    }
                )
                self.memory.add_hypothesis(new_hypothesis)
                new_hypothesis_ids.append(new_hypothesis.hypothesis_id)
            
            return {
                "experiment_id": experiment_id,
                "original_hypothesis_id": hypothesis.hypothesis_id,
                "refined_hypothesis_id": refined_hypothesis.hypothesis_id,
                "new_hypothesis_ids": new_hypothesis_ids,
                "next_steps": response["next_steps"]
            }
            
        except Exception as e:
            self.logger.error(f"Error recommending refinements: {str(e)}")
            raise


class PaperWriterAgent(Agent):
    """
    Agent responsible for scientific communication and paper writing.
    
    This agent performs several types of tasks:
    - Draft research paper sections
    - Create figures and tables
    - Revise paper based on feedback
    - Generate abstracts and summaries
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the paper writer agent."""
        super().__init__(agent_id, "paper_writer", llm, memory)
    
    async def process_task(self, task: Task) -> Dict:
        """Process a task assigned to this agent."""
        if task.task_type == "draft_paper":
            return await self._draft_paper(task)
        elif task.task_type == "create_figure":
            return await self._create_figure(task)
        elif task.task_type == "revise_paper":
            return await self._revise_paper(task)
        elif task.task_type == "generate_abstract":
            return await self._generate_abstract(task)
        else:
            raise ValueError(f"Unknown task type for paper writer agent: {task.task_type}")
    
    async def _draft_paper(self, task: Task) -> Dict:
        """Draft a research paper based on hypotheses and experiments."""
        self.logger.info(f"Drafting paper for task {task.task_id}")
        
        # Get research goal and top hypotheses
        research_goal = self.memory.metadata.get("research_goal", "")
        
        # Get top hypotheses
        hypotheses = self.memory.get_all_hypotheses()
        top_hypotheses = sorted(hypotheses, key=lambda h: h.elo_rating, reverse=True)[:5]
        
        # Get experiments for top hypotheses
        experiments = []
        for hyp in top_hypotheses:
            hyp_experiments = self.memory.get_experiments_for_hypothesis(hyp.hypothesis_id)
            experiments.extend(hyp_experiments)
        
        # Create paper drafting prompt
        prompt = f"""
        You are drafting a scientific research paper based on a series of hypotheses and experiments.
        
        Research goal:
        {research_goal}
        
        Top hypotheses:
        {[h.content for h in top_hypotheses]}
        
        Experiments and results:
        {json.dumps(experiments, indent=2)}
        
        Please draft a complete research paper with the following sections:
        
        1. Title
        2. Abstract
        3. Introduction
        4. Related Work
        5. Methods
        6. Results
        7. Discussion
        8. Conclusion
        9. References
        
        Focus on clearly communicating the research question, methodology, findings, and implications.
        Use a formal academic writing style appropriate for a scientific publication.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="paper_writer",
                                                role="draft scientific research papers based on hypotheses and experimental results")
        
        schema = {
            "paper": {
                "title": "string",
                "abstract": "string",
                "introduction": "string",
                "related_work": "string",
                "methods": "string",
                "results": "string",
                "discussion": "string",
                "conclusion": "string",
                "references": ["string"]
            },
            "key_contributions": ["string"],
            "limitations": ["string"],
            "future_work": ["string"]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create paper object
            paper = {
                "paper_id": str(time.time()),
                "title": response["paper"]["title"],
                "content": response["paper"],
                "metadata": {
                    "key_contributions": response["key_contributions"],
                    "limitations": response["limitations"],
                    "future_work": response["future_work"],
                    "hypothesis_ids": [h.hypothesis_id for h in top_hypotheses],
                    "experiment_ids": [e["experiment_id"] for e in experiments]
                },
                "version": 1,
                "feedback": []
            }
            
            return paper
        except Exception as e:
            self.logger.error(f"Error drafting paper: {str(e)}")
            raise
            # Store paper in memory
            self.memory.add_paper(paper)
            
            return {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "abstract": response["paper"]["abstract"]
            }
            
        except Exception as e:
            self.logger.error(f"Error drafting paper: {str(e)}")
            raise
    
    async def _revise_paper(self, task: Task) -> Dict:
        """Revise a paper based on feedback."""
        self.logger.info(f"Revising paper for task {task.task_id}")
        
        # Get paper ID and feedback
        paper_id = task.params.get("paper_id")
        feedback = task.params.get("feedback")
        
        if not paper_id:
            raise ValueError("No paper ID provided for revision")
        
        if not feedback:
            raise ValueError("No feedback provided for revision")
        
        # Get paper from memory
        paper = self.memory.get_paper(paper_id)
        if not paper:
            raise ValueError(f"Paper {paper_id} not found")
        
        # Create revision prompt
        prompt = f"""
        You are revising a scientific research paper based on feedback.
        
        Original paper:
        {json.dumps(paper["content"], indent=2)}
        
        Feedback to address:
        {feedback}
        
        Please revise the paper to address all the feedback points while maintaining the paper's
        scientific integrity and clarity. Make specific changes to each section as needed.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="paper_writer",
                                                role="revise scientific papers based on feedback")
        
        schema = {
            "revised_paper": {
                "title": "string",
                "abstract": "string",
                "introduction": "string",
                "related_work": "string",
                "methods": "string",
                "results": "string",
                "discussion": "string",
                "conclusion": "string",
                "references": ["string"]
            },
            "changes_made": [
                {
                    "section": "string",
                    "original": "string",
                    "revised": "string",
                    "rationale": "string"
                }
            ],
            "response_to_feedback": [
                {
                    "feedback_point": "string",
                    "response": "string",
                    "addressed_in": "string"
                }
            ]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create paper object
            paper = {
                "paper_id": str(time.time()),
                "title": response["paper"]["title"],
                "content": response["paper"],
                "metadata": {
                    "key_contributions": response["key_contributions"],
                    "limitations": response["limitations"],
                    "future_work": response["future_work"],
                    "hypothesis_ids": [h.hypothesis_id for h in top_hypotheses],
                    "experiment_ids": [e["experiment_id"] for e in experiments]
                },
                "version": 1,
                "feedback": []
            }
            
            # Store paper in memory
            self.memory.add_paper(paper)
            
            return {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "abstract": response["paper"]["abstract"]
            }
            
        except Exception as e:
            self.logger.error(f"Error revising paper: {str(e)}")
            raise


class MetaReviewAgent(Agent):
    """
    Agent responsible for synthesizing insights from all reviews and tournaments.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the meta-review agent."""
        super().__init__(agent_id, "meta-review", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute a meta-review task."""
        task_type = task.task_type
        
        if task_type == "generate_meta_review":
            return await self._generate_meta_review(task)
        elif task_type == "generate_research_overview":
            return await self._generate_research_overview(task)
        elif task_type == "identify_research_contacts":
            return await self._identify_research_contacts(task)
        else:
            raise ValueError(f"Unsupported task type for MetaReviewAgent: {task_type}")
    
    async def _generate_meta_review(self, task: Task) -> Dict:
        """Generate a meta-review synthesizing insights from all reviews and tournaments."""
        self.logger.info(f"Generating meta-review for task {task.task_id}")
        
        # Get all hypotheses
        hypotheses = self.memory.get_all_hypotheses()
        
        # Collect all reviews
        all_reviews = []
        for h in hypotheses:
            for review in h.reviews:
                review_with_hypothesis = review.copy()
                review_with_hypothesis["hypothesis_id"] = h.hypothesis_id
                review_with_hypothesis["hypothesis_summary"] = h.summary
                all_reviews.append(review_with_hypothesis)
        
        # Get tournament matches
        tournament_state = self.memory.tournament_state
        matches = tournament_state.get("matches", [])
        
        # Get research goal
        research_goal = self.memory.metadata.get("research_goal", "")
        
        # Create meta-review prompt
        prompt = f"""
        You are synthesizing insights from multiple scientific reviews and tournament debates into a meta-review.
        
        Research goal:
        {research_goal}
        
        Your task is to analyze patterns across all reviews and debates to identify:
        
        1. Common strengths across high-ranking hypotheses
        2. Common weaknesses or limitations in reviewed hypotheses
        3. Recurring criteria that differentiate winning from losing hypotheses in tournaments
        4. Key unanswered questions or under-explored areas in the current hypotheses
        5. Methodological patterns in how hypotheses are being evaluated
        
        Provide a comprehensive synthesis that can guide future hypothesis generation and review.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="meta-review",
                                                role="synthesize insights across multiple scientific reviews")
        
        schema = {
            "common_strengths": {
                "patterns": ["string"],
                "examples": ["string"],
                "implications": "string"
            },
            "common_weaknesses": {
                "patterns": ["string"],
                "examples": ["string"],
                "implications": "string"
            },
            "success_factors": {
                "tournament_patterns": ["string"],
                "winning_characteristics": ["string"],
                "losing_characteristics": ["string"]
            },
            "research_gaps": ["string"],
            "evaluation_patterns": {
                "common_criteria": ["string"],
                "overlooked_dimensions": ["string"]
            },
            "recommendations": {
                "for_hypothesis_generation": ["string"],
                "for_hypothesis_evaluation": ["string"],
                "for_future_research_directions": ["string"]
            }
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create meta-review
            meta_review = {
                "meta_review_id": str(time.time()),
                "common_strengths": response["common_strengths"],
                "common_weaknesses": response["common_weaknesses"],
                "success_factors": response["success_factors"],
                "research_gaps": response["research_gaps"],
                "evaluation_patterns": response["evaluation_patterns"],
                "recommendations": response["recommendations"],
                "review_count": len(all_reviews),
                "match_count": len(matches),
                "hypothesis_count": len(hypotheses)
            }
            
            # Update agent state with the meta-review
            agent_state = self.memory.get_agent_state(self.agent_id) or {}
            agent_state["meta_review"] = meta_review
            self.memory.set_agent_state(self.agent_id, agent_state)
            
            return meta_review
            
        except Exception as e:
            self.logger.error(f"Error generating meta-review: {str(e)}")
            raise
    
    async def _generate_research_overview(self, task: Task) -> Dict:
        """Generate a comprehensive research overview based on top hypotheses."""
        self.logger.info(f"Generating research overview for task {task.task_id}")
        
        # Get top-ranked hypotheses
        hypotheses = self.memory.get_all_hypotheses()
        top_hypotheses = sorted(hypotheses, key=lambda h: h.elo_rating, reverse=True)[:10]
        
        # Get research goal
        research_goal = self.memory.metadata.get("research_goal", "")
        plan_config = self.memory.metadata.get("research_plan_config", {})
        
        # Get meta-review if available
        agent_state = self.memory.get_agent_state(self.agent_id) or {}
        meta_review = agent_state.get("meta_review", {})
        
        # Format hypothesis summaries
        hypothesis_summaries = []
        for i, h in enumerate(top_hypotheses):
            rating_info = f"(Elo rating: {h.elo_rating:.1f})"
            hypothesis_summaries.append(f"Hypothesis {i+1} {rating_info}: {h.summary}")
        
        hypothesis_list = "\n".join(hypothesis_summaries)
        
        # Create research overview prompt
        prompt = f"""
        You are generating a comprehensive research overview based on the research goal and top-ranked hypotheses.
        
        Research goal:
        {research_goal}
        
        Top-ranked hypotheses:
        {hypothesis_list}
        
        Meta-review insights:
        - Common strengths: {meta_review.get("common_strengths", {}).get("patterns", [])}
        - Common weaknesses: {meta_review.get("common_weaknesses", {}).get("patterns", [])}
        - Research gaps: {meta_review.get("research_gaps", [])}
        
        Your task is to create a structured research overview that:
        
        1. Summarizes the current state of knowledge related to the research goal
        2. Presents the most promising research directions based on top hypotheses
        3. Outlines specific research questions and experiments to pursue
        4. Provides a roadmap for future investigation
        
        Format this as a formal research overview suitable for scientific communication.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="meta-review",
                                                role="create comprehensive research overviews and roadmaps")
        
        schema = {
            "title": "string",
            "executive_summary": "string",
            "background": "string",
            "current_state_of_knowledge": "string",
            "promising_directions": [
                {
                    "direction": "string",
                    "rationale": "string",
                    "key_hypotheses": ["string"],
                    "research_questions": ["string"],
                    "proposed_experiments": ["string"]
                }
            ],
            "research_roadmap": {
                "short_term_goals": ["string"],
                "medium_term_goals": ["string"],
                "long_term_goals": ["string"]
            },
            "potential_impact": "string",
            "conclusion": "string"
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create research overview
            research_overview = {
                "overview_id": str(time.time()),
                "title": response["title"],
                "executive_summary": response["executive_summary"],
                "background": response["background"],
                "current_state_of_knowledge": response["current_state_of_knowledge"],
                "promising_directions": response["promising_directions"],
                "research_roadmap": response["research_roadmap"],
                "potential_impact": response["potential_impact"],
                "conclusion": response["conclusion"],
                "based_on_hypotheses": [h.hypothesis_id for h in top_hypotheses]
            }
            
            # Update agent state with the research overview
            agent_state = self.memory.get_agent_state(self.agent_id) or {}
            agent_state["research_overview"] = research_overview
            self.memory.set_agent_state(self.agent_id, agent_state)
            
            return research_overview
            
        except Exception as e:
            self.logger.error(f"Error generating research overview: {str(e)}")
            raise
    
    async def _identify_research_contacts(self, task: Task) -> Dict:
        """Identify potential research contacts and collaborators."""
        self.logger.info(f"Identifying research contacts for task {task.task_id}")
        
        # Get research goal
        research_goal = self.memory.metadata.get("research_goal", "")
        
        # Get top hypotheses for context
        hypotheses = self.memory.get_all_hypotheses()
        top_hypotheses = sorted(hypotheses, key=lambda h: h.elo_rating, reverse=True)[:3]
        
        hypothesis_summaries = [h.summary for h in top_hypotheses]
        
        # Create contacts identification prompt
        prompt = f"""
        You are identifying potential research contacts and collaborators for a scientific research project.
        
        Research goal:
        {research_goal}
        
        Top hypothesis directions:
        {hypothesis_summaries}
        
        Your task is to identify categories of researchers or specific research areas that would be valuable 
        collaborators or contacts for this research. Focus on identifying complementary expertise and 
        potential collaborations that would enhance the research.
        
        Do not provide specific names of individual researchers, but rather describe the types of expertise,
        research backgrounds, or institutional affiliations that would be beneficial.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="meta-review",
                                                role="identify valuable research contacts and collaborations")
        
        schema = {
            "key_expertise_areas": [
                {
                    "area": "string",
                    "relevance": "string",
                    "potential_contribution": "string"
                }
            ],
            "complementary_disciplines": ["string"],
            "suggested_institutional_types": ["string"],
            "collaboration_opportunities": ["string"]
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create contacts recommendation
            contacts = {
                "contacts_id": str(time.time()),
                "key_expertise_areas": response["key_expertise_areas"],
                "complementary_disciplines": response["complementary_disciplines"],
                "suggested_institutional_types": response["suggested_institutional_types"],
                "collaboration_opportunities": response["collaboration_opportunities"]
            }
            
            # Update agent state with the contacts
            agent_state = self.memory.get_agent_state(self.agent_id) or {}
            agent_state["research_contacts"] = contacts
            self.memory.set_agent_state(self.agent_id, agent_state)
            
            return contacts
            
        except Exception as e:
            self.logger.error(f"Error identifying research contacts: {str(e)}")
            raise


class ModelAdaptationAgent(Agent):
    """
    Agent responsible for adapting language models using CS-ReFT.
    
    This agent performs several types of tasks:
    - Create task-specific datasets
    - Train CS-ReFT adapters
    - Evaluate adapted models
    - Analyze representation dynamics
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the model adaptation agent."""
        super().__init__(agent_id, "model_adaptation", llm, memory)
        
        # Initialize model adapter
        from model_adaptation import ModelAdapter
        self.model_adapter = ModelAdapter(
            base_model_name="llama-2-7b",
            output_dir="./adapted_models",
            hidden_size=4096,
            subspace_dim=32
        )
    
    async def process_task(self, task: Task) -> Dict:
        """Process a task assigned to this agent."""
        if task.task_type == "create_dataset":
            return await self._create_dataset(task)
        elif task.task_type == "train_adapter":
            return await self._train_adapter(task)
        elif task.task_type == "evaluate_adapter":
            return await self._evaluate_adapter(task)
        elif task.task_type == "analyze_representations":
            return await self._analyze_representations(task)
        else:
            raise ValueError(f"Unknown task type for model adaptation agent: {task.task_type}")
    
    async def _create_dataset(self, task: Task) -> Dict:
        """Create a task-specific dataset for model adaptation."""
        self.logger.info(f"Creating dataset for task {task.task_id}")
        
        # Get task information
        task_id = task.params.get("task_id")
        task_description = task.params.get("task_description")
        
        if not task_id or not task_description:
            raise ValueError("Task ID and description are required for dataset creation")
        
        # Create dataset creation prompt
        prompt = f"""
        You are creating a dataset for fine-tuning a language model on a specific task.
        
        Task ID: {task_id}
        Task Description: {task_description}
        
        Please generate 10 diverse examples for this task. Each example should include:
        1. An input prompt that the model would receive
        2. The expected output that the model should generate
        
        Make the examples representative of the task and cover different aspects or variations.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="model_adaptation",
                                                role="create high-quality datasets for model fine-tuning")
        
        schema = {
            "dataset": [
                {
                    "input": "string",
                    "output": "string",
                    "explanation": "string"
                }
            ],
            "task_analysis": {
                "key_skills_required": ["string"],
                "potential_challenges": ["string"],
                "evaluation_metrics": ["string"]
            }
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create dataset object
            dataset = {
                "dataset_id": str(time.time()),
                "task_id": task_id,
                "task_description": task_description,
                "examples": response["dataset"],
                "analysis": response["task_analysis"]
            }
            
            # Store dataset in memory
            self.memory.set_dataset(task_id, dataset)
            
            return {
                "dataset_id": dataset["dataset_id"],
                "task_id": task_id,
                "example_count": len(response["dataset"])
            }
            
        except Exception as e:
            self.logger.error(f"Error creating dataset: {str(e)}")
            raise
    
    async def _train_adapter(self, task: Task) -> Dict:
        """Train a CS-ReFT adapter for specific tasks."""
        self.logger.info(f"Training adapter for task {task.task_id}")
        
        # Get task IDs
        task_ids = task.params.get("task_ids", [])
        if not task_ids:
            raise ValueError("No task IDs provided for adapter training")
        
        # Get datasets for the specified tasks
        datasets = {}
        for task_id in task_ids:
            dataset = self.memory.get_dataset(task_id)
            if not dataset:
                raise ValueError(f"Dataset for task ID {task_id} not found")
            datasets[task_id] = dataset["examples"]
        
        # Create training prompt
        prompt = f"""
        You are training a CS-ReFT adapter for specific tasks.
        
        Task IDs: {task_ids}
        
        Please provide a detailed training plan for the CS-ReFT adapter, including:
        1. A description of the tasks to be adapted
        2. The datasets to be used for training
        3. The training process and parameters
        4. Expected outcomes and performance metrics
        
        Ensure the plan is clear, concise, and provides enough detail for the adapter to be trained effectively.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="model_adaptation",
                                                role="train CS-ReFT adapters for specific tasks")
        
        schema = {
            "training_plan": {
                "task_descriptions": ["string"],
                "datasets_used": ["string"],
                "training_process": "string",
                "parameters": {
                    "learning_rate": "number",
                    "batch_size": "number",
                    "epochs": "number"
                },
                "expected_outcomes": "string",
                "performance_metrics": ["string"]
            }
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create training plan object
            training_plan = {
                "training_plan_id": str(time.time()),
                "task_ids": task_ids,
                "plan": response["training_plan"]
            }
            
            # Store training plan in memory
            self.memory.set_training_plan(task_ids, training_plan)
            
            return {
                "training_plan_id": training_plan["training_plan_id"],
                "task_ids": task_ids,
                "training_process": response["training_plan"]["training_process"]
            }
            
        except Exception as e:
            self.logger.error(f"Error training adapter: {str(e)}")
            raise
    
    async def _evaluate_adapter(self, task: Task) -> Dict:
        """Evaluate the performance of a CS-ReFT adapter."""
        self.logger.info(f"Evaluating adapter for task {task.task_id}")
        
        # Get task IDs
        task_ids = task.params.get("task_ids", [])
        if not task_ids:
            raise ValueError("No task IDs provided for adapter evaluation")
        
        # Get training plan for the specified tasks
        training_plan = self.memory.get_training_plan(task_ids)
        if not training_plan:
            raise ValueError(f"No training plan found for task IDs: {task_ids}")
        
        # Create evaluation prompt
        prompt = f"""
        You are evaluating the performance of a CS-ReFT adapter.
        
        Task IDs: {task_ids}
        
        Training plan:
        {json.dumps(training_plan["plan"], indent=2)}
        
        Please provide a detailed evaluation of the CS-ReFT adapter's performance, including:
        1. A summary of the training process
        2. Key performance metrics
        3. Analysis of the adapter's strengths and weaknesses
        4. Recommendations for improvement
        
        Ensure the evaluation is thorough and provides actionable insights.
        """
        
        system_prompt = self.fill_prompt_template("system", 
                                                agent_type="model_adaptation",
                                                role="evaluate CS-ReFT adapters")
        
        schema = {
            "evaluation": {
                "summary": "string",
                "performance_metrics": {
                    "accuracy": "number",
                    "f1_score": "number",
                    "loss": "number"
                },
                "strengths": ["string"],
                "weaknesses": ["string"],
                "recommendations": "string"
            }
        }
        
        try:
            response, prompt_tokens, completion_tokens = self.llm.generate_with_json_output(prompt, schema, system_prompt=system_prompt)
            
            self.total_calls += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            
            # Create evaluation object
            evaluation = {
                "evaluation_id": str(time.time()),
                "task_ids": task_ids,
                "evaluation": response["evaluation"]
            }
            
            # Store evaluation in memory
            self.memory.set_evaluation(task_ids, evaluation)
            
            return {
                "evaluation_id": evaluation["evaluation_id"],
                "task_ids": task_ids,
                "summary": response["evaluation"]["summary"],
                "performance_metrics": response["evaluation"]["performance_metrics"]
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating adapter: {str(e)}")
            raise
    
    async def _analyze_representations(self, task: Task) -> Dict:
        """Analyze the representation dynamics of a CS-ReFT adapter."""
        self.logger
