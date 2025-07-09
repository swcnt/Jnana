#!/usr/bin/env python3
"""
Simple demo server for Jnana Web Interface.
"""

import os
import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

class JnanaDemoHandler(SimpleHTTPRequestHandler):
    """Custom handler for Jnana demo with API endpoints."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_file('index.html')
        elif parsed_path.path == '/api/health':
            self.send_json_response({
                'status': 'healthy',
                'service': 'jnana-demo',
                'timestamp': datetime.now().isoformat()
            })
        else:
            super().do_GET()
    
    def serve_file(self, filename):
        """Serve a specific file."""
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-length', len(content))
            self.end_headers()
            self.wfile.write(content)
            
        except FileNotFoundError:
            self.send_error(404, f"File not found: {filename}")
    
    def send_json_response(self, data, status=200):
        """Send a JSON response."""
        response = json.dumps(data, indent=2)
        
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', len(response))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

def run_demo_server(port=8080):
    """Run the demo server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, JnanaDemoHandler)
    
    print(f"🌐 Jnana Web Interface Demo")
    print(f"📱 Open your browser to: http://localhost:{port}")
    print(f"⚡ Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down demo server...")
        httpd.shutdown()

if __name__ == '__main__':
    run_demo_server(8080)
