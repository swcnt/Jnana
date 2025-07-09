#!/usr/bin/env python3
"""
Jnana: AI Co-Scientist with Interactive Hypothesis Generation

Main entry point for the Jnana system.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from jnana import JnanaSystem
from jnana.utils import setup_logging


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Jnana: AI Co-Scientist with Interactive Hypothesis Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python jnana.py --mode interactive --goal "How can we improve cancer treatment?"
  
  # Batch processing
  python jnana.py --mode batch --goal "Climate change solutions" --count 20
  
  # Hybrid mode with interactive refinement
  python jnana.py --mode hybrid --goal "AI safety research" --interactive-refinement
  
  # Resume from previous session
  python jnana.py --resume session_20240115_143022.json
        """
    )
    
    # Core arguments
    parser.add_argument(
        "--mode", 
        choices=["interactive", "batch", "hybrid"],
        default="interactive",
        help="Operating mode (default: interactive)"
    )
    
    parser.add_argument(
        "--goal",
        type=str,
        help="Research goal or question"
    )
    
    parser.add_argument(
        "--goal-file",
        type=Path,
        help="File containing the research goal"
    )
    
    # Session management
    parser.add_argument(
        "--resume",
        type=Path,
        help="Resume from a previous session file"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for session data (default: auto-generated)"
    )
    
    # Generation parameters
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of hypotheses to generate (default: 5)"
    )
    
    parser.add_argument(
        "--strategies",
        nargs="+",
        choices=["literature_exploration", "scientific_debate", 
                "assumptions_identification", "research_expansion"],
        help="Generation strategies to use"
    )
    
    # Interactive options
    parser.add_argument(
        "--interactive-refinement",
        action="store_true",
        help="Enable interactive refinement in hybrid mode"
    )
    
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Disable interactive UI (CLI only)"
    )
    
    # Configuration
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/models.yaml"),
        help="Model configuration file (default: config/models.yaml)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Override default model for interactive mode"
    )
    
    # Advanced options
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of concurrent workers (default: 4)"
    )
    
    parser.add_argument(
        "--tournament-matches",
        type=int,
        default=25,
        help="Number of tournament matches for ranking (default: 25)"
    )
    
    # Logging and debugging
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path (default: logs to console)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else args.log_level
    setup_logging(level=log_level, log_file=args.log_file)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Jnana v0.1.0 in {args.mode} mode")
    
    try:
        # Validate arguments
        if not args.resume and not args.goal and not args.goal_file:
            logger.error("Must provide --goal, --goal-file, or --resume")
            sys.exit(1)
        
        # Get research goal
        research_goal = None
        if args.goal:
            research_goal = args.goal
        elif args.goal_file:
            if not args.goal_file.exists():
                logger.error(f"Goal file not found: {args.goal_file}")
                sys.exit(1)
            research_goal = args.goal_file.read_text().strip()
        
        # Initialize Jnana system
        jnana = JnanaSystem(
            config_path=args.config,
            max_workers=args.max_workers,
            output_path=args.output,
            enable_ui=not args.no_ui
        )
        
        # Handle resume mode
        if args.resume:
            if not args.resume.exists():
                logger.error(f"Resume file not found: {args.resume}")
                sys.exit(1)
            logger.info(f"Resuming from session: {args.resume}")
            await jnana.resume_session(args.resume)
        else:
            # Set research goal
            logger.info(f"Setting research goal: {research_goal[:100]}...")
            await jnana.set_research_goal(research_goal)
        
        # Run based on mode
        if args.mode == "interactive":
            await jnana.run_interactive_mode(
                model_override=args.model
            )
        elif args.mode == "batch":
            await jnana.run_batch_mode(
                hypothesis_count=args.count,
                strategies=args.strategies,
                tournament_matches=args.tournament_matches
            )
        elif args.mode == "hybrid":
            await jnana.run_hybrid_mode(
                hypothesis_count=args.count,
                strategies=args.strategies,
                interactive_refinement=args.interactive_refinement,
                tournament_matches=args.tournament_matches
            )
        
        logger.info("Jnana session completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Session interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        sys.exit(1)


def main_sync():
    """Synchronous entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
