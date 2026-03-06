#!/usr/bin/env python3
"""
VoxQuery - Ultra Minimal Test Server
No external dependencies - for quick testing
"""

import json
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

class VoxQueryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "service": "VoxQuery - Natural Language SQL",
                "version": "1.0.0",
                "status": "running",
                "endpoints": ["/", "/health", "/docs"],
                "message": "Backend is working! Full API will be ready with: python main_simple.py"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        elif path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "ok", "service": "VoxQuery"}
            self.wfile.write(json.dumps(response).encode())
        
        elif path == "/docs":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <html>
            <head>
                <title>VoxQuery API</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #1e1e1e; color: #e0e0e0; }
                    h1 { color: #4a9eff; }
                    .status { background: #2d2d2d; padding: 20px; border-radius: 5px; margin: 20px 0; }
                    .endpoint { background: #3d3d3d; padding: 10px; margin: 10px 0; border-left: 3px solid #4a9eff; }
                    code { background: #2d2d2d; padding: 2px 6px; border-radius: 3px; }
                    .success { color: #4ade80; }
                </style>
            </head>
            <body>
                <h1>🚀 VoxQuery Backend</h1>
                <div class="status">
                    <h2>Status: <span class="success">✓ Running</span></h2>
                    <p>Test server is active. Dependencies are being installed.</p>
                </div>
                
                <h2>Available Endpoints</h2>
                <div class="endpoint">
                    <code>GET /</code> - Root endpoint
                </div>
                <div class="endpoint">
                    <code>GET /health</code> - Health check
                </div>
                <div class="endpoint">
                    <code>GET /docs</code> - This page
                </div>
                
                <h2>Next Steps</h2>
                <p>Once dependencies finish installing, run:</p>
                <div style="background: #2d2d2d; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <code>python main_simple.py</code>
                </div>
                <p>Then full API docs will be available with interactive testing.</p>
                
                <h2>What's Happening</h2>
                <ul>
                    <li>✓ Backend server is running</li>
                    <li>⏳ Installing FastAPI, LangChain, database drivers...</li>
                    <li>⏳ Once complete, run <code>python main_simple.py</code></li>
                    <li>✓ Then visit http://localhost:8000/docs for full API</li>
                </ul>
                
                <p style="margin-top: 40px; font-size: 12px; color: #808080;">VoxQuery v1.0.0</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"error": "Not Found", "path": path, "available": ["/", "/health", "/docs"]}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Suppress logging"""
        pass

def run():
    """Start the minimal test server"""
    print("\n" + "=" * 60)
    print("🚀 VoxQuery Minimal Test Server")
    print("=" * 60)
    print()
    print("📍 API:  http://localhost:8000")
    print("🏥 Health: http://localhost:8000/health")
    print()
    print("⏳ Dependencies are installing in background...")
    print("📖 Once done, run: python main.py")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        server = HTTPServer(("0.0.0.0", 8000), VoxQueryHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Stopping server...")
        server.shutdown()
        print("✅ Done!")

if __name__ == "__main__":
    run()
