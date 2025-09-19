"""
RAG (Retrieval-Augmented Generation) Agent for predictive maintenance
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from app.core.config import settings
from app.core.database import get_supabase

logger = logging.getLogger(__name__)


class RAGAgent:
    """RAG Agent for predictive maintenance analysis"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name="gpt-4",
            temperature=0.1
        )
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector store with historical data"""
        try:
            # Try to load existing vector store
            self.vector_store = Chroma(
                persist_directory=settings.VECTOR_STORE_PATH,
                embedding_function=self.embeddings
            )
            logger.info("Vector store loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {e}")
            self._create_vector_store()
    
    def _create_vector_store(self):
        """Create a new vector store from historical data"""
        try:
            # Get historical data from Supabase
            historical_data = self._get_historical_data()
            
            # Convert to documents
            documents = self._prepare_documents(historical_data)
            
            # Create vector store
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=settings.VECTOR_STORE_PATH
            )
            
            logger.info("Vector store created successfully")
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    def _get_historical_data(self) -> List[Dict[str, Any]]:
        """Retrieve historical data from Supabase"""
        supabase = get_supabase()
        
        # Get data from last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        
        try:
            response = supabase.table("sensor_data").select(
                "*, equipment:equipment_id(name, type, location)"
            ).gte("timestamp", six_months_ago.isoformat()).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Failed to retrieve historical data: {e}")
            return []
    
    def _prepare_documents(self, data: List[Dict[str, Any]]) -> List[Document]:
        """Convert historical data to documents for vector store"""
        documents = []
        
        for record in data:
            # Create a comprehensive document for each equipment
            equipment = record.get("equipment", {})
            doc_content = f"""
            Equipment: {equipment.get('name', 'Unknown')}
            Type: {equipment.get('type', 'Unknown')}
            Location: {equipment.get('location', 'Unknown')}
            Timestamp: {record.get('timestamp', 'Unknown')}
            Temperature: {record.get('temperature', 'N/A')}
            Vibration: {record.get('vibration', 'N/A')}
            Pressure: {record.get('pressure', 'N/A')}
            Humidity: {record.get('humidity', 'N/A')}
            Voltage: {record.get('voltage', 'N/A')}
            Current: {record.get('current', 'N/A')}
            """
            
            documents.append(Document(
                page_content=doc_content,
                metadata={
                    "equipment_id": record.get("equipment_id"),
                    "timestamp": record.get("timestamp"),
                    "equipment_name": equipment.get("name"),
                    "equipment_type": equipment.get("type")
                }
            ))
        
        return documents
    
    def analyze_patterns(self, equipment_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze patterns in equipment data"""
        try:
            supabase = get_supabase()
            
            # Get recent data
            start_date = datetime.now() - timedelta(days=days)
            response = supabase.table("sensor_data").select("*").eq(
                "equipment_id", equipment_id
            ).gte("timestamp", start_date.isoformat()).execute()
            
            if not response.data:
                return {"error": "No data available for analysis"}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(response.data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Analyze patterns
            patterns = {
                "temperature_trend": self._analyze_trend(df, 'temperature'),
                "vibration_trend": self._analyze_trend(df, 'vibration'),
                "pressure_trend": self._analyze_trend(df, 'pressure'),
                "anomalies": self._detect_anomalies(df),
                "correlations": self._analyze_correlations(df),
                "summary": self._generate_summary(df)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze patterns: {e}")
            return {"error": str(e)}
    
    def _analyze_trend(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Analyze trend for a specific column"""
        if column not in df.columns or df[column].isna().all():
            return {"trend": "no_data", "slope": 0, "r_squared": 0}
        
        # Remove NaN values
        clean_df = df.dropna(subset=[column])
        if len(clean_df) < 2:
            return {"trend": "insufficient_data", "slope": 0, "r_squared": 0}
        
        # Calculate trend
        x = np.arange(len(clean_df))
        y = clean_df[column].values
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        # Calculate R-squared
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.01:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "slope": float(slope),
            "r_squared": float(r_squared),
            "current_value": float(y[-1]) if len(y) > 0 else None,
            "average_value": float(np.mean(y))
        }
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in the data"""
        anomalies = []
        
        numeric_columns = ['temperature', 'vibration', 'pressure', 'humidity', 'voltage', 'current']
        
        for column in numeric_columns:
            if column not in df.columns or df[column].isna().all():
                continue
            
            # Remove NaN values
            clean_data = df[column].dropna()
            if len(clean_data) < 10:  # Need minimum data points
                continue
            
            # Calculate Z-scores
            mean = clean_data.mean()
            std = clean_data.std()
            
            if std == 0:  # No variation
                continue
            
            z_scores = np.abs((clean_data - mean) / std)
            anomaly_threshold = 2.5  # Z-score threshold
            
            # Find anomalies
            anomaly_indices = clean_data[z_scores > anomaly_threshold].index
            
            for idx in anomaly_indices:
                anomalies.append({
                    "column": column,
                    "timestamp": df.loc[idx, 'timestamp'].isoformat(),
                    "value": float(clean_data.loc[idx]),
                    "z_score": float(z_scores.loc[idx]),
                    "severity": "high" if z_scores.loc[idx] > 3 else "medium"
                })
        
        return anomalies
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze correlations between different metrics"""
        numeric_columns = ['temperature', 'vibration', 'pressure', 'humidity', 'voltage', 'current']
        available_columns = [col for col in numeric_columns if col in df.columns]
        
        if len(available_columns) < 2:
            return {}
        
        # Calculate correlation matrix
        corr_matrix = df[available_columns].corr()
        
        # Extract significant correlations (|r| > 0.5)
        correlations = {}
        for i in range(len(available_columns)):
            for j in range(i+1, len(available_columns)):
                col1, col2 = available_columns[i], available_columns[j]
                corr_value = corr_matrix.loc[col1, col2]
                
                if abs(corr_value) > 0.5:
                    correlations[f"{col1}_vs_{col2}"] = float(corr_value)
        
        return correlations
    
    def _generate_summary(self, df: pd.DataFrame) -> str:
        """Generate a summary of the data"""
        summary_parts = []
        
        # Data availability
        total_records = len(df)
        summary_parts.append(f"Total records analyzed: {total_records}")
        
        # Time range
        if not df.empty:
            start_time = df['timestamp'].min()
            end_time = df['timestamp'].max()
            summary_parts.append(f"Time range: {start_time} to {end_time}")
        
        # Data quality
        numeric_columns = ['temperature', 'vibration', 'pressure', 'humidity', 'voltage', 'current']
        available_columns = [col for col in numeric_columns if col in df.columns]
        
        for col in available_columns:
            non_null_count = df[col].count()
            completeness = (non_null_count / total_records) * 100
            summary_parts.append(f"{col} completeness: {completeness:.1f}%")
        
        return "\n".join(summary_parts)
    
    def generate_prediction(self, equipment_id: str, query: str) -> Dict[str, Any]:
        """Generate prediction using RAG"""
        try:
            # Create retrieval QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 5, "filter": {"equipment_id": equipment_id}}
                ),
                return_source_documents=True
            )
            
            # Generate response
            result = qa_chain({"query": query})
            
            return {
                "answer": result["result"],
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result["source_documents"]
                ],
                "confidence": self._calculate_confidence(result)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate prediction: {e}")
            return {"error": str(e)}
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score for the prediction"""
        # Simple confidence calculation based on source document relevance
        source_docs = result.get("source_documents", [])
        if not source_docs:
            return 0.0
        
        # For now, return a base confidence score
        # In a more sophisticated implementation, you could use
        # similarity scores or other metrics
        return min(0.9, 0.5 + (len(source_docs) * 0.1))
    
    def update_knowledge_base(self):
        """Update the knowledge base with new data"""
        try:
            # Get recent data that hasn't been processed
            recent_data = self._get_recent_data()
            
            if recent_data:
                # Convert to documents
                new_documents = self._prepare_documents(recent_data)
                
                # Add to vector store
                self.vector_store.add_documents(new_documents)
                
                logger.info(f"Updated knowledge base with {len(new_documents)} new documents")
            
        except Exception as e:
            logger.error(f"Failed to update knowledge base: {e}")
    
    def _get_recent_data(self) -> List[Dict[str, Any]]:
        """Get recent data that hasn't been processed yet"""
        supabase = get_supabase()
        
        # Get data from last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        
        try:
            response = supabase.table("sensor_data").select(
                "*, equipment:equipment_id(name, type, location)"
            ).gte("timestamp", yesterday.isoformat()).execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Failed to retrieve recent data: {e}")
            return []
