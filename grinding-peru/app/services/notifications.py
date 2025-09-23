"""
Servicio de notificaciones
"""
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.notifications = []
    
    async def send_notification(
        self, 
        recipient: str, 
        message: str, 
        notification_type: str = "info"
    ) -> bool:
        """Enviar notificación"""
        try:
            notification = {
                "recipient": recipient,
                "message": message,
                "type": notification_type,
                "timestamp": datetime.now().isoformat(),
                "status": "sent"
            }
            
            self.notifications.append(notification)
            logger.info(f"Notificación enviada a {recipient}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return False
    
    async def send_incident_notification(
        self, 
        incident_id: str, 
        technician_id: str, 
        message: str
    ) -> bool:
        """Enviar notificación de incidencia"""
        return await self.send_notification(
            recipient=technician_id,
            message=f"Incidencia {incident_id}: {message}",
            notification_type="incident"
        )
    
    async def send_alert_notification(
        self, 
        alert_type: str, 
        message: str, 
        recipients: List[str]
    ) -> bool:
        """Enviar notificación de alerta"""
        success = True
        for recipient in recipients:
            result = await self.send_notification(
                recipient=recipient,
                message=f"ALERTA {alert_type}: {message}",
                notification_type="alert"
            )
            if not result:
                success = False
        
        return success
    
    def get_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener notificaciones"""
        return self.notifications[-limit:]

# Instancia global
_notification_service = None

def get_notification_service() -> NotificationService:
    """Obtener instancia del servicio de notificaciones"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
