"""
Evolution Agent for ProtoGnosis.

This agent evolves and improves hypotheses through iterative refinement.
"""

import json
import time
from typing import Dict, List, Optional, Any
import logging

from ..core.agent_core import Agent, Task, ResearchHypothesis, ContextMemory
from ..core.llm_interface import LLMInterface


class EvolutionAgent(Agent):
    """
    Agent responsible for evolving and improving hypotheses.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the evolution agent."""
        super().__init__(agent_id, "evolution", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute a hypothesis evolution task.
        
        Args:
            task: Task containing hypothesis to evolve
            
        Returns:
            Dictionary containing evolved hypothesis
        """
        try:
            hypothesis_id = task.parameters.get("hypothesis_id")
            evolution_type = task.parameters.get("evolution_type", "refinement")
            feedback = task.parameters.get("feedback", "")
            
            # Get hypothesis from memory
            hypothesis = self.memory.get_hypothesis(hypothesis_id)
            if not hypothesis:
                return {"error": f"Hypothesis {hypothesis_id} not found"}
            
            self.logger.info(f"Evolving hypothesis {hypothesis_id} with type: {evolution_type}")
            
            # Evolve hypothesis
            evolved_hypothesis = await self._evolve_hypothesis(hypothesis, evolution_type, feedback)
            
            # Store evolved hypothesis
            self.memory.add_hypothesis(evolved_hypothesis)
            
            return {
                "original_hypothesis_id": hypothesis_id,
                "evolved_hypothesis_id": evolved_hypothesis.hypothesis_id,
                "evolution_type": evolution_type,
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error evolving hypothesis: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
    
    async def _evolve_hypothesis(self, hypothesis: ResearchHypothesis, 
                                evolution_type: str, feedback: str) -> ResearchHypothesis:
        """Evolve a hypothesis based on the specified type and feedback."""
        
        prompt = f"""
        Evolve and improve the following research hypothesis:
        
        Original Hypothesis: {hypothesis.content}
        
        Evolution Type: {evolution_type}
        Feedback: {feedback}
        
        Please provide an improved version that:
        1. Addresses any feedback provided
        2. Enhances clarity and specificity
        3. Improves testability
        4. Strengthens scientific rationale
        5. Maintains the core innovative idea
        
        Provide the evolved hypothesis with clear improvements noted.
        """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        # Create evolved hypothesis
        evolved_hypothesis = ResearchHypothesis(
            content=response,
            summary=self._extract_summary(response),
            agent_id=self.agent_id,
            metadata={
                "evolution_type": evolution_type,
                "parent_hypothesis_id": hypothesis.hypothesis_id,
                "feedback_applied": feedback,
                "generation_method": "evolution"
            }
        )
        
        return evolved_hypothesis
    
    def _extract_summary(self, content: str) -> str:
        """Extract a brief summary from the hypothesis content."""
        sentences = content.split('.')
        if sentences:
            summary = sentences[0].strip()
            if len(summary) > 200:
                summary = summary[:200] + "..."
            return summary
        else:
            return content[:200] + "..." if len(content) > 200 else content
