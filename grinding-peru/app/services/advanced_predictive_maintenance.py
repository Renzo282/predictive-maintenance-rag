"""
Sistema Avanzado de Mantenimiento Predictivo con RAG
Para Grinding Perú - Soporte a la Decisión Inteligente
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import logging
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class AdvancedPredictiveMaintenance:
    """
    Sistema avanzado de mantenimiento predictivo que combina:
    - Machine Learning para predicción de fallas
    - RAG para recomendaciones contextuales
    - Análisis de tendencias
    - Alertas inteligentes
    """
    
    def __init__(self, db_connection, openai_api_key: str):
        self.db = db_connection
        self.openai_api_key = openai_api_key
        
        # Configurar OpenAI
        openai.api_key = openai_api_key
        
        # Inicializar modelos ML
        self.failure_predictor = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Inicializar RAG
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.vectorstore = None
        self.qa_chain = None
        
        # Inicializar base de conocimiento
        self._initialize_knowledge_base()
        
    def _initialize_knowledge_base(self):
        """Inicializa la base de conocimiento RAG"""
        try:
            # Configurar ChromaDB
            chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # Crear colección para documentos técnicos
            self.vectorstore = Chroma(
                client=chroma_client,
                collection_name="maintenance_knowledge",
                embedding_function=self.embeddings
            )
            
            # Cargar documentos de conocimiento
            self._load_knowledge_documents()
            
            # Configurar cadena de QA
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(openai_api_key=self.openai_api_key, temperature=0),
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                return_source_documents=True
            )
            
            logger.info("Base de conocimiento RAG inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando base de conocimiento: {e}")
    
    def _load_knowledge_documents(self):
        """Carga documentos técnicos en la base de conocimiento"""
        try:
            # Documentos de conocimiento técnico
            knowledge_docs = [
                {
                    "content": """
                    MANTENIMIENTO PREVENTIVO - MOTORES ELÉCTRICOS
                    
                    Síntomas de falla inminente:
                    - Vibración excesiva (>2.5 mm/s)
                    - Temperatura elevada (>80°C)
                    - Ruido anormal
                    - Consumo de corriente irregular
                    
                    Acciones preventivas:
                    1. Lubricación de rodamientos cada 3 meses
                    2. Verificación de alineación cada 6 meses
                    3. Medición de vibraciones mensual
                    4. Análisis de aceite cada 6 meses
                    
                    Técnicos recomendados:
                    - Especialidad: Mecánico/Electrico
                    - Experiencia mínima: 3 años
                    - Certificaciones: ISO 18436-2
                    """,
                    "metadata": {"type": "motor_electrico", "category": "preventivo"}
                },
                {
                    "content": """
                    MANTENIMIENTO PREDICTIVO - BOMBAS CENTRÍFUGAS
                    
                    Indicadores de falla:
                    - Caída de presión >15%
                    - Eficiencia <85%
                    - Cavitación audible
                    - Desgaste de impulsores
                    
                    Protocolo de mantenimiento:
                    1. Inspección visual diaria
                    2. Medición de vibraciones semanal
                    3. Análisis de aceite mensual
                    4. Revisión de sellos cada 3 meses
                    
                    Especialistas requeridos:
                    - Mecánico hidráulico
                    - Técnico en bombas
                    - Experiencia en sistemas de bombeo
                    """,
                    "metadata": {"type": "bomba_centrifuga", "category": "predictivo"}
                },
                {
                    "content": """
                    DIAGNÓSTICO DE FALLAS - SISTEMAS NEUMÁTICOS
                    
                    Fallas comunes:
                    1. Fuga de aire: Verificar conexiones y juntas
                    2. Presión insuficiente: Revisar compresor y filtros
                    3. Contaminación: Cambiar filtros y secadores
                    4. Desgaste de cilindros: Inspeccionar sellos
                    
                    Herramientas de diagnóstico:
                    - Manómetros digitales
                    - Detector de fugas ultrasónico
                    - Análisis de aceite neumático
                    
                    Técnicos especializados:
                    - Especialidad: Neumática
                    - Certificación: ISO 8573
                    - Experiencia en sistemas industriales
                    """,
                    "metadata": {"type": "neumatico", "category": "diagnostico"}
                },
                {
                    "content": """
                    MANTENIMIENTO CRÍTICO - GENERADORES
                    
                    Parámetros críticos:
                    - Voltaje: 220V ±5%
                    - Frecuencia: 60Hz ±0.5%
                    - Temperatura: <90°C
                    - Vibración: <2.8 mm/s
                    
                    Checklist de mantenimiento:
                    □ Verificación de conexiones eléctricas
                    □ Prueba de arranque automático
                    □ Medición de aislamiento
                    □ Revisión de sistema de combustible
                    □ Calibración de sensores
                    
                    Personal calificado:
                    - Electricista industrial
                    - Técnico en generadores
                    - Certificación en sistemas de emergencia
                    """,
                    "metadata": {"type": "generador", "category": "critico"}
                }
            ]
            
            # Agregar documentos al vectorstore
            for doc in knowledge_docs:
                self.vectorstore.add_texts(
                    texts=[doc["content"]],
                    metadatas=[doc["metadata"]]
                )
            
            logger.info(f"Cargados {len(knowledge_docs)} documentos de conocimiento")
            
        except Exception as e:
            logger.error(f"Error cargando documentos: {e}")
    
    def predict_failure(
        self, 
        equipment_data: Dict,
        sensor_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Predice fallas basado en datos de sensores y características del equipo
        
        Args:
            equipment_data: Información del equipo
            sensor_data: Datos de sensores históricos
            
        Returns:
            Predicción con probabilidad y recomendaciones
        """
        try:
            # 1. Preparar datos para ML
            features = self._prepare_features(equipment_data, sensor_data)
            
            # 2. Detectar anomalías
            anomaly_score = self._detect_anomalies(features)
            
            # 3. Predecir falla
            failure_probability = self._predict_failure_probability(features)
            
            # 4. Generar recomendaciones RAG
            recommendations = self._get_rag_recommendations(
                equipment_data, 
                sensor_data, 
                failure_probability
            )
            
            # 5. Determinar criticidad
            criticality = self._assess_criticality(
                failure_probability, 
                anomaly_score, 
                equipment_data
            )
            
            return {
                "failure_probability": failure_probability,
                "anomaly_score": anomaly_score,
                "criticality": criticality,
                "recommendations": recommendations,
                "predicted_failure_type": self._predict_failure_type(features),
                "time_to_failure": self._estimate_time_to_failure(features),
                "confidence": self._calculate_confidence(features),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en predicción de falla: {e}")
            return {
                "error": str(e),
                "failure_probability": 0.0,
                "criticality": "unknown"
            }
    
    def _prepare_features(self, equipment_data: Dict, sensor_data: List[Dict]) -> np.ndarray:
        """Prepara características para el modelo ML"""
        try:
            features = []
            
            # Características del equipo
            features.extend([
                equipment_data.get('age_months', 0),
                equipment_data.get('operating_hours', 0),
                equipment_data.get('maintenance_frequency', 0)
            ])
            
            # Características de sensores (últimos 7 días)
            if sensor_data:
                sensor_df = pd.DataFrame(sensor_data)
                sensor_df['timestamp'] = pd.to_datetime(sensor_df['timestamp'])
                recent_data = sensor_df[sensor_df['timestamp'] >= 
                                      datetime.now() - timedelta(days=7)]
                
                if not recent_data.empty:
                    # Estadísticas de sensores
                    for sensor_type in ['temperature', 'vibration', 'pressure', 'current']:
                        if sensor_type in recent_data.columns:
                            features.extend([
                                recent_data[sensor_type].mean(),
                                recent_data[sensor_type].std(),
                                recent_data[sensor_type].max(),
                                recent_data[sensor_type].min()
                            ])
                        else:
                            features.extend([0, 0, 0, 0])
                else:
                    features.extend([0] * 16)  # 4 sensores * 4 estadísticas
            else:
                features.extend([0] * 16)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparando características: {e}")
            return np.zeros((1, 19))  # 3 + 16 características
    
    def _detect_anomalies(self, features: np.ndarray) -> float:
        """Detecta anomalías en los datos"""
        try:
            # Normalizar características
            features_scaled = self.scaler.fit_transform(features)
            
            # Detectar anomalías
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            
            # Normalizar score a 0-1
            return max(0, min(1, (anomaly_score + 0.5) / 1.0))
            
        except Exception as e:
            logger.error(f"Error detectando anomalías: {e}")
            return 0.5
    
    def _predict_failure_probability(self, features: np.ndarray) -> float:
        """Predice probabilidad de falla"""
        try:
            # Normalizar características
            features_scaled = self.scaler.fit_transform(features)
            
            # Predecir probabilidad
            probability = self.failure_predictor.predict_proba(features_scaled)[0]
            
            # Retornar probabilidad de clase positiva (falla)
            return probability[1] if len(probability) > 1 else probability[0]
            
        except Exception as e:
            logger.error(f"Error prediciendo falla: {e}")
            return 0.0
    
    def _get_rag_recommendations(
        self, 
        equipment_data: Dict, 
        sensor_data: List[Dict], 
        failure_probability: float
    ) -> List[Dict]:
        """Obtiene recomendaciones usando RAG"""
        try:
            # Construir consulta contextual
            query = f"""
            Equipo: {equipment_data.get('type', 'desconocido')}
            Probabilidad de falla: {failure_probability:.2%}
            Datos de sensores: {len(sensor_data)} mediciones
            
            ¿Qué acciones preventivas recomiendas?
            ¿Qué técnicos especializados necesito?
            ¿Cuáles son los pasos críticos a seguir?
            """
            
            # Obtener respuesta de RAG
            result = self.qa_chain({"query": query})
            
            # Procesar respuesta
            recommendations = []
            
            if result and 'result' in result:
                response = result['result']
                
                # Extraer recomendaciones estructuradas
                recommendations = self._parse_rag_response(response)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones RAG: {e}")
            return [{"type": "error", "message": "No se pudieron obtener recomendaciones"}]
    
    def _parse_rag_response(self, response: str) -> List[Dict]:
        """Parsea respuesta RAG en recomendaciones estructuradas"""
        try:
            recommendations = []
            
            # Buscar acciones preventivas
            if "lubricación" in response.lower():
                recommendations.append({
                    "type": "preventive",
                    "action": "Verificar lubricación",
                    "priority": "high",
                    "technician_type": "mecanico"
                })
            
            if "vibración" in response.lower():
                recommendations.append({
                    "type": "measurement",
                    "action": "Medir vibraciones",
                    "priority": "high",
                    "technician_type": "mecanico"
                })
            
            if "temperatura" in response.lower():
                recommendations.append({
                    "type": "monitoring",
                    "action": "Monitorear temperatura",
                    "priority": "medium",
                    "technician_type": "electrico"
                })
            
            # Recomendación por defecto si no se encuentra nada específico
            if not recommendations:
                recommendations.append({
                    "type": "inspection",
                    "action": "Inspección general del equipo",
                    "priority": "medium",
                    "technician_type": "mecanico"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error parseando respuesta RAG: {e}")
            return []
    
    def _assess_criticality(
        self, 
        failure_probability: float, 
        anomaly_score: float, 
        equipment_data: Dict
    ) -> str:
        """Evalúa criticidad de la situación"""
        try:
            # Factores de criticidad
            equipment_criticality = equipment_data.get('criticality', 'medium')
            operating_hours = equipment_data.get('operating_hours', 0)
            
            # Calcular score de criticidad
            criticality_score = (
                failure_probability * 0.4 +
                anomaly_score * 0.3 +
                (1 if equipment_criticality == 'high' else 0.5) * 0.3
            )
            
            # Determinar nivel de criticidad
            if criticality_score >= 0.8:
                return "critical"
            elif criticality_score >= 0.6:
                return "high"
            elif criticality_score >= 0.4:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Error evaluando criticidad: {e}")
            return "unknown"
    
    def _predict_failure_type(self, features: np.ndarray) -> str:
        """Predice tipo de falla más probable"""
        try:
            # Lógica simple basada en características
            if features[0, 0] > 0.7:  # Temperatura alta
                return "sobrecalentamiento"
            elif features[0, 1] > 0.7:  # Vibración alta
                return "desbalance"
            elif features[0, 2] > 0.7:  # Presión alta
                return "sobrepresión"
            else:
                return "desgaste_general"
                
        except Exception as e:
            logger.error(f"Error prediciendo tipo de falla: {e}")
            return "desconocido"
    
    def _estimate_time_to_failure(self, features: np.ndarray) -> int:
        """Estima tiempo hasta falla en horas"""
        try:
            # Modelo simple de estimación
            base_hours = 168  # 1 semana base
            
            # Ajustar según características
            if features[0, 0] > 0.8:  # Temperatura crítica
                return max(24, base_hours * 0.2)
            elif features[0, 1] > 0.8:  # Vibración crítica
                return max(48, base_hours * 0.4)
            else:
                return base_hours
                
        except Exception as e:
            logger.error(f"Error estimando tiempo de falla: {e}")
            return 168
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """Calcula confianza en la predicción"""
        try:
            # Confianza basada en cantidad y calidad de datos
            data_quality = np.std(features)  # Variabilidad de datos
            confidence = min(0.95, max(0.5, 1 - data_quality))
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculando confianza: {e}")
            return 0.5
    
    def train_models(self, historical_data: List[Dict]):
        """Entrena modelos ML con datos históricos"""
        try:
            # Preparar datos de entrenamiento
            df = pd.DataFrame(historical_data)
            
            # Separar características y etiquetas
            feature_columns = [
                'age_months', 'operating_hours', 'maintenance_frequency',
                'avg_temperature', 'avg_vibration', 'avg_pressure', 'avg_current'
            ]
            
            X = df[feature_columns].fillna(0)
            y = df['failure_occurred'].astype(int)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Normalizar características
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entrenar modelo de predicción
            self.failure_predictor.fit(X_train_scaled, y_train)
            
            # Entrenar detector de anomalías
            self.anomaly_detector.fit(X_train_scaled)
            
            # Evaluar modelo
            y_pred = self.failure_predictor.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Modelo entrenado con accuracy: {accuracy:.3f}")
            
            return {
                "accuracy": accuracy,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error entrenando modelos: {e}")
            return {"error": str(e)}
    
    def get_maintenance_schedule(self, equipment_id: int) -> Dict:
        """Genera cronograma de mantenimiento personalizado"""
        try:
            # Obtener datos del equipo
            equipment_data = self._get_equipment_data(equipment_id)
            
            # Generar recomendaciones RAG para cronograma
            query = f"""
            Generar cronograma de mantenimiento para:
            - Equipo: {equipment_data.get('type', 'desconocido')}
            - Horas de operación: {equipment_data.get('operating_hours', 0)}
            - Último mantenimiento: {equipment_data.get('last_maintenance', 'desconocido')}
            
            Incluir:
            - Tareas diarias, semanales, mensuales
            - Especialistas requeridos
            - Herramientas necesarias
            - Tiempo estimado por tarea
            """
            
            result = self.qa_chain({"query": query})
            
            return {
                "equipment_id": equipment_id,
                "schedule": self._parse_maintenance_schedule(result),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generando cronograma: {e}")
            return {"error": str(e)}
    
    def _get_equipment_data(self, equipment_id: int) -> Dict:
        """Obtiene datos del equipo desde la base de datos"""
        try:
            query = """
            SELECT * FROM equipment 
            WHERE id = %s
            """
            result = self.db.execute_query(query, (equipment_id,))
            return result[0] if result else {}
            
        except Exception as e:
            logger.error(f"Error obteniendo datos del equipo: {e}")
            return {}
    
    def _parse_maintenance_schedule(self, rag_result) -> List[Dict]:
        """Parsea resultado RAG en cronograma estructurado"""
        try:
            # Cronograma por defecto
            schedule = [
                {
                    "frequency": "daily",
                    "tasks": [
                        {"name": "Inspección visual", "duration": 15, "technician": "operador"},
                        {"name": "Verificación de parámetros", "duration": 10, "technician": "operador"}
                    ]
                },
                {
                    "frequency": "weekly",
                    "tasks": [
                        {"name": "Medición de vibraciones", "duration": 30, "technician": "mecanico"},
                        {"name": "Verificación de lubricación", "duration": 20, "technician": "mecanico"}
                    ]
                },
                {
                    "frequency": "monthly",
                    "tasks": [
                        {"name": "Análisis de aceite", "duration": 60, "technician": "mecanico"},
                        {"name": "Calibración de sensores", "duration": 45, "technician": "electrico"}
                    ]
                }
            ]
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error parseando cronograma: {e}")
            return []
