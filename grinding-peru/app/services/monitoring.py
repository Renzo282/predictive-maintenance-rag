"""
Servicio de monitoreo del sistema
"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        self.metrics = {}
        self.alerts = []
    
    async def start_monitoring(self):
        """Iniciar monitoreo del sistema"""
        try:
            logger.info("Iniciando servicio de monitoreo...")
            
            # Configurar métricas básicas
            self.metrics = {
                "system_start_time": datetime.now(),
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "active_incidents": 0,
                "system_health": "healthy"
            }
            
            logger.info("Servicio de monitoreo iniciado")
            
        except Exception as e:
            logger.error(f"Error iniciando monitoreo: {e}")
    
    def record_request(self, success: bool = True):
        """Registrar request"""
        self.metrics["total_requests"] += 1
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        return self.metrics.copy()
    
    def add_alert(self, alert_type: str, message: str, severity: str = "medium"):
        """Agregar alerta"""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        self.alerts.append(alert)
        logger.warning(f"Alerta: {message}")

# Instancia global
_monitoring_service = None

def get_monitoring_service() -> MonitoringService:
    """Obtener instancia del servicio de monitoreo"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service

async def start_monitoring():
    """Iniciar monitoreo"""
    service = get_monitoring_service()
    await service.start_monitoring()
