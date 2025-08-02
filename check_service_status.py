#!/usr/bin/env python3
"""
Check Service Status
"""

import requests
import time

RENDER_URL = "https://policy-2.onrender.com"

def check_service():
    """Check if service is accessible"""
    print("🔍 Checking service status...")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{RENDER_URL}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.text}")
        return True
    except requests.exceptions.Timeout:
        print("❌ Service timeout - service might be down")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - service might be down")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_simple_endpoint():
    """Test a simple endpoint"""
    print("\n🔍 Testing simple endpoint...")
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/echo",
            json={"test": True},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Echo endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Echo endpoint failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Service Status Check")
    print("=" * 40)
    
    # Check basic service
    service_ok = check_service()
    
    if service_ok:
        # Test simple endpoint
        endpoint_ok = test_simple_endpoint()
        
        print("\n" + "=" * 40)
        print("📊 RESULTS")
        print("=" * 40)
        
        if endpoint_ok:
            print("🎉 Service is working! The issue might be with specific endpoints.")
        else:
            print("⚠️  Service is accessible but endpoints are failing.")
    else:
        print("\n❌ Service appears to be down or not accessible.")
        print("Check your Render deployment status.")

if __name__ == "__main__":
    main() 