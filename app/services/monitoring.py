"""
Monitoring service for continuous data analysis
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from app.core.config import settings
from app.core.database import get_supabase
from app.services.rag_agent import RAGAgent
from app.services.ml_models import PredictiveMaintenanceModel
from app.services.notifications import NotificationService

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for continuous monitoring and alerting"""
    
    def __init__(self):
        self.rag_agent = RAGAgent()
        self.ml_model = PredictiveMaintenanceModel()
        self.notification_service = NotificationService()
        self.is_running = False
        self.monitoring_tasks = []
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return
        
        self.is_running = True
        logger.info("Starting continuous monitoring...")
        
        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_anomalies()),
            asyncio.create_task(self._monitor_predictions()),
            asyncio.create_task(self._update_models()),
            asyncio.create_task(self._update_rag_knowledge())
        ]
        
        logger.info("Monitoring started successfully")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        
        logger.info("Monitoring stopped")
    
    async def _monitor_anomalies(self):
        """Monitor for anomalies in real-time data"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Get recent data (last 5 minutes)
                supabase = get_supabase()
                five_minutes_ago = datetime.now() - timedelta(minutes=5)
                
                response = supabase.table("sensor_data").select(
                    "*, equipment:equipment_id(name, type, location)"
                ).gte("timestamp", five_minutes_ago.isoformat()).execute()
                
                if not response.data:
                    continue
                
                # Group data by equipment
                df = pd.DataFrame(response.data)
                equipment_groups = df.groupby('equipment_id')
                
                for equipment_id, equipment_data in equipment_groups:
                    try:
                        # Detect anomalies
                        anomalies = self.ml_model.detect_anomalies(equipment_data)
                        
                        # Process each anomaly
                        for anomaly in anomalies:
                            await self._process_anomaly(equipment_id, anomaly, equipment_data)
                            
                    except Exception as e:
                        logger.error(f"Error processing anomalies for equipment {equipment_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error in anomaly monitoring: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _monitor_predictions(self):
        """Monitor for failure predictions"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Get recent data (last hour)
                supabase = get_supabase()
                one_hour_ago = datetime.now() - timedelta(hours=1)
                
                response = supabase.table("sensor_data").select(
                    "*, equipment:equipment_id(name, type, location)"
                ).gte("timestamp", one_hour_ago.isoformat()).execute()
                
                if not response.data:
                    continue
                
                # Group data by equipment
                df = pd.DataFrame(response.data)
                equipment_groups = df.groupby('equipment_id')
                
                for equipment_id, equipment_data in equipment_groups:
                    try:
                        # Generate failure predictions
                        predictions = self.ml_model.predict_failures(equipment_data)
                        
                        # Process each prediction
                        for prediction in predictions:
                            await self._process_prediction(equipment_id, prediction, equipment_data)
                            
                    except Exception as e:
                        logger.error(f"Error processing predictions for equipment {equipment_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error in prediction monitoring: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _update_models(self):
        """Update ML models periodically"""
        while self.is_running:
            try:
                await asyncio.sleep(settings.MODEL_UPDATE_INTERVAL)  # Update every hour by default
                
                logger.info("Updating ML models...")
                result = self.ml_model.retrain_models()
                
                if result.get("status") == "success":
                    logger.info("ML models updated successfully")
                else:
                    logger.warning(f"ML model update failed: {result.get('message')}")
                
            except Exception as e:
                logger.error(f"Error updating ML models: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _update_rag_knowledge(self):
        """Update RAG knowledge base periodically"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Update every hour
                
                logger.info("Updating RAG knowledge base...")
                self.rag_agent.update_knowledge_base()
                logger.info("RAG knowledge base updated successfully")
                
            except Exception as e:
                logger.error(f"Error updating RAG knowledge base: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _process_anomaly(self, equipment_id: str, anomaly: Dict[str, Any], equipment_data: pd.DataFrame):
        """Process detected anomaly and create alert if necessary"""
        try:
            # Get equipment details
            equipment_info = equipment_data.iloc[0]
            equipment_name = equipment_info.get('equipment', {}).get('name', 'Unknown')
            equipment_type = equipment_info.get('equipment', {}).get('type', 'Unknown')
            equipment_location = equipment_info.get('equipment', {}).get('location', 'Unknown')
            
            # Determine alert severity based on anomaly score
            severity = "high" if anomaly.get("severity") == "high" else "medium"
            
            # Create alert message
            message = f"Anomaly detected in {anomaly.get('column', 'sensor')} reading. " \
                     f"Value: {anomaly.get('value', 'N/A')}, " \
                     f"Z-score: {anomaly.get('z_score', 'N/A'):.2f}"
            
            # Generate recommendations using RAG
            recommendations = await self._generate_recommendations(
                equipment_id, f"anomaly in {anomaly.get('column')} sensor"
            )
            
            # Create alert
            alert_data = {
                "equipment_id": equipment_id,
                "equipment_name": equipment_name,
                "equipment_type": equipment_type,
                "equipment_location": equipment_location,
                "alert_type": "anomaly_detected",
                "severity": severity,
                "message": message,
                "recommendations": recommendations,
                "anomaly_details": anomaly
            }
            
            # Send alert
            result = self.notification_service.send_alert(alert_data)
            
            if result.get("status") == "success":
                logger.info(f"Anomaly alert sent for equipment {equipment_id}")
            else:
                logger.error(f"Failed to send anomaly alert: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"Error processing anomaly: {e}")
    
    async def _process_prediction(self, equipment_id: str, prediction: Dict[str, Any], equipment_data: pd.DataFrame):
        """Process failure prediction and create alert if necessary"""
        try:
            # Only create alerts for high-confidence predictions
            if prediction.get("confidence") != "high":
                return
            
            # Get equipment details
            equipment_info = equipment_data.iloc[0]
            equipment_name = equipment_info.get('equipment', {}).get('name', 'Unknown')
            equipment_type = equipment_info.get('equipment', {}).get('type', 'Unknown')
            equipment_location = equipment_info.get('equipment', {}).get('location', 'Unknown')
            
            # Create alert message
            days_until_failure = prediction.get("days_until_failure", "unknown")
            probability = prediction.get("probability", 0)
            
            message = f"High probability of failure predicted. " \
                     f"Probability: {probability:.1%}, " \
                     f"Estimated days until failure: {days_until_failure}"
            
            # Generate recommendations using RAG
            recommendations = await self._generate_recommendations(
                equipment_id, f"predicted failure in {days_until_failure} days"
            )
            
            # Create alert
            alert_data = {
                "equipment_id": equipment_id,
                "equipment_name": equipment_name,
                "equipment_type": equipment_type,
                "equipment_location": equipment_location,
                "alert_type": "failure_predicted",
                "severity": "high",
                "message": message,
                "recommendations": recommendations,
                "prediction_details": prediction
            }
            
            # Send alert
            result = self.notification_service.send_alert(alert_data)
            
            if result.get("status") == "success":
                logger.info(f"Failure prediction alert sent for equipment {equipment_id}")
            else:
                logger.error(f"Failed to send prediction alert: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"Error processing prediction: {e}")
    
    async def _generate_recommendations(self, equipment_id: str, context: str) -> list:
        """Generate recommendations using RAG"""
        try:
            # Use RAG agent to generate recommendations
            query = f"Based on the equipment data and the following issue: {context}, " \
                   f"what maintenance recommendations would you suggest for equipment {equipment_id}?"
            
            result = self.rag_agent.generate_prediction(equipment_id, query)
            
            if result.get("error"):
                # Fallback recommendations
                return [
                    "Review equipment operating parameters",
                    "Check for unusual sounds or vibrations",
                    "Schedule maintenance inspection",
                    "Monitor equipment closely"
                ]
            
            # Extract recommendations from RAG response
            answer = result.get("answer", "")
            
            # Simple parsing of recommendations (in a real implementation, you'd use more sophisticated parsing)
            recommendations = []
            if "inspect" in answer.lower():
                recommendations.append("Schedule immediate inspection")
            if "maintenance" in answer.lower():
                recommendations.append("Plan maintenance activities")
            if "replace" in answer.lower():
                recommendations.append("Consider component replacement")
            if "monitor" in answer.lower():
                recommendations.append("Increase monitoring frequency")
            
            # Add fallback recommendations if none found
            if not recommendations:
                recommendations = [
                    "Review equipment operating parameters",
                    "Schedule maintenance inspection",
                    "Monitor equipment closely"
                ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [
                "Review equipment operating parameters",
                "Schedule maintenance inspection",
                "Monitor equipment closely"
            ]


# Global monitoring service instance
monitoring_service = MonitoringService()


async def start_monitoring():
    """Start the monitoring service"""
    await monitoring_service.start_monitoring()


async def stop_monitoring():
    """Stop the monitoring service"""
    await monitoring_service.stop_monitoring()
