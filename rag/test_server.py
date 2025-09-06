"""
Test script for the RAG Vector Store Server
"""

import requests
import json
from typing import Dict, Any


def test_server(base_url: str = "http://localhost:8000"):
    """Test all endpoints of the RAG server."""
    
    print("Testing RAG Vector Store Server")
    print("=" * 50)
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test stores info endpoint
    print("\n2. Testing stores info endpoint...")
    try:
        response = requests.get(f"{base_url}/query/stores")
        print(f"Status: {response.status_code}")
        stores = response.json()
        print(f"Found {len(stores)} vector stores:")
        for store_name, info in stores.items():
            print(f"  - {store_name}: {info['name']} ({'Loaded' if info['loaded'] else 'Not Loaded'})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test health endpoint
    print("\n3. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Health: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test query endpoints
    test_queries = [
        ("1-CG-Vie", "life insurance benefits"),
        ("2-CG-Santé", "health coverage"),
        ("3-CG-Transport", "marine insurance"),
        ("4-CG-IARD", "home insurance"),
        ("5-CG-Engineering", "construction risks"),
        ("6-CG-Automobile", "car insurance"),
        ("7-Assurance-BH-Connaissances-Generales", "Wininti application")
    ]
    
    print("\n4. Testing query endpoints...")
    for store_name, query in test_queries:
        print(f"\n   Testing {store_name} with query: '{query}'")
        try:
            payload = {
                "query": query,
                "k": 3
            }
            response = requests.post(
                f"{base_url}/query/{store_name}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Found {result['total_results']} results")
                if result['results']:
                    print(f"   First result preview: {result['results'][0]['content'][:100]}...")
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\nTesting completed!")


if __name__ == "__main__":
    test_server()
