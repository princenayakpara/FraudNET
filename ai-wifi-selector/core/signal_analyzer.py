"""
Signal Analyzer - Analyzes WiFi signal strength and stability
"""
import time
from typing import Dict, List
import statistics
import logging

logger = logging.getLogger(__name__)


class SignalAnalyzer:
    """Analyzes WiFi signal quality and stability"""
    
    def __init__(self):
        self.signal_history = {}  # {ssid: [signal_readings]}
        self.history_size = 10
        
    def calculate_stability_score(self, ssid: str, current_signal: int) -> float:
        """
        Calculate stability score based on signal history
        Returns score 0-100 (higher is more stable)
        """
        if ssid not in self.signal_history:
            self.signal_history[ssid] = []
        
        history = self.signal_history[ssid]
        history.append(current_signal)
        
        # Keep only recent history
        if len(history) > self.history_size:
            history.pop(0)
        
        if len(history) < 3:
            # Not enough data, return based on current signal
            return min(100, current_signal * 0.8)
        
        # Calculate stability based on variance
        mean_signal = statistics.mean(history)
        try:
            stdev = statistics.stdev(history)
        except:
            stdev = 0
        
        # Lower standard deviation = more stable
        # Normalize: 0 stdev = 100 score, high stdev = lower score
        stability = max(0, 100 - (stdev * 2))
        
        # Factor in average signal strength
        signal_factor = mean_signal / 100
        
        final_score = (stability * 0.6) + (signal_factor * 100 * 0.4)
        
        return round(min(100, max(0, final_score)), 2)
    
    def analyze_network(self, network_data: Dict) -> Dict:
        """
        Analyze a network and return comprehensive metrics
        network_data should contain: ssid, best_signal, best_rssi
        """
        ssid = network_data.get("ssid", "unknown")
        signal = network_data.get("best_signal", 0)
        rssi = network_data.get("best_rssi", -100)
        
        stability = self.calculate_stability_score(ssid, signal)
        
        # Signal quality categories
        if signal >= 80:
            quality = "Excellent"
        elif signal >= 60:
            quality = "Good"
        elif signal >= 40:
            quality = "Fair"
        elif signal >= 20:
            quality = "Poor"
        else:
            quality = "Very Poor"
        
        return {
            "ssid": ssid,
            "signal_strength": signal,
            "rssi": rssi,
            "stability_score": stability,
            "quality": quality,
            "recommended": signal >= 60 and stability >= 70
        }
    
    def compare_networks(self, networks: List[Dict]) -> List[Dict]:
        """
        Analyze and rank multiple networks
        Returns sorted list by overall score
        """
        analyzed = []
        
        for network in networks:
            analysis = self.analyze_network(network)
            # Calculate overall score
            overall_score = (
                analysis["signal_strength"] * 0.4 +
                analysis["stability_score"] * 0.4 +
                (100 - abs(analysis["rssi"] + 50)) * 0.2  # Prefer RSSI around -50
            )
            analysis["overall_score"] = round(overall_score, 2)
            analyzed.append(analysis)
        
        # Sort by overall score descending
        analyzed.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return analyzed
    
    def reset_history(self, ssid: str = None):
        """Reset signal history for a specific SSID or all"""
        if ssid:
            if ssid in self.signal_history:
                del self.signal_history[ssid]
        else:
            self.signal_history.clear()

