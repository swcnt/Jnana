#!/usr/bin/env python3
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_server(port=3000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    
    print(f"🌐 Jnana Live Web Interface")
    print(f"📱 Frontend: http://localhost:{port}")
    print(f"🔧 Backend: http://localhost:5001")
    print(f"⚡ Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    run_server(3000)
