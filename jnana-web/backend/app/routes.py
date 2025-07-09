"""
Flask routes for Jnana web API.

This module defines the REST API endpoints for the Jnana web interface.
"""

import asyncio
from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit
from . import socketio

api_bp = Blueprint('api', __name__)


def run_async(coro):
    """Helper to run async functions in Flask routes."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'jnana-web'})


@api_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """List all sessions."""
    try:
        sessions = run_async(current_app.jnana_service.list_sessions())
        return jsonify({'sessions': sessions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new session."""
    try:
        data = request.get_json()
        research_goal = data.get('research_goal')
        mode = data.get('mode', 'interactive')
        
        if not research_goal:
            return jsonify({'error': 'research_goal is required'}), 400
        
        session = run_async(current_app.jnana_service.create_session(research_goal, mode))
        
        # Emit session created event
        socketio.emit('session_created', session, namespace='/jnana')
        
        return jsonify(session), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WebSocket event handlers
@socketio.on('connect', namespace='/jnana')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to Jnana WebSocket'})


@socketio.on('disconnect', namespace='/jnana')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected from Jnana WebSocket')
