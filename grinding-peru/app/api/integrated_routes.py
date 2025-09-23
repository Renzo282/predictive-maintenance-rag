"""
Rutas API Integradas para Sistema de Soporte a la Decisión
Grinding Perú - Mantenimiento Predictivo con RAG
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field
import json

# Importar servicios
from ..services.technician_recommendation import TechnicianRecommendationSystem
from ..services.advanced_predictive_maintenance import AdvancedPredictiveMaintenance
from ..services.intelligent_incident_management import IntelligentIncidentManager, IncidentStatus, IncidentPriority
from ..auth.authentication import get_current_user, verify_token
from ..core.database import get_db_connection

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Inicializar router
router = APIRouter(prefix="/api/v1", tags=["Sistema Integrado"])

# ==================== MODELOS PYDANTIC ====================

class IncidentCreateRequest(BaseModel):
    title: str = Field(..., description="Título de la incidencia")
    description: str = Field(..., description="Descripción detallada")
    equipment_id: str = Field(..., description="ID del equipo")
    location: str = Field(..., description="Ubicación del incidente")
    equipment_criticality: str = Field(default="medium", description="Criticidad del equipo")
    production_impact: str = Field(default="medium", description="Impacto en producción")
    attachments: List[str] = Field(default=[], description="Archivos adjuntos")
    auto_assign: bool = Field(default=True, description="Asignación automática")

class IncidentUpdateRequest(BaseModel):
    status: str = Field(..., description="Nuevo estado")
    notes: Optional[str] = Field(None, description="Notas de resolución")
    actual_duration: Optional[int] = Field(None, description="Duración real en minutos")

class TechnicianRecommendationRequest(BaseModel):
    incident_data: Dict[str, Any] = Field(..., description="Datos de la incidencia")
    limit: int = Field(default=5, description="Número de recomendaciones")

class PredictiveAnalysisRequest(BaseModel):
    equipment_id: str = Field(..., description="ID del equipo")
    sensor_data: List[Dict[str, Any]] = Field(..., description="Datos de sensores")
    analysis_type: str = Field(default="comprehensive", description="Tipo de análisis")

class MaintenanceScheduleRequest(BaseModel):
    equipment_id: int = Field(..., description="ID del equipo")
    schedule_type: str = Field(default="preventive", description="Tipo de cronograma")

# ==================== DEPENDENCIAS ====================

def get_technician_recommender():
    """Obtiene instancia del recomendador de técnicos"""
    db = get_db_connection()
    return TechnicianRecommendationSystem(db)

def get_predictive_system():
    """Obtiene instancia del sistema predictivo"""
    db = get_db_connection()
    # Obtener API key desde variables de entorno
    import os
    openai_key = os.getenv("OPENAI_API_KEY")
    return AdvancedPredictiveMaintenance(db, openai_key)

def get_incident_manager():
    """Obtiene instancia del gestor de incidencias"""
    db = get_db_connection()
    technician_recommender = get_technician_recommender()
    predictive_system = get_predictive_system()
    return IntelligentIncidentManager(db, technician_recommender, predictive_system)

# ==================== RUTAS DE INCIDENCIAS ====================

@router.post("/incidents", response_model=Dict[str, Any])
async def create_incident(
    request: IncidentCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    Crear nueva incidencia con análisis inteligente
    """
    try:
        incident_manager = get_incident_manager()
        
        # Preparar datos de la incidencia
        incident_data = {
            "title": request.title,
            "description": request.description,
            "equipment_id": request.equipment_id,
            "location": request.location,
            "equipment_criticality": request.equipment_criticality,
            "production_impact": request.production_impact,
            "attachments": request.attachments,
            "created_by": current_user["id"]
        }
        
        # Crear incidencia
        result = incident_manager.create_incident(
            incident_data, 
            auto_assign=request.auto_assign
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Procesar en segundo plano
        background_tasks.add_task(
            _process_incident_background,
            result["incident"]["id"]
        )
        
        return {
            "success": True,
            "message": "Incidencia creada exitosamente",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error creando incidencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents", response_model=List[Dict[str, Any]])
async def get_incidents(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    technician_id: Optional[str] = None,
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener lista de incidencias con filtros
    """
    try:
        db = get_db_connection()
        
        # Construir consulta con filtros
        query = "SELECT * FROM incidents WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if priority:
            query += " AND priority = %s"
            params.append(priority)
        
        if technician_id:
            query += " AND assigned_technician_id = %s"
            params.append(technician_id)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        incidents = db.execute_query(query, params)
        
        return {
            "success": True,
            "data": incidents,
            "count": len(incidents)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo incidencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/incidents/{incident_id}", response_model=Dict[str, Any])
async def update_incident(
    incident_id: str,
    request: IncidentUpdateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Actualizar estado de incidencia
    """
    try:
        incident_manager = get_incident_manager()
        
        # Validar estado
        try:
            new_status = IncidentStatus(request.status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Estado inválido")
        
        # Actualizar incidencia
        result = incident_manager.update_incident_status(
            incident_id,
            new_status,
            request.notes,
            request.actual_duration
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return {
            "success": True,
            "message": "Incidencia actualizada exitosamente",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando incidencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents/{incident_id}", response_model=Dict[str, Any])
async def get_incident(
    incident_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener detalles de una incidencia específica
    """
    try:
        db = get_db_connection()
        
        query = "SELECT * FROM incidents WHERE id = %s"
        incident = db.execute_query(query, (incident_id,))
        
        if not incident:
            raise HTTPException(status_code=404, detail="Incidencia no encontrada")
        
        return {
            "success": True,
            "data": incident[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo incidencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE RECOMENDACIÓN DE TÉCNICOS ====================

@router.post("/technicians/recommendations", response_model=Dict[str, Any])
async def get_technician_recommendations(
    request: TechnicianRecommendationRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener recomendaciones de técnicos para una incidencia
    """
    try:
        recommender = get_technician_recommender()
        
        recommendations = recommender.get_technician_recommendations(
            request.incident_data,
            request.limit
        )
        
        return {
            "success": True,
            "data": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/technicians/team-recommendations", response_model=Dict[str, Any])
async def get_team_recommendations(
    request: TechnicianRecommendationRequest,
    team_size: int = 3,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener recomendaciones de equipos de técnicos
    """
    try:
        recommender = get_technician_recommender()
        
        team_recommendations = recommender.get_team_recommendations(
            request.incident_data,
            team_size
        )
        
        return {
            "success": True,
            "data": team_recommendations,
            "count": len(team_recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones de equipo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/technicians/{technician_id}/workload", response_model=Dict[str, Any])
async def get_technician_workload(
    technician_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener carga de trabajo de un técnico
    """
    try:
        incident_manager = get_incident_manager()
        
        workload = incident_manager.get_technician_workload(technician_id)
        
        if "error" in workload:
            raise HTTPException(status_code=404, detail=workload["error"])
        
        return {
            "success": True,
            "data": workload
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo carga de trabajo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE PREDICCIÓN ====================

@router.post("/predictions/failure", response_model=Dict[str, Any])
async def predict_failure(
    request: PredictiveAnalysisRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Predecir fallas usando ML y RAG
    """
    try:
        predictive_system = get_predictive_system()
        
        # Obtener datos del equipo
        db = get_db_connection()
        equipment_query = "SELECT * FROM equipment WHERE id = %s"
        equipment_data = db.execute_query(equipment_query, (request.equipment_id,))
        
        if not equipment_data:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        # Realizar predicción
        prediction = predictive_system.predict_failure(
            equipment_data[0],
            request.sensor_data
        )
        
        return {
            "success": True,
            "data": prediction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error prediciendo falla: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predictions/anomaly-detection", response_model=Dict[str, Any])
async def detect_anomalies(
    equipment_id: str,
    sensor_data: List[Dict[str, Any]],
    current_user: Dict = Depends(get_current_user)
):
    """
    Detectar anomalías en datos de sensores
    """
    try:
        predictive_system = get_predictive_system()
        
        # Preparar datos para detección de anomalías
        features = predictive_system._prepare_features(
            {"id": equipment_id}, 
            sensor_data
        )
        
        # Detectar anomalías
        anomaly_score = predictive_system._detect_anomalies(features)
        
        # Determinar si es anomalía
        is_anomaly = anomaly_score > 0.7
        
        return {
            "success": True,
            "data": {
                "equipment_id": equipment_id,
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly,
                "severity": "high" if anomaly_score > 0.8 else "medium" if anomaly_score > 0.6 else "low",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error detectando anomalías: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/maintenance-schedule/{equipment_id}", response_model=Dict[str, Any])
async def get_maintenance_schedule(
    equipment_id: int,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener cronograma de mantenimiento personalizado
    """
    try:
        predictive_system = get_predictive_system()
        
        schedule = predictive_system.get_maintenance_schedule(equipment_id)
        
        if "error" in schedule:
            raise HTTPException(status_code=400, detail=schedule["error"])
        
        return {
            "success": True,
            "data": schedule
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo cronograma: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE ANÁLISIS ====================

@router.get("/analytics/incidents", response_model=Dict[str, Any])
async def get_incident_analytics(
    days: int = 30,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener análisis de incidencias
    """
    try:
        incident_manager = get_incident_manager()
        
        analytics = incident_manager.get_incident_analytics(days)
        
        if "error" in analytics:
            raise HTTPException(status_code=400, detail=analytics["error"])
        
        return {
            "success": True,
            "data": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo análisis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/performance", response_model=Dict[str, Any])
async def get_performance_analytics(
    period: str = "month",
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener análisis de rendimiento del sistema
    """
    try:
        db = get_db_connection()
        
        # Determinar período
        if period == "week":
            interval = "7 days"
        elif period == "month":
            interval = "30 days"
        elif period == "quarter":
            interval = "90 days"
        else:
            interval = "30 days"
        
        # Consulta de métricas de rendimiento
        query = f"""
        SELECT 
            COUNT(*) as total_incidents,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_incidents,
            AVG(actual_duration) as avg_resolution_time,
            COUNT(CASE WHEN priority = 'critical' THEN 1 END) as critical_incidents,
            COUNT(CASE WHEN created_at >= NOW() - INTERVAL '{interval}' THEN 1 END) as recent_incidents
        FROM incidents 
        WHERE created_at >= NOW() - INTERVAL '{interval}'
        """
        
        result = db.execute_query(query)
        
        if not result:
            raise HTTPException(status_code=404, detail="No se encontraron datos")
        
        metrics = result[0]
        
        # Calcular métricas adicionales
        completion_rate = (metrics['completed_incidents'] / metrics['total_incidents']) * 100 if metrics['total_incidents'] > 0 else 0
        
        return {
            "success": True,
            "data": {
                "period": period,
                "total_incidents": metrics['total_incidents'],
                "completed_incidents": metrics['completed_incidents'],
                "completion_rate": round(completion_rate, 2),
                "avg_resolution_time": round(metrics['avg_resolution_time'] or 0, 2),
                "critical_incidents": metrics['critical_incidents'],
                "recent_incidents": metrics['recent_incidents']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo análisis de rendimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== RUTAS DE EQUIPOS ====================

@router.get("/equipment", response_model=List[Dict[str, Any]])
async def get_equipment(
    status: Optional[str] = None,
    criticality: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener lista de equipos
    """
    try:
        db = get_db_connection()
        
        query = "SELECT * FROM equipment WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if criticality:
            query += " AND criticality = %s"
            params.append(criticality)
        
        equipment = db.execute_query(query, params)
        
        return {
            "success": True,
            "data": equipment,
            "count": len(equipment)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo equipos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/equipment/{equipment_id}", response_model=Dict[str, Any])
async def get_equipment_details(
    equipment_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Obtener detalles de un equipo específico
    """
    try:
        db = get_db_connection()
        
        # Obtener datos del equipo
        equipment_query = "SELECT * FROM equipment WHERE id = %s"
        equipment = db.execute_query(equipment_query, (equipment_id,))
        
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        
        # Obtener historial de mantenimiento
        maintenance_query = """
        SELECT * FROM maintenance_history 
        WHERE equipment_id = %s 
        ORDER BY maintenance_date DESC 
        LIMIT 10
        """
        maintenance_history = db.execute_query(maintenance_query, (equipment_id,))
        
        # Obtener incidencias recientes
        incidents_query = """
        SELECT * FROM incidents 
        WHERE equipment_id = %s 
        ORDER BY created_at DESC 
        LIMIT 5
        """
        recent_incidents = db.execute_query(incidents_query, (equipment_id,))
        
        return {
            "success": True,
            "data": {
                "equipment": equipment[0],
                "maintenance_history": maintenance_history,
                "recent_incidents": recent_incidents
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles del equipo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== FUNCIONES AUXILIARES ====================

async def _process_incident_background(incident_id: str):
    """Procesar incidencia en segundo plano"""
    try:
        # Aquí se pueden agregar tareas de procesamiento en segundo plano
        # como análisis adicional, notificaciones, etc.
        logger.info(f"Procesando incidencia {incident_id} en segundo plano")
        
        # Ejemplo: Análisis adicional de la incidencia
        # incident_manager = get_incident_manager()
        # additional_analysis = incident_manager.perform_additional_analysis(incident_id)
        
    except Exception as e:
        logger.error(f"Error procesando incidencia en segundo plano: {e}")

# ==================== RUTAS DE SALUD ====================

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Verificar estado del sistema
    """
    try:
        db = get_db_connection()
        
        # Verificar conexión a base de datos
        db_status = "connected"
        try:
            db.execute_query("SELECT 1")
        except Exception:
            db_status = "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
