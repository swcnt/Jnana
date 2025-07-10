"""
Generation Agent for ProtoGnosis.

This agent is responsible for generating initial research hypotheses using
various strategies like literature exploration, scientific debate, etc.
"""

import json
import time
import random
from typing import Dict, List, Optional, Any
import logging
import os

from ..core.agent_core import Agent, Task, ResearchHypothesis, ContextMemory
from ..core.llm_interface import LLMInterface

# Import prompt templates
try:
    from ..prompts.generation_agent_prompts import (
        create_scientific_debate_prompt,
        create_literature_exploration_prompt,
        create_assumptions_identification_prompt,
        create_research_expansion_prompt
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
        """
        Execute a hypothesis generation task.

        Args:
            task: Task containing generation parameters

        Returns:
            Dictionary containing generated hypothesis
        """
        self.logger.info(f"🔥 EXECUTE_TASK CALLED for {self.agent_id} with task {task.task_id}")
        try:
            strategy = task.parameters.get("strategy", "literature_exploration")
            research_goal = task.parameters.get("research_goal", "")

            self.logger.info(f"Generating hypothesis using strategy: {strategy}")

            # Generate hypothesis based on strategy
            if strategy == "literature_exploration":
                hypothesis = await self._literature_exploration(research_goal, task.parameters)
            elif strategy == "scientific_debate":
                hypothesis = await self._scientific_debate(research_goal, task.parameters)
            elif strategy == "assumptions_identification":
                hypothesis = await self._assumptions_identification(research_goal, task.parameters)
            elif strategy == "research_expansion":
                hypothesis = await self._research_expansion(research_goal, task.parameters)
            else:
                # Default to literature exploration
                hypothesis = await self._literature_exploration(research_goal, task.parameters)

            self.logger.info(f"Hypothesis generated successfully: {hypothesis.hypothesis_id}")

            # Store in memory
            try:
                self.memory.add_hypothesis(hypothesis)
                self.logger.info(f"Hypothesis stored in memory successfully")
            except Exception as e:
                self.logger.error(f"Error storing hypothesis in memory: {e}")
                raise

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
                    "input_parameters": task.parameters,
                    "output_quality_metrics": {
                        "content_length": len(hypothesis.content),
                        "summary_length": len(hypothesis.summary),
                        "strategy_alignment": 1.0  # Could be computed based on strategy adherence
                    }
                }
                self.memory.set_dataset(task.task_id, dataset)
                self.logger.info(f"Dataset created and saved for task {task.task_id}")
            except Exception as e:
                self.logger.error(f"Error creating dataset: {e}")
                # Don't raise - this shouldn't fail the task

            return {
                "hypothesis_id": hypothesis.hypothesis_id,
                "content": hypothesis.content,
                "summary": hypothesis.summary,
                "strategy": strategy,
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating hypothesis: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
    
    async def _literature_exploration(self, research_goal: str, parameters: Dict) -> ResearchHypothesis:
        """Generate hypothesis through literature exploration."""
        
        if EXTERNAL_PROMPTS:
            prompt = create_literature_exploration_prompt(research_goal, parameters)
        else:
            prompt = f"""
            As a research scientist, generate a novel hypothesis based on literature exploration for the following research goal:
            
            Research Goal: {research_goal}
            
            Please provide:
            1. A clear, testable hypothesis
            2. Scientific rationale based on existing literature
            3. Potential experimental approaches
            4. Expected outcomes and implications
            
            Format your response as a structured hypothesis.
            """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        # Create hypothesis object
        hypothesis = ResearchHypothesis(
            content=response,
            summary=self._extract_summary(response),
            agent_id=self.agent_id,
            metadata={
                "strategy": "literature_exploration",
                "research_goal": research_goal,
                "generation_method": "llm_generation"
            }
        )
        
        return hypothesis
    
    async def _scientific_debate(self, research_goal: str, parameters: Dict) -> ResearchHypothesis:
        """Generate hypothesis through simulated scientific debate."""
        
        if EXTERNAL_PROMPTS:
            prompt = create_scientific_debate_prompt(research_goal, parameters)
        else:
            prompt = f"""
            Engage in a scientific debate to generate a novel hypothesis for: {research_goal}
            
            Take a contrarian or alternative perspective to mainstream approaches.
            Challenge conventional thinking and propose innovative solutions.
            
            Provide:
            1. A hypothesis that challenges existing paradigms
            2. Arguments for why current approaches may be limited
            3. Evidence or reasoning supporting the alternative approach
            4. Potential experimental validation
            """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        hypothesis = ResearchHypothesis(
            content=response,
            summary=self._extract_summary(response),
            agent_id=self.agent_id,
            metadata={
                "strategy": "scientific_debate",
                "research_goal": research_goal,
                "generation_method": "contrarian_perspective"
            }
        )
        
        return hypothesis
    
    async def _assumptions_identification(self, research_goal: str, parameters: Dict) -> ResearchHypothesis:
        """Generate hypothesis by identifying and challenging assumptions."""
        
        if EXTERNAL_PROMPTS:
            prompt = create_assumptions_identification_prompt(research_goal, parameters)
        else:
            prompt = f"""
            Identify key assumptions in current approaches to: {research_goal}
            
            Then generate a hypothesis that challenges one or more of these assumptions.
            
            Steps:
            1. List 3-5 key assumptions in the field
            2. Choose one assumption to challenge
            3. Propose what might be true if this assumption is wrong
            4. Develop a testable hypothesis based on this alternative view
            """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        hypothesis = ResearchHypothesis(
            content=response,
            summary=self._extract_summary(response),
            agent_id=self.agent_id,
            metadata={
                "strategy": "assumptions_identification",
                "research_goal": research_goal,
                "generation_method": "assumption_challenging"
            }
        )
        
        return hypothesis
    
    async def _research_expansion(self, research_goal: str, parameters: Dict) -> ResearchHypothesis:
        """Generate hypothesis by expanding current research directions."""
        
        if EXTERNAL_PROMPTS:
            prompt = create_research_expansion_prompt(research_goal, parameters)
        else:
            prompt = f"""
            Expand on current research directions for: {research_goal}
            
            Generate a hypothesis that extends existing work in a novel direction.
            
            Consider:
            1. Current state of research in this area
            2. Gaps or limitations in existing approaches
            3. Emerging technologies or methods that could be applied
            4. Interdisciplinary connections that could be explored
            
            Propose a hypothesis that builds on existing work but opens new avenues.
            """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        hypothesis = ResearchHypothesis(
            content=response,
            summary=self._extract_summary(response),
            agent_id=self.agent_id,
            metadata={
                "strategy": "research_expansion",
                "research_goal": research_goal,
                "generation_method": "research_extension"
            }
        )
        
        return hypothesis
    
    def _extract_summary(self, content: str) -> str:
        """Extract a brief summary from the hypothesis content."""
        # Simple extraction - take first sentence or first 200 characters
        sentences = content.split('.')
        if sentences:
            summary = sentences[0].strip()
            if len(summary) > 200:
                summary = summary[:200] + "..."
            return summary
        else:
            return content[:200] + "..." if len(content) > 200 else content
