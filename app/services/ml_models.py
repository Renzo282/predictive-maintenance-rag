"""
Machine Learning models for predictive maintenance
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.database import get_supabase

logger = logging.getLogger(__name__)


class PredictiveMaintenanceModel:
    """Machine Learning model for predictive maintenance"""
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.failure_predictor = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "./models"
        self._ensure_model_directory()
    
    def _ensure_model_directory(self):
        """Create model directory if it doesn't exist"""
        os.makedirs(self.model_path, exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features for ML models"""
        # Select numeric columns
        feature_columns = ['temperature', 'vibration', 'pressure', 'humidity', 'voltage', 'current']
        available_columns = [col for col in feature_columns if col in df.columns]
        
        if not available_columns:
            raise ValueError("No valid feature columns found")
        
        # Fill missing values with median
        features = df[available_columns].fillna(df[available_columns].median())
        
        # Add time-based features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            # Add rolling statistics
            for col in available_columns:
                df[f'{col}_rolling_mean'] = df[col].rolling(window=24, min_periods=1).mean()
                df[f'{col}_rolling_std'] = df[col].rolling(window=24, min_periods=1).std()
            
            # Add these new features
            time_features = ['hour', 'day_of_week', 'month']
            rolling_features = [f'{col}_rolling_mean' for col in available_columns] + \
                             [f'{col}_rolling_std' for col in available_columns]
            
            all_features = available_columns + time_features + rolling_features
            features = df[all_features].fillna(0)
        
        return features.values
    
    def train_anomaly_detector(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train anomaly detection model"""
        try:
            features = self.prepare_features(df)
            
            # Train the model
            self.anomaly_detector.fit(features)
            
            # Calculate anomaly scores
            anomaly_scores = self.anomaly_detector.decision_function(features)
            predictions = self.anomaly_detector.predict(features)
            
            # Save model
            model_path = os.path.join(self.model_path, 'anomaly_detector.joblib')
            joblib.dump(self.anomaly_detector, model_path)
            
            # Calculate metrics
            anomaly_count = np.sum(predictions == -1)
            total_samples = len(predictions)
            anomaly_rate = anomaly_count / total_samples
            
            logger.info(f"Anomaly detector trained. Anomaly rate: {anomaly_rate:.2%}")
            
            return {
                "status": "success",
                "anomaly_count": int(anomaly_count),
                "total_samples": int(total_samples),
                "anomaly_rate": float(anomaly_rate),
                "model_path": model_path
            }
            
        except Exception as e:
            logger.error(f"Failed to train anomaly detector: {e}")
            return {"status": "error", "message": str(e)}
    
    def train_failure_predictor(self, df: pd.DataFrame, failure_column: str = 'failure') -> Dict[str, Any]:
        """Train failure prediction model"""
        try:
            if failure_column not in df.columns:
                # Create synthetic failure labels based on extreme values
                logger.warning(f"Failure column '{failure_column}' not found. Creating synthetic labels.")
                df[failure_column] = self._create_synthetic_failures(df)
            
            features = self.prepare_features(df)
            labels = df[failure_column].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.failure_predictor.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = self.failure_predictor.predict(X_test_scaled)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model and scaler
            model_path = os.path.join(self.model_path, 'failure_predictor.joblib')
            scaler_path = os.path.join(self.model_path, 'scaler.joblib')
            
            joblib.dump(self.failure_predictor, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            self.is_trained = True
            
            logger.info(f"Failure predictor trained. Accuracy: {accuracy:.2%}")
            
            return {
                "status": "success",
                "accuracy": float(accuracy),
                "model_path": model_path,
                "scaler_path": scaler_path,
                "classification_report": classification_report(y_test, y_pred, output_dict=True)
            }
            
        except Exception as e:
            logger.error(f"Failed to train failure predictor: {e}")
            return {"status": "error", "message": str(e)}
    
    def _create_synthetic_failures(self, df: pd.DataFrame) -> np.ndarray:
        """Create synthetic failure labels based on extreme values"""
        failure_labels = np.zeros(len(df))
        
        # Define thresholds for different metrics
        thresholds = {
            'temperature': 90,  # High temperature
            'vibration': 5.0,   # High vibration
            'pressure': 10.0,   # High pressure
            'voltage': 250,     # High voltage
            'current': 20.0     # High current
        }
        
        for metric, threshold in thresholds.items():
            if metric in df.columns:
                extreme_values = df[metric] > threshold
                failure_labels[extreme_values] = 1
        
        return failure_labels
    
    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in new data"""
        try:
            if not hasattr(self.anomaly_detector, 'decision_function'):
                logger.warning("Anomaly detector not trained. Loading from file.")
                self._load_models()
            
            features = self.prepare_features(df)
            anomaly_scores = self.anomaly_detector.decision_function(features)
            predictions = self.anomaly_detector.predict(features)
            
            anomalies = []
            for i, (score, prediction) in enumerate(zip(anomaly_scores, predictions)):
                if prediction == -1:  # Anomaly detected
                    anomalies.append({
                        "index": i,
                        "score": float(score),
                        "severity": "high" if score < -0.5 else "medium",
                        "timestamp": df.iloc[i]['timestamp'].isoformat() if 'timestamp' in df.columns else None
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def predict_failures(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predict potential failures"""
        try:
            if not self.is_trained:
                logger.warning("Failure predictor not trained. Loading from file.")
                self._load_models()
            
            features = self.prepare_features(df)
            features_scaled = self.scaler.transform(features)
            
            # Get prediction probabilities
            probabilities = self.failure_predictor.predict_proba(features_scaled)
            predictions = self.failure_predictor.predict(features_scaled)
            
            failure_predictions = []
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                if pred == 1:  # Failure predicted
                    failure_predictions.append({
                        "index": i,
                        "probability": float(prob[1]),  # Probability of failure
                        "confidence": "high" if prob[1] > 0.8 else "medium",
                        "timestamp": df.iloc[i]['timestamp'].isoformat() if 'timestamp' in df.columns else None,
                        "days_until_failure": self._estimate_days_until_failure(prob[1])
                    })
            
            return failure_predictions
            
        except Exception as e:
            logger.error(f"Failed to predict failures: {e}")
            return []
    
    def _estimate_days_until_failure(self, probability: float) -> int:
        """Estimate days until failure based on probability"""
        # Simple heuristic: higher probability = sooner failure
        if probability > 0.9:
            return 1
        elif probability > 0.8:
            return 3
        elif probability > 0.7:
            return 7
        elif probability > 0.6:
            return 14
        else:
            return 30
    
    def _load_models(self):
        """Load pre-trained models"""
        try:
            anomaly_path = os.path.join(self.model_path, 'anomaly_detector.joblib')
            predictor_path = os.path.join(self.model_path, 'failure_predictor.joblib')
            scaler_path = os.path.join(self.model_path, 'scaler.joblib')
            
            if os.path.exists(anomaly_path):
                self.anomaly_detector = joblib.load(anomaly_path)
            
            if os.path.exists(predictor_path) and os.path.exists(scaler_path):
                self.failure_predictor = joblib.load(predictor_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get current model performance metrics"""
        try:
            # Get recent data for evaluation
            supabase = get_supabase()
            recent_data = supabase.table("sensor_data").select("*").limit(1000).execute()
            
            if not recent_data.data:
                return {"error": "No data available for evaluation"}
            
            df = pd.DataFrame(recent_data.data)
            
            # Evaluate anomaly detector
            anomalies = self.detect_anomalies(df)
            anomaly_rate = len(anomalies) / len(df) if len(df) > 0 else 0
            
            # Evaluate failure predictor
            failures = self.predict_failures(df)
            failure_rate = len(failures) / len(df) if len(df) > 0 else 0
            
            return {
                "anomaly_detection": {
                    "total_samples": len(df),
                    "anomalies_detected": len(anomalies),
                    "anomaly_rate": anomaly_rate
                },
                "failure_prediction": {
                    "total_samples": len(df),
                    "failures_predicted": len(failures),
                    "failure_rate": failure_rate
                },
                "model_status": {
                    "anomaly_detector_trained": hasattr(self.anomaly_detector, 'decision_function'),
                    "failure_predictor_trained": self.is_trained
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get model performance: {e}")
            return {"error": str(e)}
    
    def retrain_models(self) -> Dict[str, Any]:
        """Retrain models with latest data"""
        try:
            # Get recent data (last 30 days)
            supabase = get_supabase()
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_data = supabase.table("sensor_data").select("*").gte(
                "timestamp", thirty_days_ago.isoformat()
            ).execute()
            
            if not recent_data.data:
                return {"error": "No recent data available for retraining"}
            
            df = pd.DataFrame(recent_data.data)
            
            # Retrain anomaly detector
            anomaly_result = self.train_anomaly_detector(df)
            
            # Retrain failure predictor
            failure_result = self.train_failure_predictor(df)
            
            return {
                "status": "success",
                "anomaly_detector": anomaly_result,
                "failure_predictor": failure_result,
                "retrained_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to retrain models: {e}")
            return {"status": "error", "message": str(e)}
