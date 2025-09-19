"""
Database configuration and connection management
"""
import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

# Supabase client
supabase: Client = None


async def init_db():
    """Initialize database connection"""
    global supabase
    
    try:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return supabase


# Database table schemas
EQUIPMENT_TABLE = "equipment"
SENSOR_DATA_TABLE = "sensor_data"
MAINTENANCE_RECORDS_TABLE = "maintenance_records"
PREDICTIONS_TABLE = "predictions"
ALERTS_TABLE = "alerts"

# Create tables if they don't exist
CREATE_TABLES_SQL = f"""
-- Equipment table
CREATE TABLE IF NOT EXISTS {EQUIPMENT_TABLE} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sensor data table
CREATE TABLE IF NOT EXISTS {SENSOR_DATA_TABLE} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES {EQUIPMENT_TABLE}(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature FLOAT,
    vibration FLOAT,
    pressure FLOAT,
    humidity FLOAT,
    voltage FLOAT,
    current FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Maintenance records table
CREATE TABLE IF NOT EXISTS {MAINTENANCE_RECORDS_TABLE} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES {EQUIPMENT_TABLE}(id),
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    technician VARCHAR(255),
    cost DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Predictions table
CREATE TABLE IF NOT EXISTS {PREDICTIONS_TABLE} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES {EQUIPMENT_TABLE}(id),
    prediction_type VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    predicted_date TIMESTAMP WITH TIME ZONE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alerts table
CREATE TABLE IF NOT EXISTS {ALERTS_TABLE} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipment_id UUID REFERENCES {EQUIPMENT_TABLE}(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sensor_data_equipment_timestamp 
ON {SENSOR_DATA_TABLE}(equipment_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_predictions_equipment_type 
ON {PREDICTIONS_TABLE}(equipment_id, prediction_type);

CREATE INDEX IF NOT EXISTS idx_alerts_equipment_resolved 
ON {ALERTS_TABLE}(equipment_id, is_resolved);
"""
