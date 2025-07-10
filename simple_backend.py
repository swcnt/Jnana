#!/usr/bin/env python3
"""
Simplified Jnana Web Backend - No async/SocketIO complications.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage
sessions_storage = {}
hypotheses_storage = {}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'jnana-web-simple',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all sessions."""
    try:
        sessions = list(sessions_storage.values())
        logger.info(f"Listed {len(sessions)} sessions")
        return jsonify({'sessions': sessions})
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session."""
    try:
        data = request.get_json()
        research_goal = data.get('research_goal')
        mode = data.get('mode', 'interactive')
        
        if not research_goal:
            return jsonify({'error': 'research_goal is required'}), 400
        
        # Generate session ID
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create session data
        session_data = {
            'session_id': session_id,
            'research_goal': research_goal,
            'mode': mode,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'hypotheses_count': 0
        }
        
        # Store session
        sessions_storage[session_id] = session_data
        
        logger.info(f"Created session {session_id} with goal: {research_goal[:100]}...")
        
        return jsonify(session_data), 201
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for debugging."""
    return jsonify({
        'message': 'Jnana Simple Backend is working!',
        'sessions_count': len(sessions_storage),
        'hypotheses_count': len(hypotheses_storage),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Jnana Simple Web Backend")
    print("📱 API available at: http://localhost:5001")
    print("🔧 Health check: http://localhost:5001/api/health")
    print("🧪 Test endpoint: http://localhost:5001/api/test")
    print("⚡ Press Ctrl+C to stop")
    print()
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False
    )
