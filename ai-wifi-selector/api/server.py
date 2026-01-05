"""
FastAPI Server - REST API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import APIRoutes
import logging
import uvicorn
import threading

logger = logging.getLogger(__name__)


class APIServer:
    """FastAPI server for REST API"""
    
    def __init__(self, app_controller, host: str = "127.0.0.1", port: int = 8000):
        self.app_controller = app_controller
        self.host = host
        self.port = port
        self.app = FastAPI(title="AI WiFi Selector API")
        self.server_thread = None
        self.running = False
        
        # Setup CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        routes = APIRoutes(app_controller)
        self.app.include_router(routes.router, prefix="/api", tags=["wifi"])
        
        # Root endpoint
        @self.app.get("/")
        async def root():
            return {
                "message": "AI WiFi Selector API",
                "version": "1.0.0",
                "endpoints": {
                    "status": "/api/status",
                    "networks": "/api/networks",
                    "switch": "/api/switch",
                    "logs": "/api/logs",
                    "current": "/api/current",
                    "scan": "/api/scan",
                    "best": "/api/best"
                }
            }
    
    def start(self):
        """Start API server in background thread"""
        if self.running:
            return
        
        def run_server():
            uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True
        logger.info(f"API server started on http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop API server"""
        self.running = False
        logger.info("API server stopped")

