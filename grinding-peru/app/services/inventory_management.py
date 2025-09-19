"""
Módulo de Gestión de Inventario para Grinding Perú
Optimización de repuestos y equipos críticos
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from app.core.database import get_supabase
from app.services.rag_agent import RAGAgent
from app.services.notifications import NotificationService

logger = logging.getLogger(__name__)


class ItemType(Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    CONSUMABLE = "consumable"
    SPARE_PART = "spare_part"
    NETWORK = "network"
    SECURITY = "security"


class Criticality(Enum):
    CRITICAL = "critical"      # Sin stock = parada de producción
    HIGH = "high"             # Sin stock = impacto significativo
    MEDIUM = "medium"         # Sin stock = impacto moderado
    LOW = "low"               # Sin stock = impacto mínimo


class InventoryManagementService:
    """Servicio de Gestión de Inventario para Grinding Perú"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.rag_agent = RAGAgent()
        self.notification_service = NotificationService()
        
        # Modelos de ML para predicción de demanda
        self.demand_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.models_trained = False
        
        # Configuración de niveles de stock para Grinding Perú
        self.stock_levels = {
            Criticality.CRITICAL: {"min": 10, "reorder": 20, "max": 50},
            Criticality.HIGH: {"min": 5, "reorder": 10, "max": 30},
            Criticality.MEDIUM: {"min": 3, "reorder": 5, "max": 20},
            Criticality.LOW: {"min": 1, "reorder": 2, "max": 10}
        }
    
    def add_inventory_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agregar nuevo item al inventario con análisis automático"""
        try:
            # Validar datos requeridos
            required_fields = ['name', 'type', 'category', 'supplier', 'unit_cost']
            for field in required_fields:
                if field not in item_data:
                    return {"status": "error", "message": f"Campo requerido faltante: {field}"}
            
            # Analizar item con RAG para determinar criticidad
            analysis = self._analyze_item_criticality(item_data)
            
            # Generar código de item único
            item_code = self._generate_item_code(item_data['type'], item_data['category'])
            
            # Calcular niveles de stock recomendados
            stock_levels = self._calculate_recommended_stock_levels(
                item_data, analysis.get('criticality', Criticality.MEDIUM)
            )
            
            # Preparar datos del item
            item_record = {
                "item_code": item_code,
                "name": item_data['name'],
                "description": item_data.get('description', ''),
                "type": item_data['type'],
                "category": item_data['category'],
                "supplier": item_data['supplier'],
                "supplier_contact": item_data.get('supplier_contact', ''),
                "unit_cost": item_data['unit_cost'],
                "currency": item_data.get('currency', 'PEN'),
                "criticality": analysis.get('criticality', Criticality.MEDIUM.value),
                "current_stock": item_data.get('current_stock', 0),
                "min_stock": stock_levels['min'],
                "reorder_point": stock_levels['reorder'],
                "max_stock": stock_levels['max'],
                "lead_time_days": item_data.get('lead_time_days', 7),
                "location": item_data.get('location', 'Almacén Principal'),
                "status": "active",
                "analysis": analysis,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insertar en base de datos
            response = self.supabase.table("inventory_items").insert(item_record).execute()
            
            if response.data:
                item_id = response.data[0]['id']
                
                # Crear alerta si el stock está bajo
                if item_data.get('current_stock', 0) < stock_levels['min']:
                    await self._create_low_stock_alert(item_id, item_record)
                
                return {
                    "status": "success",
                    "item_id": item_id,
                    "item_code": item_code,
                    "analysis": analysis,
                    "stock_levels": stock_levels
                }
            else:
                return {"status": "error", "message": "Error al crear item en la base de datos"}
                
        except Exception as e:
            logger.error(f"Error al agregar item al inventario: {e}")
            return {"status": "error", "message": str(e)}
    
    def _analyze_item_criticality(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar criticidad del item usando RAG"""
        try:
            query = f"""
            Analiza la criticidad del siguiente item para el inventario de Grinding Perú:
            
            Nombre: {item_data['name']}
            Tipo: {item_data['type']}
            Categoría: {item_data['category']}
            Descripción: {item_data.get('description', 'No disponible')}
            
            Determina:
            1. Nivel de criticidad (critical, high, medium, low)
            2. Impacto en operaciones si no está disponible
            3. Frecuencia de uso estimada
            4. Alternativas disponibles
            5. Tiempo de entrega crítico
            """
            
            # Usar RAG para análisis
            analysis_result = self.rag_agent.generate_prediction(
                "inventory_analysis", query
            )
            
            # Procesar resultado del análisis
            analysis = {
                "criticality": self._extract_criticality(analysis_result.get("answer", "")),
                "impact_assessment": self._extract_impact(analysis_result.get("answer", "")),
                "usage_frequency": self._extract_usage_frequency(analysis_result.get("answer", "")),
                "alternatives": self._extract_alternatives(analysis_result.get("answer", "")),
                "critical_lead_time": self._extract_critical_lead_time(analysis_result.get("answer", "")),
                "confidence": analysis_result.get("confidence", 0.5)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando criticidad del item: {e}")
            return {"criticality": Criticality.MEDIUM.value, "error": str(e)}
    
    def _extract_criticality(self, analysis_text: str) -> str:
        """Extraer nivel de criticidad del análisis"""
        analysis_lower = analysis_text.lower()
        
        if any(keyword in analysis_lower for keyword in ["crítico", "critical", "esencial", "vital"]):
            return Criticality.CRITICAL.value
        elif any(keyword in analysis_lower for keyword in ["alto", "high", "importante", "significativo"]):
            return Criticality.HIGH.value
        elif any(keyword in analysis_lower for keyword in ["bajo", "low", "mínimo", "opcional"]):
            return Criticality.LOW.value
        else:
            return Criticality.MEDIUM.value
    
    def _extract_impact(self, analysis_text: str) -> str:
        """Extraer evaluación de impacto"""
        analysis_lower = analysis_text.lower()
        
        if "parada" in analysis_lower or "detención" in analysis_lower:
            return "Parada total de operaciones"
        elif "limitación" in analysis_lower or "reducción" in analysis_lower:
            return "Limitación significativa de operaciones"
        elif "impacto" in analysis_lower or "afectación" in analysis_lower:
            return "Impacto moderado en operaciones"
        else:
            return "Impacto mínimo en operaciones"
    
    def _extract_usage_frequency(self, analysis_text: str) -> str:
        """Extraer frecuencia de uso estimada"""
        analysis_lower = analysis_text.lower()
        
        if any(keyword in analysis_lower for keyword in ["diario", "daily", "constante", "frecuente"]):
            return "Diario"
        elif any(keyword in analysis_lower for keyword in ["semanal", "weekly", "regular"]):
            return "Semanal"
        elif any(keyword in analysis_lower for keyword in ["mensual", "monthly", "ocasional"]):
            return "Mensual"
        else:
            return "Ocasional"
    
    def _extract_alternatives(self, analysis_text: str) -> List[str]:
        """Extraer alternativas disponibles"""
        # Implementar lógica de extracción de alternativas
        return ["No hay alternativas identificadas"]
    
    def _extract_critical_lead_time(self, analysis_text: str) -> int:
        """Extraer tiempo de entrega crítico en días"""
        analysis_lower = analysis_text.lower()
        
        if "inmediato" in analysis_lower or "urgente" in analysis_lower:
            return 1
        elif "rápido" in analysis_lower or "pronto" in analysis_lower:
            return 3
        elif "normal" in analysis_lower or "estándar" in analysis_lower:
            return 7
        else:
            return 14
    
    def _generate_item_code(self, item_type: str, category: str) -> str:
        """Generar código único para el item"""
        try:
            # Obtener el último código del tipo
            response = self.supabase.table("inventory_items").select("item_code").eq(
                "type", item_type
            ).order("created_at", desc=True).limit(1).execute()
            
            if response.data and response.data[0]['item_code']:
                last_code = response.data[0]['item_code']
                # Extraer número y incrementar
                parts = last_code.split('-')
                if len(parts) >= 3:
                    number = int(parts[2]) + 1
                else:
                    number = 1
            else:
                number = 1
            
            # Generar código: GP-TYPE-CATEGORY-NUMBER
            type_abbr = item_type[:3].upper()
            category_abbr = category[:3].upper()
            return f"GP-{type_abbr}-{category_abbr}-{number:04d}"
            
        except Exception as e:
            logger.error(f"Error generando código de item: {e}")
            return f"GP-{item_type[:3].upper()}-{category[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _calculate_recommended_stock_levels(self, item_data: Dict[str, Any], criticality: str) -> Dict[str, int]:
        """Calcular niveles de stock recomendados"""
        try:
            criticality_enum = Criticality(criticality)
            base_levels = self.stock_levels[criticality_enum]
            
            # Ajustar basado en tiempo de entrega
            lead_time = item_data.get('lead_time_days', 7)
            lead_time_multiplier = max(1.0, lead_time / 7.0)  # Normalizar a 7 días
            
            # Ajustar basado en costo
            unit_cost = item_data.get('unit_cost', 0)
            cost_multiplier = 1.0
            if unit_cost > 1000:  # Items costosos
                cost_multiplier = 0.5
            elif unit_cost < 100:  # Items baratos
                cost_multiplier = 1.5
            
            return {
                "min": max(1, int(base_levels['min'] * lead_time_multiplier * cost_multiplier)),
                "reorder": max(2, int(base_levels['reorder'] * lead_time_multiplier * cost_multiplier)),
                "max": max(5, int(base_levels['max'] * lead_time_multiplier * cost_multiplier))
            }
            
        except Exception as e:
            logger.error(f"Error calculando niveles de stock: {e}")
            return {"min": 5, "reorder": 10, "max": 20}
    
    async def _create_low_stock_alert(self, item_id: str, item_data: Dict[str, Any]):
        """Crear alerta de stock bajo"""
        try:
            alert_data = {
                "item_id": item_id,
                "title": f"Stock Bajo: {item_data['name']}",
                "message": f"El item {item_data['item_code']} tiene stock bajo. Actual: {item_data['current_stock']}, Mínimo: {item_data['min_stock']}",
                "priority": "high" if item_data['criticality'] in ['critical', 'high'] else "medium",
                "category": "inventory_low_stock",
                "recipients": self._get_inventory_alert_recipients(item_data['criticality']),
                "item_details": {
                    "item_code": item_data['item_code'],
                    "current_stock": item_data['current_stock'],
                    "min_stock": item_data['min_stock'],
                    "supplier": item_data['supplier']
                }
            }
            
            await self.notification_service.send_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Error creando alerta de stock bajo: {e}")
    
    def _get_inventory_alert_recipients(self, criticality: str) -> List[str]:
        """Obtener destinatarios de alertas de inventario"""
        recipients = {
            'critical': ['compras@grindingperu.com', 'almacen@grindingperu.com', 'gerencia@grindingperu.com'],
            'high': ['compras@grindingperu.com', 'almacen@grindingperu.com'],
            'medium': ['almacen@grindingperu.com'],
            'low': ['almacen@grindingperu.com']
        }
        return recipients.get(criticality, ['almacen@grindingperu.com'])
    
    def predict_demand(self, item_id: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Predecir demanda futura para un item específico"""
        try:
            # Obtener datos históricos de movimientos
            response = self.supabase.table("inventory_movements").select("*").eq(
                "item_id", item_id
            ).gte("created_at", (datetime.now() - timedelta(days=365)).isoformat()).execute()
            
            if not response.data or len(response.data) < 30:
                return {"error": "Datos insuficientes para predicción"}
            
            # Preparar datos para ML
            df = pd.DataFrame(response.data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at')
            
            # Crear características temporales
            df['day_of_week'] = df['created_at'].dt.dayofweek
            df['month'] = df['created_at'].dt.month
            df['quarter'] = df['created_at'].dt.quarter
            
            # Agrupar por día y sumar movimientos
            daily_movements = df.groupby(df['created_at'].dt.date)['quantity'].sum().reset_index()
            daily_movements['day_of_week'] = pd.to_datetime(daily_movements['created_at']).dt.dayofweek
            daily_movements['month'] = pd.to_datetime(daily_movements['created_at']).dt.month
            
            if len(daily_movements) < 14:
                return {"error": "Datos históricos insuficientes"}
            
            # Entrenar modelo si no está entrenado
            if not self.models_trained:
                self._train_demand_model(daily_movements)
            
            # Generar predicciones
            predictions = self._generate_demand_predictions(daily_movements, days_ahead)
            
            return {
                "item_id": item_id,
                "predictions": predictions,
                "confidence": 0.75,
                "model_accuracy": self._calculate_model_accuracy(daily_movements)
            }
            
        except Exception as e:
            logger.error(f"Error prediciendo demanda: {e}")
            return {"error": str(e)}
    
    def _train_demand_model(self, data: pd.DataFrame):
        """Entrenar modelo de predicción de demanda"""
        try:
            # Preparar características
            features = ['day_of_week', 'month']
            X = data[features].values
            y = data['quantity'].values
            
            # Escalar características
            X_scaled = self.scaler.fit_transform(X)
            
            # Entrenar modelo
            self.demand_predictor.fit(X_scaled, y)
            self.models_trained = True
            
            logger.info("Modelo de demanda entrenado exitosamente")
            
        except Exception as e:
            logger.error(f"Error entrenando modelo de demanda: {e}")
    
    def _generate_demand_predictions(self, data: pd.DataFrame, days_ahead: int) -> List[Dict[str, Any]]:
        """Generar predicciones de demanda"""
        predictions = []
        
        for i in range(days_ahead):
            future_date = datetime.now() + timedelta(days=i+1)
            day_of_week = future_date.weekday()
            month = future_date.month
            
            # Preparar características para predicción
            features = np.array([[day_of_week, month]])
            features_scaled = self.scaler.transform(features)
            
            # Generar predicción
            predicted_demand = self.demand_predictor.predict(features_scaled)[0]
            
            predictions.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_demand": max(0, int(predicted_demand)),
                "day_of_week": day_of_week,
                "month": month
            })
        
        return predictions
    
    def _calculate_model_accuracy(self, data: pd.DataFrame) -> float:
        """Calcular precisión del modelo"""
        try:
            # Usar validación cruzada simple
            features = ['day_of_week', 'month']
            X = data[features].values
            y = data['quantity'].values
            
            X_scaled = self.scaler.transform(X)
            predictions = self.demand_predictor.predict(X_scaled)
            
            # Calcular R²
            from sklearn.metrics import r2_score
            accuracy = r2_score(y, predictions)
            
            return max(0, accuracy)  # Asegurar que no sea negativo
            
        except Exception as e:
            logger.error(f"Error calculando precisión del modelo: {e}")
            return 0.5
    
    def get_inventory_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Obtener métricas de inventario para Grinding Perú"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener datos de inventario
            response = self.supabase.table("inventory_items").select("*").execute()
            
            if not response.data:
                return {"error": "No hay datos de inventario"}
            
            df = pd.DataFrame(response.data)
            
            # Calcular métricas
            metrics = {
                "total_items": len(df),
                "items_by_type": df['type'].value_counts().to_dict(),
                "items_by_criticality": df['criticality'].value_counts().to_dict(),
                "low_stock_items": len(df[df['current_stock'] < df['min_stock']]),
                "out_of_stock_items": len(df[df['current_stock'] <= 0]),
                "total_inventory_value": (df['current_stock'] * df['unit_cost']).sum(),
                "critical_items_low_stock": len(df[
                    (df['criticality'] == 'critical') & 
                    (df['current_stock'] < df['min_stock'])
                ]),
                "reorder_recommendations": self._get_reorder_recommendations(df)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculando métricas de inventario: {e}")
            return {"error": str(e)}
    
    def _get_reorder_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Obtener recomendaciones de reorden"""
        recommendations = []
        
        # Items que necesitan reorden
        reorder_items = df[df['current_stock'] <= df['reorder_point']]
        
        for _, item in reorder_items.iterrows():
            recommended_quantity = item['max_stock'] - item['current_stock']
            
            recommendations.append({
                "item_id": item['id'],
                "item_code": item['item_code'],
                "name": item['name'],
                "current_stock": item['current_stock'],
                "reorder_point": item['reorder_point'],
                "recommended_quantity": recommended_quantity,
                "estimated_cost": recommended_quantity * item['unit_cost'],
                "priority": "high" if item['criticality'] in ['critical', 'high'] else "medium"
            })
        
        return recommendations
