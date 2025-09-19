"""
Sistema de Autenticación y Autorización para Grinding Perú
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.core.config import settings
from app.core.database import get_supabase

logger = logging.getLogger(__name__)

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Modelos Pydantic
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str
    department: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    department: str
    is_active: bool
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None

# Roles y permisos para Grinding Perú
ROLES = {
    "tecnico": {
        "name": "Técnico",
        "permissions": [
            "view_incidents",
            "create_incidents",
            "update_incidents",
            "view_equipment",
            "update_equipment_status",
            "view_maintenance_history"
        ]
    },
    "supervisor": {
        "name": "Supervisor",
        "permissions": [
            "view_incidents",
            "create_incidents",
            "update_incidents",
            "assign_incidents",
            "view_all_incidents",
            "view_equipment",
            "update_equipment_status",
            "view_maintenance_history",
            "view_reports",
            "manage_technicians"
        ]
    },
    "administrador": {
        "name": "Administrador",
        "permissions": [
            "view_incidents",
            "create_incidents",
            "update_incidents",
            "assign_incidents",
            "view_all_incidents",
            "delete_incidents",
            "view_equipment",
            "create_equipment",
            "update_equipment",
            "delete_equipment",
            "view_maintenance_history",
            "create_maintenance",
            "view_reports",
            "create_reports",
            "manage_users",
            "manage_technicians",
            "view_audit_logs",
            "system_configuration"
        ]
    }
}

class AuthenticationService:
    """Servicio de autenticación y autorización"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generar hash de contraseña"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token de acceso JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verificar y decodificar token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            role: str = payload.get("role")
            
            if username is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(username=username, user_id=user_id, role=role)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuario"""
        try:
            # Buscar usuario en base de datos
            response = self.supabase.table("users").select("*").eq("username", username).execute()
            
            if not response.data:
                return None
            
            user = response.data[0]
            
            # Verificar contraseña
            if not self.verify_password(password, user["hashed_password"]):
                return None
            
            # Verificar si el usuario está activo
            if not user.get("is_active", True):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error autenticando usuario: {e}")
            return None
    
    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Crear nuevo usuario"""
        try:
            # Verificar si el usuario ya existe
            existing_user = self.supabase.table("users").select("id").eq("username", user_data.username).execute()
            if existing_user.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya existe"
                )
            
            # Verificar si el email ya existe
            existing_email = self.supabase.table("users").select("id").eq("email", user_data.email).execute()
            if existing_email.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
            
            # Verificar que el rol sea válido
            if user_data.role not in ROLES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol inválido. Roles disponibles: {list(ROLES.keys())}"
                )
            
            # Crear hash de contraseña
            hashed_password = self.get_password_hash(user_data.password)
            
            # Preparar datos del usuario
            user_record = {
                "username": user_data.username,
                "email": user_data.email,
                "hashed_password": hashed_password,
                "full_name": user_data.full_name,
                "role": user_data.role,
                "department": user_data.department,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insertar usuario en base de datos
            response = self.supabase.table("users").insert(user_record).execute()
            
            if response.data:
                user_id = response.data[0]["id"]
                
                # Crear token de acceso
                access_token = self.create_access_token(
                    data={"sub": user_data.username, "user_id": user_id, "role": user_data.role}
                )
                
                return {
                    "user": {
                        "id": user_id,
                        "username": user_data.username,
                        "email": user_data.email,
                        "full_name": user_data.full_name,
                        "role": user_data.role,
                        "department": user_data.department,
                        "is_active": True
                    },
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error creando usuario"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Iniciar sesión de usuario"""
        try:
            user = await self.authenticate_user(username, password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Crear token de acceso
            access_token = self.create_access_token(
                data={"sub": user["username"], "user_id": user["id"], "role": user["role"]}
            )
            
            return {
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "role": user["role"],
                    "department": user["department"],
                    "is_active": user["is_active"]
                },
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error en login: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Obtener usuario actual desde token"""
        try:
            token_data = self.verify_token(credentials.credentials)
            
            # Buscar usuario en base de datos
            response = self.supabase.table("users").select("*").eq("id", token_data.user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = response.data[0]
            
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario inactivo",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo usuario actual: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def check_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """Verificar si el usuario tiene un permiso específico"""
        user_role = user.get("role")
        if not user_role or user_role not in ROLES:
            return False
        
        return permission in ROLES[user_role]["permissions"]
    
    def require_permission(self, permission: str):
        """Decorador para requerir un permiso específico"""
        def permission_checker(current_user: Dict[str, Any] = Depends(self.get_current_user)):
            if not self.check_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para realizar esta acción"
                )
            return current_user
        return permission_checker
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID"""
        try:
            response = self.supabase.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID: {e}")
            return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar usuario"""
        try:
            # Verificar que el usuario existe
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            # Actualizar datos
            update_data["updated_at"] = datetime.now().isoformat()
            
            response = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error actualizando usuario"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Desactivar usuario"""
        try:
            response = self.supabase.table("users").update({
                "is_active": False,
                "updated_at": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error desactivando usuario: {e}")
            return False
    
    async def get_users_by_role(self, role: str) -> List[Dict[str, Any]]:
        """Obtener usuarios por rol"""
        try:
            response = self.supabase.table("users").select("*").eq("role", role).eq("is_active", True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error obteniendo usuarios por rol: {e}")
            return []
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Obtener todos los usuarios"""
        try:
            response = self.supabase.table("users").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error obteniendo todos los usuarios: {e}")
            return []

# Instancia global del servicio
auth_service = AuthenticationService()
