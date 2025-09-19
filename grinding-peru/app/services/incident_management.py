"""
Módulo de Gestión de Incidentes para Grinding Perú
Alineado con ISO/IEC 20000
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
from app.core.database import get_supabase
from app.services.rag_agent import RAGAgent
from app.services.notifications import NotificationService

logger = logging.getLogger(__name__)


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Category(Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"


class IncidentManagementService:
    """Servicio de Gestión de Incidentes para Grinding Perú"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.rag_agent = RAGAgent()
        self.notification_service = NotificationService()
        
        # SLA Configuration for Grinding Perú
        self.sla_hours = {
            Priority.CRITICAL: 4,    # 4 horas
            Priority.HIGH: 8,        # 8 horas
            Priority.MEDIUM: 24,     # 24 horas
            Priority.LOW: 72         # 72 horas
        }
    
    def create_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo incidente con análisis automático"""
        try:
            # Validar datos requeridos
            required_fields = ['title', 'description', 'category', 'priority', 'reported_by']
            for field in required_fields:
                if field not in incident_data:
                    return {"status": "error", "message": f"Campo requerido faltante: {field}"}
            
            # Generar número de incidente
            incident_number = self._generate_incident_number()
            
            # Analizar incidente con RAG
            analysis = self._analyze_incident(incident_data)
            
            # Calcular SLA
            sla_deadline = self._calculate_sla_deadline(
                Priority(incident_data['priority']),
                incident_data.get('created_at', datetime.now())
            )
            
            # Preparar datos del incidente
            incident_record = {
                "incident_number": incident_number,
                "title": incident_data['title'],
                "description": incident_data['description'],
                "category": incident_data['category'],
                "priority": incident_data['priority'],
                "status": Status.NEW.value,
                "reported_by": incident_data['reported_by'],
                "assigned_to": None,
                "sla_deadline": sla_deadline.isoformat(),
                "affected_services": incident_data.get('affected_services', []),
                "tags": incident_data.get('tags', []),
                "analysis": analysis,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insertar en base de datos
            response = self.supabase.table("incidents").insert(incident_record).execute()
            
            if response.data:
                incident_id = response.data[0]['id']
                
                # Crear alerta automática
                await self._create_incident_alert(incident_id, incident_record)
                
                # Buscar incidentes similares
                similar_incidents = await self._find_similar_incidents(incident_record)
                
                return {
                    "status": "success",
                    "incident_id": incident_id,
                    "incident_number": incident_number,
                    "sla_deadline": sla_deadline.isoformat(),
                    "analysis": analysis,
                    "similar_incidents": similar_incidents
                }
            else:
                return {"status": "error", "message": "Error al crear incidente en la base de datos"}
                
        except Exception as e:
            logger.error(f"Error al crear incidente: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_incident_number(self) -> str:
        """Generar número único de incidente"""
        try:
            # Obtener el último número de incidente
            response = self.supabase.table("incidents").select("incident_number").order(
                "created_at", desc=True
            ).limit(1).execute()
            
            if response.data and response.data[0]['incident_number']:
                last_number = int(response.data[0]['incident_number'].split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            return f"INC-{new_number:06d}"
            
        except Exception as e:
            logger.error(f"Error generando número de incidente: {e}")
            return f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _analyze_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar incidente usando RAG para clasificación automática"""
        try:
            # Crear query para análisis
            query = f"""
            Analiza el siguiente incidente y proporciona:
            1. Clasificación automática de categoría y prioridad
            2. Posibles causas raíz
            3. Soluciones recomendadas
            4. Servicios afectados
            5. Impacto estimado
            
            Incidente:
            Título: {incident_data['title']}
            Descripción: {incident_data['description']}
            Categoría reportada: {incident_data['category']}
            Prioridad reportada: {incident_data['priority']}
            """
            
            # Usar RAG para análisis
            analysis_result = self.rag_agent.generate_prediction(
                "incident_analysis", query
            )
            
            # Procesar resultado del análisis
            analysis = {
                "auto_classification": {
                    "suggested_category": self._extract_category(analysis_result.get("answer", "")),
                    "suggested_priority": self._extract_priority(analysis_result.get("answer", "")),
                    "confidence": analysis_result.get("confidence", 0.5)
                },
                "root_causes": self._extract_root_causes(analysis_result.get("answer", "")),
                "recommended_solutions": self._extract_solutions(analysis_result.get("answer", "")),
                "affected_services": self._extract_affected_services(analysis_result.get("answer", "")),
                "impact_assessment": self._assess_impact(incident_data),
                "estimated_resolution_time": self._estimate_resolution_time(incident_data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando incidente: {e}")
            return {"error": str(e)}
    
    def _extract_category(self, analysis_text: str) -> str:
        """Extraer categoría sugerida del análisis"""
        categories = {
            "hardware": ["hardware", "equipo", "servidor", "computadora", "disco", "memoria"],
            "software": ["software", "aplicación", "programa", "sistema operativo"],
            "network": ["red", "conexión", "internet", "wifi", "cable", "router"],
            "application": ["aplicación", "portal", "web", "base de datos"],
            "infrastructure": ["infraestructura", "servidor", "datacenter", "energía"],
            "security": ["seguridad", "acceso", "autenticación", "permisos", "virus"]
        }
        
        analysis_lower = analysis_text.lower()
        for category, keywords in categories.items():
            if any(keyword in analysis_lower for keyword in keywords):
                return category
        
        return "infrastructure"  # Default
    
    def _extract_priority(self, analysis_text: str) -> str:
        """Extraer prioridad sugerida del análisis"""
        priority_keywords = {
            "critical": ["crítico", "urgente", "emergencia", "sistema caído", "no funciona"],
            "high": ["alto", "importante", "afecta producción", "múltiples usuarios"],
            "medium": ["medio", "moderado", "algunos usuarios", "funcionalidad limitada"],
            "low": ["bajo", "menor", "cosmético", "mejora", "sugerencia"]
        }
        
        analysis_lower = analysis_text.lower()
        for priority, keywords in priority_keywords.items():
            if any(keyword in analysis_lower for keyword in keywords):
                return priority
        
        return "medium"  # Default
    
    def _extract_root_causes(self, analysis_text: str) -> List[str]:
        """Extraer posibles causas raíz"""
        # Implementar lógica de extracción de causas raíz
        # Por ahora, retornar causas genéricas basadas en palabras clave
        causes = []
        analysis_lower = analysis_text.lower()
        
        if "configuración" in analysis_lower or "config" in analysis_lower:
            causes.append("Problema de configuración")
        if "conexión" in analysis_lower or "red" in analysis_lower:
            causes.append("Problema de conectividad")
        if "permisos" in analysis_lower or "acceso" in analysis_lower:
            causes.append("Problema de permisos")
        if "recursos" in analysis_lower or "memoria" in analysis_lower:
            causes.append("Falta de recursos del sistema")
        
        return causes if causes else ["Causa por determinar"]
    
    def _extract_solutions(self, analysis_text: str) -> List[str]:
        """Extraer soluciones recomendadas"""
        solutions = []
        analysis_lower = analysis_text.lower()
        
        if "reiniciar" in analysis_lower:
            solutions.append("Reiniciar el servicio o sistema")
        if "verificar" in analysis_lower:
            solutions.append("Verificar configuración")
        if "actualizar" in analysis_lower:
            solutions.append("Actualizar software o drivers")
        if "reemplazar" in analysis_lower:
            solutions.append("Reemplazar componente")
        
        return solutions if solutions else ["Investigar más a fondo"]
    
    def _extract_affected_services(self, analysis_text: str) -> List[str]:
        """Extraer servicios afectados"""
        # Implementar lógica de extracción de servicios
        return ["Servicio por determinar"]
    
    def _assess_impact(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluar impacto del incidente"""
        priority = incident_data.get('priority', 'medium')
        affected_services = incident_data.get('affected_services', [])
        
        impact_levels = {
            'critical': 'Alto - Múltiples servicios críticos afectados',
            'high': 'Medio-Alto - Servicios importantes afectados',
            'medium': 'Medio - Servicios secundarios afectados',
            'low': 'Bajo - Impacto mínimo'
        }
        
        return {
            "level": priority,
            "description": impact_levels.get(priority, 'Desconocido'),
            "affected_services_count": len(affected_services),
            "business_impact": self._calculate_business_impact(priority, affected_services)
        }
    
    def _calculate_business_impact(self, priority: str, affected_services: List[str]) -> str:
        """Calcular impacto en el negocio"""
        if priority == 'critical':
            return 'Crítico - Operaciones detenidas'
        elif priority == 'high':
            return 'Alto - Operaciones limitadas'
        elif priority == 'medium':
            return 'Medio - Algunas funciones afectadas'
        else:
            return 'Bajo - Impacto mínimo'
    
    def _estimate_resolution_time(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimar tiempo de resolución"""
        priority = incident_data.get('priority', 'medium')
        category = incident_data.get('category', 'infrastructure')
        
        # Tiempos estimados basados en prioridad y categoría
        base_times = {
            'critical': {'min': 1, 'max': 4},
            'high': {'min': 2, 'max': 8},
            'medium': {'min': 4, 'max': 24},
            'low': {'min': 8, 'max': 72}
        }
        
        category_multipliers = {
            'hardware': 1.5,
            'software': 1.0,
            'network': 1.2,
            'application': 1.3,
            'infrastructure': 1.4,
            'security': 1.6
        }
        
        base_time = base_times.get(priority, base_times['medium'])
        multiplier = category_multipliers.get(category, 1.0)
        
        return {
            "estimated_min_hours": base_time['min'] * multiplier,
            "estimated_max_hours": base_time['max'] * multiplier,
            "confidence": 0.7
        }
    
    def _calculate_sla_deadline(self, priority: Priority, created_at: datetime) -> datetime:
        """Calcular fecha límite de SLA"""
        sla_hours = self.sla_hours.get(priority, 24)
        return created_at + timedelta(hours=sla_hours)
    
    async def _create_incident_alert(self, incident_id: str, incident_data: Dict[str, Any]):
        """Crear alerta automática para el incidente"""
        try:
            alert_data = {
                "incident_id": incident_id,
                "title": f"Nuevo Incidente: {incident_data['incident_number']}",
                "message": f"Se ha creado un nuevo incidente {incident_data['priority'].upper()}: {incident_data['title']}",
                "priority": incident_data['priority'],
                "category": "incident_created",
                "recipients": self._get_alert_recipients(incident_data['priority']),
                "sla_deadline": incident_data['sla_deadline']
            }
            
            await self.notification_service.send_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Error creando alerta de incidente: {e}")
    
    def _get_alert_recipients(self, priority: str) -> List[str]:
        """Obtener destinatarios de alertas basado en prioridad"""
        recipients = {
            'critical': ['nivel3@grindingperu.com', 'gerencia@grindingperu.com'],
            'high': ['nivel2@grindingperu.com', 'nivel3@grindingperu.com'],
            'medium': ['nivel1@grindingperu.com', 'nivel2@grindingperu.com'],
            'low': ['nivel1@grindingperu.com']
        }
        return recipients.get(priority, ['nivel1@grindingperu.com'])
    
    async def _find_similar_incidents(self, incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Buscar incidentes similares usando RAG"""
        try:
            query = f"""
            Busca incidentes similares a:
            Título: {incident_data['title']}
            Descripción: {incident_data['description']}
            Categoría: {incident_data['category']}
            """
            
            # Usar RAG para buscar incidentes similares
            similar_incidents = self.rag_agent.generate_prediction(
                "similar_incidents", query
            )
            
            # Por ahora, retornar lista vacía
            # En implementación completa, se consultaría la base de datos
            return []
            
        except Exception as e:
            logger.error(f"Error buscando incidentes similares: {e}")
            return []
    
    def get_incident_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Obtener métricas de incidentes para Grinding Perú"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener datos de incidentes
            response = self.supabase.table("incidents").select("*").gte(
                "created_at", start_date.isoformat()
            ).execute()
            
            if not response.data:
                return {"error": "No hay datos de incidentes"}
            
            df = pd.DataFrame(response.data)
            
            # Calcular métricas
            metrics = {
                "total_incidents": len(df),
                "incidents_by_priority": df['priority'].value_counts().to_dict(),
                "incidents_by_category": df['category'].value_counts().to_dict(),
                "incidents_by_status": df['status'].value_counts().to_dict(),
                "sla_compliance": self._calculate_sla_compliance(df),
                "average_resolution_time": self._calculate_avg_resolution_time(df),
                "trend_analysis": self._analyze_trends(df)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculando métricas de incidentes: {e}")
            return {"error": str(e)}
    
    def _calculate_sla_compliance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular cumplimiento de SLA"""
        # Implementar lógica de cálculo de SLA
        return {
            "overall_compliance": 0.85,
            "by_priority": {
                "critical": 0.90,
                "high": 0.85,
                "medium": 0.80,
                "low": 0.75
            }
        }
    
    def _calculate_avg_resolution_time(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular tiempo promedio de resolución"""
        # Implementar lógica de cálculo de tiempo de resolución
        return {
            "overall_hours": 12.5,
            "by_priority": {
                "critical": 3.2,
                "high": 6.8,
                "medium": 18.5,
                "low": 48.0
            }
        }
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar tendencias de incidentes"""
        # Implementar análisis de tendencias
        return {
            "trend_direction": "decreasing",
            "peak_hours": [9, 10, 14, 15],
            "common_categories": ["hardware", "network"],
            "resolution_improvement": 0.15
        }
