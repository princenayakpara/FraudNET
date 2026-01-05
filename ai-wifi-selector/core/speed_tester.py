"""
Speed Tester - Measures download, upload, ping, and packet loss
"""
import subprocess
import time
import socket
import statistics
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SpeedTester:
    """Tests network speed and connectivity metrics"""
    
    def __init__(self):
        self.test_servers = [
            "8.8.8.8",  # Google DNS
            "1.1.1.1",  # Cloudflare DNS
            "208.67.222.222"  # OpenDNS
        ]
        self.ping_count = 10
        self.timeout = 3
        
    def ping_test(self, host: str = None) -> Dict:
        """
        Perform ping test to measure latency and packet loss
        Returns: {ping_ms, packet_loss_percent}
        """
        if not host:
            host = self.test_servers[0]
        
        ping_times = []
        packet_loss = 0
        
        try:
            # Use Windows ping command
            result = subprocess.run(
                ["ping", "-n", str(self.ping_count), "-w", "1000", host],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse ping output
                lines = result.stdout.split('\n')
                for line in lines:
                    # Look for "time=XXms" or "time<1ms"
                    if 'time=' in line or 'time<' in line:
                        match = __import__('re').search(r'time[<=](\d+)ms', line)
                        if match:
                            ping_times.append(int(match.group(1)))
                    
                    # Look for packet loss percentage
                    if 'Lost' in line or 'loss' in line.lower():
                        match = __import__('re').search(r'(\d+)%', line)
                        if match:
                            packet_loss = int(match.group(1))
                
                # Calculate average ping
                avg_ping = statistics.mean(ping_times) if ping_times else 0
                
                # If no packet loss found in output, calculate from ping count
                if packet_loss == 0 and ping_times:
                    packet_loss = ((self.ping_count - len(ping_times)) / self.ping_count) * 100
                
            else:
                # Ping failed - high packet loss
                avg_ping = 999
                packet_loss = 100
                
        except subprocess.TimeoutExpired:
            avg_ping = 999
            packet_loss = 100
        except Exception as e:
            logger.error(f"Ping test error: {e}")
            avg_ping = 999
            packet_loss = 100
        
        return {
            "ping_ms": round(avg_ping, 2),
            "packet_loss_percent": round(packet_loss, 2)
        }
    
    def speedtest_simple(self) -> Dict:
        """
        Simple speed test using socket connections
        Measures approximate download/upload speeds
        Returns: {download_mbps, upload_mbps}
        """
        download_mbps = 0
        upload_mbps = 0
        
        try:
            # Simple download test - connect to fast server
            test_host = "speedtest.net"
            test_port = 80
            
            # Download test
            start_time = time.time()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect((test_host, test_port))
                sock.send(b"GET / HTTP/1.1\r\nHost: speedtest.net\r\n\r\n")
                
                data_received = 0
                end_time = time.time() + 5  # 5 second test
                
                while time.time() < end_time:
                    chunk = sock.recv(8192)
                    if not chunk:
                        break
                    data_received += len(chunk)
                
                elapsed = time.time() - start_time
                if elapsed > 0:
                    download_mbps = (data_received * 8) / (elapsed * 1000000)  # Convert to Mbps
                
                sock.close()
            except:
                pass
            
            # Upload test (simplified)
            # In production, use speedtest-cli library for accurate results
            upload_mbps = download_mbps * 0.1  # Rough estimate
            
        except Exception as e:
            logger.error(f"Speed test error: {e}")
        
        return {
            "download_mbps": round(max(0, download_mbps), 2),
            "upload_mbps": round(max(0, upload_mbps), 2)
        }
    
    def speedtest_cli(self) -> Dict:
        """
        Use speedtest-cli for accurate speed measurements
        Returns: {download_mbps, upload_mbps, ping_ms, server}
        """
        try:
            import speedtest
            
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_mbps = st.download() / 1000000  # Convert to Mbps
            upload_mbps = st.upload() / 1000000
            ping_ms = st.results.ping
            server = st.results.server.get('name', 'Unknown')
            
            return {
                "download_mbps": round(download_mbps, 2),
                "upload_mbps": round(upload_mbps, 2),
                "ping_ms": round(ping_ms, 2),
                "server": server
            }
            
        except ImportError:
            logger.warning("speedtest-cli not available, using simple test")
            return self.speedtest_simple()
        except Exception as e:
            logger.error(f"Speedtest-cli error: {e}, falling back to simple test")
            result = self.speedtest_simple()
            ping_result = self.ping_test()
            result["ping_ms"] = ping_result["ping_ms"]
            return result
    
    def full_test(self, use_cli: bool = True) -> Dict:
        """
        Perform complete network test
        Returns all metrics: download, upload, ping, packet_loss
        """
        if use_cli:
            speed_result = self.speedtest_cli()
            if "ping_ms" in speed_result:
                ping_result = {"ping_ms": speed_result["ping_ms"], "packet_loss_percent": 0}
            else:
                ping_result = self.ping_test()
        else:
            speed_result = self.speedtest_simple()
            ping_result = self.ping_test()
        
        return {
            "download_mbps": speed_result.get("download_mbps", 0),
            "upload_mbps": speed_result.get("upload_mbps", 0),
            "ping_ms": ping_result.get("ping_ms", 999),
            "packet_loss_percent": ping_result.get("packet_loss_percent", 0),
            "timestamp": time.time()
        }

