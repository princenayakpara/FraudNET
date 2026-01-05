"""
WiFi Predictor - Uses trained ML model to predict best WiFi network
"""
import os
import logging
from typing import Dict, Optional
from ai.trainer import ModelTrainer

logger = logging.getLogger(__name__)


class WiFiPredictor:
    """Predicts WiFi quality using trained ML model"""
    
    def __init__(self, model_dir: str = "models"):
        self.trainer = ModelTrainer(model_dir)
        self.model = None
        self.load_model()
    
    def load_model(self) -> bool:
        """Load the trained model"""
        if self.trainer.model_exists():
            return self.trainer.load_model()
        else:
            logger.warning("No trained model found. Using default predictions.")
            return False
    
    def predict_score(self, network_data: Dict, speed_metrics: Dict) -> float:
        """
        Predict quality score for a WiFi network
        network_data: {ssid, best_signal, best_rssi}
        speed_metrics: {download_mbps, upload_mbps, ping_ms, packet_loss_percent}
        Returns: predicted quality score (0-100)
        """
        try:
            # Prepare features
            features = {
                'rssi': network_data.get('best_rssi', network_data.get('rssi', -100)),
                'download_mbps': speed_metrics.get('download_mbps', 10.0),
                'upload_mbps': speed_metrics.get('upload_mbps', 5.0),
                'ping_ms': speed_metrics.get('ping_ms', 50.0),
                'packet_loss_percent': speed_metrics.get('packet_loss_percent', 0.0),
                'stability_score': network_data.get('stability_score', 50.0)
            }
            
            # If model is loaded, use it
            if self.trainer.model is not None:
                import pandas as pd
                import numpy as np
                
                # Create feature vector
                feature_vector = pd.DataFrame([features])
                
                # Predict
                prediction = self.trainer.model.predict(feature_vector)[0]
                return round(float(prediction), 2)
            
            # Fallback: simple heuristic if no model
            return self._heuristic_score(features)
            
        except Exception as e:
            logger.error(f"Error predicting score: {e}")
            # Return heuristic score as fallback
            return self._heuristic_score({
                'rssi': network_data.get('best_rssi', -100),
                'download_mbps': speed_metrics.get('download_mbps', 10),
                'upload_mbps': speed_metrics.get('upload_mbps', 5),
                'ping_ms': speed_metrics.get('ping_ms', 50),
                'packet_loss_percent': speed_metrics.get('packet_loss_percent', 0),
                'stability_score': network_data.get('stability_score', 50)
            })
    
    def _heuristic_score(self, features: Dict) -> float:
        """Fallback heuristic scoring when model is not available"""
        rssi = features.get('rssi', -100)
        download = features.get('download_mbps', 10)
        upload = features.get('upload_mbps', 5)
        ping = features.get('ping_ms', 50)
        packet_loss = features.get('packet_loss_percent', 0)
        stability = features.get('stability_score', 50)
        
        # Normalize and combine
        rssi_score = max(0, min(100, (rssi + 100) * 2))
        download_score = min(100, (download / 100) * 100)
        upload_score = min(100, (upload / 50) * 100)
        ping_score = max(0, min(100, 100 - (ping / 5)))
        packet_loss_score = max(0, 100 - packet_loss)
        
        score = (
            rssi_score * 0.25 +
            download_score * 0.25 +
            upload_score * 0.15 +
            ping_score * 0.15 +
            packet_loss_score * 0.10 +
            stability * 0.10
        )
        
        return round(score, 2)
    
    def predict_best_network(self, networks: list, speed_metrics: Dict = None) -> Optional[Dict]:
        """
        Predict and return the best network from a list
        Returns network with highest predicted score
        """
        if not networks:
            return None
        
        if speed_metrics is None:
            speed_metrics = {}
        
        best_network = None
        best_score = -1
        
        for network in networks:
            try:
                score = self.predict_score(network, speed_metrics)
                network['ml_score'] = score
                
                if score > best_score:
                    best_score = score
                    best_network = network
            except Exception as e:
                logger.error(f"Error predicting for network {network.get('ssid')}: {e}")
                continue
        
        return best_network
    
    def is_model_loaded(self) -> bool:
        """Check if ML model is loaded"""
        return self.trainer.model is not None

