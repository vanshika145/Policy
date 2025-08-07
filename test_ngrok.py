#!/usr/bin/env python3
"""
Test ngrok API with correct token
"""
import requests
import json

def test_ngrok_api():
    """Test the ngrok API"""
    base_url = "https://c860474c0351.ngrok-free.app"
    
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXEZOgeT%2FjUHNO7HzQ%3D",
        "questions": ["What is the grace period for premium payment?"]
    }
    
    headers = {
        "Authorization": "Bearer my_hackrx_token",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing ngrok API:")
    try:
        response = requests.post(f"{base_url}/hackrx/run", json=test_data, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCCESS!")
            print(f"   Response: {response.text}")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_ngrok_api() 