"""
Updated Co-Scientist class with support for multiple LLM providers.
"""
import os
import json
import time
import logging
from collections import Counter
from typing import Dict, List, Optional, Any, Union

from .llm_interface import LLMInterface, create_llm
from .agent_core import (
    SupervisorAgent, Task, ResearchHypothesis, ContextMemory
)
from ..agents.specialized_agents import (
    GenerationAgent, ReflectionAgent, RankingAgent,
    EvolutionAgent, ProximityAgent, MetaReviewAgent,
    ProteinAgent
)
from .multi_llm_config import LLMConfig, AgentLLMConfig

class CoScientist:
    """
    AI Co-scientist system for generating and evaluating novel research hypotheses.

    This class orchestrates the multi-agent system described in the paper,
    providing a simple interface for scientists to interact with the system.

    Supports using different LLM providers for different agent types.
    """

    def __init__(self,
                 llm_config: Optional[Union[str, LLMConfig, AgentLLMConfig]] = None,
                 storage_path: Optional[str] = None,
                 max_workers: int = 4,
                 logger_level: int = logging.INFO):
        """
        Initialize the Co-Scientist system.

        Args:
            llm_config: LLM configuration, which can be:
                - A string provider name (e.g. "anthropic", "gemini", "openai")
                - A single LLMConfig instance to use for all agents
                - An AgentLLMConfig instance for fine-grained control
            storage_path: Path to store memory (if None, memory is not persisted)
            max_workers: Maximum number of worker threads
            logger_level: Logging level
        """
        # Configure logging
        logging.basicConfig(
            level=logger_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("CoScientist")
        self.calls_per_call_type = Counter()
        self.in_tokens_per_call_type = Counter()
        self.out_tokens_per_call_type = Counter()

        # Process the llm_config parameter
        self.llm_configs = self._process_llm_config(llm_config)
        self.logger.info(f"Created LLM configuration with default provider: {self.llm_configs.default.provider}")

        # Create a dictionary to store LLM instances
        self.llm_instances = {}

        # Create memory
        self.memory = ContextMemory(storage_path)
        self.logger.info(f"Created context memory{' with persistence' if storage_path else ''}")

        # Create supervisor agent
        supervisor_llm = self._get_llm_for_agent("supervisor", "supervisor")
        self.supervisor = SupervisorAgent(supervisor_llm, self.memory, max_workers=max_workers)

        # Initialize research goal
        self.research_goal = None

        # Create specialized agents
        self._create_specialized_agents()

        self.logger.info("Co-Scientist system initialized and ready")

    def _process_llm_config(self, llm_config) -> AgentLLMConfig:
        """Process and normalize the llm_config parameter."""
        if llm_config is None:
            # Default to Anthropic if no config provided
            return AgentLLMConfig(
                default=LLMConfig(provider="anthropic")
            )
        elif isinstance(llm_config, str):
            # Simple string provider name
            return AgentLLMConfig(
                default=LLMConfig(provider=llm_config)
            )
        elif isinstance(llm_config, LLMConfig):
            # Single LLM config for all agents
            return AgentLLMConfig(
                default=llm_config
            )
        elif isinstance(llm_config, AgentLLMConfig):
            # Already an AgentLLMConfig
            return llm_config
        else:
            raise ValueError(f"Unsupported llm_config type: {type(llm_config)}")

    def _get_llm_for_agent(self, agent_type: str, agent_id: str) -> LLMInterface:
        """
        Get or create an LLM interface for a specific agent.

        Args:
            agent_type: Type of agent (e.g., "generation", "reflection")
            agent_id: Unique identifier for the agent instance

        Returns:
            An LLM interface appropriate for this agent
        """
        # Get the LLM configuration for this agent
        llm_config = self.llm_configs.get_config_for_agent(agent_type, agent_id)

        # Create a cache key based on the LLM config
        cache_key = f"{llm_config.provider}_{llm_config.model}_{llm_config.api_key}_{llm_config.base_url}"
        if llm_config.model_adapter:
            cache_key += f"_{llm_config.model_adapter.get('type')}_{llm_config.model_adapter.get('path')}_{llm_config.model_adapter.get('task_id')}"

        # Check if we already have an instance for this configuration
        if cache_key not in self.llm_instances:
            # Create a new LLM instance
            self.llm_instances[cache_key] = create_llm(
                llm_config.provider,
                api_key=llm_config.api_key,
                model=llm_config.model,
                base_url=llm_config.base_url,
                model_adapter=llm_config.model_adapter
            )
            self.logger.info(f"Created new LLM instance: {llm_config.provider} ({llm_config.model})")
            if llm_config.model_adapter:
                adapter_type = llm_config.model_adapter.get("type")
                task_id = llm_config.model_adapter.get("task_id")
                self.logger.info(f"  With {adapter_type} adapter, task_id={task_id}")

        return self.llm_instances[cache_key]

    def _create_specialized_agents(self):
        """Create and register all specialized agents."""
        # Generation agents
        #TODO: make programatically specifiable
        for i in range(5):  # Create multiple generation agents for diversity
            llm = self._get_llm_for_agent("generation", f"generation-{i}")
            agent = GenerationAgent(f"generation-{i}", llm, self.memory)
            self.supervisor.register_agent(agent)
            # Initialize agent state
            self._initialize_agent_state(agent)

        #TODO: make programatically specifiable
        # Reflection agents
        for i in range(2):  # Create multiple reflection agents
            llm = self._get_llm_for_agent("reflection", f"reflection-{i}")
            agent = ReflectionAgent(f"reflection-{i}", llm, self.memory)
            self.supervisor.register_agent(agent)
            self._initialize_agent_state(agent)

        # Protein agent
        llm = self._get_llm_for_agent("protein", "protein-0")
        protein_agent = ProteinAgent("protein-0", llm, self.memory)
        self.supervisor.register_agent(protein_agent)
        self._initialize_agent_state(protein_agent)
        
        # Ranking agent
        llm = self._get_llm_for_agent("ranking", "ranking-0")
        ranking_agent = RankingAgent("ranking-0", llm, self.memory)
        self.supervisor.register_agent(ranking_agent)
        self._initialize_agent_state(ranking_agent)

        # Evolution agent
        llm = self._get_llm_for_agent("evolution", "evolution-0")
        evolution_agent = EvolutionAgent("evolution-0", llm, self.memory)
        self.supervisor.register_agent(evolution_agent)
        self._initialize_agent_state(evolution_agent)

        # Proximity agent
        llm = self._get_llm_for_agent("proximity", "proximity-0")
        proximity_agent = ProximityAgent("proximity-0", llm, self.memory)
        self.supervisor.register_agent(proximity_agent)
        self._initialize_agent_state(proximity_agent)

        # Meta-review agent
        llm = self._get_llm_for_agent("meta-review", "meta-review-0")
        meta_review_agent = MetaReviewAgent("meta-review-0", llm, self.memory)
        self.supervisor.register_agent(meta_review_agent)
        self._initialize_agent_state(meta_review_agent)

        self.logger.info("Created and registered all specialized agents")

    def _initialize_agent_state(self, agent):
        """Initialize the state for a newly created agent."""
        initial_state = {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "created_at": time.time(),
            "last_activity": time.time(),
            "total_tasks_completed": 0,
            "status": "active"
        }

        # Add agent-specific state fields
        if agent.agent_type == "generation":
            initial_state.update({
                "hypotheses_generated": 0,
                "strategies_used": [],
                "last_strategy": None
            })
        elif agent.agent_type == "reflection":
            initial_state.update({
                "reviews_completed": 0,
                "review_types_used": [],
                "last_review_type": None
            })
        elif agent.agent_type == "ranking":
            initial_state.update({
                "rankings_completed": 0,
                "criteria_used": [],
                "last_ranking_criteria": None
            })
        elif agent.agent_type == "evolution":
            initial_state.update({
                "evolutions_completed": 0,
                "evolution_types_used": [],
                "last_evolution_type": None
            })
        elif agent.agent_type == "proximity":
            initial_state.update({
                "analyses_completed": 0,
                "analysis_types_used": [],
                "last_analysis_type": None
            })
        elif agent.agent_type == "meta_review":
            initial_state.update({
                "meta_reviews_completed": 0,
                "review_types_used": [],
                "last_review_type": None
            })

        self.memory.set_agent_state(agent.agent_id, initial_state)
        self.logger.info(f"Initialized state for agent {agent.agent_id} ({agent.agent_type})")

    def register_custom_agent(self, agent):
        """
        Register a custom agent with the system.

        Args:
            agent: The agent instance to register
        """
        self.supervisor.register_agent(agent)
        self.logger.info(f"Registered custom agent: {agent.agent_id} ({agent.agent_type})")

    def set_research_goal(self, research_goal: str) -> Dict:
        """
        Set the research goal for the system.

        Args:
            research_goal: The research goal specified by the scientist

        Returns:
            Dictionary containing the parsed research plan configuration
        """
        self.logger.info(f"Setting research goal: {research_goal[:100]}...")

        # Store as instance variable
        self.research_goal = research_goal

        # Parse the research goal
        research_plan = self.supervisor.parse_research_goal(research_goal)

        # Store in memory
        self.memory.set_research_goal(research_goal, research_plan)

        self.logger.info("Research goal set and parsed")
        return research_plan

    def start(self):
        """Start the co-scientist system."""
        self.supervisor.start()
        self.logger.info("Co-Scientist system started")

    def stop(self):
        """Stop the co-scientist system."""
        self.supervisor.stop()
        self.logger.info("Co-Scientist system stopped")

    def wait_for_completion(self, timeout: Optional[float] = None):
        """
        Wait for all current tasks to complete.

        Args:
            timeout: Optional timeout in seconds
        """
        self.supervisor.wait_for_all_tasks(timeout)

    def get_agent_usages(self, verbose=True):
        return self.supervisor.get_usages(verbose=verbose)

    def get_hypo_dict(self):
        return self.memory.hypotheses

    def get_all_hypotheses(self):
        """
        Get all hypotheses from memory.

        Returns:
            List of ResearchHypothesis objects
        """
        return list(self.memory.hypotheses.values())

    def evolve_hypothesis(self, hypothesis_id: str, feedback: str = None) -> Dict:
        """
        Evolve a hypothesis based on feedback.

        Args:
            hypothesis_id: ID of hypothesis to evolve
            feedback: Optional feedback for evolution

        Returns:
            Dictionary containing evolved hypothesis information
        """
        try:
            # Create evolution task
            task = Task(
                task_type="evolve_hypothesis",
                agent_type="evolution",
                priority=2,
                params={
                    "hypothesis_id": hypothesis_id,
                    "feedback": feedback or ""
                }
            )

            # Add task and wait for completion
            self.supervisor.add_task(task)
            self.supervisor.wait_for_all_tasks()

            # Return the task result
            return task.result or {"evolved_hypothesis_id": hypothesis_id}

        except Exception as e:
            self.logger.error(f"Error evolving hypothesis {hypothesis_id}: {e}")
            return {"error": str(e), "evolved_hypothesis_id": hypothesis_id}

    # [The rest of the CoScientist class methods remain unchanged]
    # ... (methods like generate_hypotheses, review_hypotheses, run_tournament, etc.)

    # Include the standard methods from the original CoScientist class here
    # They don't need to be modified for the multi-LLM support

    def generate_hypotheses(self, count: int = 5, strategies: Optional[List[str]] = None) -> List[str]:
        """
        Generate a specified number of research hypotheses.

        Args:
            count: Number of hypotheses to generate
            strategies: Optional list of generation strategies to use
                        ("literature_exploration", "scientific_debate",
                         "assumptions_identification", "research_expansion")

        Returns:
            List of generated hypothesis IDs
        """
        self.logger.info(f"Scheduling generation of {count} hypotheses")

        if not self.memory.metadata.get("research_goal"):
            raise ValueError("Research goal must be set before generating hypotheses")

        # Default strategies if none provided
        all_strategies = ["literature_exploration", "scientific_debate",
                         "assumptions_identification", "research_expansion"]

        if strategies:
            # Validate strategies
            for strategy in strategies:
                if strategy not in all_strategies:
                    raise ValueError(f"Unknown strategy: {strategy}")
        else:
            strategies = all_strategies

        # Create tasks for hypothesis generation
        hypothesis_ids = []
        for i in range(count):
            # Cycle through strategies
            strategy = strategies[i % len(strategies)]

            task = Task(
                task_type="generate_hypothesis",
                agent_type="generation",
                priority=1,
                params={
                    "strategy": strategy,
                    "research_goal": self.research_goal
                }
            )

            self.supervisor.add_task(task)

            #wait for completion and fetch ids?

        return hypothesis_ids

    def generate_protein_report(self,hypothesis_id):
        self.logger.info(f"Scheduling Protein Report for hypothesis {hypothesis_id}")

        task = Task(
                task_type="generate_protein_report",
                agent_type="protein",
                priority=1,
                params={
                    "hypothesis_id": hypothesis_id
                }
            )
        self.supervisor.add_task(task)


    def review_hypotheses(self, hypothesis_ids: Optional[List[str]] = None,
                         review_types: Optional[List[str]] = None) -> Dict:
        """
        Schedule reviews for hypotheses.

        Args:
            hypothesis_ids: List of hypothesis IDs to review (if None, reviews all unreviewed hypotheses)
            review_types: Types of reviews to conduct (if None, conducts all review types)
                         ("initial_review", "full_review", "deep_verification",
                          "observation_review", "simulation_review")

        Returns:
            Dictionary with task information
        """
        self.logger.info("Scheduling hypothesis reviews")

        all_review_types = ["initial_review", "full_review", "deep_verification",
                           "observation_review", "simulation_review"]

        # Validate review types
        if review_types:
            for review_type in review_types:
                if review_type not in all_review_types:
                    raise ValueError(f"Unknown review type: {review_type}")
        else:
            # Default to lighter reviews first
            review_types = ["initial_review", "full_review"]

        # Get hypotheses to review
        if hypothesis_ids:
            hypotheses = [self.memory.get_hypothesis(h_id) for h_id in hypothesis_ids]
            hypotheses = [h for h in hypotheses if h]  # Filter out None values
        else:
            # Get all hypotheses that haven't been reviewed yet
            all_hypotheses = self.memory.get_all_hypotheses()
            hypotheses = []

            for h in all_hypotheses:
                # Check if this hypothesis has had all the requested review types
                existing_review_types = set(r.get("review_type", "") for r in h.reviews)
                missing_reviews = [rt for rt in review_types if rt not in existing_review_types]

                if missing_reviews:
                    hypotheses.append((h, missing_reviews))

        # Schedule review tasks
        tasks_created = {review_type: 0 for review_type in review_types}

        if hypothesis_ids:
            # Simple case: specific hypotheses provided
            for h in hypotheses:
                for review_type in review_types:
                    task = Task(
                        task_type=review_type,
                        agent_type="reflection",
                        priority=2,
                        params={
                            "hypothesis_id": h.hypothesis_id,
                            "review_type": review_type
                        }
                    )

                    self.supervisor.add_task(task)
                    tasks_created[review_type] += 1
        else:
            # Complex case: hypotheses with missing reviews
            for h, missing_reviews in hypotheses:
                for review_type in missing_reviews:
                    task = Task(
                        task_type=review_type,
                        agent_type="reflection",
                        priority=2,
                        params={"hypothesis_id": h.hypothesis_id}
                    )

                    self.supervisor.add_task(task)
                    tasks_created[review_type] += 1

        return {"tasks_created": tasks_created, "hypotheses_count": len(hypotheses)}

    def run_tournament(self, match_count: int = 10,
                      hypothesis_ids: Optional[List[str]] = None) -> Dict:
        """
        Schedule tournament matches to compare and rank hypotheses.

        Args:
            match_count: Number of tournament matches to schedule
            hypothesis_ids: Optional list of hypothesis IDs to include in the tournament
                           (if None, includes all hypotheses)

        Returns:
            Dictionary with tournament information
        """
        self.logger.info(f"Scheduling {match_count} tournament matches")

        # Get hypotheses for the tournament
        if hypothesis_ids:
            hypotheses = [self.memory.get_hypothesis(h_id) for h_id in hypothesis_ids]
            hypotheses = [h for h in hypotheses if h]  # Filter out None values
        else:
            hypotheses = self.memory.get_all_hypotheses()

        if len(hypotheses) < 2:
            raise ValueError("Need at least 2 hypotheses for a tournament")

        # Use proximity information if available to match similar hypotheses
        agent_state = self.memory.get_agent_state("proximity-0") or {}
        similarity_cache = agent_state.get("similarity_cache", {})

        # Schedule tournament matches
        for _ in range(match_count):
            # Simple random selection for now
            # In a real implementation, this would use proximity data and more sophisticated selection
            import random
            h1, h2 = random.sample(hypotheses, 2)

            task = Task(
                task_type="tournament_match",
                agent_type="ranking",
                priority=3,
                params={
                    "hypothesis1_id": h1.hypothesis_id,
                    "hypothesis2_id": h2.hypothesis_id
                }
            )

            self.supervisor.add_task(task)

        # Schedule a task to update the rankings
        update_task = Task(
            task_type="update_rankings",
            agent_type="ranking",
            priority=4  # Lower priority so it runs after matches
        )

        self.supervisor.add_task(update_task)

        return {
            "match_count": match_count,
            "hypotheses_count": len(hypotheses)
        }

    def evolve_hypotheses(self, count: int = 3,
                         evolution_types: Optional[List[str]] = None,
                         top_k: int = 5) -> Dict:
        """
        Schedule tasks to evolve and improve hypotheses.

        Args:
            count: Number of evolution tasks to schedule per type
            evolution_types: Types of evolution to perform (if None, performs all types)
                           ("improve_hypothesis", "combine_hypotheses", "simplify_hypothesis", "out_of_box_thinking")
            top_k: Number of top hypotheses to consider for evolution

        Returns:
            Dictionary with task information
        """
        self.logger.info(f"Scheduling hypothesis evolution tasks")

        all_evolution_types = ["improve_hypothesis", "combine_hypotheses",
                             "simplify_hypothesis", "out_of_box_thinking"]

        # Validate evolution types
        if evolution_types:
            for evolution_type in evolution_types:
                if evolution_type not in all_evolution_types:
                    raise ValueError(f"Unknown evolution type: {evolution_type}")
        else:
            evolution_types = all_evolution_types

        # Get top hypotheses by Elo rating
        all_hypotheses = self.memory.get_all_hypotheses()
        top_hypotheses = sorted(all_hypotheses, key=lambda h: h.elo_rating, reverse=True)[:top_k]

        if not top_hypotheses:
            raise ValueError("No hypotheses available for evolution")

        # Schedule evolution tasks
        tasks_created = {evolution_type: 0 for evolution_type in evolution_types}

        for evolution_type in evolution_types:
            for _ in range(count):
                if evolution_type == "improve_hypothesis":
                    # Randomly select a hypothesis to improve
                    import random
                    hypothesis = random.choice(top_hypotheses)

                    task = Task(
                        task_type=evolution_type,
                        agent_type="evolution",
                        priority=3,
                        params={"hypothesis_id": hypothesis.hypothesis_id}
                    )

                elif evolution_type == "combine_hypotheses":
                    # Select 2-3 hypotheses to combine
                    import random
                    num_to_combine = min(len(top_hypotheses), random.randint(2, 3))
                    hypotheses_to_combine = random.sample(top_hypotheses, num_to_combine)

                    task = Task(
                        task_type=evolution_type,
                        agent_type="evolution",
                        priority=3,
                        params={"hypothesis_ids": [h.hypothesis_id for h in hypotheses_to_combine]}
                    )

                elif evolution_type == "simplify_hypothesis":
                    # Select a hypothesis to simplify
                    import random
                    hypothesis = random.choice(top_hypotheses)

                    task = Task(
                        task_type=evolution_type,
                        agent_type="evolution",
                        priority=3,
                        params={"hypothesis_id": hypothesis.hypothesis_id}
                    )

                elif evolution_type == "out_of_box_thinking":
                    # No specific hypothesis needed
                    task = Task(
                        task_type=evolution_type,
                        agent_type="evolution",
                        priority=3
                    )

                self.supervisor.add_task(task)
                tasks_created[evolution_type] += 1

        return {"tasks_created": tasks_created}

    def generate_research_insights(self) -> Dict:
        """
        Schedule tasks to generate meta-reviews and research overviews.

        Returns:
            Dictionary with task information
        """
        self.logger.info("Scheduling research insight generation")

        # Schedule meta-review task
        meta_review_task = Task(
            task_type="generate_meta_review",
            agent_type="meta-review",
            priority=3
        )

        self.supervisor.add_task(meta_review_task)

        # Schedule research overview task
        # This should run after the meta-review
        overview_task = Task(
            task_type="generate_research_overview",
            agent_type="meta-review",
            priority=4
        )

        self.supervisor.add_task(overview_task)

        # Schedule research contacts task
        contacts_task = Task(
            task_type="identify_research_contacts",
            agent_type="meta-review",
            priority=4
        )

        self.supervisor.add_task(contacts_task)

        return {
            "tasks_scheduled": ["meta_review", "research_overview", "research_contacts"]
        }

    def get_top_hypotheses(self, k: int = 10) -> List[Dict]:
        """
        Get the top-k hypotheses by Elo rating.

        Args:
            k: Number of top hypotheses to return

        Returns:
            List of top hypotheses with their details
        """
        # Get all hypotheses
        hypotheses = self.memory.get_all_hypotheses()

        # Sort by Elo rating
        top_hypotheses = sorted(hypotheses, key=lambda h: h.elo_rating, reverse=True)[:k]

        # Format for return
        return [
            {
                "hypothesis_id": h.hypothesis_id,
                "content": h.content,
                "summary": h.summary,
                "elo_rating": h.elo_rating,
                "created_at": h.created_at,
                "agent_id": h.agent_id,
                "review_count": len(h.reviews),
                "tournament_matches": len(h.tournament_matches)
            }
            for h in top_hypotheses
        ]

    def get_research_overview(self) -> Optional[Dict]:
        """
        Get the latest research overview.

        Returns:
            Dictionary containing the research overview, or None if not available
        """
        agent_state = self.memory.get_agent_state("meta-review-0") or {}
        return agent_state.get("research_overview")

    def get_meta_review(self) -> Optional[Dict]:
        """
        Get the latest meta-review.

        Returns:
            Dictionary containing the meta-review, or None if not available
        """
        agent_state = self.memory.get_agent_state("meta-review-0") or {}
        return agent_state.get("meta_review")

    def get_proximity_graph(self) -> Optional[Dict]:
        """
        Get the proximity graph.

        Returns:
            Dictionary containing the proximity graph, or None if not available
        """
        agent_state = self.memory.get_agent_state("proximity-0") or {}
        return agent_state.get("proximity_graph")

    def get_statistics(self) -> Dict:
        """
        Get system statistics.

        Returns:
            Dictionary containing system statistics
        """
        # Calculate statistics
        return self.supervisor.calculate_statistics()

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Dict]:
        """
        Get a specific hypothesis by ID.

        Args:
            hypothesis_id: ID of the hypothesis to retrieve

        Returns:
            Dictionary containing the hypothesis details, or None if not found
        """
        hypothesis = self.memory.get_hypothesis(hypothesis_id)

        if not hypothesis:
            return None

        return {
            "hypothesis_id": hypothesis.hypothesis_id,
            "content": hypothesis.content,
            "summary": hypothesis.summary,
            "elo_rating": hypothesis.elo_rating,
            "created_at": hypothesis.created_at,
            "agent_id": hypothesis.agent_id,
            "metadata": hypothesis.metadata,
            "reviews": hypothesis.reviews,
            "tournament_matches": hypothesis.tournament_matches
        }

    def run_full_cycle(self, iterations: int = 1, initial_hypotheses: int = 5,
                      matches_per_iteration: int = 10) -> Dict:
        """
        Run a full research cycle with multiple iterations of generation, review, tournament, and evolution.

        Args:
            iterations: Number of full cycles to run
            initial_hypotheses: Number of initial hypotheses to generate
            matches_per_iteration: Number of tournament matches per iteration

        Returns:
            Dictionary with results and statistics
        """
        self.logger.info(f"Running full research cycle with {iterations} iterations")

        if not self.memory.metadata.get("research_goal"):
            raise ValueError("Research goal must be set before running a research cycle")

        # Start the system
        self.start()

        try:
            # Generate initial hypotheses
            self.generate_hypotheses(count=initial_hypotheses)

            # Wait for initial generation to complete
            self.wait_for_completion()

            self.get_agent_usages()

            for i in range(iterations):
                self.logger.info(f"Starting iteration {i+1}/{iterations}")

                # Review all hypotheses
                self.review_hypotheses()

                # Wait for reviews to complete
                self.wait_for_completion()

                # Run tournament
                self.run_tournament(match_count=matches_per_iteration)

                # Wait for tournament to complete
                self.wait_for_completion()

                # Build proximity graph
                # self.build_proximity_graph()

                # Evolve hypotheses
                self.evolve_hypotheses()

                # Wait for evolution to complete
                self.wait_for_completion()

                # Generate new hypotheses
                self.generate_hypotheses(count=3)

                # Wait for generation to complete
                self.wait_for_completion()

                self.get_agent_usages()

            # Generate final research insights
            self.generate_research_insights()

            # Wait for insights to complete
            self.wait_for_completion()

            # Calculate final statistics
            stats = self.get_statistics()

            # Get top hypotheses
            top_hypotheses = self.get_top_hypotheses(10)

            # Get research overview
            overview = self.get_research_overview()

            self.get_agent_usages()

            return {
                "completed_iterations": iterations,
                "statistics": stats,
                "top_hypotheses": top_hypotheses,
                "research_overview": overview
            }

        finally:
            # Ensure system is stopped
            self.stop()
