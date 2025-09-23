"""
Sistema Inteligente de Gestión de Incidencias
Para Grinding Perú - Automatización y Optimización
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class IncidentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"

class IncidentPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Incident:
    id: str
    title: str
    description: str
    equipment_id: str
    location: str
    priority: IncidentPriority
    status: IncidentStatus
    created_by: str
    assigned_technician: Optional[str]
    created_at: datetime
    updated_at: datetime
    estimated_duration: Optional[int]
    actual_duration: Optional[int]
    resolution_notes: Optional[str]
    attachments: List[str]
    tags: List[str]

class IntelligentIncidentManager:
    """
    Gestor inteligente de incidencias que incluye:
    - Asignación automática de técnicos
    - Clasificación inteligente de prioridades
    - Predicción de tiempo de resolución
    - Escalamiento automático
    - Análisis de tendencias
    """
    
    def __init__(self, db_connection, technician_recommender, predictive_system):
        self.db = db_connection
        self.technician_recommender = technician_recommender
        self.predictive_system = predictive_system
        
    def create_incident(
        self, 
        incident_data: Dict,
        auto_assign: bool = True
    ) -> Dict[str, Any]:
        """
        Crea una nueva incidencia con análisis inteligente
        
        Args:
            incident_data: Datos de la incidencia
            auto_assign: Si asignar técnico automáticamente
            
        Returns:
            Incidencia creada con análisis
        """
        try:
            # 1. Generar ID único
            incident_id = str(uuid.uuid4())
            
            # 2. Analizar y clasificar incidencia
            analysis = self._analyze_incident(incident_data)
            
            # 3. Determinar prioridad inteligente
            priority = self._determine_priority(incident_data, analysis)
            
            # 4. Estimar duración
            estimated_duration = self._estimate_resolution_time(
                incident_data, 
                analysis
            )
            
            # 5. Crear incidencia
            incident = Incident(
                id=incident_id,
                title=incident_data.get('title', ''),
                description=incident_data.get('description', ''),
                equipment_id=incident_data.get('equipment_id', ''),
                location=incident_data.get('location', ''),
                priority=priority,
                status=IncidentStatus.PENDING,
                created_by=incident_data.get('created_by', ''),
                assigned_technician=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                estimated_duration=estimated_duration,
                actual_duration=None,
                resolution_notes=None,
                attachments=incident_data.get('attachments', []),
                tags=analysis.get('suggested_tags', [])
            )
            
            # 6. Asignar técnico si se solicita
            if auto_assign:
                assignment_result = self._auto_assign_technician(incident)
                incident.assigned_technician = assignment_result.get('technician_id')
            
            # 7. Guardar en base de datos
            self._save_incident(incident)
            
            # 8. Enviar notificaciones
            self._send_incident_notifications(incident, analysis)
            
            return {
                "incident": self._incident_to_dict(incident),
                "analysis": analysis,
                "assignment": assignment_result if auto_assign else None,
                "recommendations": self._get_incident_recommendations(incident)
            }
            
        except Exception as e:
            logger.error(f"Error creando incidencia: {e}")
            return {"error": str(e)}
    
    def _analyze_incident(self, incident_data: Dict) -> Dict[str, Any]:
        """Analiza la incidencia para extraer información relevante"""
        try:
            analysis = {
                "suggested_tags": [],
                "risk_level": "medium",
                "complexity": "medium",
                "required_specialties": [],
                "estimated_parts": [],
                "safety_concerns": []
            }
            
            # Análisis de texto usando NLP básico
            description = incident_data.get('description', '').lower()
            title = incident_data.get('title', '').lower()
            full_text = f"{title} {description}"
            
            # Detectar tipo de falla
            failure_types = {
                'mecanica': ['motor', 'bomba', 'compresor', 'vibracion', 'ruido'],
                'electrica': ['corto', 'cable', 'voltaje', 'corriente', 'electrico'],
                'hidraulica': ['presion', 'fuga', 'aceite', 'hidraulico'],
                'neumatica': ['aire', 'neumatico', 'valvula', 'cilindro'],
                'electronica': ['sensor', 'controlador', 'plc', 'hmi', 'digital']
            }
            
            detected_types = []
            for failure_type, keywords in failure_types.items():
                if any(keyword in full_text for keyword in keywords):
                    detected_types.append(failure_type)
                    analysis["suggested_tags"].append(failure_type)
            
            # Detectar criticidad por palabras clave
            critical_keywords = ['parada', 'emergencia', 'critico', 'urgente', 'falla total']
            if any(keyword in full_text for keyword in critical_keywords):
                analysis["risk_level"] = "high"
                analysis["suggested_tags"].append("critico")
            
            # Detectar complejidad
            complex_keywords = ['complejo', 'multiple', 'sistema', 'integrado']
            if any(keyword in full_text for keyword in complex_keywords):
                analysis["complexity"] = "high"
            
            # Determinar especialidades requeridas
            specialty_mapping = {
                'mecanica': ['mecanico'],
                'electrica': ['electrico'],
                'hidraulica': ['hidraulico', 'mecanico'],
                'neumatica': ['neumatico', 'mecanico'],
                'electronica': ['electronico', 'electrico']
            }
            
            for failure_type in detected_types:
                if failure_type in specialty_mapping:
                    analysis["required_specialties"].extend(specialty_mapping[failure_type])
            
            # Detectar preocupaciones de seguridad
            safety_keywords = ['seguridad', 'riesgo', 'peligro', 'accidente']
            if any(keyword in full_text for keyword in safety_keywords):
                analysis["safety_concerns"].append("requiere_evaluacion_seguridad")
            
            # Limpiar duplicados
            analysis["required_specialties"] = list(set(analysis["required_specialties"]))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando incidencia: {e}")
            return {"suggested_tags": [], "risk_level": "medium", "complexity": "medium"}
    
    def _determine_priority(
        self, 
        incident_data: Dict, 
        analysis: Dict
    ) -> IncidentPriority:
        """Determina prioridad inteligente de la incidencia"""
        try:
            priority_score = 0
            
            # Factor 1: Nivel de riesgo
            risk_multiplier = {
                "low": 1,
                "medium": 2,
                "high": 3
            }
            priority_score += risk_multiplier.get(analysis.get("risk_level", "medium"), 2)
            
            # Factor 2: Equipo crítico
            equipment_criticality = incident_data.get('equipment_criticality', 'medium')
            criticality_multiplier = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "critical": 4
            }
            priority_score += criticality_multiplier.get(equipment_criticality, 2)
            
            # Factor 3: Impacto en producción
            production_impact = incident_data.get('production_impact', 'medium')
            impact_multiplier = {
                "none": 0,
                "low": 1,
                "medium": 2,
                "high": 3
            }
            priority_score += impact_multiplier.get(production_impact, 2)
            
            # Factor 4: Palabras clave críticas
            description = incident_data.get('description', '').lower()
            critical_words = ['parada', 'emergencia', 'critico', 'urgente']
            if any(word in description for word in critical_words):
                priority_score += 2
            
            # Determinar prioridad final
            if priority_score >= 8:
                return IncidentPriority.CRITICAL
            elif priority_score >= 6:
                return IncidentPriority.HIGH
            elif priority_score >= 4:
                return IncidentPriority.MEDIUM
            else:
                return IncidentPriority.LOW
                
        except Exception as e:
            logger.error(f"Error determinando prioridad: {e}")
            return IncidentPriority.MEDIUM
    
    def _estimate_resolution_time(
        self, 
        incident_data: Dict, 
        analysis: Dict
    ) -> int:
        """Estima tiempo de resolución en minutos"""
        try:
            base_time = 120  # 2 horas base
            
            # Ajustar por complejidad
            complexity_multiplier = {
                "low": 0.5,
                "medium": 1.0,
                "high": 2.0
            }
            base_time *= complexity_multiplier.get(analysis.get("complexity", "medium"), 1.0)
            
            # Ajustar por tipo de falla
            failure_type = analysis.get("suggested_tags", [])
            if "electronica" in failure_type:
                base_time *= 1.5  # Más tiempo para electrónica
            elif "mecanica" in failure_type:
                base_time *= 1.2  # Tiempo medio para mecánica
            
            # Ajustar por especialidades requeridas
            specialties_count = len(analysis.get("required_specialties", []))
            if specialties_count > 1:
                base_time *= 1.3  # Más tiempo si requiere múltiples especialistas
            
            return int(base_time)
            
        except Exception as e:
            logger.error(f"Error estimando tiempo de resolución: {e}")
            return 120
    
    def _auto_assign_technician(self, incident: Incident) -> Dict[str, Any]:
        """Asigna técnico automáticamente usando el sistema de recomendación"""
        try:
            # Preparar datos para recomendación
            incident_data = {
                "equipment_type": incident.equipment_id,
                "failure_type": incident.description,
                "location": incident.location,
                "priority": incident.priority.value,
                "required_specialties": []  # Se determinará en el análisis
            }
            
            # Obtener recomendaciones
            recommendations = self.technician_recommender.get_technician_recommendations(
                incident_data, 
                limit=3
            )
            
            if not recommendations:
                return {
                    "success": False,
                    "message": "No hay técnicos disponibles",
                    "technician_id": None
                }
            
            # Seleccionar mejor técnico
            best_technician = recommendations[0]
            
            return {
                "success": True,
                "technician_id": best_technician['technician']['id'],
                "technician_name": best_technician['technician']['name'],
                "score": best_technician['score'],
                "reasons": best_technician['reasons'],
                "alternatives": recommendations[1:] if len(recommendations) > 1 else []
            }
            
        except Exception as e:
            logger.error(f"Error asignando técnico: {e}")
            return {
                "success": False,
                "message": str(e),
                "technician_id": None
            }
    
    def _save_incident(self, incident: Incident):
        """Guarda la incidencia en la base de datos"""
        try:
            query = """
            INSERT INTO incidents (
                id, title, description, equipment_id, location, priority,
                status, created_by, assigned_technician_id, created_at, updated_at,
                estimated_duration, resolution_notes, attachments, tags
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            values = (
                incident.id,
                incident.title,
                incident.description,
                incident.equipment_id,
                incident.location,
                incident.priority.value,
                incident.status.value,
                incident.created_by,
                incident.assigned_technician,
                incident.created_at,
                incident.updated_at,
                incident.estimated_duration,
                incident.resolution_notes,
                json.dumps(incident.attachments),
                json.dumps(incident.tags)
            )
            
            self.db.execute_query(query, values)
            logger.info(f"Incidencia {incident.id} guardada correctamente")
            
        except Exception as e:
            logger.error(f"Error guardando incidencia: {e}")
            raise
    
    def _send_incident_notifications(self, incident: Incident, analysis: Dict):
        """Envía notificaciones sobre la nueva incidencia"""
        try:
            # Notificar al técnico asignado
            if incident.assigned_technician:
                self._notify_technician(incident)
            
            # Notificar a supervisores si es crítica
            if incident.priority == IncidentPriority.CRITICAL:
                self._notify_supervisors(incident)
            
            # Notificar a administradores si es de alta prioridad
            if incident.priority in [IncidentPriority.HIGH, IncidentPriority.CRITICAL]:
                self._notify_administrators(incident)
            
            logger.info(f"Notificaciones enviadas para incidencia {incident.id}")
            
        except Exception as e:
            logger.error(f"Error enviando notificaciones: {e}")
    
    def _notify_technician(self, incident: Incident):
        """Notifica al técnico asignado"""
        # Implementar notificación (email, SMS, push, etc.)
        pass
    
    def _notify_supervisors(self, incident: Incident):
        """Notifica a supervisores"""
        # Implementar notificación
        pass
    
    def _notify_administrators(self, incident: Incident):
        """Notifica a administradores"""
        # Implementar notificación
        pass
    
    def _get_incident_recommendations(self, incident: Incident) -> List[Dict]:
        """Obtiene recomendaciones para la incidencia"""
        try:
            recommendations = []
            
            # Recomendación de herramientas
            if "mecanica" in incident.tags:
                recommendations.append({
                    "type": "tools",
                    "suggestion": "Herramientas de medición de vibraciones",
                    "priority": "high"
                })
            
            # Recomendación de repuestos
            if "hidraulica" in incident.tags:
                recommendations.append({
                    "type": "parts",
                    "suggestion": "Verificar disponibilidad de sellos hidráulicos",
                    "priority": "medium"
                })
            
            # Recomendación de seguridad
            if incident.priority == IncidentPriority.CRITICAL:
                recommendations.append({
                    "type": "safety",
                    "suggestion": "Procedimiento de seguridad especial requerido",
                    "priority": "high"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones: {e}")
            return []
    
    def _incident_to_dict(self, incident: Incident) -> Dict:
        """Convierte incidente a diccionario"""
        return {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "equipment_id": incident.equipment_id,
            "location": incident.location,
            "priority": incident.priority.value,
            "status": incident.status.value,
            "created_by": incident.created_by,
            "assigned_technician": incident.assigned_technician,
            "created_at": incident.created_at.isoformat(),
            "updated_at": incident.updated_at.isoformat(),
            "estimated_duration": incident.estimated_duration,
            "actual_duration": incident.actual_duration,
            "resolution_notes": incident.resolution_notes,
            "attachments": incident.attachments,
            "tags": incident.tags
        }
    
    def update_incident_status(
        self, 
        incident_id: str, 
        new_status: IncidentStatus,
        notes: Optional[str] = None,
        actual_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """Actualiza el estado de una incidencia"""
        try:
            # Actualizar en base de datos
            query = """
            UPDATE incidents 
            SET status = %s, updated_at = %s, resolution_notes = %s, actual_duration = %s
            WHERE id = %s
            """
            
            self.db.execute_query(query, (
                new_status.value,
                datetime.now(),
                notes,
                actual_duration,
                incident_id
            ))
            
            # Si se completa, generar análisis de rendimiento
            if new_status == IncidentStatus.COMPLETED:
                self._generate_performance_analysis(incident_id)
            
            return {
                "success": True,
                "incident_id": incident_id,
                "new_status": new_status.value,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error actualizando estado: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_performance_analysis(self, incident_id: str):
        """Genera análisis de rendimiento para incidencia completada"""
        try:
            # Obtener datos de la incidencia
            query = """
            SELECT * FROM incidents WHERE id = %s
            """
            incident_data = self.db.execute_query(query, (incident_id,))
            
            if not incident_data:
                return
            
            incident = incident_data[0]
            
            # Calcular métricas de rendimiento
            estimated = incident.get('estimated_duration', 0)
            actual = incident.get('actual_duration', 0)
            
            if estimated > 0 and actual > 0:
                efficiency = min(1.0, estimated / actual)
                
                # Guardar análisis
                analysis_query = """
                INSERT INTO incident_performance (
                    incident_id, estimated_duration, actual_duration, 
                    efficiency, completed_at
                ) VALUES (%s, %s, %s, %s, %s)
                """
                
                self.db.execute_query(analysis_query, (
                    incident_id, estimated, actual, efficiency, datetime.now()
                ))
            
        except Exception as e:
            logger.error(f"Error generando análisis de rendimiento: {e}")
    
    def get_incident_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene análisis de incidencias"""
        try:
            # Consulta de métricas
            query = """
            SELECT 
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN priority = 'critical' THEN 1 END) as critical,
                AVG(actual_duration) as avg_resolution_time,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '%s days' THEN 1 END) as recent_incidents
            FROM incidents 
            WHERE created_at >= NOW() - INTERVAL '%s days'
            """
            
            result = self.db.execute_query(query, (days, days))
            
            if not result:
                return {"error": "No se encontraron datos"}
            
            metrics = result[0]
            
            # Calcular tasas
            completion_rate = (metrics['completed'] / metrics['total_incidents']) * 100 if metrics['total_incidents'] > 0 else 0
            
            return {
                "period_days": days,
                "total_incidents": metrics['total_incidents'],
                "completed_incidents": metrics['completed'],
                "critical_incidents": metrics['critical'],
                "completion_rate": round(completion_rate, 2),
                "avg_resolution_time": round(metrics['avg_resolution_time'] or 0, 2),
                "recent_incidents": metrics['recent_incidents']
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo análisis: {e}")
            return {"error": str(e)}
    
    def get_technician_workload(self, technician_id: str) -> Dict[str, Any]:
        """Obtiene carga de trabajo de un técnico"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                AVG(actual_duration) as avg_resolution_time,
                COUNT(CASE WHEN priority = 'critical' THEN 1 END) as critical_count
            FROM incidents 
            WHERE assigned_technician_id = %s
                AND created_at >= NOW() - INTERVAL '30 days'
            """
            
            result = self.db.execute_query(query, (technician_id,))
            
            if not result:
                return {"error": "Técnico no encontrado"}
            
            workload = result[0]
            
            # Calcular score de carga
            workload_score = self._calculate_workload_score(workload)
            
            return {
                "technician_id": technician_id,
                "total_incidents": workload['total_incidents'],
                "pending_incidents": workload['pending'],
                "in_progress_incidents": workload['in_progress'],
                "avg_resolution_time": round(workload['avg_resolution_time'] or 0, 2),
                "critical_incidents": workload['critical_count'],
                "workload_score": workload_score,
                "status": self._get_workload_status(workload_score)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo carga de trabajo: {e}")
            return {"error": str(e)}
    
    def _calculate_workload_score(self, workload: Dict) -> float:
        """Calcula score de carga de trabajo"""
        try:
            score = 0
            
            # Factor 1: Incidencias pendientes
            pending = workload.get('pending', 0)
            if pending > 5:
                score += 0.4
            elif pending > 3:
                score += 0.3
            elif pending > 1:
                score += 0.2
            
            # Factor 2: Incidencias en progreso
            in_progress = workload.get('in_progress', 0)
            if in_progress > 3:
                score += 0.3
            elif in_progress > 2:
                score += 0.2
            elif in_progress > 0:
                score += 0.1
            
            # Factor 3: Incidencias críticas
            critical = workload.get('critical_count', 0)
            if critical > 2:
                score += 0.3
            elif critical > 0:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculando score de carga: {e}")
            return 0.5
    
    def _get_workload_status(self, score: float) -> str:
        """Determina estado de carga de trabajo"""
        if score >= 0.8:
            return "overloaded"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
