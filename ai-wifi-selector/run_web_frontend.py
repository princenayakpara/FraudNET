"""
Run Web Frontend - Simple HTTP server for the web UI
"""
import http.server
import socketserver
import webbrowser
import os
import threading
import time

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'frontend'), **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_server():
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Web frontend server started at http://localhost:{PORT}")
        print("Opening browser...")
        time.sleep(1)
        webbrowser.open(f'http://localhost:{PORT}')
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()

if __name__ == "__main__":
    # Ensure frontend directory exists
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    os.makedirs(frontend_dir, exist_ok=True)
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped")

