"""
Proximity Agent for ProtoGnosis.

This agent analyzes relationships and similarities between hypotheses.
"""

import json
import time
from typing import Dict, List, Optional, Any
import logging

from ..core.agent_core import Agent, Task, ResearchHypothesis, ContextMemory
from ..core.llm_interface import LLMInterface


class ProximityAgent(Agent):
    """
    Agent responsible for analyzing hypothesis relationships and proximity.
    """
    
    def __init__(self, agent_id: str, llm: LLMInterface, memory: ContextMemory):
        """Initialize the proximity agent."""
        super().__init__(agent_id, "proximity", llm, memory)
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute a hypothesis proximity analysis task.
        
        Args:
            task: Task containing hypotheses to analyze
            
        Returns:
            Dictionary containing proximity analysis results
        """
        try:
            hypothesis_ids = task.parameters.get("hypothesis_ids", [])
            analysis_type = task.parameters.get("analysis_type", "similarity")
            
            self.logger.info(f"Analyzing proximity for {len(hypothesis_ids)} hypotheses")
            
            # Get hypotheses from memory
            hypotheses = []
            for hyp_id in hypothesis_ids:
                hyp = self.memory.get_hypothesis(hyp_id)
                if hyp:
                    hypotheses.append(hyp)
            
            if len(hypotheses) < 2:
                return {"error": "Need at least 2 hypotheses for proximity analysis"}
            
            # Perform proximity analysis
            analysis = await self._analyze_proximity(hypotheses, analysis_type)
            
            return {
                "analysis": analysis,
                "analysis_type": analysis_type,
                "hypothesis_count": len(hypotheses),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing proximity: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
    
    async def _analyze_proximity(self, hypotheses: List[ResearchHypothesis], 
                                analysis_type: str) -> Dict:
        """Analyze proximity/relationships between hypotheses."""
        
        # Create comparison prompt
        hypothesis_texts = []
        for i, hyp in enumerate(hypotheses):
            hypothesis_texts.append(f"Hypothesis {i+1} (ID: {hyp.hypothesis_id}): {hyp.content}")
        
        prompt = f"""
        Analyze the relationships and similarities between these research hypotheses:
        
        {chr(10).join(hypothesis_texts)}
        
        Analysis Type: {analysis_type}
        
        Please provide:
        1. Similarity scores between each pair (0-1 scale)
        2. Common themes and concepts
        3. Complementary aspects
        4. Conflicting elements
        5. Potential for combination or synthesis
        
        Identify clusters of related hypotheses and explain the relationships.
        """
        
        response = await self.llm.generate_text(prompt, max_tokens=1024)
        
        # Create proximity matrix (simplified)
        proximity_matrix = {}
        for i, hyp1 in enumerate(hypotheses):
            for j, hyp2 in enumerate(hypotheses):
                if i != j:
                    # Simple similarity score (would be more sophisticated in practice)
                    similarity = 0.5  # Default similarity
                    proximity_matrix[f"{hyp1.hypothesis_id}-{hyp2.hypothesis_id}"] = similarity
        
        return {
            "proximity_matrix": proximity_matrix,
            "analysis_text": response,
            "clusters": self._identify_clusters(hypotheses),
            "recommendations": "Consider combining similar hypotheses or exploring differences"
        }
    
    def _identify_clusters(self, hypotheses: List[ResearchHypothesis]) -> List[Dict]:
        """Identify clusters of related hypotheses."""
        # Simplified clustering - in practice would use more sophisticated methods
        clusters = []
        
        if len(hypotheses) >= 2:
            clusters.append({
                "cluster_id": "cluster_1",
                "hypothesis_ids": [hyp.hypothesis_id for hyp in hypotheses[:2]],
                "theme": "Related research approaches",
                "similarity_score": 0.7
            })
        
        return clusters
