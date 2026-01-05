"""
Model Trainer - Trains RandomForestRegressor model for WiFi prediction
"""
import os
import pickle
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
from typing import Dict
from ai.dataset_builder import DatasetBuilder

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trains and saves ML model for WiFi quality prediction"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "best_wifi_model.pkl")
        self.model = None
        self.dataset_builder = DatasetBuilder()
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
    
    def train(self, retrain: bool = False) -> Dict:
        """
        Train the RandomForestRegressor model
        Returns: {success: bool, metrics: dict, message: str}
        """
        try:
            # Load dataset
            X, y = self.dataset_builder.build_dataset()
            
            if len(X) < 10:
                logger.warning("Insufficient data for training (need at least 10 samples)")
                return {
                    "success": False,
                    "message": "Insufficient training data. Need at least 10 network logs.",
                    "metrics": {}
                }
            
            # Split dataset
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Initialize model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            # Train model
            logger.info(f"Training model with {len(X_train)} samples...")
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred_train = self.model.predict(X_train)
            y_pred_test = self.model.predict(X_test)
            
            train_mse = mean_squared_error(y_train, y_pred_train)
            test_mse = mean_squared_error(y_test, y_pred_test)
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            
            metrics = {
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "train_mse": round(train_mse, 4),
                "test_mse": round(test_mse, 4),
                "train_r2": round(train_r2, 4),
                "test_r2": round(test_r2, 4),
                "feature_importance": dict(zip(
                    self.dataset_builder.feature_columns,
                    [round(x, 4) for x in self.model.feature_importances_]
                ))
            }
            
            # Save model
            self.save_model()
            
            logger.info(f"Model trained successfully. Test R²: {test_r2:.4f}")
            
            return {
                "success": True,
                "message": "Model trained successfully",
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                "success": False,
                "message": f"Training failed: {str(e)}",
                "metrics": {}
            }
    
    def save_model(self):
        """Save trained model to disk"""
        try:
            if self.model is None:
                logger.error("No model to save")
                return False
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            logger.info(f"Model saved to {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found: {self.model_path}")
                return False
            
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            logger.info(f"Model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def model_exists(self) -> bool:
        """Check if trained model exists"""
        return os.path.exists(self.model_path)
    
    def get_model_info(self) -> Dict:
        """Get information about the trained model"""
        if not self.model_exists():
            return {"exists": False}
        
        try:
            if self.model is None:
                self.load_model()
            
            if self.model is None:
                return {"exists": False}
            
            return {
                "exists": True,
                "n_estimators": self.model.n_estimators,
                "max_depth": self.model.max_depth,
                "n_features": self.model.n_features_in_,
                "feature_names": self.dataset_builder.feature_columns
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"exists": False}

