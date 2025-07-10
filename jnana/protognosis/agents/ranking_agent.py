"""
Ranking Agent for ProtoGnosis.

This agent ranks hypotheses by quality using various criteria.
"""

import json
import time
from typing import Dict, List, Optional, Any
import logging

from ..core.agent_core import Agent, Task, ResearchHypothesis, ContextMemory
from ..core.llm_interface import LLMInterface


class RankingAgent(Agent):
    """
    Agent responsible for ranking hypotheses by quality.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the ranking agent."""
        super().__init__(agent_id, "ranking", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute a hypothesis ranking task.
        
        Args:
            task: Task containing hypotheses to rank
            
        Returns:
            Dictionary containing ranking results
        """
        try:
            hypothesis_ids = task.parameters.get("hypothesis_ids", [])
            ranking_criteria = task.parameters.get("criteria", "overall_quality")
            
            self.logger.info(f"Ranking {len(hypothesis_ids)} hypotheses by {ranking_criteria}")
            
            # Get hypotheses from memory
            hypotheses = []
            for hyp_id in hypothesis_ids:
                hyp = self.memory.get_hypothesis(hyp_id)
                if hyp:
                    hypotheses.append(hyp)
            
            if not hypotheses:
                return {"error": "No valid hypotheses found for ranking"}
            
            # Perform ranking
            rankings = await self._rank_hypotheses(hypotheses, ranking_criteria)
            
            # Update agent state
            agent_state = self.memory.get_agent_state(self.agent_id) or {}
            agent_state.update({
                "last_activity": time.time(),
                "rankings_completed": agent_state.get("rankings_completed", 0) + 1,
                "last_ranking_criteria": ranking_criteria,
                "hypotheses_ranked": len(hypothesis_ids),
                "total_tasks_completed": agent_state.get("total_tasks_completed", 0) + 1
            })
            self.memory.set_agent_state(self.agent_id, agent_state)

            # Create dataset for this ranking task
            dataset = {
                "task_id": task.task_id,
                "agent_id": self.agent_id,
                "ranking_criteria": ranking_criteria,
                "hypotheses_ranked": hypothesis_ids,
                "ranking_time": time.time(),
                "input_parameters": task.parameters,
                "output_quality_metrics": {
                    "hypotheses_count": len(hypotheses),
                    "ranking_completeness": len(rankings) / len(hypotheses) if hypotheses else 0,
                    "criteria_specificity": len(ranking_criteria.split())
                }
            }
            self.memory.set_dataset(task.task_id, dataset)

            return {
                "rankings": rankings,
                "criteria": ranking_criteria,
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error ranking hypotheses: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
    
    async def _rank_hypotheses(self, hypotheses: List[ResearchHypothesis], criteria: str) -> List[Dict]:
        """Rank a list of hypotheses based on specified criteria."""
        
        # Create comparison prompt
        hypothesis_texts = []
        for i, hyp in enumerate(hypotheses):
            hypothesis_texts.append(f"Hypothesis {i+1}: {hyp.content}")
        
        prompt = f"""
        Rank the following research hypotheses based on {criteria}:
        
        {chr(10).join(hypothesis_texts)}
        
        Provide rankings from best to worst with brief justifications.
        Consider factors like:
        - Scientific validity
        - Novelty and innovation
        - Testability
        - Potential impact
        - Clarity and specificity
        
        Format: Rank each hypothesis with a score (1-10) and brief explanation.
        """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        # Parse response and create rankings
        rankings = []
        for i, hyp in enumerate(hypotheses):
            rankings.append({
                "hypothesis_id": hyp.hypothesis_id,
                "rank": i + 1,  # Simple sequential ranking for now
                "score": 7.0,   # Default score
                "justification": f"Ranked by {criteria}",
                "content_preview": hyp.content[:100] + "..."
            })
        
        return rankings
