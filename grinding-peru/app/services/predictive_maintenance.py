"""
Módulo de Mantenimiento Predictivo para Grinding Perú
Implementa ML para predicción de fallas y alertas automáticas
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from app.core.database import get_supabase
from app.services.rag_agent import RAGAgent
from app.services.notifications import NotificationService

logger = logging.getLogger(__name__)


class PredictiveMaintenanceService:
    """Servicio de Mantenimiento Predictivo para Grinding Perú"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.rag_agent = RAGAgent()
        self.notification_service = NotificationService()
        
        # Modelos de ML
        self.failure_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        # Configuración
        self.model_path = "./models"
        self.is_trained = False
        self._ensure_model_directory()
    
    def _ensure_model_directory(self):
        """Crear directorio de modelos si no existe"""
        os.makedirs(self.model_path, exist_ok=True)
    
    async def train_models(self, equipment_id: Optional[str] = None) -> Dict[str, Any]:
        """Entrenar modelos de ML con datos históricos"""
        try:
            logger.info("Iniciando entrenamiento de modelos de mantenimiento predictivo...")
            
            # Obtener datos históricos
            historical_data = await self._get_historical_data(equipment_id)
            
            if len(historical_data) < 100:
                return {
                    "status": "error",
                    "message": "Datos insuficientes para entrenamiento. Se requieren al menos 100 registros."
                }
            
            df = pd.DataFrame(historical_data)
            
            # Preparar datos para entrenamiento
            X, y = self._prepare_training_data(df)
            
            if X is None or y is None:
                return {
                    "status": "error",
                    "message": "Error preparando datos para entrenamiento"
                }
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Escalar características
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entrenar modelo de predicción de fallas
            self.failure_predictor.fit(X_train_scaled, y_train)
            
            # Entrenar detector de anomalías
            self.anomaly_detector.fit(X_train_scaled)
            
            # Evaluar modelos
            y_pred = self.failure_predictor.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Calcular anomalías
            anomaly_scores = self.anomaly_detector.decision_function(X_test_scaled)
            anomaly_predictions = self.anomaly_detector.predict(X_test_scaled)
            anomaly_rate = np.sum(anomaly_predictions == -1) / len(anomaly_predictions)
            
            # Guardar modelos
            self._save_models()
            
            self.is_trained = True
            
            return {
                "status": "success",
                "accuracy": round(accuracy, 3),
                "anomaly_rate": round(anomaly_rate, 3),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features_used": X.shape[1],
                "model_path": self.model_path
            }
            
        except Exception as e:
            logger.error(f"Error entrenando modelos: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _get_historical_data(self, equipment_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtener datos históricos de sensores y mantenimiento"""
        try:
            # Obtener datos de sensores de los últimos 6 meses
            six_months_ago = datetime.now() - timedelta(days=180)
            
            query = self.supabase.table("sensor_data").select(
                "*, equipment:equipment_id(*), maintenance_records:equipment_id(*)"
            ).gte("timestamp", six_months_ago.isoformat())
            
            if equipment_id:
                query = query.eq("equipment_id", equipment_id)
            
            response = query.execute()
            
            if not response.data:
                return []
            
            # Procesar datos para incluir información de mantenimiento
            processed_data = []
            for record in response.data:
                # Obtener registros de mantenimiento para este equipo
                maintenance_records = record.get("maintenance_records", [])
                
                # Determinar si hubo falla en los próximos 7 días
                record_date = pd.to_datetime(record['timestamp'])
                future_maintenance = [
                    m for m in maintenance_records
                    if pd.to_datetime(m['performed_at']) <= record_date + timedelta(days=7)
                    and pd.to_datetime(m['performed_at']) > record_date
                ]
                
                has_failure = len(future_maintenance) > 0
                
                processed_record = {
                    **record,
                    'has_failure': has_failure,
                    'maintenance_type': future_maintenance[0]['maintenance_type'] if future_maintenance else 'none'
                }
                
                processed_data.append(processed_record)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {e}")
            return []
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Preparar datos para entrenamiento de ML"""
        try:
            # Seleccionar características numéricas
            feature_columns = [
                'temperature', 'vibration', 'pressure', 'humidity', 
                'voltage', 'current'
            ]
            
            # Filtrar columnas que existen
            available_features = [col for col in feature_columns if col in df.columns]
            
            if not available_features:
                logger.error("No se encontraron características válidas para entrenamiento")
                return None, None
            
            # Crear características
            X = df[available_features].fillna(df[available_features].median())
            
            # Agregar características temporales
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            X['hour'] = df['timestamp'].dt.hour
            X['day_of_week'] = df['timestamp'].dt.dayofweek
            X['month'] = df['timestamp'].dt.month
            
            # Agregar características de tendencia
            for col in available_features:
                X[f'{col}_rolling_mean'] = df[col].rolling(window=24, min_periods=1).mean()
                X[f'{col}_rolling_std'] = df[col].rolling(window=24, min_periods=1).std()
            
            # Rellenar valores NaN
            X = X.fillna(0)
            
            # Crear variable objetivo
            y = df['has_failure'].astype(int)
            
            return X.values, y.values
            
        except Exception as e:
            logger.error(f"Error preparando datos de entrenamiento: {e}")
            return None, None
    
    def _save_models(self):
        """Guardar modelos entrenados"""
        try:
            joblib.dump(self.failure_predictor, os.path.join(self.model_path, 'failure_predictor.joblib'))
            joblib.dump(self.anomaly_detector, os.path.join(self.model_path, 'anomaly_detector.joblib'))
            joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.joblib'))
            
            logger.info("Modelos guardados exitosamente")
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
    
    def _load_models(self):
        """Cargar modelos pre-entrenados"""
        try:
            failure_path = os.path.join(self.model_path, 'failure_predictor.joblib')
            anomaly_path = os.path.join(self.model_path, 'anomaly_detector.joblib')
            scaler_path = os.path.join(self.model_path, 'scaler.joblib')
            
            if all(os.path.exists(p) for p in [failure_path, anomaly_path, scaler_path]):
                self.failure_predictor = joblib.load(failure_path)
                self.anomaly_detector = joblib.load(anomaly_path)
                self.scaler = joblib.load(scaler_path)
                self.is_trained = True
                
                logger.info("Modelos cargados exitosamente")
                return True
            else:
                logger.warning("Modelos no encontrados, necesita entrenamiento")
                return False
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            return False
    
    async def predict_equipment_failure(self, equipment_id: str) -> Dict[str, Any]:
        """Predecir falla de equipo específico"""
        try:
            if not self.is_trained:
                if not self._load_models():
                    return {"error": "Modelos no entrenados. Ejecute entrenamiento primero."}
            
            # Obtener datos recientes del equipo
            recent_data = await self._get_recent_equipment_data(equipment_id)
            
            if not recent_data:
                return {"error": "No hay datos recientes para el equipo"}
            
            # Preparar datos para predicción
            X = self._prepare_prediction_data(recent_data)
            
            if X is None:
                return {"error": "Error preparando datos para predicción"}
            
            # Escalar características
            X_scaled = self.scaler.transform(X)
            
            # Realizar predicción
            failure_probability = self.failure_predictor.predict_proba(X_scaled)[0][1]
            failure_prediction = self.failure_predictor.predict(X_scaled)[0]
            
            # Detectar anomalías
            anomaly_score = self.anomaly_detector.decision_function(X_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(X_scaled)[0] == -1
            
            # Generar recomendaciones usando RAG
            recommendations = await self._generate_maintenance_recommendations(
                equipment_id, failure_probability, is_anomaly, recent_data
            )
            
            # Determinar nivel de alerta
            alert_level = self._determine_alert_level(failure_probability, is_anomaly)
            
            # Crear alerta si es necesario
            if alert_level in ["high", "critical"]:
                await self._create_predictive_alert(equipment_id, failure_probability, recommendations)
            
            return {
                "equipment_id": equipment_id,
                "failure_probability": round(failure_probability, 3),
                "failure_predicted": bool(failure_prediction),
                "anomaly_detected": bool(is_anomaly),
                "anomaly_score": round(anomaly_score, 3),
                "alert_level": alert_level,
                "recommendations": recommendations,
                "prediction_confidence": self._calculate_confidence(failure_probability, is_anomaly),
                "predicted_failure_date": self._estimate_failure_date(failure_probability),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error prediciendo falla del equipo: {e}")
            return {"error": str(e)}
    
    async def _get_recent_equipment_data(self, equipment_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener datos recientes del equipo"""
        try:
            hours_ago = datetime.now() - timedelta(hours=hours)
            
            response = self.supabase.table("sensor_data").select("*").eq(
                "equipment_id", equipment_id
            ).gte("timestamp", hours_ago.isoformat()).order("timestamp", desc=True).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error obteniendo datos recientes del equipo: {e}")
            return []
    
    def _prepare_prediction_data(self, data: List[Dict[str, Any]]) -> Optional[np.ndarray]:
        """Preparar datos para predicción"""
        try:
            if not data:
                return None
            
            df = pd.DataFrame(data)
            
            # Seleccionar características numéricas
            feature_columns = [
                'temperature', 'vibration', 'pressure', 'humidity', 
                'voltage', 'current'
            ]
            
            available_features = [col for col in feature_columns if col in df.columns]
            
            if not available_features:
                return None
            
            # Crear características
            X = df[available_features].fillna(df[available_features].median())
            
            # Agregar características temporales
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            X['hour'] = df['timestamp'].dt.hour
            X['day_of_week'] = df['timestamp'].dt.dayofweek
            X['month'] = df['timestamp'].dt.month
            
            # Agregar características de tendencia
            for col in available_features:
                X[f'{col}_rolling_mean'] = df[col].rolling(window=24, min_periods=1).mean()
                X[f'{col}_rolling_std'] = df[col].rolling(window=24, min_periods=1).std()
            
            # Rellenar valores NaN
            X = X.fillna(0)
            
            # Tomar el último registro
            return X.iloc[-1:].values
            
        except Exception as e:
            logger.error(f"Error preparando datos de predicción: {e}")
            return None
    
    async def _generate_maintenance_recommendations(self, equipment_id: str, failure_probability: float, 
                                                  is_anomaly: bool, recent_data: List[Dict[str, Any]]) -> List[str]:
        """Generar recomendaciones de mantenimiento usando RAG"""
        try:
            # Obtener información del equipo
            equipment_response = self.supabase.table("equipment").select("*").eq("id", equipment_id).execute()
            equipment = equipment_response.data[0] if equipment_response.data else {}
            
            # Crear query para RAG
            query = f"""
            Basado en el análisis del equipo {equipment.get('name', 'desconocido')} de Grinding Perú:
            
            - Probabilidad de falla: {failure_probability:.1%}
            - Anomalía detectada: {'Sí' if is_anomaly else 'No'}
            - Datos recientes: {len(recent_data)} registros
            - Tipo de equipo: {equipment.get('type', 'desconocido')}
            
            Proporciona recomendaciones específicas de mantenimiento preventivo:
            1. Acciones inmediatas requeridas
            2. Inspecciones recomendadas
            3. Repuestos que podrían necesitarse
            4. Frecuencia de monitoreo sugerida
            5. Protocolos de seguridad a seguir
            """
            
            # Usar RAG para generar recomendaciones
            analysis_result = self.rag_agent.generate_prediction(
                "maintenance_recommendations", query
            )
            
            # Procesar recomendaciones
            recommendations = self._extract_recommendations(analysis_result.get("answer", ""))
            
            # Agregar recomendaciones basadas en probabilidad
            if failure_probability > 0.8:
                recommendations.insert(0, "⚠️ ALERTA CRÍTICA: Revisión inmediata requerida")
            elif failure_probability > 0.6:
                recommendations.insert(0, "🔶 Mantenimiento preventivo recomendado en las próximas 24 horas")
            elif failure_probability > 0.4:
                recommendations.insert(0, "🔸 Programar mantenimiento preventivo en la próxima semana")
            
            if is_anomaly:
                recommendations.insert(0, "🚨 Anomalía detectada: Investigar causa raíz")
            
            return recommendations[:10]  # Limitar a 10 recomendaciones
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            return [
                "Revisar manual de mantenimiento del equipo",
                "Verificar parámetros operativos normales",
                "Programar inspección visual completa"
            ]
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extraer recomendaciones del análisis de RAG"""
        try:
            recommendations = []
            lines = analysis_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or 
                           line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or 
                           line.startswith('5.') or 'recomend' in line.lower() or 'suger' in line.lower()):
                    # Limpiar la línea
                    clean_line = line.lstrip('-•123456789. ').strip()
                    if clean_line and len(clean_line) > 10:  # Filtrar líneas muy cortas
                        recommendations.append(clean_line)
            
            return recommendations if recommendations else [
                "Revisar manual de mantenimiento",
                "Verificar parámetros operativos",
                "Programar inspección visual"
            ]
            
        except Exception as e:
            logger.error(f"Error extrayendo recomendaciones: {e}")
            return ["Revisar manual de mantenimiento del equipo"]
    
    def _determine_alert_level(self, failure_probability: float, is_anomaly: bool) -> str:
        """Determinar nivel de alerta"""
        if failure_probability > 0.8 or is_anomaly:
            return "critical"
        elif failure_probability > 0.6:
            return "high"
        elif failure_probability > 0.4:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, failure_probability: float, is_anomaly: bool) -> float:
        """Calcular confianza de la predicción"""
        base_confidence = min(0.9, 0.5 + failure_probability * 0.4)
        
        if is_anomaly:
            base_confidence += 0.1
        
        return min(0.95, base_confidence)
    
    def _estimate_failure_date(self, failure_probability: float) -> str:
        """Estimar fecha de falla probable"""
        if failure_probability > 0.8:
            days = 1
        elif failure_probability > 0.6:
            days = 3
        elif failure_probability > 0.4:
            days = 7
        elif failure_probability > 0.2:
            days = 14
        else:
            days = 30
        
        estimated_date = datetime.now() + timedelta(days=days)
        return estimated_date.strftime("%Y-%m-%d")
    
    async def _create_predictive_alert(self, equipment_id: str, failure_probability: float, recommendations: List[str]):
        """Crear alerta predictiva"""
        try:
            # Obtener información del equipo
            equipment_response = self.supabase.table("equipment").select("*").eq("id", equipment_id).execute()
            equipment = equipment_response.data[0] if equipment_response.data else {}
            
            alert_data = {
                "equipment_id": equipment_id,
                "title": f"Alerta Predictiva: {equipment.get('name', 'Equipo Desconocido')}",
                "message": f"Se ha detectado una probabilidad de falla del {failure_probability:.1%} en el equipo {equipment.get('name', 'desconocido')}",
                "priority": "high" if failure_probability > 0.6 else "medium",
                "category": "predictive_maintenance",
                "recipients": self._get_predictive_alert_recipients(equipment),
                "recommendations": recommendations,
                "failure_probability": failure_probability
            }
            
            await self.notification_service.send_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Error creando alerta predictiva: {e}")
    
    def _get_predictive_alert_recipients(self, equipment: Dict[str, Any]) -> List[str]:
        """Obtener destinatarios de alertas predictivas"""
        criticality = equipment.get("criticality", "medium")
        
        recipients = {
            "critical": ["mantenimiento@grindingperu.com", "supervisor@grindingperu.com", "gerencia@grindingperu.com"],
            "high": ["mantenimiento@grindingperu.com", "supervisor@grindingperu.com"],
            "medium": ["mantenimiento@grindingperu.com"],
            "low": ["mantenimiento@grindingperu.com"]
        }
        
        return recipients.get(criticality, ["mantenimiento@grindingperu.com"])
    
    async def get_equipment_health_summary(self, equipment_id: str) -> Dict[str, Any]:
        """Obtener resumen de salud del equipo"""
        try:
            # Obtener información del equipo
            equipment_response = self.supabase.table("equipment").select("*").eq("id", equipment_id).execute()
            equipment = equipment_response.data[0] if equipment_response.data else {}
            
            # Obtener datos recientes
            recent_data = await self._get_recent_equipment_data(equipment_id, hours=168)  # Última semana
            
            if not recent_data:
                return {"error": "No hay datos recientes para el equipo"}
            
            # Calcular métricas de salud
            df = pd.DataFrame(recent_data)
            
            health_metrics = {
                "equipment_name": equipment.get("name", "Desconocido"),
                "equipment_type": equipment.get("type", "Desconocido"),
                "last_maintenance": equipment.get("last_maintenance"),
                "next_maintenance": equipment.get("next_maintenance"),
                "data_points": len(df),
                "time_range": {
                    "start": df['timestamp'].min(),
                    "end": df['timestamp'].max()
                },
                "sensor_readings": self._calculate_sensor_metrics(df),
                "health_score": self._calculate_health_score(df),
                "recommendations": await self._generate_health_recommendations(equipment_id, df)
            }
            
            return health_metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de salud del equipo: {e}")
            return {"error": str(e)}
    
    def _calculate_sensor_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcular métricas de sensores"""
        try:
            sensor_columns = ['temperature', 'vibration', 'pressure', 'humidity', 'voltage', 'current']
            metrics = {}
            
            for col in sensor_columns:
                if col in df.columns:
                    values = df[col].dropna()
                    if not values.empty:
                        metrics[col] = {
                            "current": float(values.iloc[-1]) if len(values) > 0 else None,
                            "average": float(values.mean()),
                            "min": float(values.min()),
                            "max": float(values.max()),
                            "std": float(values.std()),
                            "trend": self._calculate_trend(values)
                        }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculando métricas de sensores: {e}")
            return {}
    
    def _calculate_trend(self, values: pd.Series) -> str:
        """Calcular tendencia de valores"""
        try:
            if len(values) < 2:
                return "stable"
            
            # Regresión lineal simple
            x = np.arange(len(values))
            y = values.values
            
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculando tendencia: {e}")
            return "stable"
    
    def _calculate_health_score(self, df: pd.DataFrame) -> float:
        """Calcular puntuación de salud del equipo (0-100)"""
        try:
            score = 100.0
            
            # Penalizar por valores anómalos
            sensor_columns = ['temperature', 'vibration', 'pressure', 'voltage', 'current']
            
            for col in sensor_columns:
                if col in df.columns:
                    values = df[col].dropna()
                    if not values.empty:
                        # Calcular Z-scores
                        mean_val = values.mean()
                        std_val = values.std()
                        
                        if std_val > 0:
                            z_scores = np.abs((values - mean_val) / std_val)
                            anomaly_count = np.sum(z_scores > 2.5)
                            anomaly_rate = anomaly_count / len(values)
                            
                            # Reducir score por anomalías
                            score -= anomaly_rate * 20
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculando puntuación de salud: {e}")
            return 50.0
    
    async def _generate_health_recommendations(self, equipment_id: str, df: pd.DataFrame) -> List[str]:
        """Generar recomendaciones de salud del equipo"""
        try:
            recommendations = []
            
            # Analizar cada sensor
            sensor_columns = ['temperature', 'vibration', 'pressure', 'voltage', 'current']
            
            for col in sensor_columns:
                if col in df.columns:
                    values = df[col].dropna()
                    if not values.empty:
                        current_val = values.iloc[-1]
                        mean_val = values.mean()
                        std_val = values.std()
                        
                        # Detectar valores anómalos
                        if std_val > 0:
                            z_score = abs(current_val - mean_val) / std_val
                            
                            if z_score > 3:
                                recommendations.append(f"🚨 Valor crítico en {col}: {current_val:.2f}")
                            elif z_score > 2:
                                recommendations.append(f"⚠️ Valor anómalo en {col}: {current_val:.2f}")
            
            # Agregar recomendaciones generales
            if not recommendations:
                recommendations.append("✅ Equipo funcionando dentro de parámetros normales")
            
            recommendations.append("📋 Revisar manual de mantenimiento del fabricante")
            recommendations.append("🔍 Programar inspección visual regular")
            
            return recommendations[:8]  # Limitar a 8 recomendaciones
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones de salud: {e}")
            return ["Revisar manual de mantenimiento del equipo"]
    
    async def get_predictive_analytics_dashboard(self) -> Dict[str, Any]:
        """Obtener dashboard de análisis predictivo"""
        try:
            # Obtener todos los equipos
            equipment_response = self.supabase.table("equipment").select("*").execute()
            equipment_list = equipment_response.data if equipment_response.data else []
            
            dashboard_data = {
                "total_equipment": len(equipment_list),
                "equipment_health": [],
                "predictions_summary": {
                    "high_risk": 0,
                    "medium_risk": 0,
                    "low_risk": 0
                },
                "alerts_generated": 0,
                "maintenance_recommendations": []
            }
            
            # Analizar cada equipo
            for equipment in equipment_list:
                equipment_id = equipment['id']
                
                # Obtener predicción de falla
                prediction = await self.predict_equipment_failure(equipment_id)
                
                if 'error' not in prediction:
                    health_data = {
                        "equipment_id": equipment_id,
                        "equipment_name": equipment['name'],
                        "failure_probability": prediction['failure_probability'],
                        "alert_level": prediction['alert_level'],
                        "anomaly_detected": prediction['anomaly_detected']
                    }
                    
                    dashboard_data["equipment_health"].append(health_data)
                    
                    # Contar por nivel de riesgo
                    alert_level = prediction['alert_level']
                    if alert_level in ['critical', 'high']:
                        dashboard_data["predictions_summary"]["high_risk"] += 1
                    elif alert_level == 'medium':
                        dashboard_data["predictions_summary"]["medium_risk"] += 1
                    else:
                        dashboard_data["predictions_summary"]["low_risk"] += 1
                    
                    # Agregar recomendaciones
                    if prediction['recommendations']:
                        dashboard_data["maintenance_recommendations"].extend(
                            prediction['recommendations'][:3]  # Máximo 3 por equipo
                        )
            
            # Limitar recomendaciones totales
            dashboard_data["maintenance_recommendations"] = list(set(
                dashboard_data["maintenance_recommendations"]
            ))[:10]
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generando dashboard de análisis predictivo: {e}")
            return {"error": str(e)}
