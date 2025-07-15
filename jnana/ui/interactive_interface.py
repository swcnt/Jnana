"""
Interactive interface for Jnana system.

This module provides the interactive user interface that integrates
Wisteria's curses-based interface with Jnana's unified system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from ..core.event_manager import EventManager, EventType, EventSubscriber
from ..core.session_manager import SessionManager
from ..data.unified_hypothesis import UnifiedHypothesis

# Try to import Wisteria components
try:
    import sys
    import os
    # Add Wisteria to path
    wisteria_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Wisteria')
    if os.path.exists(wisteria_path):
        sys.path.insert(0, wisteria_path)
    
    # Import Wisteria's CursesInterface if available
    try:
        from curses_wisteria_v5 import CursesInterface
        WISTERIA_UI_AVAILABLE = True
    except ImportError:
        WISTERIA_UI_AVAILABLE = False
        CursesInterface = None
        
except ImportError:
    WISTERIA_UI_AVAILABLE = False
    CursesInterface = None


class InteractiveInterface(EventSubscriber):
    """
    Interactive interface that provides real-time user interaction
    for hypothesis generation and refinement.
    """
    
    def __init__(self, event_manager: EventManager, session_manager: SessionManager, jnana_system=None):
        """
        Initialize the interactive interface.

        Args:
            event_manager: Event manager for communication
            session_manager: Session manager for data persistence
            jnana_system: Reference to the main Jnana system for AI operations
        """
        super().__init__(event_manager, "interactive_interface")

        self.session_manager = session_manager
        self.jnana_system = jnana_system  # Add reference to main system
        self.running = False

        # UI state
        self.current_hypothesis_idx = 0
        self.show_hallmarks = True
        self.show_references = True

        # Wisteria integration
        self.wisteria_interface: Optional[CursesInterface] = None

        # Subscribe to relevant events
        self.subscribe_to_event(EventType.HYPOTHESIS_GENERATED, self._handle_hypothesis_generated)
        self.subscribe_to_event(EventType.HYPOTHESIS_UPDATED, self._handle_hypothesis_updated)
        self.subscribe_to_event(EventType.AGENT_PROGRESS, self._handle_agent_progress)
    
    async def start_interactive_session(self, model_config: Dict[str, Any]):
        """
        Start an interactive session for hypothesis generation and refinement.
        
        Args:
            model_config: Model configuration for generation
        """
        if WISTERIA_UI_AVAILABLE:
            await self._start_wisteria_session(model_config)
        else:
            await self._start_basic_session(model_config)
    
    async def start_refinement_session(self):
        """Start an interactive session focused on hypothesis refinement."""
        self.logger.info("Starting refinement session")
        
        hypotheses = self.session_manager.get_all_hypotheses()
        if not hypotheses:
            print("No hypotheses available for refinement.")
            return
        
        # Simple text-based refinement interface
        print(f"\nFound {len(hypotheses)} hypotheses for refinement:")
        
        for i, hypothesis in enumerate(hypotheses):
            print(f"{i+1}. {hypothesis.title}")
        
        while True:
            try:
                choice = input("\nSelect hypothesis to refine (number) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    break
                
                idx = int(choice) - 1
                if 0 <= idx < len(hypotheses):
                    await self._refine_hypothesis_interactive(hypotheses[idx])
                else:
                    print("Invalid selection.")
                    
            except (ValueError, KeyboardInterrupt):
                break
        
        print("Refinement session completed.")
    
    async def _start_wisteria_session(self, model_config: Dict[str, Any]):
        """Start session using Wisteria's curses interface."""
        self.logger.info("Starting Wisteria-based interactive session")
        
        # This would integrate with Wisteria's curses interface
        # For now, fall back to basic session
        await self._start_basic_session(model_config)
    
    async def _start_basic_session(self, model_config: Dict[str, Any]):
        """Start a basic text-based interactive session."""
        self.logger.info("Starting basic interactive session")
        self.running = True
        
        print("\n=== Jnana Interactive Session ===")
        print("Commands: 'generate', 'refine', 'list', 'select <n>', 'save', 'quit'")
        
        while self.running:
            try:
                command = input("\nJnana> ").strip().lower()
                
                if command == 'quit' or command == 'q':
                    break
                elif command == 'generate' or command == 'g':
                    await self._generate_hypothesis_interactive()
                elif command == 'refine' or command == 'r':
                    await self._refine_current_hypothesis()
                elif command == 'list' or command == 'l':
                    self._list_hypotheses()
                elif command.startswith('select '):
                    try:
                        idx = int(command.split()[1]) - 1
                        self._select_hypothesis(idx)
                    except (ValueError, IndexError):
                        print("Invalid selection. Use 'select <number>'")
                elif command == 'save' or command == 's':
                    await self._save_session()
                elif command == 'help' or command == 'h':
                    self._show_help()
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        self.running = False
        print("Interactive session ended.")
    
    async def _generate_hypothesis_interactive(self):
        """Generate a new hypothesis interactively using the Jnana system."""
        print("\nGenerating new hypothesis...")

        # Check if Jnana system is available
        if not self.jnana_system:
            print("❌ Error: Jnana system not available for hypothesis generation.")
            print("   Using placeholder generation instead...")
            await self._generate_placeholder_hypothesis()
            return

        # Get research goal from session
        session_info = self.session_manager.get_session_info()
        if not session_info:
            print("No active session. Please set a research goal first.")
            return

        research_goal = session_info.get("research_goal", "")
        print(f"Research goal: {research_goal}")

        # Ask user for generation strategy
        print("\nAvailable generation strategies:")
        strategies = ["literature_exploration", "scientific_debate", "assumptions_identification", "research_expansion"]
        for i, strategy in enumerate(strategies, 1):
            print(f"  {i}. {strategy.replace('_', ' ').title()}")

        try:
            choice = input("\nSelect strategy (1-4) or press Enter for default: ").strip()
            if choice and choice.isdigit() and 1 <= int(choice) <= 4:
                strategy = strategies[int(choice) - 1]
            else:
                strategy = "literature_exploration"  # Default

            print(f"Using strategy: {strategy.replace('_', ' ').title()}")
            print("🔄 Generating hypothesis with AI agents...")

            # Use the actual Jnana system to generate hypothesis
            hypothesis = await self.jnana_system.generate_single_hypothesis(strategy)

            if hypothesis:
                print(f"✅ Generated: {hypothesis.title}")
                print(f"📝 Description: {hypothesis.description[:200]}...")

                await self.session_manager.add_hypothesis(hypothesis)

                # Publish event
                await self.publish_event(
                    EventType.HYPOTHESIS_GENERATED,
                    {
                        "hypothesis_id": hypothesis.hypothesis_id,
                        "title": hypothesis.title,
                        "strategy": strategy
                    }
                )
            else:
                print("❌ Failed to generate hypothesis. Please try again.")

        except KeyboardInterrupt:
            print("\n⚠️  Generation cancelled by user.")
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            print("   Falling back to placeholder generation...")
            await self._generate_placeholder_hypothesis()

    async def _generate_placeholder_hypothesis(self):
        """Generate a placeholder hypothesis when AI generation is not available."""
        # Get research goal from session
        session_info = self.session_manager.get_session_info()
        research_goal = session_info.get("research_goal", "Unknown research goal") if session_info else "Unknown research goal"

        # Create a placeholder hypothesis
        hypothesis = UnifiedHypothesis(
            title=f"Generated Hypothesis {len(self.session_manager.get_all_hypotheses()) + 1}",
            description=f"This hypothesis addresses the research goal: {research_goal}",
            generation_strategy="interactive_placeholder"
        )

        # Add to session
        await self.session_manager.add_hypothesis(hypothesis)

        print(f"📝 Placeholder Generated: {hypothesis.title}")
        print(f"📄 Description: {hypothesis.description}")

        # Publish event
        await self.publish_event(
            EventType.HYPOTHESIS_GENERATED,
            {
                "hypothesis_id": hypothesis.hypothesis_id,
                "title": hypothesis.title,
                "strategy": "placeholder"
            }
        )
    
    async def _refine_current_hypothesis(self):
        """Refine the currently selected hypothesis."""
        current_hypothesis = self.session_manager.get_active_hypothesis()
        
        if not current_hypothesis:
            hypotheses = self.session_manager.get_all_hypotheses()
            if hypotheses:
                current_hypothesis = hypotheses[0]
                self.session_manager.set_active_hypothesis(current_hypothesis.hypothesis_id)
            else:
                print("No hypotheses available. Generate one first.")
                return
        
        await self._refine_hypothesis_interactive(current_hypothesis)
    
    async def _refine_hypothesis_interactive(self, hypothesis: UnifiedHypothesis):
        """Interactively refine a specific hypothesis using AI."""
        print(f"\n🔧 Refining: {hypothesis.title}")
        print(f"📄 Current description: {hypothesis.description[:300]}...")

        feedback = input("\n💬 Enter your feedback for improvement: ").strip()

        if feedback:
            print("🔄 Processing refinement with AI agents...")

            # Add feedback to hypothesis
            hypothesis.add_feedback(feedback)

            try:
                if self.jnana_system:
                    # Use the actual Jnana system for AI-powered refinement
                    refined_hypothesis = await self.jnana_system.refine_hypothesis_with_feedback(
                        hypothesis, feedback
                    )

                    if refined_hypothesis:
                        print("✅ Hypothesis refined successfully with AI!")
                        print(f"📝 New description: {refined_hypothesis.description[:300]}...")

                        # Publish event
                        await self.publish_event(
                            EventType.HYPOTHESIS_UPDATED,
                            {
                                "hypothesis_id": refined_hypothesis.hypothesis_id,
                                "feedback": feedback,
                                "version": refined_hypothesis.version_string,
                                "refinement_type": "ai_powered"
                            }
                        )
                    else:
                        print("⚠️  AI refinement failed, using simple refinement...")
                        await self._simple_refinement(hypothesis, feedback)
                else:
                    print("⚠️  Jnana system not available, using simple refinement...")
                    await self._simple_refinement(hypothesis, feedback)

            except Exception as e:
                print(f"❌ Error during AI refinement: {e}")
                print("   Falling back to simple refinement...")
                await self._simple_refinement(hypothesis, feedback)
        else:
            print("⚠️  No feedback provided.")

    async def _simple_refinement(self, hypothesis: UnifiedHypothesis, feedback: str):
        """Perform simple text-based refinement when AI is not available."""
        # Simple refinement - append feedback to description
        hypothesis.description += f"\n\nRefinement based on feedback: {feedback}"
        hypothesis.improvements_made = f"Incorporated user feedback: {feedback[:100]}..."

        # Update in session
        await self.session_manager.update_hypothesis(hypothesis)

        print("📝 Hypothesis refined with simple text processing!")

        # Publish event
        await self.publish_event(
            EventType.HYPOTHESIS_UPDATED,
            {
                "hypothesis_id": hypothesis.hypothesis_id,
                "feedback": feedback,
                "version": hypothesis.version_string,
                "refinement_type": "simple"
            }
        )
    
    def _list_hypotheses(self):
        """List all hypotheses in the current session."""
        hypotheses = self.session_manager.get_all_hypotheses()
        
        if not hypotheses:
            print("No hypotheses in current session.")
            return
        
        print(f"\nHypotheses in current session ({len(hypotheses)}):")
        
        for i, hypothesis in enumerate(hypotheses):
            marker = "* " if hypothesis == self.session_manager.get_active_hypothesis() else "  "
            print(f"{marker}{i+1}. {hypothesis.title} (v{hypothesis.version_string})")
    
    def _select_hypothesis(self, index: int):
        """Select a hypothesis by index."""
        hypotheses = self.session_manager.get_all_hypotheses()
        
        if 0 <= index < len(hypotheses):
            selected = hypotheses[index]
            self.session_manager.set_active_hypothesis(selected.hypothesis_id)
            print(f"Selected: {selected.title}")
        else:
            print(f"Invalid index. Available: 1-{len(hypotheses)}")
    
    async def _save_session(self):
        """Save the current session."""
        try:
            output_path = await self.session_manager.save_session()
            print(f"Session saved to: {output_path}")
        except Exception as e:
            print(f"Failed to save session: {e}")
    
    def _show_help(self):
        """Show help information."""
        print("\nAvailable commands:")
        print("  generate (g)    - Generate a new hypothesis")
        print("  refine (r)      - Refine the current hypothesis")
        print("  list (l)        - List all hypotheses")
        print("  select <n>      - Select hypothesis by number")
        print("  save (s)        - Save current session")
        print("  help (h)        - Show this help")
        print("  quit (q)        - Exit the session")
    
    async def _handle_hypothesis_generated(self, event):
        """Handle hypothesis generation events."""
        self.logger.debug(f"Hypothesis generated: {event.data.get('title', 'Unknown')}")
    
    async def _handle_hypothesis_updated(self, event):
        """Handle hypothesis update events."""
        self.logger.debug(f"Hypothesis updated: {event.data.get('hypothesis_id', 'Unknown')}")
    
    async def _handle_agent_progress(self, event):
        """Handle agent progress events."""
        agent_type = event.data.get("agent_type", "unknown")
        step = event.data.get("step", "unknown")
        progress = event.data.get("progress", 0)
        
        # Show progress in UI (basic implementation)
        if self.running:
            print(f"\r{agent_type}: {step} ({progress*100:.0f}%)", end="", flush=True)
    
    def display_hypothesis(self, hypothesis: UnifiedHypothesis):
        """Display a hypothesis in a formatted way."""
        print(f"\n{'='*60}")
        print(f"Title: {hypothesis.title}")
        print(f"Version: {hypothesis.version_string}")
        print(f"Type: {hypothesis.hypothesis_type}")
        print(f"{'='*60}")
        
        print(f"\nDescription:")
        print(hypothesis.description)
        
        if hypothesis.experimental_validation:
            print(f"\nExperimental Validation:")
            print(hypothesis.experimental_validation)
        
        if hypothesis.notes:
            print(f"\nNotes:")
            print(hypothesis.notes)
        
        if hypothesis.feedback_history:
            print(f"\nFeedback History ({len(hypothesis.feedback_history)} entries):")
            for i, feedback in enumerate(hypothesis.feedback_history[-3:], 1):  # Show last 3
                print(f"  {i}. {feedback.feedback[:100]}...")
        
        print(f"{'='*60}")
    
    async def show_progress(self, message: str, progress: float = None):
        """Show progress message to user."""
        if progress is not None:
            print(f"\r{message} ({progress*100:.0f}%)", end="", flush=True)
        else:
            print(f"\r{message}", end="", flush=True)
    
    async def request_user_input(self, prompt: str, input_type: str = "text") -> Optional[str]:
        """Request input from the user."""
        try:
            if input_type == "confirmation":
                response = input(f"{prompt} (y/n): ").strip().lower()
                return "yes" if response in ['y', 'yes'] else "no"
            else:
                return input(f"{prompt}: ").strip()
        except KeyboardInterrupt:
            return None
