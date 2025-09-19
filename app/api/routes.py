"""
API routes for predictive maintenance system
"""
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd

from app.services.rag_agent import RAGAgent
from app.services.ml_models import PredictiveMaintenanceModel
from app.services.notifications import NotificationService
from app.core.database import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
rag_agent = RAGAgent()
ml_model = PredictiveMaintenanceModel()
notification_service = NotificationService()


# Pydantic models for request/response
class EquipmentData(BaseModel):
    equipment_id: str
    timestamp: datetime
    temperature: Optional[float] = None
    vibration: Optional[float] = None
    pressure: Optional[float] = None
    humidity: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None


class AlertRequest(BaseModel):
    equipment_id: str
    alert_type: str
    severity: str
    message: str
    recommendations: Optional[List[str]] = []


class PredictionRequest(BaseModel):
    equipment_id: str
    query: str


class MaintenanceScheduleRequest(BaseModel):
    equipment_id: str
    maintenance_type: str
    scheduled_date: str
    description: str


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Predictive Maintenance RAG Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        supabase = get_supabase()
        # Test database connection
        response = supabase.table("equipment").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.post("/data/ingest")
async def ingest_sensor_data(data: EquipmentData):
    """Ingest sensor data"""
    try:
        supabase = get_supabase()
        
        # Insert sensor data
        sensor_data = {
            "equipment_id": data.equipment_id,
            "timestamp": data.timestamp.isoformat(),
            "temperature": data.temperature,
            "vibration": data.vibration,
            "pressure": data.pressure,
            "humidity": data.humidity,
            "voltage": data.voltage,
            "current": data.current
        }
        
        response = supabase.table("sensor_data").insert(sensor_data).execute()
        
        if response.data:
            # Analyze data for anomalies
            analysis_result = await analyze_equipment_data(data.equipment_id)
            
            return {
                "status": "success",
                "data_id": response.data[0]["id"],
                "analysis": analysis_result
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to insert data")
            
    except Exception as e:
        logger.error(f"Failed to ingest sensor data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equipment/{equipment_id}/analysis")
async def analyze_equipment_data(equipment_id: str, days: int = 30):
    """Analyze equipment data for patterns and anomalies"""
    try:
        # Get equipment details
        supabase = get_supabase()
        equipment_response = supabase.table("equipment").select("*").eq("id", equipment_id).execute()
        
        if not equipment_response.data:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        equipment = equipment_response.data[0]
        
        # Analyze patterns using RAG agent
        patterns = rag_agent.analyze_patterns(equipment_id, days)
        
        # Detect anomalies using ML model
        recent_data = supabase.table("sensor_data").select("*").eq(
            "equipment_id", equipment_id
        ).gte("timestamp", (datetime.now() - timedelta(days=days)).isoformat()).execute()
        
        anomalies = []
        if recent_data.data:
            df = pd.DataFrame(recent_data.data)
            anomalies = ml_model.detect_anomalies(df)
        
        # Generate predictions
        predictions = []
        if recent_data.data:
            df = pd.DataFrame(recent_data.data)
            predictions = ml_model.predict_failures(df)
        
        return {
            "equipment": equipment,
            "analysis_period_days": days,
            "patterns": patterns,
            "anomalies": anomalies,
            "predictions": predictions,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze equipment data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/equipment/{equipment_id}/predict")
async def generate_prediction(equipment_id: str, request: PredictionRequest):
    """Generate prediction using RAG"""
    try:
        # Generate prediction using RAG agent
        prediction = rag_agent.generate_prediction(equipment_id, request.query)
        
        return {
            "equipment_id": equipment_id,
            "query": request.query,
            "prediction": prediction,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts")
async def create_alert(alert: AlertRequest):
    """Create and send maintenance alert"""
    try:
        # Get equipment details
        supabase = get_supabase()
        equipment_response = supabase.table("equipment").select("*").eq("id", alert.equipment_id).execute()
        
        if not equipment_response.data:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        equipment = equipment_response.data[0]
        
        # Prepare alert data
        alert_data = {
            "equipment_id": alert.equipment_id,
            "equipment_name": equipment.get("name"),
            "equipment_type": equipment.get("type"),
            "equipment_location": equipment.get("location"),
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "recommendations": alert.recommendations
        }
        
        # Send alert
        result = notification_service.send_alert(alert_data)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/schedule")
async def schedule_maintenance(request: MaintenanceScheduleRequest):
    """Schedule maintenance and create alert"""
    try:
        result = notification_service.create_maintenance_schedule_alert(
            equipment_id=request.equipment_id,
            maintenance_type=request.maintenance_type,
            scheduled_date=request.scheduled_date,
            description=request.description
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to schedule maintenance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(
    equipment_id: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = Query(100, le=1000)
):
    """Get alert history"""
    try:
        alerts = notification_service.get_alert_history(equipment_id, limit)
        
        # Filter by resolved status if specified
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.get("is_resolved") == resolved]
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark alert as resolved"""
    try:
        result = notification_service.resolve_alert(alert_id)
        return result
        
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/performance")
async def get_model_performance():
    """Get ML model performance metrics"""
    try:
        performance = ml_model.get_model_performance()
        return performance
        
    except Exception as e:
        logger.error(f"Failed to get model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/retrain")
async def retrain_models():
    """Retrain ML models with latest data"""
    try:
        result = ml_model.retrain_models()
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrain models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equipment")
async def get_equipment_list():
    """Get list of all equipment"""
    try:
        supabase = get_supabase()
        response = supabase.table("equipment").select("*").execute()
        
        return {
            "equipment": response.data if response.data else [],
            "total_count": len(response.data) if response.data else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get equipment list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equipment/{equipment_id}/data")
async def get_equipment_data(
    equipment_id: str,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(1000, le=10000)
):
    """Get historical data for equipment"""
    try:
        supabase = get_supabase()
        
        start_date = datetime.now() - timedelta(days=days)
        
        response = supabase.table("sensor_data").select("*").eq(
            "equipment_id", equipment_id
        ).gte("timestamp", start_date.isoformat()).order(
            "timestamp", desc=True
        ).limit(limit).execute()
        
        return {
            "equipment_id": equipment_id,
            "data": response.data if response.data else [],
            "total_count": len(response.data) if response.data else 0,
            "date_range": {
                "start": start_date.isoformat(),
                "end": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get equipment data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/update")
async def update_rag_knowledge_base():
    """Update RAG knowledge base with new data"""
    try:
        rag_agent.update_knowledge_base()
        
        return {
            "status": "success",
            "message": "Knowledge base updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update RAG knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))
