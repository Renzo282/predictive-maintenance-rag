"""
Aplicación principal para Grinding Perú
Agente Inteligente de Mantenimiento Predictivo con RAG
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db
from app.api.grinding_peru_enhanced_routes import router as grinding_peru_router
from app.api.integrated_routes import router as integrated_router
from app.services.monitoring import start_monitoring
from app.services.notifications import NotificationService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Iniciando Agente Inteligente de Mantenimiento Predictivo - Grinding Perú...")
    await init_db()
    await start_monitoring()
    logger.info("Aplicación iniciada exitosamente")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")


# Create FastAPI application
app = FastAPI(
    title="Agente Inteligente de Mantenimiento Predictivo - Grinding Perú",
    description="Sistema de gestión de servicios IT con RAG para Grinding Perú, alineado con ISO/IEC 20000",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar apropiadamente para producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(grinding_peru_router, prefix="/api/v1/grinding-peru")
app.include_router(integrated_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agente Inteligente de Mantenimiento Predictivo - Grinding Perú",
        "version": "1.0.0",
        "company": "Grinding Perú",
        "compliance": "ISO/IEC 20000",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "api": "/api/v1/grinding-peru",
            "health": "/api/v1/grinding-peru/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        # Test database connection
        response = supabase.table("equipment").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-15T10:30:00Z",
            "services": {
                "incident_management": "active",
                "inventory_management": "active",
                "communication_management": "active",
                "predictive_analytics": "active",
                "rag_agent": "active"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-15T10:30:00Z"
        }


@app.get("/info")
async def get_system_info():
    """Obtener información del sistema"""
    return {
        "system": "Agente Inteligente de Mantenimiento Predictivo",
        "company": "Grinding Perú",
        "version": "1.0.0",
        "description": "Sistema de gestión de servicios IT con capacidades de RAG y análisis predictivo",
        "compliance": "ISO/IEC 20000",
        "features": [
            "Gestión de Incidentes",
            "Gestión de Inventario",
            "Gestión de Comunicaciones",
            "Análisis Predictivo",
            "RAG Agent",
            "Métricas de Servicio",
            "Dashboard Ejecutivo",
            "Notificaciones Automáticas"
        ],
        "objectives": {
            "primary": "Mejorar tiempo de respuesta y eficiencia del mantenimiento predictivo",
            "specific": [
                "Diagnosticar deficiencias en registro y seguimiento de solicitudes",
                "Optimizar gestión de repuestos y equipos críticos",
                "Formalizar canales de comunicación según ISO/IEC 20000"
            ]
        },
        "technology_stack": {
            "backend": "FastAPI + Python 3.9+",
            "database": "Supabase (PostgreSQL)",
            "ai_ml": "OpenAI GPT-4 + Scikit-learn",
            "rag": "LangChain + ChromaDB",
            "monitoring": "Prometheus + Grafana",
            "notifications": "Email + Slack + Teams"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
