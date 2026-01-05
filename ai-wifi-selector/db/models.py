"""
Database Models - SQLAlchemy models for network logs
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class NetworkLog(Base):
    """Network log entry model"""
    __tablename__ = 'network_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ssid = Column(String(255), nullable=False)
    bssid = Column(String(50))
    rssi = Column(Float, nullable=False)
    signal_strength = Column(Integer)  # Percentage 0-100
    download_mbps = Column(Float)
    upload_mbps = Column(Float)
    ping_ms = Column(Float)
    packet_loss_percent = Column(Float)
    stability_score = Column(Float)
    quality_score = Column(Float)
    ml_score = Column(Float)
    notes = Column(Text)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ssid': self.ssid,
            'bssid': self.bssid,
            'rssi': self.rssi,
            'signal_strength': self.signal_strength,
            'download_mbps': self.download_mbps,
            'upload_mbps': self.upload_mbps,
            'ping_ms': self.ping_ms,
            'packet_loss_percent': self.packet_loss_percent,
            'stability_score': self.stability_score,
            'quality_score': self.quality_score,
            'ml_score': self.ml_score,
            'notes': self.notes
        }

