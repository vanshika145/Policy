#!/usr/bin/env python3
"""
Deployment test script
"""
import requests
import json

def test_deployment():
    """Test the deployed API"""
    base_url = "https://policy-2.onrender.com"
    
    print("🔧 Testing Deployment")
    print("=" * 30)
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint:")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Health check
    print("2. Testing health endpoint:")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: Ping endpoint
    print("3. Testing ping endpoint:")
    try:
        response = requests.get(f"{base_url}/ping")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 4: Main API with authorization
    print("4. Testing main API endpoint:")
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXEZOgeT%2FjUHNO7HzQ%3D",
        "questions": ["What is the grace period for premium payment?"]
    }
    
    try:
        headers = {"Authorization": "Bearer HACKRX_TOKEN"}
        response = requests.post(f"{base_url}/hackrx/run", json=test_data, headers=headers, timeout=60)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCCESS! API is working!")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("📋 Summary:")
    print("✅ Deployment test completed!")

if __name__ == "__main__":
    test_deployment() 