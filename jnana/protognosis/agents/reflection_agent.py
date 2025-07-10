"""
Reflection Agent for ProtoGnosis.

This agent provides peer review and critique of research hypotheses.
"""

import json
import time
from typing import Dict, List, Optional, Any
import logging

from ..core.agent_core import Agent, Task, ResearchHypothesis, ContextMemory
from ..core.llm_interface import LLMInterface


class ReflectionAgent(Agent):
    """
    Agent responsible for providing peer review and critique of hypotheses.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the reflection agent."""
        super().__init__(agent_id, "reflection", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute a hypothesis reflection/review task.
        
        Args:
            task: Task containing hypothesis to review
            
        Returns:
            Dictionary containing review results
        """
        try:
            hypothesis_id = task.parameters.get("hypothesis_id")
            review_type = task.parameters.get("review_type", "initial_review")
            
            # Get hypothesis from memory
            hypothesis = self.memory.get_hypothesis(hypothesis_id)
            if not hypothesis:
                return {"error": f"Hypothesis {hypothesis_id} not found"}
            
            self.logger.info(f"Reviewing hypothesis {hypothesis_id} with type: {review_type}")
            
            # Perform review based on type
            if review_type == "initial_review":
                review = await self._initial_review(hypothesis)
            elif review_type == "deep_verification":
                review = await self._deep_verification(hypothesis)
            else:
                review = await self._initial_review(hypothesis)
            
            # Update agent state
            agent_state = self.memory.get_agent_state(self.agent_id) or {}
            agent_state.update({
                "last_activity": time.time(),
                "reviews_completed": agent_state.get("reviews_completed", 0) + 1,
                "last_review_type": review_type,
                "last_hypothesis_reviewed": hypothesis_id,
                "total_tasks_completed": agent_state.get("total_tasks_completed", 0) + 1
            })
            self.memory.set_agent_state(self.agent_id, agent_state)

            # Create dataset for this review task
            dataset = {
                "task_id": task.task_id,
                "agent_id": self.agent_id,
                "review_type": review_type,
                "hypothesis_reviewed": hypothesis_id,
                "review_time": time.time(),
                "input_parameters": task.parameters,
                "output_quality_metrics": {
                    "review_length": len(str(review)),
                    "review_depth": "deep" if review_type == "deep_verification" else "initial"
                }
            }
            self.memory.set_dataset(task.task_id, dataset)

            return {
                "hypothesis_id": hypothesis_id,
                "review": review,
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error reviewing hypothesis: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
    
    async def _initial_review(self, hypothesis: ResearchHypothesis) -> Dict:
        """Perform initial review of a hypothesis."""
        
        prompt = f"""
        As a peer reviewer, provide a critical but constructive review of this research hypothesis:
        
        Hypothesis: {hypothesis.content}
        
        Please evaluate:
        1. Scientific validity and plausibility
        2. Novelty and significance
        3. Testability and experimental feasibility
        4. Clarity and specificity
        5. Potential impact and implications
        
        Provide specific feedback and suggestions for improvement.
        Rate each aspect on a scale of 1-10.
        """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        return {
            "review_type": "initial_review",
            "content": response,
            "reviewer_id": self.agent_id,
            "timestamp": time.time()
        }
    
    async def _deep_verification(self, hypothesis: ResearchHypothesis) -> Dict:
        """Perform deep verification of a hypothesis."""
        
        prompt = f"""
        Conduct a thorough verification of this research hypothesis:
        
        Hypothesis: {hypothesis.content}
        
        Deep analysis should include:
        1. Literature consistency check
        2. Methodological soundness
        3. Potential confounding factors
        4. Alternative explanations
        5. Reproducibility considerations
        6. Ethical implications
        
        Provide detailed analysis and identify any potential issues.
        """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        return {
            "review_type": "deep_verification",
            "content": response,
            "reviewer_id": self.agent_id,
            "timestamp": time.time()
        }
