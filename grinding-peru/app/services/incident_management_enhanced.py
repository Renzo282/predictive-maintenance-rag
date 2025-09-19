"""
Sistema de Gestión de Incidencias Mejorado para Grinding Perú
Incluye asignación automática, seguimiento y auditoría
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
from app.core.database import get_supabase
from app.services.rag_agent import RAGAgent
from app.services.notifications import NotificationService
from app.auth.authentication import auth_service

logger = logging.getLogger(__name__)


class IncidentStatus(Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class IncidentPriority(Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class IncidentType(Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    RED = "red"
    ELECTRICO = "electrico"
    MECANICO = "mecanico"
    OTROS = "otros"


class EnhancedIncidentManagementService:
    """Servicio mejorado de gestión de incidencias para Grinding Perú"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.rag_agent = RAGAgent()
        self.notification_service = NotificationService()
        
        # Configuración de SLA para Grinding Perú
        self.sla_hours = {
            IncidentPriority.CRITICA: 2,    # 2 horas
            IncidentPriority.ALTA: 8,       # 8 horas
            IncidentPriority.MEDIA: 24,     # 24 horas
            IncidentPriority.BAJA: 72       # 72 horas
        }
    
    async def create_incident(self, incident_data: Dict[str, Any], current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nueva incidencia con análisis automático"""
        try:
            # Validar datos requeridos
            required_fields = ['tipo_falla', 'equipo_involucrado', 'ubicacion', 'prioridad', 'descripcion']
            for field in required_fields:
                if field not in incident_data:
                    return {"status": "error", "message": f"Campo requerido faltante: {field}"}
            
            # Generar número de incidencia
            incident_number = await self._generate_incident_number()
            
            # Analizar incidencia con RAG para asignación automática
            analysis = await self._analyze_incident_for_assignment(incident_data)
            
            # Asignar técnico automáticamente
            assigned_technician = await self._assign_technician_automatically(incident_data, analysis)
            
            # Calcular SLA
            sla_deadline = self._calculate_sla_deadline(
                IncidentPriority(incident_data['prioridad']),
                datetime.now()
            )
            
            # Preparar datos de la incidencia
            incident_record = {
                "numero_incidencia": incident_number,
                "tipo_falla": incident_data['tipo_falla'],
                "equipo_involucrado": incident_data['equipo_involucrado'],
                "ubicacion": incident_data['ubicacion'],
                "prioridad": incident_data['prioridad'],
                "descripcion": incident_data['descripcion'],
                "estado": IncidentStatus.PENDIENTE.value,
                "reportado_por": current_user['id'],
                "asignado_a": assigned_technician['id'] if assigned_technician else None,
                "sla_deadline": sla_deadline.isoformat(),
                "fotos": incident_data.get('fotos', []),
                "archivos": incident_data.get('archivos', []),
                "analisis": analysis,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insertar en base de datos
            response = self.supabase.table("incidencias").insert(incident_record).execute()
            
            if response.data:
                incident_id = response.data[0]['id']
                
                # Crear alerta automática
                await self._create_incident_alert(incident_id, incident_record, assigned_technician)
                
                # Registrar en auditoría
                await self._log_audit_action(
                    user_id=current_user['id'],
                    action="create_incident",
                    resource_type="incident",
                    resource_id=incident_id,
                    details=f"Incidencia {incident_number} creada"
                )
                
                return {
                    "status": "success",
                    "incident_id": incident_id,
                    "numero_incidencia": incident_number,
                    "asignado_a": assigned_technician,
                    "sla_deadline": sla_deadline.isoformat(),
                    "analysis": analysis
                }
            else:
                return {"status": "error", "message": "Error al crear incidencia en la base de datos"}
                
        except Exception as e:
            logger.error(f"Error creando incidencia: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _generate_incident_number(self) -> str:
        """Generar número único de incidencia"""
        try:
            # Obtener el último número de incidencia
            response = self.supabase.table("incidencias").select("numero_incidencia").order(
                "created_at", desc=True
            ).limit(1).execute()
            
            if response.data and response.data[0]['numero_incidencia']:
                last_number = int(response.data[0]['numero_incidencia'].split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            return f"INC-{new_number:06d}"
            
        except Exception as e:
            logger.error(f"Error generando número de incidencia: {e}")
            return f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    async def _analyze_incident_for_assignment(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar incidencia para asignación automática usando RAG"""
        try:
            query = f"""
            Analiza la siguiente incidencia para Grinding Perú y determina:
            
            1. Especialidad técnica requerida
            2. Nivel de complejidad
            3. Tiempo estimado de resolución
            4. Recursos necesarios
            5. Técnico más adecuado basado en:
               - Especialidad técnica
               - Carga laboral actual
               - Disponibilidad
               - Experiencia previa con el tipo de falla
            
            Tipo de falla: {incident_data['tipo_falla']}
            Equipo involucrado: {incident_data['equipo_involucrado']}
            Ubicación: {incident_data['ubicacion']}
            Prioridad: {incident_data['prioridad']}
            Descripción: {incident_data['descripcion']}
            """
            
            # Usar RAG para análisis
            analysis_result = self.rag_agent.generate_prediction(
                "incident_assignment_analysis", query
            )
            
            # Procesar resultado del análisis
            analysis = {
                "required_specialty": self._extract_required_specialty(analysis_result.get("answer", "")),
                "complexity_level": self._extract_complexity_level(analysis_result.get("answer", "")),
                "estimated_resolution_time": self._extract_estimated_time(analysis_result.get("answer", "")),
                "required_resources": self._extract_required_resources(analysis_result.get("answer", "")),
                "confidence": analysis_result.get("confidence", 0.5)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando incidencia: {e}")
            return {"error": str(e)}
    
    def _extract_required_specialty(self, analysis_text: str) -> str:
        """Extraer especialidad técnica requerida"""
        analysis_lower = analysis_text.lower()
        
        specialties = {
            "hardware": ["hardware", "equipo", "servidor", "computadora", "disco", "memoria"],
            "software": ["software", "aplicación", "programa", "sistema operativo", "base de datos"],
            "red": ["red", "conexión", "internet", "wifi", "cable", "router", "switch"],
            "electrico": ["eléctrico", "electricidad", "energía", "voltaje", "corriente"],
            "mecanico": ["mecánico", "motor", "bomba", "compresor", "vibración"]
        }
        
        for specialty, keywords in specialties.items():
            if any(keyword in analysis_lower for keyword in keywords):
                return specialty
        
        return "otros"
    
    def _extract_complexity_level(self, analysis_text: str) -> str:
        """Extraer nivel de complejidad"""
        analysis_lower = analysis_text.lower()
        
        if any(keyword in analysis_lower for keyword in ["complejo", "difícil", "avanzado", "especializado"]):
            return "alta"
        elif any(keyword in analysis_lower for keyword in ["moderado", "intermedio", "estándar"]):
            return "media"
        else:
            return "baja"
    
    def _extract_estimated_time(self, analysis_text: str) -> int:
        """Extraer tiempo estimado de resolución en horas"""
        analysis_lower = analysis_text.lower()
        
        if "inmediato" in analysis_lower or "rápido" in analysis_lower:
            return 1
        elif "pocas horas" in analysis_lower:
            return 4
        elif "día" in analysis_lower:
            return 8
        elif "días" in analysis_lower:
            return 24
        else:
            return 8  # Default
    
    def _extract_required_resources(self, analysis_text: str) -> List[str]:
        """Extraer recursos necesarios"""
        resources = []
        analysis_lower = analysis_text.lower()
        
        if "herramientas" in analysis_lower:
            resources.append("Herramientas especializadas")
        if "repuestos" in analysis_lower:
            resources.append("Repuestos")
        if "equipo" in analysis_lower:
            resources.append("Equipo de medición")
        if "personal" in analysis_lower:
            resources.append("Personal adicional")
        
        return resources if resources else ["Herramientas básicas"]
    
    async def _assign_technician_automatically(self, incident_data: Dict[str, Any], analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Asignar técnico automáticamente basado en análisis"""
        try:
            required_specialty = analysis.get("required_specialty", "otros")
            complexity_level = analysis.get("complexity_level", "media")
            
            # Obtener técnicos disponibles con la especialidad requerida
            technicians = await self._get_available_technicians(required_specialty)
            
            if not technicians:
                logger.warning(f"No hay técnicos disponibles para especialidad: {required_specialty}")
                return None
            
            # Calcular score para cada técnico
            best_technician = None
            best_score = -1
            
            for technician in technicians:
                score = await self._calculate_technician_score(technician, incident_data, analysis)
                if score > best_score:
                    best_score = score
                    best_technician = technician
            
            if best_technician:
                # Actualizar carga laboral del técnico
                await self._update_technician_workload(best_technician['id'], 1)
                
                logger.info(f"Técnico asignado: {best_technician['full_name']} (Score: {best_score})")
            
            return best_technician
            
        except Exception as e:
            logger.error(f"Error asignando técnico: {e}")
            return None
    
    async def _get_available_technicians(self, specialty: str) -> List[Dict[str, Any]]:
        """Obtener técnicos disponibles con especialidad específica"""
        try:
            # Buscar técnicos activos con la especialidad requerida
            response = self.supabase.table("users").select("*").eq(
                "role", "tecnico"
            ).eq("is_active", True).execute()
            
            if not response.data:
                return []
            
            # Filtrar por especialidad (asumiendo que hay un campo specialty en users)
            technicians = []
            for tech in response.data:
                tech_specialty = tech.get("specialty", "otros")
                if tech_specialty == specialty or specialty == "otros":
                    technicians.append(tech)
            
            return technicians
            
        except Exception as e:
            logger.error(f"Error obteniendo técnicos: {e}")
            return []
    
    async def _calculate_technician_score(self, technician: Dict[str, Any], incident_data: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Calcular score del técnico para la asignación"""
        try:
            score = 0.0
            
            # Score por especialidad (40%)
            tech_specialty = technician.get("specialty", "otros")
            required_specialty = analysis.get("required_specialty", "otros")
            if tech_specialty == required_specialty:
                score += 40
            elif tech_specialty != "otros":
                score += 20
            
            # Score por carga laboral (30%)
            current_workload = technician.get("current_workload", 0)
            max_workload = technician.get("max_workload", 10)
            workload_ratio = current_workload / max_workload if max_workload > 0 else 0
            score += 30 * (1 - workload_ratio)  # Menos carga = más score
            
            # Score por experiencia (20%)
            experience_years = technician.get("experience_years", 0)
            if experience_years >= 5:
                score += 20
            elif experience_years >= 3:
                score += 15
            elif experience_years >= 1:
                score += 10
            
            # Score por ubicación (10%)
            tech_location = technician.get("location", "")
            incident_location = incident_data.get("ubicacion", "")
            if tech_location.lower() in incident_location.lower() or incident_location.lower() in tech_location.lower():
                score += 10
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculando score del técnico: {e}")
            return 0.0
    
    async def _update_technician_workload(self, technician_id: str, increment: int):
        """Actualizar carga laboral del técnico"""
        try:
            # Obtener carga actual
            response = self.supabase.table("users").select("current_workload").eq("id", technician_id).execute()
            
            if response.data:
                current_workload = response.data[0].get("current_workload", 0)
                new_workload = max(0, current_workload + increment)
                
                # Actualizar carga laboral
                self.supabase.table("users").update({
                    "current_workload": new_workload,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", technician_id).execute()
                
        except Exception as e:
            logger.error(f"Error actualizando carga laboral: {e}")
    
    def _calculate_sla_deadline(self, priority: IncidentPriority, created_at: datetime) -> datetime:
        """Calcular fecha límite de SLA"""
        sla_hours = self.sla_hours.get(priority, 24)
        return created_at + timedelta(hours=sla_hours)
    
    async def _create_incident_alert(self, incident_id: str, incident_data: Dict[str, Any], technician: Optional[Dict[str, Any]]):
        """Crear alerta automática para la incidencia"""
        try:
            alert_data = {
                "incident_id": incident_id,
                "title": f"Nueva Incidencia: {incident_data['numero_incidencia']}",
                "message": f"Se ha creado una nueva incidencia {incident_data['prioridad'].upper()}: {incident_data['descripcion']}",
                "priority": incident_data['prioridad'],
                "category": "incident_created",
                "recipients": self._get_alert_recipients(incident_data['prioridad'], technician),
                "sla_deadline": incident_data['sla_deadline']
            }
            
            await self.notification_service.send_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Error creando alerta de incidencia: {e}")
    
    def _get_alert_recipients(self, priority: str, technician: Optional[Dict[str, Any]]) -> List[str]:
        """Obtener destinatarios de alertas basado en prioridad"""
        recipients = {
            'critica': ['supervisor@grindingperu.com', 'gerencia@grindingperu.com'],
            'alta': ['supervisor@grindingperu.com'],
            'media': ['soporte@grindingperu.com'],
            'baja': ['soporte@grindingperu.com']
        }
        
        base_recipients = recipients.get(priority, ['soporte@grindingperu.com'])
        
        # Agregar técnico asignado si existe
        if technician and technician.get('email'):
            base_recipients.append(technician['email'])
        
        return base_recipients
    
    async def _log_audit_action(self, user_id: str, action: str, resource_type: str, resource_id: str, details: str):
        """Registrar acción en auditoría"""
        try:
            audit_record = {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "ip_address": "127.0.0.1"  # En producción, obtener IP real
            }
            
            self.supabase.table("audit_logs").insert(audit_record).execute()
            
        except Exception as e:
            logger.error(f"Error registrando auditoría: {e}")
    
    async def update_incident_status(self, incident_id: str, new_status: str, current_user: Dict[str, Any], 
                                   comments: str = "", fotos: List[str] = None, archivos: List[str] = None) -> Dict[str, Any]:
        """Actualizar estado de incidencia"""
        try:
            # Validar estado
            valid_statuses = [status.value for status in IncidentStatus]
            if new_status not in valid_statuses:
                return {"status": "error", "message": f"Estado inválido. Estados válidos: {valid_statuses}"}
            
            # Obtener incidencia actual
            response = self.supabase.table("incidencias").select("*").eq("id", incident_id).execute()
            
            if not response.data:
                return {"status": "error", "message": "Incidencia no encontrada"}
            
            incident = response.data[0]
            
            # Verificar permisos
            if not self._can_update_incident(incident, current_user):
                return {"status": "error", "message": "No tiene permisos para actualizar esta incidencia"}
            
            # Preparar datos de actualización
            update_data = {
                "estado": new_status,
                "updated_at": datetime.now().isoformat()
            }
            
            if new_status == IncidentStatus.FINALIZADA.value:
                update_data["fecha_finalizacion"] = datetime.now().isoformat()
            
            # Actualizar incidencia
            response = self.supabase.table("incidencias").update(update_data).eq("id", incident_id).execute()
            
            if response.data:
                # Agregar comentario si se proporciona
                if comments:
                    await self._add_incident_comment(incident_id, current_user['id'], comments, fotos, archivos)
                
                # Registrar en auditoría
                await self._log_audit_action(
                    user_id=current_user['id'],
                    action="update_incident_status",
                    resource_type="incident",
                    resource_id=incident_id,
                    details=f"Estado cambiado a {new_status}"
                )
                
                return {
                    "status": "success",
                    "incident_id": incident_id,
                    "new_status": new_status,
                    "updated_at": update_data["updated_at"]
                }
            else:
                return {"status": "error", "message": "Error actualizando incidencia"}
                
        except Exception as e:
            logger.error(f"Error actualizando estado de incidencia: {e}")
            return {"status": "error", "message": str(e)}
    
    def _can_update_incident(self, incident: Dict[str, Any], current_user: Dict[str, Any]) -> bool:
        """Verificar si el usuario puede actualizar la incidencia"""
        user_role = current_user.get("role")
        user_id = current_user.get("id")
        
        # Administradores y supervisores pueden actualizar cualquier incidencia
        if user_role in ["administrador", "supervisor"]:
            return True
        
        # Técnicos solo pueden actualizar incidencias asignadas a ellos
        if user_role == "tecnico":
            return incident.get("asignado_a") == user_id
        
        return False
    
    async def _add_incident_comment(self, incident_id: str, user_id: str, comment: str, 
                                  fotos: List[str] = None, archivos: List[str] = None):
        """Agregar comentario a incidencia"""
        try:
            comment_record = {
                "incident_id": incident_id,
                "user_id": user_id,
                "comment": comment,
                "fotos": fotos or [],
                "archivos": archivos or [],
                "created_at": datetime.now().isoformat()
            }
            
            self.supabase.table("incident_comments").insert(comment_record).execute()
            
        except Exception as e:
            logger.error(f"Error agregando comentario: {e}")
    
    async def get_incidents_by_user(self, current_user: Dict[str, Any], status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtener incidencias según el rol del usuario"""
        try:
            user_role = current_user.get("role")
            user_id = current_user.get("id")
            
            query = self.supabase.table("incidencias").select("*")
            
            # Filtrar según rol
            if user_role == "tecnico":
                query = query.eq("asignado_a", user_id)
            elif user_role == "supervisor":
                # Supervisores ven todas las incidencias de su departamento
                pass
            elif user_role == "administrador":
                # Administradores ven todas las incidencias
                pass
            else:
                # Usuarios regulares solo ven sus propias incidencias
                query = query.eq("reportado_por", user_id)
            
            # Filtrar por estado si se especifica
            if status:
                query = query.eq("estado", status)
            
            response = query.order("created_at", desc=True).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error obteniendo incidencias: {e}")
            return []
    
    async def get_incident_details(self, incident_id: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener detalles completos de una incidencia"""
        try:
            # Obtener incidencia
            response = self.supabase.table("incidencias").select("*").eq("id", incident_id).execute()
            
            if not response.data:
                return {"error": "Incidencia no encontrada"}
            
            incident = response.data[0]
            
            # Verificar permisos
            if not self._can_view_incident(incident, current_user):
                return {"error": "No tiene permisos para ver esta incidencia"}
            
            # Obtener comentarios
            comments_response = self.supabase.table("incident_comments").select(
                "*, users:user_id(full_name, role)"
            ).eq("incident_id", incident_id).order("created_at", desc=True).execute()
            
            # Obtener historial de cambios
            audit_response = self.supabase.table("audit_logs").select("*").eq(
                "resource_type", "incident"
            ).eq("resource_id", incident_id).order("timestamp", desc=True).execute()
            
            return {
                "incident": incident,
                "comments": comments_response.data if comments_response.data else [],
                "audit_history": audit_response.data if audit_response.data else []
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de incidencia: {e}")
            return {"error": str(e)}
    
    def _can_view_incident(self, incident: Dict[str, Any], current_user: Dict[str, Any]) -> bool:
        """Verificar si el usuario puede ver la incidencia"""
        user_role = current_user.get("role")
        user_id = current_user.get("id")
        
        # Administradores y supervisores pueden ver cualquier incidencia
        if user_role in ["administrador", "supervisor"]:
            return True
        
        # Técnicos pueden ver incidencias asignadas a ellos
        if user_role == "tecnico":
            return incident.get("asignado_a") == user_id
        
        # Usuarios regulares solo pueden ver sus propias incidencias
        return incident.get("reportado_por") == user_id
    
    async def get_incident_metrics(self, current_user: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
        """Obtener métricas de incidencias"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener incidencias según permisos del usuario
            incidents = await self.get_incidents_by_user(current_user)
            
            if not incidents:
                return {"error": "No hay datos de incidencias"}
            
            df = pd.DataFrame(incidents)
            
            # Calcular métricas
            metrics = {
                "total_incidencias": len(df),
                "incidencias_por_estado": df['estado'].value_counts().to_dict(),
                "incidencias_por_prioridad": df['prioridad'].value_counts().to_dict(),
                "incidencias_por_tipo": df['tipo_falla'].value_counts().to_dict(),
                "tiempo_promedio_resolucion": self._calculate_avg_resolution_time(df),
                "cumplimiento_sla": self._calculate_sla_compliance(df),
                "tendencias": self._analyze_trends(df)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculando métricas de incidencias: {e}")
            return {"error": str(e)}
    
    def _calculate_avg_resolution_time(self, df: pd.DataFrame) -> float:
        """Calcular tiempo promedio de resolución"""
        try:
            resolved_incidents = df[df['estado'] == IncidentStatus.FINALIZADA.value]
            
            if resolved_incidents.empty:
                return 0.0
            
            # Calcular tiempo de resolución
            resolved_incidents['created_at'] = pd.to_datetime(resolved_incidents['created_at'])
            resolved_incidents['fecha_finalizacion'] = pd.to_datetime(resolved_incidents['fecha_finalizacion'])
            
            resolved_incidents['resolution_hours'] = (
                resolved_incidents['fecha_finalizacion'] - resolved_incidents['created_at']
            ).dt.total_seconds() / 3600
            
            return round(resolved_incidents['resolution_hours'].mean(), 2)
            
        except Exception as e:
            logger.error(f"Error calculando tiempo promedio de resolución: {e}")
            return 0.0
    
    def _calculate_sla_compliance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular cumplimiento de SLA"""
        try:
            resolved_incidents = df[df['estado'] == IncidentStatus.FINALIZADA.value]
            
            if resolved_incidents.empty:
                return {"overall": 100.0, "by_priority": {}}
            
            # Calcular cumplimiento por prioridad
            compliance_by_priority = {}
            total_breaches = 0
            
            for priority in ['critica', 'alta', 'media', 'baja']:
                priority_incidents = resolved_incidents[resolved_incidents['prioridad'] == priority]
                
                if not priority_incidents.empty:
                    sla_target = self.sla_hours.get(IncidentPriority(priority), 24)
                    
                    # Calcular tiempo de resolución
                    priority_incidents['created_at'] = pd.to_datetime(priority_incidents['created_at'])
                    priority_incidents['fecha_finalizacion'] = pd.to_datetime(priority_incidents['fecha_finalizacion'])
                    
                    priority_incidents['resolution_hours'] = (
                        priority_incidents['fecha_finalizacion'] - priority_incidents['created_at']
                    ).dt.total_seconds() / 3600
                    
                    breaches = len(priority_incidents[priority_incidents['resolution_hours'] > sla_target])
                    total = len(priority_incidents)
                    compliance = ((total - breaches) / total) * 100 if total > 0 else 100
                    
                    compliance_by_priority[priority] = round(compliance, 2)
                    total_breaches += breaches
                else:
                    compliance_by_priority[priority] = 100.0
            
            # Cumplimiento general
            total_incidents = len(resolved_incidents)
            overall_compliance = ((total_incidents - total_breaches) / total_incidents) * 100 if total_incidents > 0 else 100
            
            return {
                "overall": round(overall_compliance, 2),
                "by_priority": compliance_by_priority,
                "breaches": total_breaches
            }
            
        except Exception as e:
            logger.error(f"Error calculando cumplimiento de SLA: {e}")
            return {"overall": 0, "by_priority": {}, "breaches": 0}
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar tendencias de incidencias"""
        try:
            if df.empty or len(df) < 7:
                return {"trend_direction": "stable", "peak_hours": [], "common_types": []}
            
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.date
            df['hour'] = df['created_at'].dt.hour
            
            # Tendencia general
            daily_counts = df.groupby('date').size()
            if len(daily_counts) >= 7:
                first_half = daily_counts[:len(daily_counts)//2].mean()
                second_half = daily_counts[len(daily_counts)//2:].mean()
                
                if second_half > first_half * 1.1:
                    trend_direction = "increasing"
                elif second_half < first_half * 0.9:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "stable"
            
            # Horas pico
            hourly_counts = df.groupby('hour').size()
            peak_hours = hourly_counts.nlargest(3).index.tolist()
            
            # Tipos más comunes
            common_types = df['tipo_falla'].value_counts().head(3).index.tolist()
            
            return {
                "trend_direction": trend_direction,
                "peak_hours": peak_hours,
                "common_types": common_types
            }
            
        except Exception as e:
            logger.error(f"Error analizando tendencias: {e}")
            return {"trend_direction": "stable", "peak_hours": [], "common_types": []}
