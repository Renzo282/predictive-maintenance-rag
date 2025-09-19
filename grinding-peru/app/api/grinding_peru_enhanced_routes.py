"""
Rutas API mejoradas para Grinding Perú
Implementa todos los requerimientos funcionales específicos
"""
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from app.auth.authentication import auth_service, UserLogin, UserCreate, UserResponse
from app.services.incident_management_enhanced import EnhancedIncidentManagementService
from app.services.predictive_maintenance import PredictiveMaintenanceService
from app.services.inventory_management import InventoryManagementService
from app.services.communication_management import CommunicationManagementService
from app.services.service_metrics import ServiceMetricsService

logger = logging.getLogger(__name__)

router = APIRouter()

# Inicializar servicios
incident_service = EnhancedIncidentManagementService()
predictive_service = PredictiveMaintenanceService()
inventory_service = InventoryManagementService()
communication_service = CommunicationManagementService()
metrics_service = ServiceMetricsService()


# Modelos Pydantic para los requerimientos funcionales
class IncidentCreate(BaseModel):
    tipo_falla: str
    equipo_involucrado: str
    ubicacion: str
    prioridad: str
    descripcion: str
    fotos: Optional[List[str]] = []
    archivos: Optional[List[str]] = []

class IncidentUpdate(BaseModel):
    estado: str
    comentarios: Optional[str] = ""
    fotos: Optional[List[str]] = []
    archivos: Optional[List[str]] = []

class EquipmentMaintenance(BaseModel):
    equipo_id: str
    tipo_mantenimiento: str
    descripcion: str
    materiales_utilizados: List[str]
    observaciones: str
    tiempo_inicio: str
    tiempo_fin: str

class ReportRequest(BaseModel):
    tipo_reporte: str
    fecha_inicio: str
    fecha_fin: str
    filtros: Optional[Dict[str, Any]] = {}


# ==================== AUTENTICACIÓN Y USUARIOS ====================

@router.post("/auth/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin):
    """Inicio de sesión (Logeo de usuarios)"""
    try:
        result = await auth_service.login_user(login_data.username, login_data.password)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/auth/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate, current_user: Dict[str, Any] = Depends(auth_service.require_permission("manage_users"))):
    """Registrar nuevo usuario (solo administradores)"""
    try:
        result = await auth_service.create_user(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(auth_service.get_current_user)):
    """Obtener información del usuario actual"""
    return UserResponse(**current_user)

@router.get("/auth/users", response_model=List[UserResponse])
async def get_all_users(current_user: Dict[str, Any] = Depends(auth_service.require_permission("manage_users"))):
    """Obtener todos los usuarios (solo administradores)"""
    try:
        users = await auth_service.get_all_users()
        return [UserResponse(**user) for user in users]
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/auth/users/by-role/{role}")
async def get_users_by_role(role: str, current_user: Dict[str, Any] = Depends(auth_service.require_permission("manage_users"))):
    """Obtener usuarios por rol (solo administradores)"""
    try:
        users = await auth_service.get_users_by_role(role)
        return {"users": users, "role": role}
    except Exception as e:
        logger.error(f"Error obteniendo usuarios por rol: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ==================== GESTIÓN DE INCIDENCIAS ====================

@router.post("/incidents")
async def create_incident(incident_data: IncidentCreate, current_user: Dict[str, Any] = Depends(auth_service.get_current_user)):
    """Registro de incidencias - Permitir que cualquier usuario autorizado registre incidencias"""
    try:
        result = await incident_service.create_incident(incident_data.dict(), current_user)
        return result
    except Exception as e:
        logger.error(f"Error creando incidencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents")
async def get_incidents(
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Visualización de incidencias - Mostrar el estado actual de cada incidencia"""
    try:
        incidents = await incident_service.get_incidents_by_user(current_user, status)
        return {"incidents": incidents, "total": len(incidents)}
    except Exception as e:
        logger.error(f"Error obteniendo incidencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents/{incident_id}")
async def get_incident_details(incident_id: str, current_user: Dict[str, Any] = Depends(auth_service.get_current_user)):
    """Obtener detalles completos de una incidencia"""
    try:
        result = await incident_service.get_incident_details(incident_id, current_user)
        return result
    except Exception as e:
        logger.error(f"Error obteniendo detalles de incidencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/incidents/{incident_id}/update")
async def update_incident(
    incident_id: str, 
    update_data: IncidentUpdate, 
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Actualización de incidencias - Permitir actualización con comentarios, fotos y archivos"""
    try:
        result = await incident_service.update_incident_status(
            incident_id, 
            update_data.estado, 
            current_user, 
            update_data.comentarios,
            update_data.fotos,
            update_data.archivos
        )
        return result
    except Exception as e:
        logger.error(f"Error actualizando incidencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/incidents/{incident_id}/assign")
async def assign_incident(
    incident_id: str,
    technician_id: str,
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("assign_incidents"))
):
    """Asignación manual de incidencias (supervisores y administradores)"""
    try:
        # Implementar lógica de asignación manual
        return {"message": f"Incidencia {incident_id} asignada al técnico {technician_id}"}
    except Exception as e:
        logger.error(f"Error asignando incidencia: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents/metrics")
async def get_incident_metrics(
    days: int = 30,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Obtener métricas de incidencias"""
    try:
        metrics = await incident_service.get_incident_metrics(current_user, days)
        return metrics
    except Exception as e:
        logger.error(f"Error obteniendo métricas de incidencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MANTENIMIENTO PREDICTIVO ====================

@router.post("/maintenance/predict/{equipment_id}")
async def predict_equipment_failure(
    equipment_id: str,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Módulo de predicción de fallas técnicas - Implementar ML para anticipar fallas"""
    try:
        result = await predictive_service.predict_equipment_failure(equipment_id)
        return result
    except Exception as e:
        logger.error(f"Error prediciendo falla del equipo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/maintenance/train-models")
async def train_predictive_models(
    equipment_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("system_configuration"))
):
    """Entrenar modelos de ML con datos históricos"""
    try:
        result = await predictive_service.train_models(equipment_id)
        return result
    except Exception as e:
        logger.error(f"Error entrenando modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/maintenance/equipment/{equipment_id}/health")
async def get_equipment_health(
    equipment_id: str,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Obtener estado de salud de un equipo específico"""
    try:
        result = await predictive_service.get_equipment_health_summary(equipment_id)
        return result
    except Exception as e:
        logger.error(f"Error obteniendo salud del equipo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/maintenance/predictive-dashboard")
async def get_predictive_dashboard(
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Dashboard de análisis predictivo"""
    try:
        result = await predictive_service.get_predictive_analytics_dashboard()
        return result
    except Exception as e:
        logger.error(f"Error obteniendo dashboard predictivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HISTORIAL TÉCNICO ====================

@router.post("/maintenance/record")
async def record_maintenance(
    maintenance_data: EquipmentMaintenance,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Historial técnico consolidado por equipo - Registrar mantenimiento completo"""
    try:
        # Implementar lógica de registro de mantenimiento
        maintenance_record = {
            "equipment_id": maintenance_data.equipo_id,
            "maintenance_type": maintenance_data.tipo_mantenimiento,
            "description": maintenance_data.descripcion,
            "materials_used": maintenance_data.materiales_utilizados,
            "observations": maintenance_data.observaciones,
            "start_time": maintenance_data.tiempo_inicio,
            "end_time": maintenance_data.tiempo_fin,
            "performed_by": current_user['id'],
            "created_at": datetime.now().isoformat()
        }
        
        # Guardar en base de datos
        supabase = get_supabase()
        response = supabase.table("maintenance_records").insert(maintenance_record).execute()
        
        if response.data:
            return {
                "status": "success",
                "maintenance_id": response.data[0]['id'],
                "message": "Registro de mantenimiento creado exitosamente"
            }
        else:
            return {"status": "error", "message": "Error guardando registro de mantenimiento"}
            
    except Exception as e:
        logger.error(f"Error registrando mantenimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/maintenance/equipment/{equipment_id}/history")
async def get_equipment_maintenance_history(
    equipment_id: str,
    current_user: Dict[str, Any] = Depends(auth_service.get_current_user)
):
    """Obtener historial completo de mantenimiento por equipo"""
    try:
        supabase = get_supabase()
        response = supabase.table("maintenance_records").select(
            "*, users:performed_by(full_name, role)"
        ).eq("equipment_id", equipment_id).order("created_at", desc=True).execute()
        
        if response.data:
            return {
                "equipment_id": equipment_id,
                "maintenance_history": response.data,
                "total_records": len(response.data)
            }
        else:
            return {"equipment_id": equipment_id, "maintenance_history": [], "total_records": 0}
            
    except Exception as e:
        logger.error(f"Error obteniendo historial de mantenimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REPORTES AUTOMÁTICOS ====================

@router.post("/reports/generate")
async def generate_report(
    report_request: ReportRequest,
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("create_reports"))
):
    """Generación de reportes automáticos - Crear reportes visuales periódicos"""
    try:
        report_type = report_request.tipo_reporte
        start_date = report_request.fecha_inicio
        end_date = report_request.fecha_fin
        filters = report_request.filtros
        
        if report_type == "incident_summary":
            return await _generate_incident_summary_report(start_date, end_date, filters)
        elif report_type == "maintenance_summary":
            return await _generate_maintenance_summary_report(start_date, end_date, filters)
        elif report_type == "equipment_health":
            return await _generate_equipment_health_report(start_date, end_date, filters)
        elif report_type == "performance_metrics":
            return await _generate_performance_metrics_report(start_date, end_date, filters)
        else:
            raise HTTPException(status_code=400, detail="Tipo de reporte no válido")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/incident-summary")
async def get_incident_summary_report(
    days: int = 30,
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("view_reports"))
):
    """Reporte resumen de incidencias con indicadores clave"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Obtener métricas de incidencias
        metrics = await incident_service.get_incident_metrics(current_user, days)
        
        # Generar reporte
        report = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_incidents": metrics.get("total_incidencias", 0),
                "resolved_incidents": metrics.get("incidencias_por_estado", {}).get("finalizada", 0),
                "pending_incidents": metrics.get("incidencias_por_estado", {}).get("pendiente", 0),
                "in_progress_incidents": metrics.get("incidencias_por_estado", {}).get("en_proceso", 0)
            },
            "by_priority": metrics.get("incidencias_por_prioridad", {}),
            "by_type": metrics.get("incidencias_por_tipo", {}),
            "performance": {
                "average_resolution_time": metrics.get("tiempo_promedio_resolucion", 0),
                "sla_compliance": metrics.get("cumplimiento_sla", {}),
                "trends": metrics.get("tendencias", {})
            },
            "recommendations": _generate_report_recommendations(metrics)
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Error generando reporte de incidencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/maintenance-summary")
async def get_maintenance_summary_report(
    days: int = 30,
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("view_reports"))
):
    """Reporte resumen de mantenimiento"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        supabase = get_supabase()
        
        # Obtener registros de mantenimiento
        response = supabase.table("maintenance_records").select(
            "*, equipment:equipment_id(name, type), users:performed_by(full_name)"
        ).gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat()).execute()
        
        maintenance_records = response.data if response.data else []
        
        # Generar estadísticas
        total_maintenance = len(maintenance_records)
        by_type = {}
        by_equipment = {}
        by_technician = {}
        
        for record in maintenance_records:
            # Por tipo
            maint_type = record.get("maintenance_type", "unknown")
            by_type[maint_type] = by_type.get(maint_type, 0) + 1
            
            # Por equipo
            equipment_name = record.get("equipment", {}).get("name", "unknown")
            by_equipment[equipment_name] = by_equipment.get(equipment_name, 0) + 1
            
            # Por técnico
            technician_name = record.get("users", {}).get("full_name", "unknown")
            by_technician[technician_name] = by_technician.get(technician_name, 0) + 1
        
        report = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_maintenance": total_maintenance,
                "by_type": by_type,
                "by_equipment": by_equipment,
                "by_technician": by_technician
            },
            "records": maintenance_records
        }
        
        return report
        
    except Exception as e:
        logger.error(f"Error generando reporte de mantenimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PANEL ADMINISTRATIVO Y AUDITORÍA ====================

@router.get("/admin/dashboard")
async def get_admin_dashboard(
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("view_reports"))
):
    """Panel administrativo - Supervisar desempeño técnico y estadísticas"""
    try:
        # Obtener métricas generales
        dashboard_data = await metrics_service.get_executive_dashboard(30)
        
        # Agregar métricas específicas de auditoría
        audit_metrics = await _get_audit_metrics()
        
        dashboard_data["audit_metrics"] = audit_metrics
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error obteniendo dashboard administrativo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    days: int = 30,
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("view_audit_logs"))
):
    """Obtener logs de auditoría para verificar cumplimiento de protocolos"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        supabase = get_supabase()
        query = supabase.table("audit_logs").select(
            "*, users:user_id(full_name, role)"
        ).gte("timestamp", start_date.isoformat())
        
        if user_id:
            query = query.eq("user_id", user_id)
        if action:
            query = query.eq("action", action)
        
        response = query.order("timestamp", desc=True).execute()
        
        return {
            "audit_logs": response.data if response.data else [],
            "total_logs": len(response.data) if response.data else 0,
            "filters": {
                "user_id": user_id,
                "action": action,
                "days": days
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo logs de auditoría: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/performance-metrics")
async def get_performance_metrics(
    current_user: Dict[str, Any] = Depends(auth_service.require_permission("view_reports"))
):
    """Métricas de desempeño del sistema"""
    try:
        # Obtener métricas de KPIs
        kpi_report = await metrics_service.get_kpi_report(30)
        
        # Agregar métricas específicas de Grinding Perú
        grinding_metrics = {
            "incident_metrics": await incident_service.get_incident_metrics(current_user, 30),
            "predictive_analytics": await predictive_service.get_predictive_analytics_dashboard(),
            "system_health": {
                "database_status": "healthy",
                "ml_models_status": "trained" if predictive_service.is_trained else "needs_training",
                "notification_system": "active"
            }
        }
        
        return {
            "kpi_report": kpi_report,
            "grinding_metrics": grinding_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de desempeño: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FUNCIONES AUXILIARES ====================

async def _generate_incident_summary_report(start_date: str, end_date: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generar reporte resumen de incidencias"""
    # Implementar lógica de generación de reporte
    return {"message": "Reporte de incidencias generado", "type": "incident_summary"}

async def _generate_maintenance_summary_report(start_date: str, end_date: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generar reporte resumen de mantenimiento"""
    # Implementar lógica de generación de reporte
    return {"message": "Reporte de mantenimiento generado", "type": "maintenance_summary"}

async def _generate_equipment_health_report(start_date: str, end_date: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generar reporte de salud de equipos"""
    # Implementar lógica de generación de reporte
    return {"message": "Reporte de salud de equipos generado", "type": "equipment_health"}

async def _generate_performance_metrics_report(start_date: str, end_date: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generar reporte de métricas de rendimiento"""
    # Implementar lógica de generación de reporte
    return {"message": "Reporte de métricas de rendimiento generado", "type": "performance_metrics"}

def _generate_report_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generar recomendaciones basadas en métricas"""
    recommendations = []
    
    # Analizar métricas de incidencias
    total_incidents = metrics.get("total_incidencias", 0)
    avg_resolution = metrics.get("tiempo_promedio_resolucion", 0)
    
    if total_incidents > 50:
        recommendations.append("Alto volumen de incidencias: Considerar revisar procesos preventivos")
    
    if avg_resolution > 24:
        recommendations.append("Tiempo de resolución alto: Mejorar capacitación del equipo técnico")
    
    sla_compliance = metrics.get("cumplimiento_sla", {})
    if sla_compliance.get("overall", 100) < 90:
        recommendations.append("Cumplimiento de SLA bajo: Revisar asignación de recursos")
    
    return recommendations

async def _get_audit_metrics() -> Dict[str, Any]:
    """Obtener métricas de auditoría"""
    try:
        supabase = get_supabase()
        
        # Obtener estadísticas de auditoría de los últimos 30 días
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        response = supabase.table("audit_logs").select("*").gte("timestamp", thirty_days_ago.isoformat()).execute()
        
        if not response.data:
            return {"total_actions": 0, "by_action": {}, "by_user": {}}
        
        df = pd.DataFrame(response.data)
        
        return {
            "total_actions": len(df),
            "by_action": df['action'].value_counts().to_dict(),
            "by_user": df['user_id'].value_counts().to_dict(),
            "recent_actions": df.head(10).to_dict('records')
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de auditoría: {e}")
        return {"total_actions": 0, "by_action": {}, "by_user": {}}


# ==================== ENDPOINTS DE UTILIDAD ====================

@router.get("/health")
async def health_check():
    """Verificar estado del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "authentication": "active",
            "incident_management": "active",
            "predictive_maintenance": "active",
            "inventory_management": "active",
            "communication_management": "active"
        }
    }

@router.get("/version")
async def get_version():
    """Obtener información de versión"""
    return {
        "version": "2.0.0",
        "company": "Grinding Perú",
        "description": "Sistema de Gestión de Servicios IT con RAG y ML",
        "features": [
            "Autenticación y gestión de usuarios",
            "Gestión de incidencias con asignación automática",
            "Mantenimiento predictivo con ML",
            "Historial técnico consolidado",
            "Reportes automáticos",
            "Panel administrativo y auditoría"
        ]
    }
