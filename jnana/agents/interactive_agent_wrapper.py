"""
Interactive Agent Wrapper for Jnana system.

This module provides wrappers for ProtoGnosis agents that enable
interactive capabilities and integration with the Jnana UI system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from ..core.event_manager import EventManager, EventType, EventSubscriber
from ..data.unified_hypothesis import UnifiedHypothesis

# Import ProtoGnosis components if available
try:
    from agent_core import Agent, Task
    PROTOGNOSIS_AVAILABLE = True
except ImportError:
    PROTOGNOSIS_AVAILABLE = False
    # Create placeholder classes
    class Agent:
        def __init__(self, *args, **kwargs):
            pass
        
        async def process_task(self, task):
            pass
    
    class Task:
        def __init__(self, *args, **kwargs):
            pass


class InteractiveAgentWrapper(EventSubscriber):
    """
    Wraps ProtoGnosis agents to provide interactive capabilities.
    
    This wrapper allows agents to:
    - Pause for user input during processing
    - Provide real-time progress updates
    - Accept user feedback and incorporate it into processing
    - Operate in both automated and interactive modes
    """
    
    def __init__(self, agent: Agent, event_manager: EventManager, 
                 agent_type: str, agent_id: str = None):
        """
        Initialize the interactive agent wrapper.
        
        Args:
            agent: The ProtoGnosis agent to wrap
            event_manager: Event manager for communication
            agent_type: Type of agent (generation, reflection, etc.)
            agent_id: Unique identifier for this agent instance
        """
        super().__init__(event_manager, f"agent_{agent_type}")
        
        self.agent = agent
        self.agent_type = agent_type
        self.agent_id = agent_id or f"{agent_type}_{id(self)}"
        
        # Interactive state
        self.interactive_mode = False
        self.paused = False
        self.user_feedback_queue: asyncio.Queue = asyncio.Queue()
        self.progress_callback: Optional[Callable] = None
        
        # Processing state
        self.current_task: Optional[Task] = None
        self.processing_state: Dict[str, Any] = {}
        
        # Subscribe to relevant events
        self.subscribe_to_event(EventType.USER_FEEDBACK, self._handle_user_feedback)
        self.subscribe_to_event(EventType.USER_ACTION, self._handle_user_action)
    
    def set_interactive_mode(self, enabled: bool):
        """Enable or disable interactive mode."""
        self.interactive_mode = enabled
        self.logger.info(f"Interactive mode {'enabled' if enabled else 'disabled'}")
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    async def process_task_interactive(self, task: Task, 
                                     allow_user_input: bool = True) -> Any:
        """
        Process a task with interactive capabilities.
        
        Args:
            task: Task to process
            allow_user_input: Whether to allow user interaction
            
        Returns:
            Task result
        """
        self.current_task = task
        self.paused = False
        
        # Publish agent started event
        await self.publish_event(
            EventType.AGENT_STARTED,
            {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "task_id": getattr(task, 'task_id', 'unknown'),
                "interactive_mode": self.interactive_mode and allow_user_input
            }
        )
        
        try:
            if self.interactive_mode and allow_user_input:
                result = await self._process_with_interaction(task)
            else:
                result = await self._process_without_interaction(task)
            
            # Publish completion event
            await self.publish_event(
                EventType.AGENT_COMPLETED,
                {
                    "agent_id": self.agent_id,
                    "agent_type": self.agent_type,
                    "task_id": getattr(task, 'task_id', 'unknown'),
                    "result": result
                }
            )
            
            return result
            
        except Exception as e:
            # Publish error event
            await self.publish_event(
                EventType.AGENT_ERROR,
                {
                    "agent_id": self.agent_id,
                    "agent_type": self.agent_type,
                    "task_id": getattr(task, 'task_id', 'unknown'),
                    "error": str(e)
                }
            )
            raise
        
        finally:
            self.current_task = None
            self.processing_state.clear()
    
    async def _process_with_interaction(self, task: Task) -> Any:
        """Process task with user interaction enabled."""
        # Start processing in background
        processing_task = asyncio.create_task(self._monitored_processing(task))
        
        # Wait for completion or user interaction
        while not processing_task.done():
            try:
                # Check for user feedback with timeout
                feedback = await asyncio.wait_for(
                    self.user_feedback_queue.get(),
                    timeout=1.0
                )
                
                # Handle feedback
                await self._incorporate_feedback(feedback)
                
            except asyncio.TimeoutError:
                # No feedback, continue processing
                continue
        
        return await processing_task
    
    async def _process_without_interaction(self, task: Task) -> Any:
        """Process task without user interaction."""
        return await self.agent.process_task(task)
    
    async def _monitored_processing(self, task: Task) -> Any:
        """Process task with monitoring and progress updates."""
        # This is where we would integrate with the actual agent processing
        # For now, we'll simulate the process
        
        steps = ["initializing", "analyzing", "generating", "evaluating", "finalizing"]
        
        for i, step in enumerate(steps):
            # Update progress
            progress = (i + 1) / len(steps)
            await self._update_progress(step, progress)
            
            # Check if paused
            while self.paused:
                await asyncio.sleep(0.1)
            
            # Simulate processing time
            await asyncio.sleep(0.5)
        
        # Call the actual agent processing
        return await self.agent.process_task(task)
    
    async def _update_progress(self, step: str, progress: float):
        """Update processing progress."""
        self.processing_state["current_step"] = step
        self.processing_state["progress"] = progress
        
        # Call progress callback if set
        if self.progress_callback:
            self.progress_callback(step, progress)
        
        # Publish progress event
        await self.publish_event(
            EventType.AGENT_PROGRESS,
            {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "step": step,
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def _handle_user_feedback(self, event):
        """Handle user feedback events."""
        # Check if feedback is for this agent
        if event.data.get("agent_id") == self.agent_id:
            await self.user_feedback_queue.put(event.data)
    
    async def _handle_user_action(self, event):
        """Handle user action events."""
        action = event.data.get("action")
        target_agent = event.data.get("agent_id")
        
        if target_agent == self.agent_id:
            if action == "pause":
                self.paused = True
                self.logger.info("Agent paused by user")
            elif action == "resume":
                self.paused = False
                self.logger.info("Agent resumed by user")
            elif action == "stop":
                # Cancel current processing
                if self.current_task:
                    self.logger.info("Agent stopped by user")
                    # Implementation would cancel the current task
    
    async def _incorporate_feedback(self, feedback_data: Dict[str, Any]):
        """Incorporate user feedback into processing."""
        feedback_text = feedback_data.get("feedback", "")
        feedback_type = feedback_data.get("type", "general")
        
        self.logger.info(f"Incorporating user feedback: {feedback_text[:100]}...")
        
        # Store feedback in processing state
        if "user_feedback" not in self.processing_state:
            self.processing_state["user_feedback"] = []
        
        self.processing_state["user_feedback"].append({
            "feedback": feedback_text,
            "type": feedback_type,
            "timestamp": datetime.now().isoformat()
        })
        
        # Here we would modify the agent's processing based on feedback
        # This is agent-type specific and would need to be implemented
        # for each agent type
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "interactive_mode": self.interactive_mode,
            "paused": self.paused,
            "processing": self.current_task is not None,
            "processing_state": self.processing_state.copy()
        }
    
    async def request_user_input(self, prompt: str, input_type: str = "text",
                               timeout: Optional[float] = None) -> Optional[str]:
        """
        Request input from the user during processing.
        
        Args:
            prompt: Prompt to show to the user
            input_type: Type of input expected ("text", "choice", "confirmation")
            timeout: Optional timeout in seconds
            
        Returns:
            User input or None if timeout
        """
        # Publish request for user input
        await self.publish_event(
            EventType.UI_UPDATE,
            {
                "type": "user_input_request",
                "agent_id": self.agent_id,
                "prompt": prompt,
                "input_type": input_type
            }
        )
        
        try:
            # Wait for user response
            if timeout:
                feedback = await asyncio.wait_for(
                    self.user_feedback_queue.get(),
                    timeout=timeout
                )
            else:
                feedback = await self.user_feedback_queue.get()
            
            return feedback.get("response")
            
        except asyncio.TimeoutError:
            self.logger.warning(f"User input request timed out: {prompt}")
            return None
    
    async def pause_for_review(self, content: Any, review_type: str = "hypothesis") -> bool:
        """
        Pause processing for user review of content.
        
        Args:
            content: Content to review
            review_type: Type of content being reviewed
            
        Returns:
            True if user approves, False otherwise
        """
        # Publish review request
        await self.publish_event(
            EventType.UI_UPDATE,
            {
                "type": "review_request",
                "agent_id": self.agent_id,
                "content": content,
                "review_type": review_type
            }
        )
        
        # Wait for user decision
        feedback = await self.user_feedback_queue.get()
        decision = feedback.get("decision", "approve")
        
        return decision == "approve"
