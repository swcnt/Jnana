"""
Event management system for Jnana.

This module provides an event-driven communication system between
the UI components and the multi-agent processing system.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
import uuid


class EventType(Enum):
    """Types of events in the Jnana system."""
    
    # Hypothesis events
    HYPOTHESIS_GENERATED = "hypothesis_generated"
    HYPOTHESIS_UPDATED = "hypothesis_updated"
    HYPOTHESIS_DELETED = "hypothesis_deleted"
    HYPOTHESIS_SELECTED = "hypothesis_selected"
    
    # Agent events
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_ERROR = "agent_error"
    AGENT_PROGRESS = "agent_progress"
    
    # User interaction events
    USER_FEEDBACK = "user_feedback"
    USER_ACTION = "user_action"
    UI_UPDATE = "ui_update"
    
    # System events
    SESSION_STARTED = "session_started"
    SESSION_SAVED = "session_saved"
    SESSION_LOADED = "session_loaded"
    SYSTEM_ERROR = "system_error"
    
    # Tournament events
    TOURNAMENT_STARTED = "tournament_started"
    TOURNAMENT_MATCH = "tournament_match"
    TOURNAMENT_COMPLETED = "tournament_completed"


@dataclass
class Event:
    """Represents an event in the system."""
    
    event_id: str
    event_type: EventType
    timestamp: str
    source: str  # Component that generated the event
    data: Dict[str, Any]
    priority: int = 0  # Higher numbers = higher priority
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class EventManager:
    """
    Manages event-driven communication in the Jnana system.
    
    Provides pub/sub functionality for loose coupling between components.
    """
    
    def __init__(self):
        """Initialize the event manager."""
        self.logger = logging.getLogger(__name__)
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._event_history: List[Event] = []
        self._max_history = 1000  # Keep last 1000 events
    
    async def start(self):
        """Start the event processing system."""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        self.logger.info("Event manager started")
    
    async def stop(self):
        """Stop the event processing system."""
        if not self._running:
            return
        
        self._running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Event manager stopped")
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                self.logger.debug(f"Unsubscribed from {event_type.value}")
            except ValueError:
                pass
    
    async def publish(self, event_type: EventType, source: str, 
                     data: Dict[str, Any], priority: int = 0):
        """
        Publish an event to the system.
        
        Args:
            event_type: Type of event
            source: Component publishing the event
            data: Event data
            priority: Event priority (higher = more important)
        """
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            source=source,
            data=data,
            priority=priority
        )
        
        await self._event_queue.put(event)
        self.logger.debug(f"Published event: {event_type.value} from {source}")
    
    async def _process_events(self):
        """Process events from the queue."""
        while self._running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(
                    self._event_queue.get(), 
                    timeout=1.0
                )
                
                # Add to history
                self._event_history.append(event)
                if len(self._event_history) > self._max_history:
                    self._event_history.pop(0)
                
                # Notify subscribers
                await self._notify_subscribers(event)
                
            except asyncio.TimeoutError:
                # No events to process, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    async def _notify_subscribers(self, event: Event):
        """Notify all subscribers of an event."""
        subscribers = self._subscribers.get(event.event_type, [])
        
        for callback in subscribers:
            try:
                # Handle both sync and async callbacks
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                self.logger.error(f"Error in event callback: {e}")
    
    def get_event_history(self, event_type: Optional[EventType] = None, 
                         limit: int = 100) -> List[Event]:
        """
        Get recent event history.
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Return most recent events first
        return list(reversed(events[-limit:]))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event system statistics."""
        event_counts = {}
        for event in self._event_history:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_events": len(self._event_history),
            "event_counts": event_counts,
            "subscribers": {
                event_type.value: len(callbacks) 
                for event_type, callbacks in self._subscribers.items()
            },
            "queue_size": self._event_queue.qsize(),
            "running": self._running
        }


class EventSubscriber:
    """Base class for components that subscribe to events."""
    
    def __init__(self, event_manager: EventManager, component_name: str):
        """
        Initialize event subscriber.
        
        Args:
            event_manager: Event manager instance
            component_name: Name of the subscribing component
        """
        self.event_manager = event_manager
        self.component_name = component_name
        self.logger = logging.getLogger(f"{__name__}.{component_name}")
    
    async def publish_event(self, event_type: EventType, data: Dict[str, Any], 
                           priority: int = 0):
        """
        Publish an event from this component.
        
        Args:
            event_type: Type of event
            data: Event data
            priority: Event priority
        """
        await self.event_manager.publish(
            event_type=event_type,
            source=self.component_name,
            data=data,
            priority=priority
        )
    
    def subscribe_to_event(self, event_type: EventType, 
                          callback: Callable[[Event], None]):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Callback function
        """
        self.event_manager.subscribe(event_type, callback)


class EventAggregator:
    """Aggregates and filters events for specific use cases."""
    
    def __init__(self, event_manager: EventManager):
        """Initialize event aggregator."""
        self.event_manager = event_manager
        self._filters: List[Callable[[Event], bool]] = []
    
    def add_filter(self, filter_func: Callable[[Event], bool]):
        """Add a filter function for events."""
        self._filters.append(filter_func)
    
    def get_filtered_events(self, limit: int = 100) -> List[Event]:
        """Get events that pass all filters."""
        events = self.event_manager.get_event_history(limit=limit)
        
        filtered_events = []
        for event in events:
            if all(f(event) for f in self._filters):
                filtered_events.append(event)
        
        return filtered_events
    
    def create_hypothesis_filter(self, hypothesis_id: str) -> Callable[[Event], bool]:
        """Create a filter for events related to a specific hypothesis."""
        def filter_func(event: Event) -> bool:
            return event.data.get("hypothesis_id") == hypothesis_id
        return filter_func
    
    def create_agent_filter(self, agent_type: str) -> Callable[[Event], bool]:
        """Create a filter for events from a specific agent type."""
        def filter_func(event: Event) -> bool:
            return event.data.get("agent_type") == agent_type
        return filter_func
    
    def create_time_filter(self, start_time: str, end_time: str) -> Callable[[Event], bool]:
        """Create a filter for events within a time range."""
        def filter_func(event: Event) -> bool:
            return start_time <= event.timestamp <= end_time
        return filter_func
