"""
Database - SQLite database operations
"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db.models import Base, NetworkLog
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class Database:
    """Database operations for network logs"""
    
    def __init__(self, db_path: str = "ai_wifi.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def add_log(self, log_data: Dict) -> bool:
        """Add a network log entry"""
        session = self.get_session()
        try:
            log = NetworkLog(**log_data)
            session.add(log)
            session.commit()
            logger.debug(f"Log added: {log_data.get('ssid')}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding log: {e}")
            return False
        finally:
            session.close()
    
    def get_all_logs(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """Get all network logs"""
        session = self.get_session()
        try:
            query = session.query(NetworkLog).order_by(NetworkLog.timestamp.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            logs = query.all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
        finally:
            session.close()
    
    def get_logs_by_ssid(self, ssid: str, limit: int = None) -> List[Dict]:
        """Get logs for a specific SSID"""
        session = self.get_session()
        try:
            query = session.query(NetworkLog).filter(NetworkLog.ssid == ssid)
            query = query.order_by(NetworkLog.timestamp.desc())
            if limit:
                query = query.limit(limit)
            logs = query.all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error getting logs by SSID: {e}")
            return []
        finally:
            session.close()
    
    def get_recent_logs(self, hours: int = 24, limit: int = None) -> List[Dict]:
        """Get logs from the last N hours"""
        session = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = session.query(NetworkLog).filter(NetworkLog.timestamp >= cutoff_time)
            query = query.order_by(NetworkLog.timestamp.desc())
            if limit:
                query = query.limit(limit)
            logs = query.all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            return []
        finally:
            session.close()
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        session = self.get_session()
        try:
            total_logs = session.query(NetworkLog).count()
            unique_ssids = session.query(NetworkLog.ssid).distinct().count()
            
            # Get oldest and newest logs
            oldest = session.query(NetworkLog).order_by(NetworkLog.timestamp.asc()).first()
            newest = session.query(NetworkLog).order_by(NetworkLog.timestamp.desc()).first()
            
            return {
                'total_logs': total_logs,
                'unique_networks': unique_ssids,
                'oldest_log': oldest.timestamp.isoformat() if oldest else None,
                'newest_log': newest.timestamp.isoformat() if newest else None
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            session.close()
    
    def delete_old_logs(self, days: int = 30) -> int:
        """Delete logs older than N days"""
        session = self.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            deleted = session.query(NetworkLog).filter(NetworkLog.timestamp < cutoff_time).delete()
            session.commit()
            logger.info(f"Deleted {deleted} old logs")
            return deleted
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting old logs: {e}")
            return 0
        finally:
            session.close()
    
    def export_to_csv(self, filepath: str, limit: int = None):
        """Export logs to CSV file"""
        try:
            import pandas as pd
            logs = self.get_all_logs(limit=limit)
            if logs:
                df = pd.DataFrame(logs)
                df.to_csv(filepath, index=False)
                logger.info(f"Exported {len(logs)} logs to {filepath}")
            else:
                logger.warning("No logs to export")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def export_to_json(self, filepath: str, limit: int = None):
        """Export logs to JSON file"""
        try:
            import json
            logs = self.get_all_logs(limit=limit)
            if logs:
                with open(filepath, 'w') as f:
                    json.dump(logs, f, indent=2, default=str)
                logger.info(f"Exported {len(logs)} logs to {filepath}")
            else:
                logger.warning("No logs to export")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")

