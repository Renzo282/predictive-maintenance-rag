"""
Conexión a base de datos Supabase
"""
import os
import logging
from typing import Dict, List, Any, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Conexión a Supabase establecida")
            except Exception as e:
                logger.error(f"Error conectando a Supabase: {e}")
        else:
            logger.warning("Variables de entorno de Supabase no configuradas")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Ejecutar consulta SQL"""
        try:
            if not self.client:
                raise Exception("Cliente de Supabase no inicializado")
            
            # Para consultas simples, usar RPC
            if query.strip().upper().startswith("SELECT"):
                # Convertir consulta SQL a formato Supabase
                if "FROM users" in query.upper():
                    result = self.client.table("users").select("*").execute()
                elif "FROM equipment" in query.upper():
                    result = self.client.table("equipment").select("*").execute()
                elif "FROM incidents" in query.upper():
                    result = self.client.table("incidents").select("*").execute()
                else:
                    result = self.client.rpc("execute_sql", {"query": query}).execute()
                
                return result.data if hasattr(result, 'data') else []
            
            # Para otras operaciones
            return []
            
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return []
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insertar datos en tabla"""
        try:
            if not self.client:
                raise Exception("Cliente de Supabase no inicializado")
            
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error insertando datos: {e}")
            return {}
    
    def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar datos en tabla"""
        try:
            if not self.client:
                raise Exception("Cliente de Supabase no inicializado")
            
            query = self.client.table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error actualizando datos: {e}")
            return {}
    
    def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """Eliminar datos de tabla"""
        try:
            if not self.client:
                raise Exception("Cliente de Supabase no inicializado")
            
            query = self.client.table(table)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.delete().execute()
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando datos: {e}")
            return False

# Instancia global
_db_connection = None

def get_db_connection() -> DatabaseConnection:
    """Obtener instancia de conexión a base de datos"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection

def get_supabase() -> Client:
    """Obtener cliente de Supabase"""
    db = get_db_connection()
    return db.client

async def init_db():
    """Inicializar base de datos"""
    try:
        db = get_db_connection()
        if db.client:
            logger.info("Base de datos inicializada correctamente")
        else:
            logger.warning("Base de datos no disponible")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
