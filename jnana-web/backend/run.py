#!/usr/bin/env python3
"""
Jnana Web Backend Application Runner.

This script starts the Flask application with SocketIO support.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for Jnana imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from app import create_app, socketio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main application entry point."""
    # Create Flask app
    app = create_app()
    
    # Ensure sessions directory exists
    sessions_dir = parent_dir / 'sessions'
    sessions_dir.mkdir(exist_ok=True)
    
    # Get configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Jnana Web Backend on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Jnana config: {app.config['JNANA_CONFIG_PATH']}")
    
    # Run with SocketIO
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True  # For development only
    )

if __name__ == '__main__':
    main()
