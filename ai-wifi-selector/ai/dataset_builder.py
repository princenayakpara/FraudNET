"""
Dataset Builder - Builds training dataset from network logs
"""
import pandas as pd
import os
from typing import List, Dict
from db.database import Database
import logging

logger = logging.getLogger(__name__)


class DatasetBuilder:
    """Builds ML training dataset from database logs"""
    
    def __init__(self, db_path: str = "ai_wifi.db"):
        self.db = Database(db_path)
        self.feature_columns = [
            'rssi',
            'download_mbps',
            'upload_mbps',
            'ping_ms',
            'packet_loss_percent',
            'stability_score'
        ]
        self.target_column = 'quality_score'
        
    def load_from_database(self, limit: int = None) -> pd.DataFrame:
        """Load network logs from database and convert to DataFrame"""
        try:
            logs = self.db.get_all_logs(limit=limit)
            
            if not logs:
                logger.warning("No logs found in database")
                return pd.DataFrame()
            
            # Convert logs to DataFrame
            data = []
            for log in logs:
                row = {
                    'rssi': log.get('rssi', -100),
                    'download_mbps': log.get('download_mbps', 0),
                    'upload_mbps': log.get('upload_mbps', 0),
                    'ping_ms': log.get('ping_ms', 999),
                    'packet_loss_percent': log.get('packet_loss_percent', 100),
                    'stability_score': log.get('stability_score', 0),
                    'quality_score': self._calculate_quality_score(log)
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            logger.info(f"Loaded {len(df)} records from database")
            return df
            
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
            return pd.DataFrame()
    
    def _calculate_quality_score(self, log: Dict) -> float:
        """
        Calculate quality score (target variable) from network metrics
        Higher score = better network
        """
        rssi = log.get('rssi', -100)
        download = log.get('download_mbps', 0)
        upload = log.get('upload_mbps', 0)
        ping = log.get('ping_ms', 999)
        packet_loss = log.get('packet_loss_percent', 100)
        stability = log.get('stability_score', 0)
        
        # Normalize RSSI (-100 to -50) to 0-100 scale
        rssi_score = max(0, min(100, (rssi + 100) * 2))
        
        # Normalize download speed (0-100 Mbps) to 0-100 scale
        download_score = min(100, (download / 100) * 100)
        
        # Normalize upload speed (0-50 Mbps) to 0-100 scale
        upload_score = min(100, (upload / 50) * 100)
        
        # Normalize ping (0-500ms) - lower is better
        ping_score = max(0, min(100, 100 - (ping / 5)))
        
        # Normalize packet loss (0-100%) - lower is better
        packet_loss_score = max(0, 100 - packet_loss)
        
        # Weighted combination
        quality_score = (
            rssi_score * 0.25 +
            download_score * 0.25 +
            upload_score * 0.15 +
            ping_score * 0.15 +
            packet_loss_score * 0.10 +
            stability * 0.10
        )
        
        return round(quality_score, 2)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and clean features for training"""
        if df.empty:
            return df
        
        # Select feature columns
        feature_df = df[self.feature_columns].copy()
        
        # Handle missing values
        feature_df = feature_df.fillna(0)
        
        # Clip outliers
        feature_df['rssi'] = feature_df['rssi'].clip(-100, -30)
        feature_df['download_mbps'] = feature_df['download_mbps'].clip(0, 1000)
        feature_df['upload_mbps'] = feature_df['upload_mbps'].clip(0, 500)
        feature_df['ping_ms'] = feature_df['ping_ms'].clip(0, 1000)
        feature_df['packet_loss_percent'] = feature_df['packet_loss_percent'].clip(0, 100)
        feature_df['stability_score'] = feature_df['stability_score'].clip(0, 100)
        
        return feature_df
    
    def prepare_target(self, df: pd.DataFrame) -> pd.Series:
        """Prepare target variable"""
        if df.empty:
            return pd.Series()
        
        return df[self.target_column].clip(0, 100)
    
    def build_dataset(self, limit: int = None) -> tuple:
        """
        Build complete dataset for training
        Returns: (X, y) where X is features DataFrame and y is target Series
        """
        df = self.load_from_database(limit=limit)
        
        if df.empty:
            logger.warning("Empty dataset, returning default values")
            # Return default dataset structure
            default_df = pd.DataFrame({
                col: [0] for col in self.feature_columns
            })
            default_df[self.target_column] = 50.0
            return self.prepare_features(default_df), self.prepare_target(default_df)
        
        X = self.prepare_features(df)
        y = self.prepare_target(df)
        
        logger.info(f"Dataset built: {len(X)} samples, {len(self.feature_columns)} features")
        
        return X, y
    
    def export_to_csv(self, filepath: str, limit: int = None):
        """Export dataset to CSV file"""
        try:
            df = self.load_from_database(limit=limit)
            if not df.empty:
                df.to_csv(filepath, index=False)
                logger.info(f"Dataset exported to {filepath}")
            else:
                logger.warning("No data to export")
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")

