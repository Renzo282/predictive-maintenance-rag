"""
Módulo de Gestión de Comunicaciones para Grinding Perú
Formalización de canales de comunicación según ISO/IEC 20000
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


class CommunicationChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    PHONE = "phone"
    TICKET_SYSTEM = "ticket_system"
    PORTAL = "portal"


class CommunicationType(Enum):
    INCIDENT = "incident"
    CHANGE = "change"
    PROBLEM = "problem"
    REQUEST = "request"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


class CommunicationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CommunicationManagementService:
    """Servicio de Gestión de Comunicaciones para Grinding Perú"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.rag_agent = RAGAgent()
        self.notification_service = NotificationService()
        
        # Configuración de canales de comunicación para Grinding Perú
        self.channel_config = {
            CommunicationChannel.EMAIL: {
                "enabled": True,
                "response_time_minutes": 15,
                "escalation_time_minutes": 60,
                "recipients": {
                    "critical": ["soporte@grindingperu.com", "gerencia@grindingperu.com"],
                    "high": ["soporte@grindingperu.com", "nivel2@grindingperu.com"],
                    "medium": ["soporte@grindingperu.com"],
                    "low": ["soporte@grindingperu.com"]
                }
            },
            CommunicationChannel.SLACK: {
                "enabled": True,
                "response_time_minutes": 5,
                "escalation_time_minutes": 30,
                "channels": {
                    "critical": "#soporte-critico",
                    "high": "#soporte-alto",
                    "medium": "#soporte-medio",
                    "low": "#soporte-general"
                }
            },
            CommunicationChannel.TEAMS: {
                "enabled": True,
                "response_time_minutes": 10,
                "escalation_time_minutes": 45,
                "channels": {
                    "critical": "Soporte Crítico",
                    "high": "Soporte Alto",
                    "medium": "Soporte Medio",
                    "low": "Soporte General"
                }
            },
            CommunicationChannel.PHONE: {
                "enabled": True,
                "response_time_minutes": 2,
                "escalation_time_minutes": 15,
                "numbers": {
                    "critical": "+51-1-XXX-XXXX",
                    "high": "+51-1-XXX-XXXX",
                    "medium": "+51-1-XXX-XXXX",
                    "low": "+51-1-XXX-XXXX"
                }
            }
        }
    
    def create_communication_workflow(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear workflow de comunicación formalizado"""
        try:
            # Validar datos requeridos
            required_fields = ['type', 'priority', 'subject', 'message', 'sender']
            for field in required_fields:
                if field not in communication_data:
                    return {"status": "error", "message": f"Campo requerido faltante: {field}"}
            
            # Analizar comunicación con RAG
            analysis = self._analyze_communication(communication_data)
            
            # Determinar canales apropiados
            recommended_channels = self._determine_communication_channels(
                communication_data['type'],
                communication_data['priority'],
                analysis
            )
            
            # Crear registro de comunicación
            communication_record = {
                "communication_id": self._generate_communication_id(),
                "type": communication_data['type'],
                "priority": communication_data['priority'],
                "subject": communication_data['subject'],
                "message": communication_data['message'],
                "sender": communication_data['sender'],
                "recipients": communication_data.get('recipients', []),
                "channels": recommended_channels,
                "status": "pending",
                "analysis": analysis,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insertar en base de datos
            response = self.supabase.table("communications").insert(communication_record).execute()
            
            if response.data:
                communication_id = response.data[0]['id']
                
                # Enviar comunicación a través de canales recomendados
                send_results = await self._send_communication(
                    communication_id, communication_record, recommended_channels
                )
                
                return {
                    "status": "success",
                    "communication_id": communication_id,
                    "analysis": analysis,
                    "recommended_channels": recommended_channels,
                    "send_results": send_results
                }
            else:
                return {"status": "error", "message": "Error al crear comunicación en la base de datos"}
                
        except Exception as e:
            logger.error(f"Error creando workflow de comunicación: {e}")
            return {"status": "error", "message": str(e)}
    
    def _analyze_communication(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar comunicación usando RAG para clasificación y routing"""
        try:
            query = f"""
            Analiza la siguiente comunicación para Grinding Perú y determina:
            
            1. Tipo de comunicación (incident, change, problem, request, maintenance, emergency)
            2. Prioridad correcta (critical, high, medium, low)
            3. Canales de comunicación más apropiados
            4. Destinatarios recomendados
            5. Tiempo de respuesta esperado
            6. Acciones requeridas
            7. Escalamiento necesario
            
            Tipo reportado: {communication_data['type']}
            Prioridad reportada: {communication_data['priority']}
            Asunto: {communication_data['subject']}
            Mensaje: {communication_data['message']}
            Remitente: {communication_data['sender']}
            """
            
            # Usar RAG para análisis
            analysis_result = self.rag_agent.generate_prediction(
                "communication_analysis", query
            )
            
            # Procesar resultado del análisis
            analysis = {
                "suggested_type": self._extract_communication_type(analysis_result.get("answer", "")),
                "suggested_priority": self._extract_priority(analysis_result.get("answer", "")),
                "recommended_channels": self._extract_channels(analysis_result.get("answer", "")),
                "recommended_recipients": self._extract_recipients(analysis_result.get("answer", "")),
                "response_time_expectation": self._extract_response_time(analysis_result.get("answer", "")),
                "required_actions": self._extract_actions(analysis_result.get("answer", "")),
                "escalation_needed": self._extract_escalation(analysis_result.get("answer", "")),
                "confidence": analysis_result.get("confidence", 0.5)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando comunicación: {e}")
            return {"error": str(e)}
    
    def _extract_communication_type(self, analysis_text: str) -> str:
        """Extraer tipo de comunicación sugerido"""
        analysis_lower = analysis_text.lower()
        
        if any(keyword in analysis_lower for keyword in ["incidente", "incident", "falla", "error"]):
            return CommunicationType.INCIDENT.value
        elif any(keyword in analysis_lower for keyword in ["cambio", "change", "modificación", "actualización"]):
            return CommunicationType.CHANGE.value
        elif any(keyword in analysis_lower for keyword in ["problema", "problem", "recurrente", "patrón"]):
            return CommunicationType.PROBLEM.value
        elif any(keyword in analysis_lower for keyword in ["solicitud", "request", "pedido", "requerimiento"]):
            return CommunicationType.REQUEST.value
        elif any(keyword in analysis_lower for keyword in ["mantenimiento", "maintenance", "reparación"]):
            return CommunicationType.MAINTENANCE.value
        elif any(keyword in analysis_lower for keyword in ["emergencia", "emergency", "urgente", "crítico"]):
            return CommunicationType.EMERGENCY.value
        else:
            return CommunicationType.REQUEST.value  # Default
    
    def _extract_priority(self, analysis_text: str) -> str:
        """Extraer prioridad sugerida"""
        analysis_lower = analysis_text.lower()
        
        if any(keyword in analysis_lower for keyword in ["crítico", "critical", "emergencia", "urgente"]):
            return CommunicationPriority.CRITICAL.value
        elif any(keyword in analysis_lower for keyword in ["alto", "high", "importante", "significativo"]):
            return CommunicationPriority.HIGH.value
        elif any(keyword in analysis_lower for keyword in ["bajo", "low", "mínimo", "opcional"]):
            return CommunicationPriority.LOW.value
        else:
            return CommunicationPriority.MEDIUM.value  # Default
    
    def _extract_channels(self, analysis_text: str) -> List[str]:
        """Extraer canales de comunicación recomendados"""
        channels = []
        analysis_lower = analysis_text.lower()
        
        if "email" in analysis_lower or "correo" in analysis_lower:
            channels.append(CommunicationChannel.EMAIL.value)
        if "slack" in analysis_lower:
            channels.append(CommunicationChannel.SLACK.value)
        if "teams" in analysis_lower:
            channels.append(CommunicationChannel.TEAMS.value)
        if "teléfono" in analysis_lower or "phone" in analysis_lower or "llamada" in analysis_lower:
            channels.append(CommunicationChannel.PHONE.value)
        
        # Default channels based on priority
        if not channels:
            channels = [CommunicationChannel.EMAIL.value, CommunicationChannel.SLACK.value]
        
        return channels
    
    def _extract_recipients(self, analysis_text: str) -> List[str]:
        """Extraer destinatarios recomendados"""
        recipients = []
        analysis_lower = analysis_text.lower()
        
        if "gerencia" in analysis_lower or "management" in analysis_lower:
            recipients.append("gerencia@grindingperu.com")
        if "soporte" in analysis_lower or "support" in analysis_lower:
            recipients.append("soporte@grindingperu.com")
        if "compras" in analysis_lower or "purchasing" in analysis_lower:
            recipients.append("compras@grindingperu.com")
        if "almacén" in analysis_lower or "warehouse" in analysis_lower:
            recipients.append("almacen@grindingperu.com")
        
        return recipients if recipients else ["soporte@grindingperu.com"]
    
    def _extract_response_time(self, analysis_text: str) -> int:
        """Extraer tiempo de respuesta esperado en minutos"""
        analysis_lower = analysis_text.lower()
        
        if "inmediato" in analysis_lower or "urgente" in analysis_lower:
            return 5
        elif "rápido" in analysis_lower or "pronto" in analysis_lower:
            return 15
        elif "normal" in analysis_lower or "estándar" in analysis_lower:
            return 60
        else:
            return 30  # Default
    
    def _extract_actions(self, analysis_text: str) -> List[str]:
        """Extraer acciones requeridas"""
        actions = []
        analysis_lower = analysis_text.lower()
        
        if "investigar" in analysis_lower:
            actions.append("Investigar el problema")
        if "escalar" in analysis_lower:
            actions.append("Escalar a nivel superior")
        if "contactar" in analysis_lower:
            actions.append("Contactar al usuario")
        if "documentar" in analysis_lower:
            actions.append("Documentar el caso")
        
        return actions if actions else ["Revisar y responder"]
    
    def _extract_escalation(self, analysis_text: str) -> bool:
        """Determinar si se requiere escalamiento"""
        analysis_lower = analysis_text.lower()
        
        escalation_keywords = [
            "escalar", "escalation", "gerencia", "management", 
            "supervisor", "nivel superior", "crítico", "urgente"
        ]
        
        return any(keyword in analysis_lower for keyword in escalation_keywords)
    
    def _determine_communication_channels(self, comm_type: str, priority: str, analysis: Dict[str, Any]) -> List[str]:
        """Determinar canales de comunicación apropiados"""
        channels = []
        
        # Canales basados en prioridad
        if priority == CommunicationPriority.CRITICAL.value:
            channels = [
                CommunicationChannel.PHONE.value,
                CommunicationChannel.SLACK.value,
                CommunicationChannel.EMAIL.value
            ]
        elif priority == CommunicationPriority.HIGH.value:
            channels = [
                CommunicationChannel.SLACK.value,
                CommunicationChannel.EMAIL.value,
                CommunicationChannel.TEAMS.value
            ]
        elif priority == CommunicationPriority.MEDIUM.value:
            channels = [
                CommunicationChannel.EMAIL.value,
                CommunicationChannel.SLACK.value
            ]
        else:  # LOW
            channels = [
                CommunicationChannel.EMAIL.value
            ]
        
        # Ajustar basado en tipo de comunicación
        if comm_type == CommunicationType.EMERGENCY.value:
            channels.insert(0, CommunicationChannel.PHONE.value)
        elif comm_type == CommunicationType.CHANGE.value:
            channels.append(CommunicationChannel.TEAMS.value)
        
        return channels
    
    def _generate_communication_id(self) -> str:
        """Generar ID único para comunicación"""
        try:
            # Obtener el último ID
            response = self.supabase.table("communications").select("communication_id").order(
                "created_at", desc=True
            ).limit(1).execute()
            
            if response.data and response.data[0]['communication_id']:
                last_id = int(response.data[0]['communication_id'].split('-')[1])
                new_id = last_id + 1
            else:
                new_id = 1
            
            return f"COMM-{new_id:06d}"
            
        except Exception as e:
            logger.error(f"Error generando ID de comunicación: {e}")
            return f"COMM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    async def _send_communication(self, communication_id: str, communication_data: Dict[str, Any], channels: List[str]) -> Dict[str, Any]:
        """Enviar comunicación a través de canales especificados"""
        results = {}
        
        for channel in channels:
            try:
                if channel == CommunicationChannel.EMAIL.value:
                    result = await self._send_email_communication(communication_data)
                elif channel == CommunicationChannel.SLACK.value:
                    result = await self._send_slack_communication(communication_data)
                elif channel == CommunicationChannel.TEAMS.value:
                    result = await self._send_teams_communication(communication_data)
                elif channel == CommunicationChannel.PHONE.value:
                    result = await self._send_phone_communication(communication_data)
                else:
                    result = {"status": "error", "message": f"Canal no soportado: {channel}"}
                
                results[channel] = result
                
            except Exception as e:
                logger.error(f"Error enviando comunicación por {channel}: {e}")
                results[channel] = {"status": "error", "message": str(e)}
        
        return results
    
    async def _send_email_communication(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar comunicación por email"""
        try:
            # Crear contenido del email
            subject = f"[{communication_data['communication_id']}] {communication_data['subject']}"
            
            body = f"""
            <h2>Comunicación de Soporte - Grinding Perú</h2>
            <p><strong>ID:</strong> {communication_data['communication_id']}</p>
            <p><strong>Tipo:</strong> {communication_data['type']}</p>
            <p><strong>Prioridad:</strong> {communication_data['priority']}</p>
            <p><strong>Remitente:</strong> {communication_data['sender']}</p>
            <p><strong>Mensaje:</strong></p>
            <p>{communication_data['message']}</p>
            <hr>
            <p><em>Esta es una comunicación automática del sistema de soporte de Grinding Perú.</em></p>
            """
            
            # Enviar email
            alert_data = {
                "title": subject,
                "message": body,
                "priority": communication_data['priority'],
                "category": "communication",
                "recipients": communication_data.get('recipients', ['soporte@grindingperu.com'])
            }
            
            result = await self.notification_service.send_alert(alert_data)
            return result
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_slack_communication(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar comunicación por Slack"""
        try:
            # Determinar canal basado en prioridad
            priority = communication_data['priority']
            channel_config = self.channel_config[CommunicationChannel.SLACK]
            channel = channel_config['channels'].get(priority, '#soporte-general')
            
            # Crear mensaje de Slack
            message = {
                "channel": channel,
                "text": f"📢 Nueva Comunicación: {communication_data['subject']}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"📢 {communication_data['subject']}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*ID:* {communication_data['communication_id']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Tipo:* {communication_data['type']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Prioridad:* {communication_data['priority']}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Remitente:* {communication_data['sender']}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Mensaje:*\n{communication_data['message']}"
                        }
                    }
                ]
            }
            
            # Enviar a Slack
            result = await self.notification_service.send_slack_alert(message)
            return result
            
        except Exception as e:
            logger.error(f"Error enviando a Slack: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_teams_communication(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar comunicación por Microsoft Teams"""
        try:
            # Crear mensaje de Teams
            message = {
                "title": f"Comunicación: {communication_data['subject']}",
                "text": f"""
                **ID:** {communication_data['communication_id']}
                **Tipo:** {communication_data['type']}
                **Prioridad:** {communication_data['priority']}
                **Remitente:** {communication_data['sender']}
                
                **Mensaje:**
                {communication_data['message']}
                """,
                "themeColor": self._get_priority_color(communication_data['priority'])
            }
            
            # Enviar a Teams
            result = await self.notification_service.send_teams_alert(message)
            return result
            
        except Exception as e:
            logger.error(f"Error enviando a Teams: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _send_phone_communication(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar comunicación por teléfono (simulado)"""
        try:
            # En un sistema real, esto integraría con un sistema de telefonía
            # Por ahora, solo registramos la acción
            logger.info(f"Llamada telefónica simulada para comunicación {communication_data['communication_id']}")
            
            return {
                "status": "success",
                "message": "Llamada telefónica programada",
                "method": "phone"
            }
            
        except Exception as e:
            logger.error(f"Error en llamada telefónica: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_priority_color(self, priority: str) -> str:
        """Obtener color basado en prioridad"""
        colors = {
            "critical": "FF0000",  # Rojo
            "high": "FFA500",      # Naranja
            "medium": "FFFF00",    # Amarillo
            "low": "00FF00"        # Verde
        }
        return colors.get(priority, "0000FF")  # Azul por defecto
    
    def get_communication_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Obtener métricas de comunicaciones para Grinding Perú"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener datos de comunicaciones
            response = self.supabase.table("communications").select("*").gte(
                "created_at", start_date.isoformat()
            ).execute()
            
            if not response.data:
                return {"error": "No hay datos de comunicaciones"}
            
            df = pd.DataFrame(response.data)
            
            # Calcular métricas
            metrics = {
                "total_communications": len(df),
                "communications_by_type": df['type'].value_counts().to_dict(),
                "communications_by_priority": df['priority'].value_counts().to_dict(),
                "communications_by_channel": self._calculate_channel_metrics(df),
                "response_time_metrics": self._calculate_response_time_metrics(df),
                "escalation_rate": self._calculate_escalation_rate(df),
                "communication_trends": self._analyze_communication_trends(df)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculando métricas de comunicaciones: {e}")
            return {"error": str(e)}
    
    def _calculate_channel_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas por canal de comunicación"""
        # Implementar lógica de cálculo de métricas por canal
        return {
            "email": {"count": 0, "success_rate": 0.95},
            "slack": {"count": 0, "success_rate": 0.90},
            "teams": {"count": 0, "success_rate": 0.85},
            "phone": {"count": 0, "success_rate": 0.80}
        }
    
    def _calculate_response_time_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de tiempo de respuesta"""
        # Implementar lógica de cálculo de tiempo de respuesta
        return {
            "average_response_time_minutes": 25,
            "sla_compliance_rate": 0.88,
            "by_priority": {
                "critical": 5,
                "high": 15,
                "medium": 45,
                "low": 120
            }
        }
    
    def _calculate_escalation_rate(self, df: pd.DataFrame) -> float:
        """Calcular tasa de escalamiento"""
        # Implementar lógica de cálculo de escalamiento
        return 0.15  # 15% de escalamiento
    
    def _analyze_communication_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analizar tendencias de comunicaciones"""
        # Implementar análisis de tendencias
        return {
            "trend_direction": "stable",
            "peak_hours": [9, 10, 14, 15],
            "common_types": ["incident", "request"],
            "channel_preferences": ["email", "slack"]
        }
