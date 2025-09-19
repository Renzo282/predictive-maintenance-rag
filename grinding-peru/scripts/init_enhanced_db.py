"""
Script de inicialización de base de datos mejorada para Grinding Perú
Incluye todas las tablas para los requerimientos funcionales específicos
"""
import asyncio
import logging
from datetime import datetime
from app.core.database import init_db, get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL para crear tablas específicas de Grinding Perú con todos los requerimientos funcionales
ENHANCED_GRINDING_PERU_TABLES_SQL = """
-- Tabla de usuarios (para autenticación y roles)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('tecnico', 'supervisor', 'administrador')),
    department VARCHAR(100),
    specialty VARCHAR(100),
    location VARCHAR(255),
    experience_years INTEGER DEFAULT 0,
    current_workload INTEGER DEFAULT 0,
    max_workload INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de incidencias (requerimiento funcional principal)
CREATE TABLE IF NOT EXISTS incidencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_incidencia VARCHAR(20) UNIQUE NOT NULL,
    tipo_falla VARCHAR(100) NOT NULL,
    equipo_involucrado VARCHAR(255) NOT NULL,
    ubicacion VARCHAR(255) NOT NULL,
    prioridad VARCHAR(50) NOT NULL CHECK (prioridad IN ('critica', 'alta', 'media', 'baja')),
    descripcion TEXT NOT NULL,
    estado VARCHAR(50) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_proceso', 'finalizada', 'cancelada')),
    reportado_por UUID REFERENCES users(id),
    asignado_a UUID REFERENCES users(id),
    sla_deadline TIMESTAMP WITH TIME ZONE,
    fotos TEXT[],
    archivos TEXT[],
    analisis JSONB,
    fecha_finalizacion TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de comentarios de incidencias
CREATE TABLE IF NOT EXISTS incident_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidencias(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    comment TEXT NOT NULL,
    fotos TEXT[],
    archivos TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de equipos
CREATE TABLE IF NOT EXISTS equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    model VARCHAR(255),
    serial_number VARCHAR(255),
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance', 'retired')),
    criticality VARCHAR(50) DEFAULT 'medium' CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    purchase_date DATE,
    warranty_expiry DATE,
    last_maintenance DATE,
    next_maintenance DATE,
    specifications JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de datos de sensores
CREATE TABLE IF NOT EXISTS sensor_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES equipment(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature FLOAT,
    vibration FLOAT,
    pressure FLOAT,
    humidity FLOAT,
    voltage FLOAT,
    current FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de registros de mantenimiento (historial técnico consolidado)
CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES equipment(id),
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    performed_by UUID REFERENCES users(id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    materials_used TEXT[],
    observations TEXT,
    cost DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de predicciones de fallas
CREATE TABLE IF NOT EXISTS failure_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES equipment(id),
    prediction_type VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    predicted_date TIMESTAMP WITH TIME ZONE,
    description TEXT,
    recommendations TEXT[],
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de alertas
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES equipment(id),
    incident_id UUID REFERENCES incidencias(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Tabla de inventario
CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    supplier VARCHAR(255) NOT NULL,
    supplier_contact VARCHAR(255),
    unit_cost DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'PEN',
    criticality VARCHAR(50) NOT NULL CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    current_stock INTEGER DEFAULT 0,
    min_stock INTEGER NOT NULL,
    reorder_point INTEGER NOT NULL,
    max_stock INTEGER NOT NULL,
    lead_time_days INTEGER DEFAULT 7,
    location VARCHAR(255) DEFAULT 'Almacén Principal',
    status VARCHAR(50) DEFAULT 'active',
    analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de movimientos de inventario
CREATE TABLE IF NOT EXISTS inventory_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES inventory_items(id),
    movement_type VARCHAR(50) NOT NULL CHECK (movement_type IN ('in', 'out', 'transfer', 'adjustment')),
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    reference_number VARCHAR(100),
    notes TEXT,
    performed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de comunicaciones
CREATE TABLE IF NOT EXISTS communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    communication_id VARCHAR(20) UNIQUE NOT NULL,
    type VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    sender UUID REFERENCES users(id),
    recipients TEXT[],
    channels TEXT[],
    status VARCHAR(50) DEFAULT 'pending',
    analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de logs de auditoría
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de reportes generados
CREATE TABLE IF NOT EXISTS generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    parameters JSONB,
    generated_by UUID REFERENCES users(id),
    file_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'generating',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Tabla de configuraciones del sistema
CREATE TABLE IF NOT EXISTS system_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_incidencias_numero ON incidencias(numero_incidencia);
CREATE INDEX IF NOT EXISTS idx_incidencias_estado ON incidencias(estado);
CREATE INDEX IF NOT EXISTS idx_incidencias_prioridad ON incidencias(prioridad);
CREATE INDEX IF NOT EXISTS idx_incidencias_reportado_por ON incidencias(reportado_por);
CREATE INDEX IF NOT EXISTS idx_incidencias_asignado_a ON incidencias(asignado_a);
CREATE INDEX IF NOT EXISTS idx_incidencias_created_at ON incidencias(created_at);

CREATE INDEX IF NOT EXISTS idx_incident_comments_incident_id ON incident_comments(incident_id);
CREATE INDEX IF NOT EXISTS idx_incident_comments_user_id ON incident_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_incident_comments_created_at ON incident_comments(created_at);

CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(type);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_criticality ON equipment(criticality);
CREATE INDEX IF NOT EXISTS idx_equipment_location ON equipment(location);

CREATE INDEX IF NOT EXISTS idx_sensor_data_equipment_timestamp ON sensor_data(equipment_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);

CREATE INDEX IF NOT EXISTS idx_maintenance_records_equipment_id ON maintenance_records(equipment_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_records_performed_at ON maintenance_records(performed_at);
CREATE INDEX IF NOT EXISTS idx_maintenance_records_performed_by ON maintenance_records(performed_by);

CREATE INDEX IF NOT EXISTS idx_failure_predictions_equipment_id ON failure_predictions(equipment_id);
CREATE INDEX IF NOT EXISTS idx_failure_predictions_type ON failure_predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_failure_predictions_resolved ON failure_predictions(is_resolved);

CREATE INDEX IF NOT EXISTS idx_alerts_equipment_id ON alerts(equipment_id);
CREATE INDEX IF NOT EXISTS idx_alerts_incident_id ON alerts(incident_id);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

CREATE INDEX IF NOT EXISTS idx_inventory_items_code ON inventory_items(item_code);
CREATE INDEX IF NOT EXISTS idx_inventory_items_type ON inventory_items(type);
CREATE INDEX IF NOT EXISTS idx_inventory_items_criticality ON inventory_items(criticality);
CREATE INDEX IF NOT EXISTS idx_inventory_items_status ON inventory_items(status);

CREATE INDEX IF NOT EXISTS idx_inventory_movements_item_id ON inventory_movements(item_id);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_type ON inventory_movements(movement_type);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_created_at ON inventory_movements(created_at);

CREATE INDEX IF NOT EXISTS idx_communications_type ON communications(type);
CREATE INDEX IF NOT EXISTS idx_communications_priority ON communications(priority);
CREATE INDEX IF NOT EXISTS idx_communications_created_at ON communications(created_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

CREATE INDEX IF NOT EXISTS idx_generated_reports_type ON generated_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_generated_reports_generated_by ON generated_reports(generated_by);
CREATE INDEX IF NOT EXISTS idx_generated_reports_created_at ON generated_reports(created_at);

CREATE INDEX IF NOT EXISTS idx_system_configurations_key ON system_configurations(config_key);
"""


async def initialize_enhanced_database():
    """Inicializar base de datos mejorada para Grinding Perú"""
    try:
        logger.info("Inicializando base de datos mejorada para Grinding Perú...")
        
        # Inicializar conexión a base de datos
        await init_db()
        supabase = get_supabase()
        
        # Ejecutar SQL de creación de tablas
        statements = [stmt.strip() for stmt in ENHANCED_GRINDING_PERU_TABLES_SQL.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                logger.info(f"Ejecutando: {statement[:50]}...")
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                logger.info("Declaración ejecutada exitosamente")
            except Exception as e:
                logger.warning(f"La declaración puede haber fallado (tabla podría ya existir): {e}")
        
        logger.info("Base de datos mejorada de Grinding Perú inicializada exitosamente")
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos mejorada de Grinding Perú: {e}")
        raise


async def create_enhanced_sample_data():
    """Crear datos de ejemplo mejorados para Grinding Perú"""
    try:
        supabase = get_supabase()
        
        logger.info("Creando datos de ejemplo mejorados para Grinding Perú...")
        
        # Crear usuarios de ejemplo
        users_data = [
            {
                "username": "admin",
                "email": "admin@grindingperu.com",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2",  # password: admin123
                "full_name": "Administrador del Sistema",
                "role": "administrador",
                "department": "TI",
                "specialty": "sistemas",
                "location": "Oficina Principal",
                "experience_years": 10,
                "is_active": True
            },
            {
                "username": "supervisor1",
                "email": "supervisor@grindingperu.com",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2",  # password: admin123
                "full_name": "Juan Pérez",
                "role": "supervisor",
                "department": "Mantenimiento",
                "specialty": "mecanico",
                "location": "Planta Principal",
                "experience_years": 8,
                "is_active": True
            },
            {
                "username": "tecnico1",
                "email": "tecnico1@grindingperu.com",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2",  # password: admin123
                "full_name": "Carlos Rodríguez",
                "role": "tecnico",
                "department": "Mantenimiento",
                "specialty": "hardware",
                "location": "Planta Principal",
                "experience_years": 5,
                "current_workload": 2,
                "max_workload": 8,
                "is_active": True
            },
            {
                "username": "tecnico2",
                "email": "tecnico2@grindingperu.com",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2",  # password: admin123
                "full_name": "María González",
                "role": "tecnico",
                "department": "Mantenimiento",
                "specialty": "software",
                "location": "Planta Principal",
                "experience_years": 3,
                "current_workload": 1,
                "max_workload": 8,
                "is_active": True
            }
        ]
        
        users_response = supabase.table("users").insert(users_data).execute()
        
        if users_response.data:
            logger.info(f"Creados {len(users_response.data)} usuarios de ejemplo")
            
            # Crear equipos de ejemplo
            equipment_data = [
                {
                    "name": "Servidor Principal - Grinding Perú",
                    "type": "server",
                    "model": "Dell PowerEdge R740",
                    "serial_number": "GP-SRV-001",
                    "location": "Data Center Principal",
                    "status": "active",
                    "criticality": "critical",
                    "purchase_date": "2023-01-15",
                    "warranty_expiry": "2026-01-15",
                    "last_maintenance": "2024-01-01",
                    "next_maintenance": "2024-04-01"
                },
                {
                    "name": "Switch Core - Red Principal",
                    "type": "network",
                    "model": "Cisco Catalyst 9300",
                    "serial_number": "GP-NET-001",
                    "location": "Rack Principal",
                    "status": "active",
                    "criticality": "critical",
                    "purchase_date": "2023-03-10",
                    "warranty_expiry": "2026-03-10",
                    "last_maintenance": "2024-01-15",
                    "next_maintenance": "2024-04-15"
                },
                {
                    "name": "Motor Principal - Línea 1",
                    "type": "motor",
                    "model": "Siemens 1LA7",
                    "serial_number": "GP-MOT-001",
                    "location": "Línea de Producción 1",
                    "status": "active",
                    "criticality": "high",
                    "purchase_date": "2023-02-20",
                    "warranty_expiry": "2026-02-20",
                    "last_maintenance": "2024-01-10",
                    "next_maintenance": "2024-04-10"
                }
            ]
            
            equipment_response = supabase.table("equipment").insert(equipment_data).execute()
            
            if equipment_response.data:
                logger.info(f"Creados {len(equipment_response.data)} equipos de ejemplo")
                
                # Crear incidencias de ejemplo
                incidents_data = [
                    {
                        "numero_incidencia": "INC-000001",
                        "tipo_falla": "hardware",
                        "equipo_involucrado": "Servidor Principal - Grinding Perú",
                        "ubicacion": "Data Center Principal",
                        "prioridad": "critica",
                        "descripcion": "El servidor principal no responde a las peticiones de red",
                        "estado": "finalizada",
                        "reportado_por": users_response.data[0]["id"],  # admin
                        "asignado_a": users_response.data[2]["id"],  # tecnico1
                        "fecha_finalizacion": "2024-01-10T10:15:00Z",
                        "fotos": ["foto1.jpg", "foto2.jpg"],
                        "archivos": ["log_sistema.txt"]
                    },
                    {
                        "numero_incidencia": "INC-000002",
                        "tipo_falla": "red",
                        "equipo_involucrado": "Switch Core - Red Principal",
                        "ubicacion": "Rack Principal",
                        "prioridad": "alta",
                        "descripcion": "Conexión de red intermitente en el switch principal",
                        "estado": "en_proceso",
                        "reportado_por": users_response.data[1]["id"],  # supervisor
                        "asignado_a": users_response.data[3]["id"],  # tecnico2
                        "fotos": ["switch_foto.jpg"],
                        "archivos": []
                    }
                ]
                
                incidents_response = supabase.table("incidencias").insert(incidents_data).execute()
                
                if incidents_response.data:
                    logger.info(f"Creadas {len(incidents_response.data)} incidencias de ejemplo")
                    
                    # Crear registros de mantenimiento de ejemplo
                    maintenance_data = [
                        {
                            "equipment_id": equipment_response.data[0]["id"],
                            "maintenance_type": "preventivo",
                            "description": "Mantenimiento preventivo mensual del servidor principal",
                            "performed_at": "2024-01-01T08:00:00Z",
                            "performed_by": users_response.data[2]["id"],  # tecnico1
                            "start_time": "2024-01-01T08:00:00Z",
                            "end_time": "2024-01-01T12:00:00Z",
                            "materials_used": ["Aire comprimido", "Paños de limpieza"],
                            "observations": "Equipo en buen estado, limpieza completa realizada",
                            "cost": 150.00
                        },
                        {
                            "equipment_id": equipment_response.data[2]["id"],
                            "maintenance_type": "correctivo",
                            "description": "Reparación de vibración anómala en motor principal",
                            "performed_at": "2024-01-10T14:00:00Z",
                            "performed_by": users_response.data[2]["id"],  # tecnico1
                            "start_time": "2024-01-10T14:00:00Z",
                            "end_time": "2024-01-10T18:30:00Z",
                            "materials_used": ["Rodamientos nuevos", "Grasa especializada"],
                            "observations": "Rodamientos desgastados reemplazados, motor funcionando normalmente",
                            "cost": 450.00
                        }
                    ]
                    
                    maintenance_response = supabase.table("maintenance_records").insert(maintenance_data).execute()
                    
                    if maintenance_response.data:
                        logger.info(f"Creados {len(maintenance_response.data)} registros de mantenimiento de ejemplo")
                    
                    # Crear items de inventario de ejemplo
                    inventory_data = [
                        {
                            "item_code": "GP-HAR-SRV-0001",
                            "name": "Memoria RAM DDR4 32GB",
                            "description": "Memoria RAM para servidores Dell PowerEdge",
                            "type": "hardware",
                            "category": "memory",
                            "supplier": "Dell Technologies",
                            "supplier_contact": "ventas@dell.com",
                            "unit_cost": 450.00,
                            "currency": "PEN",
                            "criticality": "critical",
                            "current_stock": 5,
                            "min_stock": 3,
                            "reorder_point": 5,
                            "max_stock": 15,
                            "lead_time_days": 7,
                            "location": "Almacén Principal"
                        },
                        {
                            "item_code": "GP-HAR-MOT-0001",
                            "name": "Rodamientos 6205-2RS",
                            "description": "Rodamientos para motores eléctricos",
                            "type": "hardware",
                            "category": "bearings",
                            "supplier": "SKF Perú",
                            "supplier_contact": "ventas@skf.com",
                            "unit_cost": 25.00,
                            "currency": "PEN",
                            "criticality": "high",
                            "current_stock": 20,
                            "min_stock": 10,
                            "reorder_point": 15,
                            "max_stock": 50,
                            "lead_time_days": 3,
                            "location": "Almacén Principal"
                        }
                    ]
                    
                    inventory_response = supabase.table("inventory_items").insert(inventory_data).execute()
                    
                    if inventory_response.data:
                        logger.info(f"Creados {len(inventory_response.data)} items de inventario de ejemplo")
                    
                    # Crear comunicaciones de ejemplo
                    communications_data = [
                        {
                            "communication_id": "COMM-000001",
                            "type": "incident",
                            "priority": "critica",
                            "subject": "Notificación de incidencia crítica",
                            "message": "Se ha detectado una incidencia crítica que requiere atención inmediata del equipo técnico",
                            "sender": users_response.data[0]["id"],  # admin
                            "recipients": ["tecnico1@grindingperu.com", "supervisor@grindingperu.com"],
                            "channels": ["email", "slack"],
                            "status": "sent"
                        },
                        {
                            "communication_id": "COMM-000002",
                            "type": "maintenance",
                            "priority": "media",
                            "subject": "Mantenimiento programado - Motor Principal",
                            "message": "Se programará mantenimiento preventivo para el motor principal el próximo fin de semana",
                            "sender": users_response.data[1]["id"],  # supervisor
                            "recipients": ["tecnico1@grindingperu.com"],
                            "channels": ["email"],
                            "status": "sent"
                        }
                    ]
                    
                    communications_response = supabase.table("communications").insert(communications_data).execute()
                    
                    if communications_response.data:
                        logger.info(f"Creadas {len(communications_response.data)} comunicaciones de ejemplo")
                    
                    # Crear logs de auditoría de ejemplo
                    audit_logs_data = [
                        {
                            "user_id": users_response.data[0]["id"],  # admin
                            "action": "create_incident",
                            "resource_type": "incident",
                            "resource_id": incidents_response.data[0]["id"],
                            "details": "Incidencia INC-000001 creada",
                            "ip_address": "192.168.1.100"
                        },
                        {
                            "user_id": users_response.data[2]["id"],  # tecnico1
                            "action": "update_incident_status",
                            "resource_type": "incident",
                            "resource_id": incidents_response.data[0]["id"],
                            "details": "Estado cambiado a finalizada",
                            "ip_address": "192.168.1.101"
                        },
                        {
                            "user_id": users_response.data[2]["id"],  # tecnico1
                            "action": "create_maintenance_record",
                            "resource_type": "maintenance",
                            "resource_id": maintenance_response.data[0]["id"],
                            "details": "Registro de mantenimiento creado",
                            "ip_address": "192.168.1.101"
                        }
                    ]
                    
                    audit_response = supabase.table("audit_logs").insert(audit_logs_data).execute()
                    
                    if audit_response.data:
                        logger.info(f"Creados {len(audit_response.data)} logs de auditoría de ejemplo")
        
        logger.info("Datos de ejemplo mejorados creados exitosamente para Grinding Perú")
        
    except Exception as e:
        logger.error(f"Error creando datos de ejemplo mejorados: {e}")
        raise


async def main():
    """Función principal"""
    try:
        # Inicializar base de datos
        await initialize_enhanced_database()
        
        # Crear datos de ejemplo
        await create_enhanced_sample_data()
        
        logger.info("Inicialización completa mejorada para Grinding Perú")
        logger.info("Usuarios de prueba creados:")
        logger.info("- admin / admin123 (Administrador)")
        logger.info("- supervisor1 / admin123 (Supervisor)")
        logger.info("- tecnico1 / admin123 (Técnico Hardware)")
        logger.info("- tecnico2 / admin123 (Técnico Software)")
        
    except Exception as e:
        logger.error(f"Error en la inicialización: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
