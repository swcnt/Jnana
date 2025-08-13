"""
Main Jnana system class.

This module provides the core Jnana system that integrates Wisteria's
interactive capabilities with ProtoGnosis's multi-agent processing.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .model_manager import UnifiedModelManager
from .session_manager import SessionManager
from .event_manager import EventManager, EventType
from ..data.storage import JnanaStorage
from ..data.unified_hypothesis import UnifiedHypothesis
from ..ui.interactive_interface import InteractiveInterface
from ..agents.biomni_modern import ModernBiomniAgent as BiomniAgent, ModernBiomniConfig as BiomniConfig

# Import ProtoGnosis components (integrated)
try:
    from ..protognosis import CoScientist, is_protognosis_available
    from ..protognosis.utils.jnana_adapter import JnanaProtoGnosisAdapter
    PROTOGNOSIS_AVAILABLE = is_protognosis_available()
except ImportError as e:
    PROTOGNOSIS_AVAILABLE = False
    CoScientist = None
    JnanaProtoGnosisAdapter = None


class JnanaSystem:
    """
    Main Jnana system that integrates interactive hypothesis generation
    with scalable multi-agent processing.
    """
    
    def __init__(self, config_path: Union[str, Path] = "config/models.yaml",
                 storage_path: Union[str, Path] = "data/jnana_run29.db",
                 storage_type: str = "json",
                 max_workers: int = 4,
                 output_path: Optional[Union[str, Path]] = None,
                 enable_ui: bool = True):
        """
        Initialize the Jnana system.
        
        Args:
            config_path: Path to model configuration file
            storage_path: Path to storage location
            storage_type: Type of storage ("json", "sqlite")
            max_workers: Maximum number of concurrent workers
            output_path: Optional output path for session files
            enable_ui: Whether to enable the interactive UI
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.model_manager = UnifiedModelManager(config_path)
        self.event_manager = EventManager()
        self.storage = JnanaStorage(storage_path, storage_type)
        self.session_manager = SessionManager(self.storage, self.event_manager)
        
        # Configuration
        self.max_workers = max_workers
        self.output_path = Path(output_path) if output_path else None
        self.enable_ui = enable_ui
        
        # System state
        self.running = False
        self.current_mode = "interactive"
        
        # UI component
        self.ui: Optional[InteractiveInterface] = None
        if enable_ui:
            self.ui = InteractiveInterface(self.event_manager, self.session_manager, self)
        
        # ProtoGnosis integration
        self.protognosis_adapter: Optional[JnanaProtoGnosisAdapter] = None
        if PROTOGNOSIS_AVAILABLE and JnanaProtoGnosisAdapter:
            self._initialize_protognosis()

        # Biomni integration
        self.biomni_agent: Optional[BiomniAgent] = None
        self._initialize_biomni()

        self.logger.info("Jnana system initialized")
    
    def _initialize_protognosis(self):
        """Initialize ProtoGnosis adapter if available."""
        try:
            self.protognosis_adapter = JnanaProtoGnosisAdapter(
                model_manager=self.model_manager,
                storage_path=str(self.storage.storage_path),
                max_workers=self.max_workers
            )
            self.logger.info("ProtoGnosis adapter initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize ProtoGnosis adapter: {e}")
            self.protognosis_adapter = None

    def _initialize_biomni(self):
        """Initialize Biomni biomedical verification agent."""
        try:
            # Load Biomni configuration from models.yaml
            biomni_config_dict = self.model_manager.config.get("biomni", {})

            # Check if Biomni is enabled in configuration
            if not biomni_config_dict.get("enabled", False):
                self.logger.info("Biomni integration disabled in configuration")
                self.biomni_agent = None
                return

            biomni_config = BiomniConfig(
                enabled=biomni_config_dict.get("enabled", False),
                data_path=biomni_config_dict.get("data_path", "./data/biomni"),
                llm_model=biomni_config_dict.get("llm_model", "claude-sonnet-4-20250514"),
                api_key=biomni_config_dict.get("api_key", ""),
                confidence_threshold=biomni_config_dict.get("confidence_threshold", 0.6),
                max_execution_time=biomni_config_dict.get("max_execution_time", 300),
                enable_experimental_suggestions=biomni_config_dict.get("enable_experimental_suggestions", True)
            )

            self.biomni_agent = BiomniAgent(biomni_config)
            self.logger.info("Biomni agent initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize Biomni agent: {e}")
            self.biomni_agent = None
    
    async def start(self):
        """Start the Jnana system."""
        if self.running:
            return
        
        self.running = True
        
        # Start event manager
        await self.event_manager.start()
        
        # Initialize ProtoGnosis if available
        if self.protognosis_adapter:
            await self.protognosis_adapter.initialize()
        
        # Initialize Biomni agent if available
        if self.biomni_agent:
            await self.biomni_agent.initialize()
        
        self.logger.info("Jnana system started")
    
    async def stop(self):
        """Stop the Jnana system."""
        if not self.running:
            return
        
        self.running = False
        
        # Stop event manager
        await self.event_manager.stop()

        # Stop ProtoGnosis adapter if running
        if self.protognosis_adapter:
            await self.protognosis_adapter.shutdown()

        self.logger.info("Jnana system stopped")
    
    async def set_research_goal(self, research_goal: str) -> str:
        """
        Set the research goal and create a new session.
        
        Args:
            research_goal: The research question or goal
            
        Returns:
            Session ID
        """
        session_id = await self.session_manager.create_session(
            research_goal=research_goal,
            mode=self.current_mode
        )
        
        # ProtoGnosis adapter doesn't need explicit research goal setting
        # It gets the research goal from session when generating hypotheses
        
        self.logger.info(f"Research goal set: {research_goal[:100]}...")
        return session_id
    
    async def resume_session(self, session_path: Union[str, Path]) -> str:
        """
        Resume a previous session.
        
        Args:
            session_path: Path to session file
            
        Returns:
            Session ID
        """
        await self.protognosis_adapter.initialize()
        session_id = await self.session_manager.load_session(session_path)
        
        # Session info is automatically available to ProtoGnosis adapter when needed
        
        self.logger.info(f"Session resumed: {session_id}")
        return session_id
    
    async def run_interactive_mode(self, model_override: Optional[str] = None):
        """
        Run in interactive mode with real-time user interaction.
        
        Args:
            model_override: Optional model to use instead of default
        """
        if not self.ui:
            raise ValueError("UI not enabled for interactive mode")
        
        self.current_mode = "interactive"
        
        # Get model configuration
        if model_override:
            # TODO: Handle model override
            pass
        
        model_config = self.model_manager.get_interactive_model()
        
        # Start the interactive interface
        await self.ui.start_interactive_session(model_config)
    
    async def run_batch_mode(self, hypothesis_count: int = 5,
                           strategies: Optional[List[str]] = None,
                           tournament_matches: int = 25):
        """
        Run in batch mode for large-scale hypothesis generation.
        
        Args:
            hypothesis_count: Number of hypotheses to generate
            strategies: Generation strategies to use
            tournament_matches: Number of tournament matches for ranking
        """
        self.current_mode = "batch"

        if self.protognosis_adapter:
            # Full batch mode with ProtoGnosis
            self.logger.info(f"Generating {hypothesis_count} hypotheses with ProtoGnosis...")

            # Get research goal
            session_info = self.session_manager.get_session_info()
            research_goal = session_info.get('research_goal', 'No research goal set')

            # Generate hypotheses using adapter
            hypotheses = await self.protognosis_adapter.generate_hypotheses(
                research_goal=research_goal,
                count=hypothesis_count,
                strategies=strategies
            )

            # Run tournament evaluation
            self.logger.info(f"Running tournament with {tournament_matches} matches...")
            ranked_hypotheses = await self.protognosis_adapter.run_tournament(
                hypotheses, match_count=tournament_matches
            )

            # Add to session
            for hypothesis in ranked_hypotheses:
                await self.session_manager.add_hypothesis(hypothesis)
        else:
            # Fallback batch mode without ProtoGnosis
            self.logger.info(f"Running batch mode without ProtoGnosis (fallback mode)...")
            await self._run_fallback_batch_mode(hypothesis_count, strategies)
        
        # Save session
        if self.output_path:
            await self.session_manager.save_session(self.output_path)
        else:
            await self.session_manager.save_session()
    
    async def run_hybrid_mode(self, hypothesis_count: int = 5,
                            strategies: Optional[List[str]] = None,
                            interactive_refinement: bool = True,
                            tournament_matches: int = 25):
        """
        Run in hybrid mode combining batch generation with interactive refinement.
        
        Args:
            hypothesis_count: Number of initial hypotheses to generate
            strategies: Generation strategies to use
            interactive_refinement: Whether to allow interactive refinement
            tournament_matches: Number of tournament matches for ranking
        """
        self.current_mode = "hybrid"

        if self.protognosis_adapter:
            # Full hybrid mode with ProtoGnosis
            self.logger.info("Phase 1: Batch hypothesis generation with ProtoGnosis")

            # Get research goal
            session_info = self.session_manager.get_session_info()
            research_goal = session_info.get('research_goal', 'No research goal set')

            # Generate initial hypotheses
            hypotheses = await self.protognosis_adapter.generate_hypotheses(
                research_goal=research_goal,
                count=hypothesis_count,
                strategies=strategies
            )

            # Add to session
            for hypothesis in hypotheses:
                await self.session_manager.add_hypothesis(hypothesis)

            # Phase 2: Interactive refinement (if enabled)
            if interactive_refinement and self.ui:
                self.logger.info("Phase 2: Interactive refinement")
                await self.ui.start_refinement_session()

            # Phase 3: Final tournament
            self.logger.info("Phase 3: Final tournament evaluation")
            # Get updated hypotheses from session
            session_hypotheses = self.session_manager.get_all_hypotheses()
            ranked_hypotheses = await self.protognosis_adapter.run_tournament(
                session_hypotheses, match_count=tournament_matches
            )

            # Update session with ranked results
            for hypothesis in ranked_hypotheses:
                await self.session_manager.update_hypothesis(hypothesis)
        else:
            # Fallback hybrid mode without ProtoGnosis
            self.logger.info("Running hybrid mode without ProtoGnosis (fallback mode)")
            await self._run_fallback_hybrid_mode(hypothesis_count, strategies, interactive_refinement)
        
        # Save session
        if self.output_path:
            await self.session_manager.save_session(self.output_path)
        else:
            await self.session_manager.save_session()

    async def _run_fallback_batch_mode(self, hypothesis_count: int, strategies: Optional[List[str]]):
        """
        Fallback batch mode implementation without ProtoGnosis.

        This generates hypotheses using the model manager directly and performs
        basic ranking without tournament evaluation.
        """
        self.logger.info(f"Generating {hypothesis_count} hypotheses using fallback batch mode...")

        # Default strategies if none provided
        if not strategies:
            strategies = ["literature_exploration", "scientific_debate", "assumptions_identification", "research_expansion"]

        # Generate hypotheses individually
        generated_hypotheses = []
        for i in range(hypothesis_count):
            strategy = strategies[i % len(strategies)]
            self.logger.info(f"Generating hypothesis {i+1}/{hypothesis_count} using strategy: {strategy}")

            try:
                hypothesis = await self._generate_hypothesis_with_model_manager(strategy)
                generated_hypotheses.append(hypothesis)

                # Check if hypothesis is biomedical and verify with Biomni
                await self._verify_hypothesis_with_biomni(hypothesis)

                # Add to session
                await self.session_manager.add_hypothesis(hypothesis)

            except Exception as e:
                self.logger.error(f"Failed to generate hypothesis {i+1}: {e}")
                continue

        self.logger.info(f"Generated {len(generated_hypotheses)} hypotheses successfully")

        # Perform basic ranking (fallback for tournament)
        self.logger.info("Performing basic hypothesis ranking...")
        await self._perform_basic_ranking(generated_hypotheses)

    async def _run_fallback_hybrid_mode(self, hypothesis_count: int, strategies: Optional[List[str]], interactive_refinement: bool):
        """
        Fallback hybrid mode implementation without ProtoGnosis.

        This generates hypotheses using the model manager directly and provides
        interactive refinement capabilities.
        """
        self.logger.info(f"Generating {hypothesis_count} hypotheses using fallback mode...")

        # Default strategies if none provided
        if not strategies:
            strategies = ["literature_exploration", "scientific_debate", "assumptions_identification"]

        # Generate hypotheses individually using model manager
        generated_hypotheses = []
        for i in range(hypothesis_count):
            strategy = strategies[i % len(strategies)]
            self.logger.info(f"Generating hypothesis {i+1}/{hypothesis_count} using strategy: {strategy}")

            try:
                hypothesis = await self._generate_hypothesis_with_model_manager(strategy)
                generated_hypotheses.append(hypothesis)

                # Check if hypothesis is biomedical and verify with Biomni
                await self._verify_hypothesis_with_biomni(hypothesis)

                # Add to session
                await self.session_manager.add_hypothesis(hypothesis)

            except Exception as e:
                self.logger.error(f"Failed to generate hypothesis {i+1}: {e}")
                continue

        self.logger.info(f"Generated {len(generated_hypotheses)} hypotheses successfully")

        # Interactive refinement phase
        if interactive_refinement and self.ui:
            self.logger.info("Starting interactive refinement phase...")
            try:
                await self.ui.start_refinement_session()
            except Exception as e:
                self.logger.error(f"Interactive refinement failed: {e}")
                self.logger.info("Continuing without interactive refinement...")

        # Simple ranking based on basic criteria (fallback for tournament)
        self.logger.info("Performing basic hypothesis ranking...")
        await self._perform_basic_ranking(generated_hypotheses)

    async def _generate_hypothesis_with_model_manager(self, strategy: str) -> UnifiedHypothesis:
        """Generate a single hypothesis using the model manager directly."""
        from ..data.unified_hypothesis import UnifiedHypothesis
        import uuid
        import time

        # Get the research goal
        session_info = self.session_manager.get_session_info()
        research_goal = session_info.get('research_goal', 'No research goal set')

        # Get appropriate model for hypothesis generation
        model_config = self.model_manager.get_task_model("hypothesis_generation")

        # Create prompt based on strategy
        prompt = self._create_strategy_prompt(strategy, research_goal)

        # For now, create a structured hypothesis based on the strategy and research goal
        # TODO: Implement actual LLM API calls through model manager
        self.logger.info(f"Creating structured hypothesis using {strategy} strategy")

        hypothesis_content = self._generate_structured_hypothesis_content(strategy, research_goal)

        hypothesis = UnifiedHypothesis(
            hypothesis_id=str(uuid.uuid4()),
            title=f"Hypothesis: {strategy.replace('_', ' ').title()} Approach",
            description=f"Hypothesis generated using {strategy} strategy",
            content=hypothesis_content,
            generation_strategy=strategy,
            created_at=time.time(),
            version_string="1.0",
            hypothesis_type="generated"
        )

        # Add research goal to metadata
        hypothesis.metadata["research_goal"] = research_goal
        hypothesis.metadata["source_system"] = "jnana_fallback"

        return hypothesis

    def _generate_structured_hypothesis_content(self, strategy: str, research_goal: str) -> str:
        """Generate structured hypothesis content based on strategy and research goal."""

        if strategy == "literature_exploration":
            return f"""**Literature-Based Hypothesis**

Research Goal: {research_goal}

**Hypothesis Statement:**
Based on current scientific literature, we hypothesize that [specific mechanism/relationship] plays a crucial role in addressing the research goal. This hypothesis is grounded in established scientific principles and recent findings in the field.

**Scientific Rationale:**
- Current literature suggests multiple pathways that could be relevant
- Recent studies have identified key factors that influence the outcome
- Established theoretical frameworks provide a foundation for this approach

**Testable Predictions:**
1. If this hypothesis is correct, we should observe [specific measurable outcome]
2. Under controlled conditions, [specific intervention] should produce [expected result]
3. Comparative analysis should reveal [distinguishable pattern]

**Experimental Approach:**
- Design controlled experiments to test the proposed mechanism
- Use established methodologies from the literature
- Implement appropriate controls and statistical analysis

**Expected Impact:**
This hypothesis, if validated, could significantly advance our understanding and provide practical solutions for the research goal."""

        elif strategy == "scientific_debate":
            return f"""**Contrarian Perspective Hypothesis**

Research Goal: {research_goal}

**Hypothesis Statement:**
Challenging conventional approaches, we hypothesize that the mainstream understanding may be incomplete or misdirected. An alternative mechanism or approach might be more effective than currently accepted methods.

**Contrarian Rationale:**
- Current approaches may have inherent limitations that are not widely acknowledged
- Alternative perspectives from related fields suggest different mechanisms
- Historical precedents show that paradigm shifts often come from questioning established views

**Alternative Mechanism:**
Instead of the commonly accepted pathway, we propose that [alternative mechanism] is the primary driver. This challenges the assumption that [conventional assumption] is correct.

**Testing the Alternative:**
1. Design experiments that can distinguish between conventional and alternative mechanisms
2. Look for evidence that contradicts mainstream predictions
3. Explore edge cases where conventional approaches fail

**Potential Paradigm Shift:**
If validated, this hypothesis could fundamentally change how we approach the research goal and lead to breakthrough solutions."""

        elif strategy == "assumptions_identification":
            return f"""**Assumption-Challenging Hypothesis**

Research Goal: {research_goal}

**Identified Assumptions:**
Current approaches to this research goal typically assume:
1. [Assumption 1] - that certain conditions or mechanisms are primary
2. [Assumption 2] - that established methods are optimal
3. [Assumption 3] - that certain variables are independent

**Hypothesis Statement:**
We hypothesize that by questioning these fundamental assumptions, particularly [key assumption], we can uncover new approaches that are more effective than current methods.

**What If These Assumptions Are Wrong:**
- If [Assumption 1] is incorrect, then [alternative possibility] becomes viable
- Challenging [Assumption 2] opens up [new methodological approaches]
- Reconsidering [Assumption 3] reveals [hidden interactions]

**Testing Assumption Validity:**
1. Design experiments that directly test the validity of key assumptions
2. Create conditions where assumptions might not hold
3. Look for counter-examples in the literature or natural systems

**Revolutionary Potential:**
Overturning these assumptions could lead to breakthrough discoveries and fundamentally new approaches to the research goal."""

        elif strategy == "research_expansion":
            return f"""**Research Expansion Hypothesis**

Research Goal: {research_goal}

**Hypothesis Statement:**
Building upon established findings in the field, we hypothesize that extending current research in [new direction] will unlock additional potential and create novel solutions for the research goal.

**Foundation in Existing Research:**
- Current research has established [key findings]
- Successful methodologies have been developed for [related areas]
- Emerging technologies provide new opportunities for expansion

**Proposed Extension:**
We propose to expand current research by:
1. Applying established methods to [new domain/context]
2. Integrating findings from [related field] with current approaches
3. Scaling up successful small-scale results to [larger scope]

**Novel Applications:**
- [Application 1]: Using current knowledge in a new context
- [Application 2]: Combining multiple established approaches
- [Application 3]: Leveraging new technology with proven methods

**Implementation Strategy:**
1. Adapt existing methodologies for the expanded scope
2. Develop new metrics appropriate for the extended application
3. Create validation frameworks for the expanded approach

**Expected Outcomes:**
This expansion should not only address the original research goal but also open up new research directions and applications."""

        else:
            return f"""**General Scientific Hypothesis**

Research Goal: {research_goal}

**Hypothesis Statement:**
We hypothesize that [specific approach using {strategy}] will effectively address the research goal through [proposed mechanism].

**Scientific Basis:**
This hypothesis is based on scientific principles and methodological approaches relevant to the research goal.

**Testable Elements:**
1. The hypothesis makes specific, measurable predictions
2. It can be tested through controlled experiments
3. Results will either support or refute the proposed mechanism

**Methodology:**
- Apply appropriate scientific methods for testing
- Use controls and statistical analysis
- Follow established protocols for validation

**Significance:**
If validated, this hypothesis will contribute to advancing knowledge and practical solutions for the research goal."""

    def _create_strategy_prompt(self, strategy: str, research_goal: str) -> str:
        """Create a prompt based on the generation strategy."""
        base_prompt = f"Research Goal: {research_goal}\n\n"

        if strategy == "literature_exploration":
            return base_prompt + """Based on existing scientific literature and research, generate a novel, testable hypothesis that addresses the research goal. The hypothesis should:
1. Be grounded in current scientific knowledge
2. Propose a specific, testable mechanism or relationship
3. Include potential experimental approaches
4. Reference relevant scientific principles

Generate a detailed hypothesis:"""

        elif strategy == "scientific_debate":
            return base_prompt + """Taking a contrarian or alternative perspective to mainstream approaches, generate a hypothesis that challenges conventional thinking about the research goal. The hypothesis should:
1. Question existing assumptions
2. Propose an alternative mechanism or approach
3. Be scientifically sound despite being unconventional
4. Suggest how it could be tested

Generate a thought-provoking hypothesis:"""

        elif strategy == "assumptions_identification":
            return base_prompt + """Identify and challenge key assumptions underlying current approaches to the research goal, then generate a hypothesis based on questioning these assumptions. The hypothesis should:
1. Explicitly identify what assumptions are being challenged
2. Propose what might be true if these assumptions are wrong
3. Suggest experimental ways to test the new perspective
4. Be specific and actionable

Generate an assumption-challenging hypothesis:"""

        elif strategy == "research_expansion":
            return base_prompt + """Expand on existing research directions by proposing a hypothesis that extends current knowledge in a new direction. The hypothesis should:
1. Build upon established findings
2. Propose a novel extension or application
3. Identify new research opportunities
4. Be feasible with current or near-future technology

Generate an expansion-focused hypothesis:"""

        else:
            return base_prompt + f"""Generate a scientific hypothesis addressing the research goal using the {strategy} approach. The hypothesis should be specific, testable, and scientifically sound."""

    async def _perform_basic_ranking(self, hypotheses: List[UnifiedHypothesis]):
        """Perform basic ranking of hypotheses without ProtoGnosis tournament."""
        if not hypotheses:
            return

        self.logger.info("Ranking hypotheses based on basic criteria...")

        # Simple scoring based on length, specificity, and strategy diversity
        for i, hypothesis in enumerate(hypotheses):
            score = 0.0

            # Length score (moderate length preferred)
            content_length = len(hypothesis.content)
            if 200 <= content_length <= 1000:
                score += 0.3
            elif content_length > 100:
                score += 0.1

            # Strategy diversity bonus
            strategy_bonus = {
                "literature_exploration": 0.2,
                "scientific_debate": 0.3,
                "assumptions_identification": 0.25,
                "research_expansion": 0.2
            }
            score += strategy_bonus.get(hypothesis.generation_strategy, 0.1)

            # Assign score and rank
            hypothesis.evaluation_scores = {"basic_ranking": score}
            hypothesis.ranking_position = i + 1

        # Sort by score (descending)
        hypotheses.sort(key=lambda h: h.evaluation_scores.get("basic_ranking", 0), reverse=True)

        # Update rankings
        for i, hypothesis in enumerate(hypotheses):
            hypothesis.ranking_position = i + 1
            await self.session_manager.update_hypothesis(hypothesis)

    async def _verify_hypothesis_with_biomni(self, hypothesis: UnifiedHypothesis) -> None:
        """
        Verify a hypothesis with Biomni if it appears to be biomedical.

        Args:
            hypothesis: The hypothesis to potentially verify
        """
        if not self.biomni_agent:
            return

        # Check if hypothesis is biomedical
        research_goal = hypothesis.metadata.get("research_goal", "")
        is_biomedical = self.biomni_agent.is_biomedical_hypothesis(
            hypothesis.content, research_goal
        )

        if not is_biomedical:
            self.logger.debug(f"Hypothesis {hypothesis.hypothesis_id[:8]} is not biomedical, skipping Biomni verification")
            return

        try:
            self.logger.info(f"Verifying biomedical hypothesis {hypothesis.hypothesis_id[:8]} with Biomni")

            # Determine verification type based on content
            verification_type = self._determine_verification_type(hypothesis.content)

            # Perform Biomni verification
            verification_result = await self.biomni_agent.verify_hypothesis(
                hypothesis.content, research_goal, verification_type
            )

            # Set the hypothesis ID in the verification result
            verification_result.hypothesis_id = hypothesis.hypothesis_id

            # Add verification results to hypothesis
            hypothesis.set_biomni_verification(verification_result)

            self.logger.info(f"Biomni verification completed for hypothesis {hypothesis.hypothesis_id[:8]} "
                           f"(confidence: {verification_result.confidence_score:.2f})")

        except Exception as e:
            self.logger.error(f"Failed to verify hypothesis with Biomni: {e}")

    def _determine_verification_type(self, hypothesis_content: str) -> str:
        """Determine the type of Biomni verification needed based on hypothesis content."""
        content_lower = hypothesis_content.lower()

        # Check for specific domains
        if any(keyword in content_lower for keyword in ["gene", "crispr", "rna", "dna", "genome", "genetic"]):
            return "genomics"
        elif any(keyword in content_lower for keyword in ["drug", "compound", "molecule", "pharmaceutical", "admet"]):
            return "drug_discovery"
        elif any(keyword in content_lower for keyword in ["protein", "structure", "folding", "binding", "enzyme"]):
            return "protein"
        else:
            return "general"

    # ProtoGnosis integration methods removed - now handled by adapter

    async def generate_single_hypothesis(self, strategy: str = "literature_exploration") -> UnifiedHypothesis:
        """
        Generate a single hypothesis using the specified strategy.
        
        Args:
            strategy: Generation strategy to use
            
        Returns:
            Generated hypothesis
        """
        if self.protognosis_adapter:
            # Use ProtoGnosis for generation
            session_info = self.session_manager.get_session_info()
            research_goal = session_info.get('research_goal', 'No research goal set')

            hypotheses = await self.protognosis_adapter.generate_hypotheses(
                research_goal=research_goal,
                count=1,
                strategies=[strategy]
            )

            if hypotheses:
                return hypotheses[0]
        
        # Fallback: create a basic hypothesis
        # This would be replaced with actual generation logic
        hypothesis = UnifiedHypothesis(
            title="Generated Hypothesis",
            description="This is a placeholder hypothesis generated by Jnana.",
            generation_strategy=strategy
        )
        
        return hypothesis
    
    async def refine_hypothesis(self, hypothesis: UnifiedHypothesis, 
                              feedback: str) -> UnifiedHypothesis:
        """
        Refine a hypothesis based on user feedback.
        
        Args:
            hypothesis: Hypothesis to refine
            feedback: User feedback
            
        Returns:
            Refined hypothesis
        """
        # Add feedback to hypothesis
        hypothesis.add_feedback(feedback)
        
        # Use ProtoGnosis evolution agent if available
        if self.protognosis_adapter:
            evolved_hypothesis = await self.protognosis_adapter.evolve_hypothesis(
                hypothesis, feedback
            )
            hypothesis = evolved_hypothesis
        
        # Update in session
        await self.session_manager.update_hypothesis(hypothesis)
        
        return hypothesis


    def prep_protein_sequence(self,hypo):
        self.logger.info(f"Hypothesis passed into jnana_system: {hypo}")
        assert isinstance(hypo, UnifiedHypothesis), "Must select a hypothesis first~"
        self.protognosis_adapter.analyze_protein(hypo)

    def gen_protein_report(self,hypo):
        self.logger.info(f"Hypothesis passed into jnana_system for protein report: {hypo}")
        assert isinstance(hypo, UnifiedHypothesis), "Must select a hypothesis first~"
        self.protognosis_adapter.make_protein_report(hypo)

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        session_info = self.session_manager.get_session_info()

        return {
            "running": self.running,
            "mode": self.current_mode,
            "protognosis_available": PROTOGNOSIS_AVAILABLE,
            "ui_enabled": self.enable_ui,
            "session": session_info,
            "storage_stats": self.storage.get_statistics(),
            "event_stats": self.event_manager.get_statistics(),
            "biomni_available": self.biomni_agent.is_initialized if self.biomni_agent else False,
            "biomni_enabled": self.biomni_agent.config.enabled if self.biomni_agent else False
        }

    def get_status(self) -> Dict[str, Any]:
        """Alias for get_system_status() for convenience."""
        return self.get_system_status()

    async def generate_single_hypothesis(self, strategy: str = "literature_exploration") -> Optional[UnifiedHypothesis]:
        """
        Generate a single hypothesis using the specified strategy.

        Args:
            strategy: Generation strategy to use

        Returns:
            Generated hypothesis or None if generation failed
        """
        try:
            if not self.protognosis_adapter:
                self.logger.warning("ProtoGnosis not available, cannot generate hypothesis")
                return None

            self.logger.info(f"Generating single hypothesis with strategy: {strategy}")

            # Get research goal from session
            session_info = self.session_manager.get_session_info()
            research_goal = session_info.get("research_goal", "") if session_info else ""

            if not research_goal:
                self.logger.warning("No research goal set, cannot generate hypothesis")
                return None

            # Use ProtoGnosis to generate a single hypothesis
            hypotheses = await self.protognosis_adapter.generate_hypotheses(
                research_goal=research_goal,
                count=1,
                strategies=[strategy]
            )

            if hypotheses:
                hypothesis = hypotheses[0]
                self.logger.info(f"Successfully generated hypothesis: {hypothesis.title}")
                return hypothesis
            else:
                self.logger.warning("No hypothesis generated")
                return None

        except Exception as e:
            self.logger.error(f"Error generating single hypothesis: {e}")
            return None

    async def refine_hypothesis_with_feedback(self, hypothesis: UnifiedHypothesis, feedback: str) -> Optional[UnifiedHypothesis]:
        """
        Refine a hypothesis using AI agents based on user feedback.

        Args:
            hypothesis: Hypothesis to refine
            feedback: User feedback for refinement

        Returns:
            Refined hypothesis or None if refinement failed
        """
        try:
            if not self.protognosis_adapter:
                self.logger.warning("ProtoGnosis not available, cannot refine hypothesis")
                return None

            self.logger.info(f"Refining hypothesis {hypothesis.hypothesis_id} with feedback")

            # Use ProtoGnosis to evolve/refine the hypothesis
            refined_hypothesis = await self.protognosis_adapter.evolve_hypothesis(
                hypothesis, feedback
            )

            if refined_hypothesis:
                self.logger.info(f"Successfully refined hypothesis: {refined_hypothesis.title}")
                return refined_hypothesis
            else:
                self.logger.warning("Hypothesis refinement failed")
                return None

        except Exception as e:
            self.logger.error(f"Error refining hypothesis: {e}")
            return None
