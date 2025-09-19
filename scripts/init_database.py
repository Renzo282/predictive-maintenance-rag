"""
Database initialization script
"""
import asyncio
import logging
from app.core.database import init_db, CREATE_TABLES_SQL
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def initialize_database():
    """Initialize database with required tables"""
    try:
        logger.info("Initializing database...")
        
        # Initialize database connection
        await init_db()
        
        # Execute table creation SQL
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in CREATE_TABLES_SQL.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                logger.info(f"Executing: {statement[:50]}...")
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                logger.info("Statement executed successfully")
            except Exception as e:
                logger.warning(f"Statement may have failed (table might already exist): {e}")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def create_sample_data():
    """Create sample data for testing"""
    try:
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        logger.info("Creating sample data...")
        
        # Create sample equipment
        equipment_data = [
            {
                "name": "Motor Principal A",
                "type": "motor",
                "location": "Planta Principal",
                "status": "active"
            },
            {
                "name": "Bomba de Agua B",
                "type": "pump",
                "location": "Sector Norte",
                "status": "active"
            },
            {
                "name": "Compresor C",
                "type": "compressor",
                "location": "Sector Sur",
                "status": "active"
            }
        ]
        
        equipment_response = supabase.table("equipment").insert(equipment_data).execute()
        
        if equipment_response.data:
            logger.info(f"Created {len(equipment_response.data)} equipment records")
            
            # Create sample sensor data
            import random
            from datetime import datetime, timedelta
            import pandas as pd
            
            sensor_data = []
            equipment_ids = [eq["id"] for eq in equipment_response.data]
            
            # Generate 30 days of hourly data
            for i in range(30 * 24):  # 30 days * 24 hours
                timestamp = datetime.now() - timedelta(hours=i)
                
                for equipment_id in equipment_ids:
                    # Generate realistic sensor data with some variation
                    base_temp = 70 + random.uniform(-5, 5)
                    base_vibration = 2.0 + random.uniform(-0.5, 0.5)
                    base_pressure = 5.0 + random.uniform(-1, 1)
                    
                    # Add some anomalies occasionally
                    if random.random() < 0.05:  # 5% chance of anomaly
                        base_temp += random.uniform(10, 20)
                        base_vibration += random.uniform(2, 5)
                    
                    sensor_data.append({
                        "equipment_id": equipment_id,
                        "timestamp": timestamp.isoformat(),
                        "temperature": round(base_temp, 2),
                        "vibration": round(base_vibration, 2),
                        "pressure": round(base_pressure, 2),
                        "humidity": round(50 + random.uniform(-10, 10), 2),
                        "voltage": round(220 + random.uniform(-10, 10), 2),
                        "current": round(10 + random.uniform(-2, 2), 2)
                    })
            
            # Insert sensor data in batches
            batch_size = 100
            for i in range(0, len(sensor_data), batch_size):
                batch = sensor_data[i:i + batch_size]
                supabase.table("sensor_data").insert(batch).execute()
            
            logger.info(f"Created {len(sensor_data)} sensor data records")
        
        logger.info("Sample data creation completed")
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")


if __name__ == "__main__":
    asyncio.run(initialize_database())
    asyncio.run(create_sample_data())
