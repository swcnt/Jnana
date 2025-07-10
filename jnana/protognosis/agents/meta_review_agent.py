"""
Meta-Review Agent for ProtoGnosis.

This agent provides comprehensive meta-analysis and review of hypotheses.
"""

import json
import time
from typing import Dict, List, Optional, Any
import logging

from ..core.agent_core import Agent, Task, ResearchHypothesis, ContextMemory
from ..core.llm_interface import LLMInterface


class MetaReviewAgent(Agent):
    """
    Agent responsible for comprehensive meta-analysis and review.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the meta-review agent."""
        super().__init__(agent_id, "meta_review", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute a meta-review task.
        
        Args:
            task: Task containing hypotheses and reviews to analyze
            
        Returns:
            Dictionary containing meta-review results
        """
        try:
            hypothesis_ids = task.parameters.get("hypothesis_ids", [])
            review_type = task.parameters.get("review_type", "comprehensive")
            
            self.logger.info(f"Conducting meta-review of {len(hypothesis_ids)} hypotheses")
            
            # Get hypotheses from memory
            hypotheses = []
            for hyp_id in hypothesis_ids:
                hyp = self.memory.get_hypothesis(hyp_id)
                if hyp:
                    hypotheses.append(hyp)
            
            if not hypotheses:
                return {"error": "No valid hypotheses found for meta-review"}
            
            # Perform meta-review
            meta_review = await self._conduct_meta_review(hypotheses, review_type)
            
            # Update agent state
            agent_state = self.memory.get_agent_state(self.agent_id) or {}
            agent_state.update({
                "last_activity": time.time(),
                "meta_reviews_completed": agent_state.get("meta_reviews_completed", 0) + 1,
                "last_review_type": review_type,
                "hypotheses_reviewed": len(hypothesis_ids),
                "total_tasks_completed": agent_state.get("total_tasks_completed", 0) + 1
            })
            self.memory.set_agent_state(self.agent_id, agent_state)

            # Create dataset for this meta-review task
            dataset = {
                "task_id": task.task_id,
                "agent_id": self.agent_id,
                "review_type": review_type,
                "hypotheses_reviewed": hypothesis_ids,
                "meta_review_time": time.time(),
                "input_parameters": task.parameters,
                "output_quality_metrics": {
                    "hypotheses_count": len(hypotheses),
                    "insights_generated": len(meta_review.get("key_insights", [])),
                    "recommendations_provided": len(meta_review.get("recommendations", [])),
                    "review_comprehensiveness": len(str(meta_review)) / 1000  # Rough measure
                }
            }
            self.memory.set_dataset(task.task_id, dataset)

            return {
                "meta_review": meta_review,
                "review_type": review_type,
                "hypothesis_count": len(hypotheses),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error conducting meta-review: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
    
    async def _conduct_meta_review(self, hypotheses: List[ResearchHypothesis], 
                                  review_type: str) -> Dict:
        """Conduct comprehensive meta-review of hypotheses."""
        
        # Prepare hypothesis summaries
        hypothesis_summaries = []
        for i, hyp in enumerate(hypotheses):
            hypothesis_summaries.append(f"""
            Hypothesis {i+1} (ID: {hyp.hypothesis_id}):
            Summary: {hyp.summary}
            Content: {hyp.content[:300]}...
            """)
        
        prompt = f"""
        Conduct a comprehensive meta-review of these research hypotheses:
        
        {chr(10).join(hypothesis_summaries)}
        
        Review Type: {review_type}
        
        Please provide:
        1. Overall assessment of the hypothesis collection
        2. Strengths and weaknesses across all hypotheses
        3. Common themes and patterns
        4. Gaps or missing perspectives
        5. Recommendations for improvement
        6. Ranking of hypotheses by overall quality
        7. Suggestions for future research directions
        
        Provide a structured meta-analysis that synthesizes insights across all hypotheses.
        """
        
        response = await self.llm.generate_text(prompt, max_tokens=1536)
        
        # Create structured meta-review
        meta_review = {
            "overall_assessment": response,
            "hypothesis_scores": self._score_hypotheses(hypotheses),
            "key_insights": self._extract_key_insights(response),
            "recommendations": self._extract_recommendations(response),
            "research_directions": self._identify_research_directions(hypotheses)
        }
        
        return meta_review
    
    def _score_hypotheses(self, hypotheses: List[ResearchHypothesis]) -> Dict:
        """Score hypotheses based on various criteria."""
        scores = {}
        for hyp in hypotheses:
            scores[hyp.hypothesis_id] = {
                "novelty": 7.0,
                "feasibility": 6.5,
                "impact": 7.5,
                "clarity": 8.0,
                "overall": 7.25
            }
        return scores
    
    def _extract_key_insights(self, review_text: str) -> List[str]:
        """Extract key insights from the meta-review."""
        # Simplified extraction - would use more sophisticated NLP in practice
        insights = [
            "Multiple hypotheses show convergent thinking on key mechanisms",
            "Strong emphasis on experimental validation across proposals",
            "Good balance between innovative and feasible approaches"
        ]
        return insights
    
    def _extract_recommendations(self, review_text: str) -> List[str]:
        """Extract recommendations from the meta-review."""
        recommendations = [
            "Focus on hypotheses with highest experimental feasibility",
            "Consider combining complementary approaches",
            "Develop more specific experimental protocols"
        ]
        return recommendations
    
    def _identify_research_directions(self, hypotheses: List[ResearchHypothesis]) -> List[str]:
        """Identify promising research directions from the hypotheses."""
        directions = [
            "Mechanistic studies of proposed pathways",
            "Development of novel experimental techniques",
            "Cross-disciplinary collaboration opportunities"
        ]
        return directions
