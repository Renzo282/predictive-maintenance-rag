"""
Script de inicialización de base de datos para Grinding Perú
Configuración específica para gestión de servicios IT
"""
import asyncio
import logging
from datetime import datetime
from app.core.database import init_db, get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL para crear tablas específicas de Grinding Perú
GRINDING_PERU_TABLES_SQL = """
-- Tabla de incidentes
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'new',
    reported_by VARCHAR(255) NOT NULL,
    assigned_to VARCHAR(255),
    sla_deadline TIMESTAMP WITH TIME ZONE,
    affected_services TEXT[],
    tags TEXT[],
    analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Tabla de cambios
CREATE TABLE IF NOT EXISTS changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    change_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    requested_by VARCHAR(255) NOT NULL,
    approved_by VARCHAR(255),
    implementation_plan TEXT,
    rollback_plan TEXT,
    risk_assessment JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Tabla de problemas
CREATE TABLE IF NOT EXISTS problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    assigned_to VARCHAR(255),
    root_cause TEXT,
    workaround TEXT,
    solution TEXT,
    related_incidents UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Tabla de items de inventario
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
    criticality VARCHAR(50) NOT NULL,
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
    movement_type VARCHAR(50) NOT NULL, -- 'in', 'out', 'transfer', 'adjustment'
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    reference_number VARCHAR(100),
    notes TEXT,
    performed_by VARCHAR(255),
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
    sender VARCHAR(255) NOT NULL,
    recipients TEXT[],
    channels TEXT[],
    status VARCHAR(50) DEFAULT 'pending',
    analysis JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de equipos
CREATE TABLE IF NOT EXISTS equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    model VARCHAR(255),
    serial_number VARCHAR(255),
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    criticality VARCHAR(50) DEFAULT 'medium',
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

-- Tabla de registros de mantenimiento
CREATE TABLE IF NOT EXISTS maintenance_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES equipment(id),
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    technician VARCHAR(255),
    cost DECIMAL(10,2),
    parts_used TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de predicciones
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES equipment(id),
    prediction_type VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    predicted_date TIMESTAMP WITH TIME ZONE,
    description TEXT,
    recommendations TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de alertas
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES equipment(id),
    incident_id UUID REFERENCES incidents(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_priority ON incidents(priority);
CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents(created_at);
CREATE INDEX IF NOT EXISTS idx_incidents_reported_by ON incidents(reported_by);

CREATE INDEX IF NOT EXISTS idx_changes_status ON changes(status);
CREATE INDEX IF NOT EXISTS idx_changes_type ON changes(type);
CREATE INDEX IF NOT EXISTS idx_changes_created_at ON changes(created_at);

CREATE INDEX IF NOT EXISTS idx_problems_status ON problems(status);
CREATE INDEX IF NOT EXISTS idx_problems_priority ON problems(priority);

CREATE INDEX IF NOT EXISTS idx_inventory_items_type ON inventory_items(type);
CREATE INDEX IF NOT EXISTS idx_inventory_items_criticality ON inventory_items(criticality);
CREATE INDEX IF NOT EXISTS idx_inventory_items_status ON inventory_items(status);

CREATE INDEX IF NOT EXISTS idx_inventory_movements_item_id ON inventory_movements(item_id);
CREATE INDEX IF NOT EXISTS idx_inventory_movements_created_at ON inventory_movements(created_at);

CREATE INDEX IF NOT EXISTS idx_communications_type ON communications(type);
CREATE INDEX IF NOT EXISTS idx_communications_priority ON communications(priority);
CREATE INDEX IF NOT EXISTS idx_communications_created_at ON communications(created_at);

CREATE INDEX IF NOT EXISTS idx_equipment_type ON equipment(type);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_location ON equipment(location);

CREATE INDEX IF NOT EXISTS idx_sensor_data_equipment_timestamp ON sensor_data(equipment_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);

CREATE INDEX IF NOT EXISTS idx_maintenance_records_equipment_id ON maintenance_records(equipment_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_records_performed_at ON maintenance_records(performed_at);

CREATE INDEX IF NOT EXISTS idx_predictions_equipment_id ON predictions(equipment_id);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions(prediction_type);

CREATE INDEX IF NOT EXISTS idx_alerts_equipment_id ON alerts(equipment_id);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
"""


async def initialize_grinding_peru_database():
    """Inicializar base de datos específica para Grinding Perú"""
    try:
        logger.info("Inicializando base de datos para Grinding Perú...")
        
        # Inicializar conexión a base de datos
        await init_db()
        supabase = get_supabase()
        
        # Ejecutar SQL de creación de tablas
        statements = [stmt.strip() for stmt in GRINDING_PERU_TABLES_SQL.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                logger.info(f"Ejecutando: {statement[:50]}...")
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                logger.info("Declaración ejecutada exitosamente")
            except Exception as e:
                logger.warning(f"La declaración puede haber fallado (tabla podría ya existir): {e}")
        
        logger.info("Base de datos de Grinding Perú inicializada exitosamente")
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos de Grinding Perú: {e}")
        raise


async def create_sample_data():
    """Crear datos de ejemplo para Grinding Perú"""
    try:
        supabase = get_supabase()
        
        logger.info("Creando datos de ejemplo para Grinding Perú...")
        
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
                "name": "UPS Principal - Data Center",
                "type": "power",
                "model": "APC Smart-UPS 3000VA",
                "serial_number": "GP-PWR-001",
                "location": "Data Center Principal",
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
                    "item_code": "GP-HAR-NET-0001",
                    "name": "Cable de Red Cat6 100m",
                    "description": "Cable de red categoría 6 para infraestructura",
                    "type": "hardware",
                    "category": "cable",
                    "supplier": "Cable Perú",
                    "supplier_contact": "ventas@cableperu.com",
                    "unit_cost": 25.00,
                    "currency": "PEN",
                    "criticality": "medium",
                    "current_stock": 20,
                    "min_stock": 10,
                    "reorder_point": 15,
                    "max_stock": 50,
                    "lead_time_days": 3,
                    "location": "Almacén Principal"
                },
                {
                    "item_code": "GP-SOF-LIC-0001",
                    "name": "Licencia Windows Server 2022",
                    "description": "Licencia de sistema operativo para servidores",
                    "type": "software",
                    "category": "license",
                    "supplier": "Microsoft Perú",
                    "supplier_contact": "licencias@microsoft.com",
                    "unit_cost": 1200.00,
                    "currency": "PEN",
                    "criticality": "high",
                    "current_stock": 2,
                    "min_stock": 1,
                    "reorder_point": 2,
                    "max_stock": 5,
                    "lead_time_days": 14,
                    "location": "Almacén Digital"
                }
            ]
            
            inventory_response = supabase.table("inventory_items").insert(inventory_data).execute()
            
            if inventory_response.data:
                logger.info(f"Creados {len(inventory_response.data)} items de inventario de ejemplo")
            
            # Crear incidentes de ejemplo
            incidents_data = [
                {
                    "incident_number": "INC-000001",
                    "title": "Servidor principal no responde",
                    "description": "El servidor principal de Grinding Perú no está respondiendo a las peticiones",
                    "category": "infrastructure",
                    "priority": "critical",
                    "status": "resolved",
                    "reported_by": "admin@grindingperu.com",
                    "assigned_to": "soporte@grindingperu.com",
                    "affected_services": ["Web Portal", "API Gateway", "Base de Datos"],
                    "tags": ["servidor", "infraestructura", "crítico"],
                    "created_at": "2024-01-10T08:30:00Z",
                    "resolved_at": "2024-01-10T10:15:00Z"
                },
                {
                    "incident_number": "INC-000002",
                    "title": "Conexión de red intermitente",
                    "description": "La conexión de red presenta interrupciones esporádicas",
                    "category": "network",
                    "priority": "high",
                    "status": "in_progress",
                    "reported_by": "usuario@grindingperu.com",
                    "assigned_to": "nivel2@grindingperu.com",
                    "affected_services": ["Red Interna", "Acceso a Internet"],
                    "tags": ["red", "conectividad", "intermitente"],
                    "created_at": "2024-01-12T14:20:00Z"
                }
            ]
            
            incidents_response = supabase.table("incidents").insert(incidents_data).execute()
            
            if incidents_response.data:
                logger.info(f"Creados {len(incidents_response.data)} incidentes de ejemplo")
            
            # Crear comunicaciones de ejemplo
            communications_data = [
                {
                    "communication_id": "COMM-000001",
                    "type": "incident",
                    "priority": "critical",
                    "subject": "Notificación de incidente crítico",
                    "message": "Se ha detectado un incidente crítico que requiere atención inmediata",
                    "sender": "sistema@grindingperu.com",
                    "recipients": ["soporte@grindingperu.com", "gerencia@grindingperu.com"],
                    "channels": ["email", "slack"],
                    "status": "sent",
                    "created_at": "2024-01-10T08:35:00Z"
                },
                {
                    "communication_id": "COMM-000002",
                    "type": "maintenance",
                    "priority": "medium",
                    "subject": "Mantenimiento programado - Servidor Principal",
                    "message": "Se programará mantenimiento preventivo para el servidor principal el próximo fin de semana",
                    "sender": "mantenimiento@grindingperu.com",
                    "recipients": ["soporte@grindingperu.com"],
                    "channels": ["email"],
                    "status": "sent",
                    "created_at": "2024-01-15T09:00:00Z"
                }
            ]
            
            communications_response = supabase.table("communications").insert(communications_data).execute()
            
            if communications_response.data:
                logger.info(f"Creadas {len(communications_response.data)} comunicaciones de ejemplo")
        
        logger.info("Datos de ejemplo creados exitosamente para Grinding Perú")
        
    except Exception as e:
        logger.error(f"Error creando datos de ejemplo: {e}")
        raise


async def main():
    """Función principal"""
    try:
        # Inicializar base de datos
        await initialize_grinding_peru_database()
        
        # Crear datos de ejemplo
        await create_sample_data()
        
        logger.info("Inicialización completa para Grinding Perú")
        
    except Exception as e:
        logger.error(f"Error en la inicialización: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
