"""
API Routes - FastAPI route handlers
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class NetworkSwitchRequest(BaseModel):
    ssid: str
    password: Optional[str] = None


class APIRoutes:
    """API route handlers"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.router.get("/status")
        async def get_status():
            """Get application status"""
            try:
                current = self.app_controller.get_current_connection()
                monitoring = self.app_controller.is_monitoring()
                
                return {
                    "status": "running",
                    "connected": current is not None,
                    "current_network": current,
                    "monitoring": monitoring
                }
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/networks")
        async def get_networks():
            """Get available WiFi networks"""
            try:
                networks = self.app_controller.scanner.scan_networks()
                return {
                    "count": len(networks),
                    "networks": networks
                }
            except Exception as e:
                logger.error(f"Error getting networks: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/switch")
        async def switch_network(request: NetworkSwitchRequest):
            """Switch to a different WiFi network"""
            try:
                result = self.app_controller.connect_to_network(
                    request.ssid,
                    request.password
                )
                
                if result.get("success"):
                    return {
                        "success": True,
                        "message": result.get("message"),
                        "ssid": request.ssid
                    }
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=result.get("message", "Connection failed")
                    )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error switching network: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/logs")
        async def get_logs(limit: int = 100):
            """Get network logs"""
            try:
                logs = self.app_controller.get_recent_logs(limit=limit)
                return {
                    "count": len(logs),
                    "logs": logs
                }
            except Exception as e:
                logger.error(f"Error getting logs: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/current")
        async def get_current():
            """Get current network connection"""
            try:
                current = self.app_controller.get_current_connection()
                if current:
                    return current
                else:
                    raise HTTPException(status_code=404, detail="Not connected")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting current connection: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/scan")
        async def scan():
            """Trigger network scan"""
            try:
                networks = self.app_controller.scanner.scan_networks()
                return {
                    "success": True,
                    "count": len(networks),
                    "networks": networks
                }
            except Exception as e:
                logger.error(f"Error scanning: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/best")
        async def connect_best():
            """Connect to best available network"""
            try:
                result = self.app_controller.connect_to_best()
                return result
            except Exception as e:
                logger.error(f"Error connecting to best: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/model/info")
        async def get_model_info():
            """Get ML model information"""
            try:
                info = self.app_controller.get_model_info()
                return info
            except Exception as e:
                logger.error(f"Error getting model info: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/model/train")
        async def train_model():
            """Train ML model"""
            try:
                result = self.app_controller.train_model()
                return result
            except Exception as e:
                logger.error(f"Error training model: {e}")
                raise HTTPException(status_code=500, detail=str(e))

