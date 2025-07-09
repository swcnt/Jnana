"""
Monitoring interface for Jnana system.

This module provides monitoring capabilities for tracking system performance,
agent activities, and research progress.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.event_manager import EventManager, EventType, EventSubscriber


class MonitoringInterface(EventSubscriber):
    """
    Monitoring interface for tracking system performance and activities.
    
    This interface provides real-time monitoring of:
    - Agent activities and performance
    - Hypothesis generation and refinement
    - System resource usage
    - Research session progress
    """
    
    def __init__(self, event_manager: EventManager):
        """
        Initialize the monitoring interface.
        
        Args:
            event_manager: Event manager for receiving system events
        """
        super().__init__(event_manager, "monitoring_interface")
        
        # Monitoring state
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.hypothesis_metrics: Dict[str, Any] = {
            "total_generated": 0,
            "total_refined": 0,
            "average_refinement_cycles": 0,
            "generation_rate": 0.0  # hypotheses per minute
        }
        self.system_metrics: Dict[str, Any] = {
            "uptime": 0,
            "memory_usage": 0,
            "cpu_usage": 0,
            "active_sessions": 0
        }
        
        # Subscribe to relevant events
        self.subscribe_to_event(EventType.AGENT_STARTED, self._handle_agent_started)
        self.subscribe_to_event(EventType.AGENT_COMPLETED, self._handle_agent_completed)
        self.subscribe_to_event(EventType.AGENT_PROGRESS, self._handle_agent_progress)
        self.subscribe_to_event(EventType.HYPOTHESIS_GENERATED, self._handle_hypothesis_generated)
        self.subscribe_to_event(EventType.HYPOTHESIS_UPDATED, self._handle_hypothesis_updated)
        self.subscribe_to_event(EventType.SESSION_STARTED, self._handle_session_started)
    
    async def _handle_agent_started(self, event):
        """Handle agent started events."""
        agent_id = event.data.get("agent_id")
        agent_type = event.data.get("agent_type")
        
        self.active_agents[agent_id] = {
            "agent_type": agent_type,
            "started_at": event.timestamp,
            "status": "running",
            "progress": 0.0,
            "current_step": "initializing"
        }
        
        self.logger.info(f"Agent started: {agent_type} ({agent_id})")
    
    async def _handle_agent_completed(self, event):
        """Handle agent completed events."""
        agent_id = event.data.get("agent_id")
        
        if agent_id in self.active_agents:
            self.active_agents[agent_id]["status"] = "completed"
            self.active_agents[agent_id]["completed_at"] = event.timestamp
            self.active_agents[agent_id]["progress"] = 1.0
            
            self.logger.info(f"Agent completed: {agent_id}")
    
    async def _handle_agent_progress(self, event):
        """Handle agent progress events."""
        agent_id = event.data.get("agent_id")
        progress = event.data.get("progress", 0.0)
        step = event.data.get("step", "unknown")
        
        if agent_id in self.active_agents:
            self.active_agents[agent_id]["progress"] = progress
            self.active_agents[agent_id]["current_step"] = step
    
    async def _handle_hypothesis_generated(self, event):
        """Handle hypothesis generation events."""
        self.hypothesis_metrics["total_generated"] += 1
        
        # Calculate generation rate (simplified)
        # In a real implementation, this would use a sliding window
        self.hypothesis_metrics["generation_rate"] = self.hypothesis_metrics["total_generated"] / max(1, self.get_uptime_minutes())
    
    async def _handle_hypothesis_updated(self, event):
        """Handle hypothesis update events."""
        self.hypothesis_metrics["total_refined"] += 1
    
    async def _handle_session_started(self, event):
        """Handle session started events."""
        self.system_metrics["active_sessions"] += 1
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents."""
        return {
            "active_count": len([a for a in self.active_agents.values() if a["status"] == "running"]),
            "completed_count": len([a for a in self.active_agents.values() if a["status"] == "completed"]),
            "agents": self.active_agents.copy()
        }
    
    def get_hypothesis_metrics(self) -> Dict[str, Any]:
        """Get hypothesis generation and refinement metrics."""
        return self.hypothesis_metrics.copy()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        # Update uptime
        self.system_metrics["uptime"] = self.get_uptime_minutes()
        
        # In a real implementation, these would be actual system metrics
        return self.system_metrics.copy()
    
    def get_uptime_minutes(self) -> float:
        """Get system uptime in minutes."""
        # Simplified implementation - would track actual start time
        return 1.0  # Placeholder
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": self.get_agent_status(),
            "hypotheses": self.get_hypothesis_metrics(),
            "system": self.get_system_metrics(),
            "events": {
                "total_processed": len(self.event_manager.get_event_history()),
                "recent_events": len(self.event_manager.get_event_history(limit=10))
            }
        }
    
    def display_status(self) -> str:
        """Generate a formatted status display."""
        status = self.get_comprehensive_status()
        
        output = []
        output.append("=== Jnana System Status ===")
        output.append(f"Timestamp: {status['timestamp']}")
        output.append("")
        
        # Agent status
        agents = status['agents']
        output.append(f"Agents: {agents['active_count']} active, {agents['completed_count']} completed")
        
        for agent_id, agent_info in agents['agents'].items():
            progress_bar = "█" * int(agent_info['progress'] * 10) + "░" * (10 - int(agent_info['progress'] * 10))
            output.append(f"  {agent_info['agent_type']}: [{progress_bar}] {agent_info['progress']*100:.0f}% - {agent_info['current_step']}")
        
        output.append("")
        
        # Hypothesis metrics
        hyp = status['hypotheses']
        output.append(f"Hypotheses: {hyp['total_generated']} generated, {hyp['total_refined']} refined")
        output.append(f"Generation rate: {hyp['generation_rate']:.2f} per minute")
        output.append("")
        
        # System metrics
        sys = status['system']
        output.append(f"System: {sys['uptime']:.1f}min uptime, {sys['active_sessions']} sessions")
        
        return "\n".join(output)
    
    async def start_monitoring(self, update_interval: float = 5.0):
        """Start continuous monitoring with periodic updates."""
        self.logger.info("Starting monitoring interface")
        
        while True:
            try:
                # In a real implementation, this would update a dashboard
                # or send metrics to a monitoring system
                status = self.get_comprehensive_status()
                
                # Log key metrics
                agents = status['agents']
                hyp = status['hypotheses']
                
                if agents['active_count'] > 0:
                    self.logger.info(f"Monitoring: {agents['active_count']} agents active, "
                                   f"{hyp['total_generated']} hypotheses generated")
                
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(update_interval)
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        status = self.get_comprehensive_status()
        
        if format.lower() == "json":
            import json
            return json.dumps(status, indent=2)
        elif format.lower() == "csv":
            # Simplified CSV export
            lines = []
            lines.append("metric,value")
            lines.append(f"active_agents,{status['agents']['active_count']}")
            lines.append(f"completed_agents,{status['agents']['completed_count']}")
            lines.append(f"total_hypotheses,{status['hypotheses']['total_generated']}")
            lines.append(f"refined_hypotheses,{status['hypotheses']['total_refined']}")
            lines.append(f"generation_rate,{status['hypotheses']['generation_rate']}")
            lines.append(f"uptime_minutes,{status['system']['uptime']}")
            return "\n".join(lines)
        else:
            return self.display_status()
    
    def reset_metrics(self):
        """Reset all metrics to initial state."""
        self.active_agents.clear()
        self.hypothesis_metrics = {
            "total_generated": 0,
            "total_refined": 0,
            "average_refinement_cycles": 0,
            "generation_rate": 0.0
        }
        self.system_metrics = {
            "uptime": 0,
            "memory_usage": 0,
            "cpu_usage": 0,
            "active_sessions": 0
        }
        
        self.logger.info("Monitoring metrics reset")
