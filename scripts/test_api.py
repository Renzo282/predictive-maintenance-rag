"""
Test script for the API endpoints
"""
import requests
import json
import time
from datetime import datetime, timedelta
import random

# API base URL
BASE_URL = "http://localhost:3000/api/v1"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_equipment_list():
    """Test equipment list endpoint"""
    print("Testing equipment list...")
    response = requests.get(f"{BASE_URL}/equipment")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_data_ingestion():
    """Test sensor data ingestion"""
    print("Testing data ingestion...")
    
    # Sample sensor data
    data = {
        "equipment_id": "123e4567-e89b-12d3-a456-426614174000",  # Replace with actual equipment ID
        "timestamp": datetime.now().isoformat(),
        "temperature": round(75.5 + random.uniform(-5, 5), 2),
        "vibration": round(2.3 + random.uniform(-0.5, 0.5), 2),
        "pressure": round(5.2 + random.uniform(-1, 1), 2),
        "humidity": round(55.0 + random.uniform(-10, 10), 2),
        "voltage": round(220.0 + random.uniform(-10, 10), 2),
        "current": round(10.5 + random.uniform(-2, 2), 2)
    }
    
    response = requests.post(f"{BASE_URL}/data/ingest", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_equipment_analysis():
    """Test equipment analysis"""
    print("Testing equipment analysis...")
    
    equipment_id = "123e4567-e89b-12d3-a456-426614174000"  # Replace with actual equipment ID
    response = requests.get(f"{BASE_URL}/equipment/{equipment_id}/analysis?days=7")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_prediction():
    """Test prediction endpoint"""
    print("Testing prediction...")
    
    equipment_id = "123e4567-e89b-12d3-a456-426614174000"  # Replace with actual equipment ID
    data = {
        "query": "What is the current health status of this equipment and what maintenance is recommended?"
    }
    
    response = requests.post(f"{BASE_URL}/equipment/{equipment_id}/predict", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_alert_creation():
    """Test alert creation"""
    print("Testing alert creation...")
    
    data = {
        "equipment_id": "123e4567-e89b-12d3-a456-426614174000",  # Replace with actual equipment ID
        "alert_type": "maintenance_required",
        "severity": "medium",
        "message": "Equipment requires scheduled maintenance",
        "recommendations": [
            "Schedule maintenance inspection",
            "Check all components",
            "Update maintenance records"
        ]
    }
    
    response = requests.post(f"{BASE_URL}/alerts", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_model_performance():
    """Test model performance endpoint"""
    print("Testing model performance...")
    response = requests.get(f"{BASE_URL}/models/performance")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_rag_update():
    """Test RAG knowledge base update"""
    print("Testing RAG update...")
    response = requests.post(f"{BASE_URL}/rag/update")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def main():
    """Run all tests"""
    print("Starting API tests...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_equipment_list()
        test_data_ingestion()
        test_equipment_analysis()
        test_prediction()
        test_alert_creation()
        test_model_performance()
        test_rag_update()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on port 3000.")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()
