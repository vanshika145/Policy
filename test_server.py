#!/usr/bin/env python3
"""
Simple server test script
"""
import requests
import json

def test_server():
    """Test if server is responding"""
    base_url = "https://policy-2.onrender.com"
    
    print("🔧 Testing Server Response")
    print("=" * 30)
    
    # Test 1: Simple test endpoint
    print("1. Testing simple endpoint:")
    try:
        response = requests.get(f"{base_url}/test-simple", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Root endpoint
    print("2. Testing root endpoint:")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: Health endpoint
    print("3. Testing health endpoint:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 4: Show token endpoint
    print("4. Testing token endpoint:")
    try:
        response = requests.get(f"{base_url}/show-token", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

if __name__ == "__main__":
    test_server() 