"""
Notification service for maintenance alerts
"""
import logging
import smtplib
import json
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from app.core.config import settings
from app.core.database import get_supabase

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending maintenance notifications"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.slack_webhook = None
        self._setup_slack()
    
    def _setup_slack(self):
        """Setup Slack integration if configured"""
        if settings.SLACK_BOT_TOKEN and settings.SLACK_CHANNEL:
            try:
                # Test Slack connection
                response = requests.post(
                    "https://slack.com/api/auth.test",
                    headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"}
                )
                if response.json().get("ok"):
                    self.slack_webhook = True
                    logger.info("Slack integration configured successfully")
                else:
                    logger.warning("Slack token validation failed")
            except Exception as e:
                logger.warning(f"Failed to setup Slack: {e}")
    
    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send maintenance alert through configured channels"""
        try:
            # Store alert in database
            alert_id = self._store_alert(alert_data)
            
            # Send notifications
            results = {}
            
            # Email notification
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                email_result = self._send_email_alert(alert_data)
                results["email"] = email_result
            
            # Slack notification
            if self.slack_webhook:
                slack_result = self._send_slack_alert(alert_data)
                results["slack"] = slack_result
            
            # Webhook notification (if configured)
            webhook_result = self._send_webhook_alert(alert_data)
            if webhook_result:
                results["webhook"] = webhook_result
            
            return {
                "status": "success",
                "alert_id": alert_id,
                "notifications_sent": results
            }
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return {"status": "error", "message": str(e)}
    
    def _store_alert(self, alert_data: Dict[str, Any]) -> str:
        """Store alert in database"""
        try:
            alert_record = {
                "equipment_id": alert_data.get("equipment_id"),
                "alert_type": alert_data.get("alert_type", "maintenance"),
                "severity": alert_data.get("severity", "medium"),
                "message": alert_data.get("message", ""),
                "is_resolved": False,
                "created_at": datetime.now().isoformat()
            }
            
            response = self.supabase.table("alerts").insert(alert_record).execute()
            
            if response.data:
                return response.data[0]["id"]
            else:
                raise Exception("Failed to store alert in database")
                
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
            raise
    
    def _send_email_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email alert"""
        try:
            # Create email content
            subject = f"🚨 Maintenance Alert - {alert_data.get('equipment_name', 'Unknown Equipment')}"
            
            body = self._create_email_body(alert_data)
            
            # Setup email
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USERNAME
            msg['To'] = alert_data.get('recipient_email', settings.SMTP_USERNAME)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(settings.SMTP_USERNAME, msg['To'], text)
            server.quit()
            
            logger.info(f"Email alert sent successfully")
            return {"status": "success", "method": "email"}
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return {"status": "error", "method": "email", "message": str(e)}
    
    def _create_email_body(self, alert_data: Dict[str, Any]) -> str:
        """Create HTML email body"""
        severity_colors = {
            "low": "#28a745",
            "medium": "#ffc107", 
            "high": "#fd7e14",
            "critical": "#dc3545"
        }
        
        severity = alert_data.get("severity", "medium")
        color = severity_colors.get(severity, "#ffc107")
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">🚨 Maintenance Alert</h1>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="color: #495057; margin-top: 0;">Equipment Details</h2>
                    <p><strong>Equipment:</strong> {alert_data.get('equipment_name', 'Unknown')}</p>
                    <p><strong>Type:</strong> {alert_data.get('equipment_type', 'Unknown')}</p>
                    <p><strong>Location:</strong> {alert_data.get('equipment_location', 'Unknown')}</p>
                    <p><strong>Severity:</strong> <span style="color: {color}; font-weight: bold;">{severity.upper()}</span></p>
                </div>
                
                <div style="background-color: #fff; padding: 20px; border: 1px solid #dee2e6; border-radius: 5px; margin-bottom: 20px;">
                    <h3 style="color: #495057; margin-top: 0;">Alert Details</h3>
                    <p><strong>Type:</strong> {alert_data.get('alert_type', 'Maintenance')}</p>
                    <p><strong>Message:</strong> {alert_data.get('message', 'No additional details')}</p>
                    <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                {self._create_recommendations_section(alert_data)}
                
                <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-top: 20px;">
                    <p style="margin: 0; font-size: 14px; color: #6c757d;">
                        This is an automated alert from the Predictive Maintenance System.
                        Please take appropriate action based on the severity level.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_recommendations_section(self, alert_data: Dict[str, Any]) -> str:
        """Create recommendations section for email"""
        recommendations = alert_data.get("recommendations", [])
        
        if not recommendations:
            return ""
        
        rec_html = """
        <div style="background-color: #d1ecf1; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: #0c5460; margin-top: 0;">Recommended Actions</h3>
            <ul style="margin: 0; padding-left: 20px;">
        """
        
        for rec in recommendations:
            rec_html += f"<li style="margin-bottom: 10px;">{rec}</li>"
        
        rec_html += """
            </ul>
        </div>
        """
        
        return rec_html
    
    def _send_slack_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send Slack alert"""
        try:
            severity_emojis = {
                "low": "🟢",
                "medium": "🟡", 
                "high": "🟠",
                "critical": "🔴"
            }
            
            severity = alert_data.get("severity", "medium")
            emoji = severity_emojis.get(severity, "🟡")
            
            # Create Slack message
            message = {
                "channel": settings.SLACK_CHANNEL,
                "text": f"{emoji} Maintenance Alert",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} Maintenance Alert - {alert_data.get('equipment_name', 'Unknown Equipment')}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Equipment:* {alert_data.get('equipment_name', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Type:* {alert_data.get('equipment_type', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Location:* {alert_data.get('equipment_location', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Severity:* {severity.upper()}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Message:* {alert_data.get('message', 'No additional details')}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Alert Type: {alert_data.get('alert_type', 'Maintenance')} | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
            
            # Send to Slack
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
                json=message
            )
            
            if response.json().get("ok"):
                logger.info("Slack alert sent successfully")
                return {"status": "success", "method": "slack"}
            else:
                raise Exception(f"Slack API error: {response.json()}")
                
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return {"status": "error", "method": "slack", "message": str(e)}
    
    def _send_webhook_alert(self, alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send webhook alert (if configured)"""
        webhook_url = alert_data.get("webhook_url")
        
        if not webhook_url:
            return None
        
        try:
            payload = {
                "alert_id": alert_data.get("alert_id"),
                "equipment_id": alert_data.get("equipment_id"),
                "equipment_name": alert_data.get("equipment_name"),
                "alert_type": alert_data.get("alert_type"),
                "severity": alert_data.get("severity"),
                "message": alert_data.get("message"),
                "timestamp": datetime.now().isoformat(),
                "recommendations": alert_data.get("recommendations", [])
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Webhook alert sent successfully")
                return {"status": "success", "method": "webhook"}
            else:
                raise Exception(f"Webhook returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return {"status": "error", "method": "webhook", "message": str(e)}
    
    def get_alert_history(self, equipment_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        try:
            query = self.supabase.table("alerts").select("*")
            
            if equipment_id:
                query = query.eq("equipment_id", equipment_id)
            
            response = query.order("created_at", desc=True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return []
    
    def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """Mark alert as resolved"""
        try:
            response = self.supabase.table("alerts").update({
                "is_resolved": True,
                "resolved_at": datetime.now().isoformat()
            }).eq("id", alert_id).execute()
            
            if response.data:
                logger.info(f"Alert {alert_id} resolved successfully")
                return {"status": "success", "alert_id": alert_id}
            else:
                raise Exception("Failed to resolve alert")
                
        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_maintenance_schedule_alert(self, equipment_id: str, maintenance_type: str, 
                                        scheduled_date: str, description: str) -> Dict[str, Any]:
        """Create scheduled maintenance alert"""
        try:
            # Get equipment details
            equipment_response = self.supabase.table("equipment").select("*").eq("id", equipment_id).execute()
            
            if not equipment_response.data:
                return {"status": "error", "message": "Equipment not found"}
            
            equipment = equipment_response.data[0]
            
            alert_data = {
                "equipment_id": equipment_id,
                "equipment_name": equipment.get("name"),
                "equipment_type": equipment.get("type"),
                "equipment_location": equipment.get("location"),
                "alert_type": "scheduled_maintenance",
                "severity": "medium",
                "message": f"Scheduled maintenance: {maintenance_type} - {description}",
                "scheduled_date": scheduled_date,
                "recommendations": [
                    f"Prepare for {maintenance_type} maintenance",
                    "Review maintenance procedures",
                    "Ensure equipment is accessible",
                    "Schedule technician if required"
                ]
            }
            
            return self.send_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Failed to create maintenance schedule alert: {e}")
            return {"status": "error", "message": str(e)}
