"""
Módulo de Métricas de Gestión de Servicios para Grinding Perú
Alineado con ISO/IEC 20000
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.core.database import get_supabase
from app.services.rag_agent import RAGAgent

logger = logging.getLogger(__name__)


class ServiceMetricsService:
    """Servicio de Métricas de Gestión de Servicios para Grinding Perú"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.rag_agent = RAGAgent()
        
        # SLA Targets para Grinding Perú (ISO/IEC 20000)
        self.sla_targets = {
            "incident_resolution": {
                "critical": 4,    # horas
                "high": 8,        # horas
                "medium": 24,     # horas
                "low": 72         # horas
            },
            "incident_response": {
                "critical": 0.25,  # horas (15 minutos)
                "high": 0.5,       # horas (30 minutos)
                "medium": 2,       # horas
                "low": 8           # horas
            },
            "change_approval": {
                "emergency": 2,    # horas
                "standard": 24,    # horas
                "normal": 72       # horas
            },
            "problem_resolution": {
                "critical": 24,    # horas
                "high": 72,        # horas
                "medium": 168,     # horas (1 semana)
                "low": 720         # horas (1 mes)
            }
        }
        
        # KPIs críticos para Grinding Perú
        self.kpi_targets = {
            "availability": 99.5,      # %
            "sla_compliance": 95.0,    # %
            "customer_satisfaction": 4.0,  # escala 1-5
            "first_call_resolution": 70.0,  # %
            "mean_time_to_resolution": 8.0,  # horas
            "incident_volume": 100,    # por mes
            "change_success_rate": 95.0,  # %
            "problem_recurrence": 5.0   # %
        }
    
    def get_executive_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """Obtener dashboard ejecutivo con métricas clave"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener datos de todas las tablas
            incidents_data = self._get_incidents_data(start_date)
            changes_data = self._get_changes_data(start_date)
            problems_data = self._get_problems_data(start_date)
            inventory_data = self._get_inventory_data()
            communications_data = self._get_communications_data(start_date)
            
            # Calcular métricas principales
            dashboard = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.now().isoformat(),
                    "days": days
                },
                "service_availability": self._calculate_availability(incidents_data),
                "sla_compliance": self._calculate_sla_compliance(incidents_data),
                "incident_metrics": self._calculate_incident_metrics(incidents_data),
                "change_metrics": self._calculate_change_metrics(changes_data),
                "problem_metrics": self._calculate_problem_metrics(problems_data),
                "inventory_metrics": self._calculate_inventory_metrics(inventory_data),
                "communication_metrics": self._calculate_communication_metrics(communications_data),
                "customer_satisfaction": self._calculate_customer_satisfaction(incidents_data),
                "cost_metrics": self._calculate_cost_metrics(incidents_data, changes_data),
                "trend_analysis": self._analyze_trends(incidents_data, changes_data, problems_data),
                "recommendations": self._generate_recommendations(incidents_data, changes_data, problems_data)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generando dashboard ejecutivo: {e}")
            return {"error": str(e)}
    
    def _get_incidents_data(self, start_date: datetime) -> pd.DataFrame:
        """Obtener datos de incidentes"""
        try:
            response = self.supabase.table("incidents").select("*").gte(
                "created_at", start_date.isoformat()
            ).execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de incidentes: {e}")
            return pd.DataFrame()
    
    def _get_changes_data(self, start_date: datetime) -> pd.DataFrame:
        """Obtener datos de cambios"""
        try:
            response = self.supabase.table("changes").select("*").gte(
                "created_at", start_date.isoformat()
            ).execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de cambios: {e}")
            return pd.DataFrame()
    
    def _get_problems_data(self, start_date: datetime) -> pd.DataFrame:
        """Obtener datos de problemas"""
        try:
            response = self.supabase.table("problems").select("*").gte(
                "created_at", start_date.isoformat()
            ).execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de problemas: {e}")
            return pd.DataFrame()
    
    def _get_inventory_data(self) -> pd.DataFrame:
        """Obtener datos de inventario"""
        try:
            response = self.supabase.table("inventory_items").select("*").execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de inventario: {e}")
            return pd.DataFrame()
    
    def _get_communications_data(self, start_date: datetime) -> pd.DataFrame:
        """Obtener datos de comunicaciones"""
        try:
            response = self.supabase.table("communications").select("*").gte(
                "created_at", start_date.isoformat()
            ).execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de comunicaciones: {e}")
            return pd.DataFrame()
    
    def _calculate_availability(self, incidents_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular disponibilidad del servicio"""
        try:
            if incidents_df.empty:
                return {"overall": 100.0, "by_priority": {}, "downtime_hours": 0}
            
            # Calcular tiempo de inactividad por incidente
            incidents_df['created_at'] = pd.to_datetime(incidents_df['created_at'])
            incidents_df['resolved_at'] = pd.to_datetime(incidents_df['resolved_at'])
            
            # Filtrar incidentes resueltos
            resolved_incidents = incidents_df[incidents_df['status'] == 'resolved'].copy()
            
            if resolved_incidents.empty:
                return {"overall": 100.0, "by_priority": {}, "downtime_hours": 0}
            
            # Calcular tiempo de inactividad
            resolved_incidents['downtime_hours'] = (
                resolved_incidents['resolved_at'] - resolved_incidents['created_at']
            ).dt.total_seconds() / 3600
            
            total_downtime = resolved_incidents['downtime_hours'].sum()
            total_hours = 24 * 30  # 30 días
            availability = max(0, (total_hours - total_downtime) / total_hours * 100)
            
            # Disponibilidad por prioridad
            availability_by_priority = {}
            for priority in ['critical', 'high', 'medium', 'low']:
                priority_incidents = resolved_incidents[resolved_incidents['priority'] == priority]
                if not priority_incidents.empty:
                    priority_downtime = priority_incidents['downtime_hours'].sum()
                    priority_availability = max(0, (total_hours - priority_downtime) / total_hours * 100)
                    availability_by_priority[priority] = round(priority_availability, 2)
                else:
                    availability_by_priority[priority] = 100.0
            
            return {
                "overall": round(availability, 2),
                "by_priority": availability_by_priority,
                "downtime_hours": round(total_downtime, 2),
                "target": self.kpi_targets["availability"]
            }
            
        except Exception as e:
            logger.error(f"Error calculando disponibilidad: {e}")
            return {"overall": 0, "by_priority": {}, "downtime_hours": 0}
    
    def _calculate_sla_compliance(self, incidents_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular cumplimiento de SLA"""
        try:
            if incidents_df.empty:
                return {"overall": 100.0, "by_priority": {}, "breaches": 0}
            
            incidents_df['created_at'] = pd.to_datetime(incidents_df['created_at'])
            incidents_df['resolved_at'] = pd.to_datetime(incidents_df['resolved_at'])
            
            # Filtrar incidentes resueltos
            resolved_incidents = incidents_df[incidents_df['status'] == 'resolved'].copy()
            
            if resolved_incidents.empty:
                return {"overall": 100.0, "by_priority": {}, "breaches": 0}
            
            # Calcular tiempo de resolución
            resolved_incidents['resolution_hours'] = (
                resolved_incidents['resolved_at'] - resolved_incidents['created_at']
            ).dt.total_seconds() / 3600
            
            # Verificar cumplimiento de SLA
            sla_breaches = 0
            compliance_by_priority = {}
            
            for priority in ['critical', 'high', 'medium', 'low']:
                priority_incidents = resolved_incidents[resolved_incidents['priority'] == priority]
                
                if not priority_incidents.empty:
                    sla_target = self.sla_targets["incident_resolution"][priority]
                    breaches = len(priority_incidents[priority_incidents['resolution_hours'] > sla_target])
                    total = len(priority_incidents)
                    compliance = ((total - breaches) / total) * 100 if total > 0 else 100
                    
                    compliance_by_priority[priority] = round(compliance, 2)
                    sla_breaches += breaches
                else:
                    compliance_by_priority[priority] = 100.0
            
            total_incidents = len(resolved_incidents)
            overall_compliance = ((total_incidents - sla_breaches) / total_incidents) * 100 if total_incidents > 0 else 100
            
            return {
                "overall": round(overall_compliance, 2),
                "by_priority": compliance_by_priority,
                "breaches": sla_breaches,
                "target": self.kpi_targets["sla_compliance"]
            }
            
        except Exception as e:
            logger.error(f"Error calculando cumplimiento de SLA: {e}")
            return {"overall": 0, "by_priority": {}, "breaches": 0}
    
    def _calculate_incident_metrics(self, incidents_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de incidentes"""
        try:
            if incidents_df.empty:
                return {
                    "total_incidents": 0,
                    "resolved_incidents": 0,
                    "open_incidents": 0,
                    "average_resolution_time": 0,
                    "by_priority": {},
                    "by_category": {},
                    "trend": "stable"
                }
            
            incidents_df['created_at'] = pd.to_datetime(incidents_df['created_at'])
            incidents_df['resolved_at'] = pd.to_datetime(incidents_df['resolved_at'])
            
            # Métricas básicas
            total_incidents = len(incidents_df)
            resolved_incidents = len(incidents_df[incidents_df['status'] == 'resolved'])
            open_incidents = total_incidents - resolved_incidents
            
            # Tiempo promedio de resolución
            resolved_df = incidents_df[incidents_df['status'] == 'resolved'].copy()
            if not resolved_df.empty:
                resolved_df['resolution_hours'] = (
                    resolved_df['resolved_at'] - resolved_df['created_at']
                ).dt.total_seconds() / 3600
                avg_resolution_time = resolved_df['resolution_hours'].mean()
            else:
                avg_resolution_time = 0
            
            # Por prioridad
            by_priority = incidents_df['priority'].value_counts().to_dict()
            
            # Por categoría
            by_category = incidents_df['category'].value_counts().to_dict()
            
            # Tendencia (comparar con período anterior)
            trend = self._calculate_incident_trend(incidents_df)
            
            return {
                "total_incidents": total_incidents,
                "resolved_incidents": resolved_incidents,
                "open_incidents": open_incidents,
                "average_resolution_time": round(avg_resolution_time, 2),
                "by_priority": by_priority,
                "by_category": by_category,
                "trend": trend
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas de incidentes: {e}")
            return {"error": str(e)}
    
    def _calculate_change_metrics(self, changes_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de cambios"""
        try:
            if changes_df.empty:
                return {
                    "total_changes": 0,
                    "successful_changes": 0,
                    "failed_changes": 0,
                    "success_rate": 0,
                    "by_type": {},
                    "average_implementation_time": 0
                }
            
            # Métricas básicas
            total_changes = len(changes_df)
            successful_changes = len(changes_df[changes_df['status'] == 'completed'])
            failed_changes = len(changes_df[changes_df['status'] == 'failed'])
            success_rate = (successful_changes / total_changes) * 100 if total_changes > 0 else 0
            
            # Por tipo
            by_type = changes_df['type'].value_counts().to_dict()
            
            # Tiempo promedio de implementación
            changes_df['created_at'] = pd.to_datetime(changes_df['created_at'])
            changes_df['completed_at'] = pd.to_datetime(changes_df['completed_at'])
            
            completed_changes = changes_df[changes_df['status'] == 'completed'].copy()
            if not completed_changes.empty:
                completed_changes['implementation_hours'] = (
                    completed_changes['completed_at'] - completed_changes['created_at']
                ).dt.total_seconds() / 3600
                avg_implementation_time = completed_changes['implementation_hours'].mean()
            else:
                avg_implementation_time = 0
            
            return {
                "total_changes": total_changes,
                "successful_changes": successful_changes,
                "failed_changes": failed_changes,
                "success_rate": round(success_rate, 2),
                "by_type": by_type,
                "average_implementation_time": round(avg_implementation_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas de cambios: {e}")
            return {"error": str(e)}
    
    def _calculate_problem_metrics(self, problems_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de problemas"""
        try:
            if problems_df.empty:
                return {
                    "total_problems": 0,
                    "resolved_problems": 0,
                    "open_problems": 0,
                    "recurrence_rate": 0,
                    "by_priority": {},
                    "root_causes": {}
                }
            
            # Métricas básicas
            total_problems = len(problems_df)
            resolved_problems = len(problems_df[problems_df['status'] == 'resolved'])
            open_problems = total_problems - resolved_problems
            
            # Tasa de recurrencia
            recurrence_rate = self._calculate_recurrence_rate(problems_df)
            
            # Por prioridad
            by_priority = problems_df['priority'].value_counts().to_dict()
            
            # Causas raíz
            root_causes = problems_df['root_cause'].value_counts().to_dict()
            
            return {
                "total_problems": total_problems,
                "resolved_problems": resolved_problems,
                "open_problems": open_problems,
                "recurrence_rate": round(recurrence_rate, 2),
                "by_priority": by_priority,
                "root_causes": root_causes
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas de problemas: {e}")
            return {"error": str(e)}
    
    def _calculate_inventory_metrics(self, inventory_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de inventario"""
        try:
            if inventory_df.empty:
                return {
                    "total_items": 0,
                    "low_stock_items": 0,
                    "out_of_stock_items": 0,
                    "total_value": 0,
                    "by_criticality": {},
                    "reorder_recommendations": 0
                }
            
            # Métricas básicas
            total_items = len(inventory_df)
            low_stock_items = len(inventory_df[inventory_df['current_stock'] < inventory_df['min_stock']])
            out_of_stock_items = len(inventory_df[inventory_df['current_stock'] <= 0])
            
            # Valor total del inventario
            inventory_df['item_value'] = inventory_df['current_stock'] * inventory_df['unit_cost']
            total_value = inventory_df['item_value'].sum()
            
            # Por criticidad
            by_criticality = inventory_df['criticality'].value_counts().to_dict()
            
            # Recomendaciones de reorden
            reorder_recommendations = len(inventory_df[inventory_df['current_stock'] <= inventory_df['reorder_point']])
            
            return {
                "total_items": total_items,
                "low_stock_items": low_stock_items,
                "out_of_stock_items": out_of_stock_items,
                "total_value": round(total_value, 2),
                "by_criticality": by_criticality,
                "reorder_recommendations": reorder_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas de inventario: {e}")
            return {"error": str(e)}
    
    def _calculate_communication_metrics(self, communications_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de comunicaciones"""
        try:
            if communications_df.empty:
                return {
                    "total_communications": 0,
                    "by_type": {},
                    "by_channel": {},
                    "response_time_avg": 0,
                    "escalation_rate": 0
                }
            
            # Métricas básicas
            total_communications = len(communications_df)
            
            # Por tipo
            by_type = communications_df['type'].value_counts().to_dict()
            
            # Por canal (necesitaría procesar el campo channels)
            by_channel = {}
            for channels in communications_df['channels']:
                if isinstance(channels, list):
                    for channel in channels:
                        by_channel[channel] = by_channel.get(channel, 0) + 1
            
            # Tiempo promedio de respuesta (simulado)
            response_time_avg = 25  # minutos
            
            # Tasa de escalamiento (simulado)
            escalation_rate = 0.15  # 15%
            
            return {
                "total_communications": total_communications,
                "by_type": by_type,
                "by_channel": by_channel,
                "response_time_avg": response_time_avg,
                "escalation_rate": escalation_rate
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas de comunicaciones: {e}")
            return {"error": str(e)}
    
    def _calculate_customer_satisfaction(self, incidents_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular satisfacción del cliente"""
        try:
            # En un sistema real, esto vendría de encuestas de satisfacción
            # Por ahora, simulamos basado en métricas de incidentes
            
            if incidents_df.empty:
                return {"overall": 4.0, "by_priority": {}, "trend": "stable"}
            
            # Simular satisfacción basada en tiempo de resolución
            resolved_incidents = incidents_df[incidents_df['status'] == 'resolved']
            
            if resolved_incidents.empty:
                return {"overall": 4.0, "by_priority": {}, "trend": "stable"}
            
            # Calcular satisfacción por prioridad
            satisfaction_by_priority = {}
            for priority in ['critical', 'high', 'medium', 'low']:
                priority_incidents = resolved_incidents[resolved_incidents['priority'] == priority]
                if not priority_incidents.empty:
                    # Simular satisfacción basada en cumplimiento de SLA
                    sla_target = self.sla_targets["incident_resolution"][priority]
                    avg_resolution = priority_incidents['resolution_hours'].mean() if 'resolution_hours' in priority_incidents.columns else sla_target
                    
                    if avg_resolution <= sla_target:
                        satisfaction = 4.5
                    elif avg_resolution <= sla_target * 1.5:
                        satisfaction = 4.0
                    elif avg_resolution <= sla_target * 2:
                        satisfaction = 3.5
                    else:
                        satisfaction = 3.0
                    
                    satisfaction_by_priority[priority] = round(satisfaction, 1)
                else:
                    satisfaction_by_priority[priority] = 4.0
            
            # Satisfacción general
            overall_satisfaction = np.mean(list(satisfaction_by_priority.values()))
            
            return {
                "overall": round(overall_satisfaction, 1),
                "by_priority": satisfaction_by_priority,
                "trend": "improving" if overall_satisfaction >= 4.0 else "declining"
            }
            
        except Exception as e:
            logger.error(f"Error calculando satisfacción del cliente: {e}")
            return {"overall": 4.0, "by_priority": {}, "trend": "stable"}
    
    def _calculate_cost_metrics(self, incidents_df: pd.DataFrame, changes_df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de costos"""
        try:
            # Costos de incidentes (tiempo de resolución * costo por hora)
            incident_cost_per_hour = 50  # USD por hora
            change_cost_per_hour = 75    # USD por hora
            
            incident_costs = 0
            if not incidents_df.empty:
                resolved_incidents = incidents_df[incidents_df['status'] == 'resolved']
                if not resolved_incidents.empty:
                    resolved_incidents['resolution_hours'] = (
                        pd.to_datetime(resolved_incidents['resolved_at']) - 
                        pd.to_datetime(resolved_incidents['created_at'])
                    ).dt.total_seconds() / 3600
                    incident_costs = resolved_incidents['resolution_hours'].sum() * incident_cost_per_hour
            
            change_costs = 0
            if not changes_df.empty:
                completed_changes = changes_df[changes_df['status'] == 'completed']
                if not completed_changes.empty:
                    completed_changes['implementation_hours'] = (
                        pd.to_datetime(completed_changes['completed_at']) - 
                        pd.to_datetime(completed_changes['created_at'])
                    ).dt.total_seconds() / 3600
                    change_costs = completed_changes['implementation_hours'].sum() * change_cost_per_hour
            
            total_costs = incident_costs + change_costs
            
            return {
                "incident_costs": round(incident_costs, 2),
                "change_costs": round(change_costs, 2),
                "total_costs": round(total_costs, 2),
                "cost_per_incident": round(incident_costs / len(incidents_df), 2) if len(incidents_df) > 0 else 0,
                "cost_per_change": round(change_costs / len(changes_df), 2) if len(changes_df) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas de costos: {e}")
            return {"error": str(e)}
    
    def _analyze_trends(self, incidents_df: pd.DataFrame, changes_df: pd.DataFrame, problems_df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar tendencias generales"""
        try:
            trends = {
                "incident_trend": self._calculate_incident_trend(incidents_df),
                "change_trend": self._calculate_change_trend(changes_df),
                "problem_trend": self._calculate_problem_trend(problems_df),
                "overall_health": "good"  # Por defecto
            }
            
            # Determinar salud general del servicio
            if trends["incident_trend"] == "increasing" or trends["problem_trend"] == "increasing":
                trends["overall_health"] = "concerning"
            elif trends["incident_trend"] == "decreasing" and trends["problem_trend"] == "decreasing":
                trends["overall_health"] = "excellent"
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analizando tendencias: {e}")
            return {"error": str(e)}
    
    def _calculate_incident_trend(self, incidents_df: pd.DataFrame) -> str:
        """Calcular tendencia de incidentes"""
        try:
            if incidents_df.empty or len(incidents_df) < 7:
                return "stable"
            
            incidents_df['created_at'] = pd.to_datetime(incidents_df['created_at'])
            incidents_df['date'] = incidents_df['created_at'].dt.date
            
            # Agrupar por día
            daily_counts = incidents_df.groupby('date').size()
            
            if len(daily_counts) < 7:
                return "stable"
            
            # Calcular tendencia simple
            first_half = daily_counts[:len(daily_counts)//2].mean()
            second_half = daily_counts[len(daily_counts)//2:].mean()
            
            if second_half > first_half * 1.1:
                return "increasing"
            elif second_half < first_half * 0.9:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculando tendencia de incidentes: {e}")
            return "stable"
    
    def _calculate_change_trend(self, changes_df: pd.DataFrame) -> str:
        """Calcular tendencia de cambios"""
        # Implementar lógica similar a incidentes
        return "stable"
    
    def _calculate_problem_trend(self, problems_df: pd.DataFrame) -> str:
        """Calcular tendencia de problemas"""
        # Implementar lógica similar a incidentes
        return "stable"
    
    def _calculate_recurrence_rate(self, problems_df: pd.DataFrame) -> float:
        """Calcular tasa de recurrencia de problemas"""
        try:
            if problems_df.empty:
                return 0.0
            
            # Simular tasa de recurrencia
            return 5.0  # 5%
            
        except Exception as e:
            logger.error(f"Error calculando tasa de recurrencia: {e}")
            return 0.0
    
    def _generate_recommendations(self, incidents_df: pd.DataFrame, changes_df: pd.DataFrame, problems_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generar recomendaciones basadas en métricas"""
        try:
            recommendations = []
            
            # Analizar incidentes
            if not incidents_df.empty:
                resolved_incidents = incidents_df[incidents_df['status'] == 'resolved']
                if not resolved_incidents.empty:
                    avg_resolution = resolved_incidents['resolution_hours'].mean()
                    
                    if avg_resolution > 24:
                        recommendations.append({
                            "category": "incident_management",
                            "priority": "high",
                            "title": "Optimizar tiempo de resolución de incidentes",
                            "description": f"El tiempo promedio de resolución es {avg_resolution:.1f} horas, excediendo el objetivo de 8 horas.",
                            "actions": [
                                "Implementar automatización para incidentes comunes",
                                "Mejorar documentación de procedimientos",
                                "Capacitar al equipo en resolución rápida"
                            ]
                        })
            
            # Analizar cambios
            if not changes_df.empty:
                failed_changes = changes_df[changes_df['status'] == 'failed']
                failure_rate = len(failed_changes) / len(changes_df) * 100
                
                if failure_rate > 10:
                    recommendations.append({
                        "category": "change_management",
                        "priority": "medium",
                        "title": "Reducir tasa de fallos en cambios",
                        "description": f"La tasa de fallos en cambios es {failure_rate:.1f}%, excediendo el objetivo del 5%.",
                        "actions": [
                            "Mejorar pruebas antes de implementación",
                            "Implementar rollback automático",
                            "Revisar proceso de aprobación de cambios"
                        ]
                    })
            
            # Recomendaciones generales
            recommendations.append({
                "category": "general",
                "priority": "low",
                "title": "Implementar monitoreo proactivo",
                "description": "Considerar implementar herramientas de monitoreo proactivo para detectar problemas antes de que afecten a los usuarios.",
                "actions": [
                            "Configurar alertas automáticas",
                            "Implementar dashboards en tiempo real",
                            "Establecer métricas de rendimiento"
                        ]
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            return []
    
    def get_kpi_report(self, days: int = 30) -> Dict[str, Any]:
        """Generar reporte de KPIs para Grinding Perú"""
        try:
            dashboard = self.get_executive_dashboard(days)
            
            kpi_report = {
                "period": dashboard["period"],
                "kpis": {
                    "availability": {
                        "current": dashboard["service_availability"]["overall"],
                        "target": self.kpi_targets["availability"],
                        "status": "met" if dashboard["service_availability"]["overall"] >= self.kpi_targets["availability"] else "not_met"
                    },
                    "sla_compliance": {
                        "current": dashboard["sla_compliance"]["overall"],
                        "target": self.kpi_targets["sla_compliance"],
                        "status": "met" if dashboard["sla_compliance"]["overall"] >= self.kpi_targets["sla_compliance"] else "not_met"
                    },
                    "customer_satisfaction": {
                        "current": dashboard["customer_satisfaction"]["overall"],
                        "target": self.kpi_targets["customer_satisfaction"],
                        "status": "met" if dashboard["customer_satisfaction"]["overall"] >= self.kpi_targets["customer_satisfaction"] else "not_met"
                    },
                    "mean_time_to_resolution": {
                        "current": dashboard["incident_metrics"]["average_resolution_time"],
                        "target": self.kpi_targets["mean_time_to_resolution"],
                        "status": "met" if dashboard["incident_metrics"]["average_resolution_time"] <= self.kpi_targets["mean_time_to_resolution"] else "not_met"
                    }
                },
                "summary": {
                    "total_kpis": 4,
                    "met_kpis": sum(1 for kpi in dashboard["kpis"].values() if kpi.get("status") == "met"),
                    "overall_status": "excellent" if all(kpi.get("status") == "met" for kpi in dashboard["kpis"].values()) else "needs_improvement"
                }
            }
            
            return kpi_report
            
        except Exception as e:
            logger.error(f"Error generando reporte de KPIs: {e}")
            return {"error": str(e)}
