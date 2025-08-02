#!/usr/bin/env python3
"""
Simple Deployment Test
"""

import requests
import time

RENDER_URL = "https://policy-2.onrender.com"

def test_basic_access():
    """Test basic service access"""
    print("🔍 Testing basic service access...")
    
    try:
        # Test with shorter timeout
        response = requests.get(f"{RENDER_URL}/health", timeout=3)
        print(f"✅ Service accessible: {response.status_code}")
        print(f"   Response: {response.text}")
        return True
    except requests.exceptions.Timeout:
        print("❌ Service timeout - service might be down or slow")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - service might be down")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_new_endpoint():
    """Test the new endpoint I added"""
    print("\n🔍 Testing new endpoint...")
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/run-with-file",
            files={"file": ("test.pdf", b"test content", "application/pdf")},
            data={"questions": '["Test question"]'},
            timeout=10
        )
        print(f"✅ New endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ New endpoint failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Simple Deployment Test")
    print("=" * 40)
    
    # Test basic access
    basic_ok = test_basic_access()
    
    if basic_ok:
        # Test new endpoint
        endpoint_ok = test_new_endpoint()
        
        print("\n" + "=" * 40)
        print("📊 RESULTS")
        print("=" * 40)
        
        if endpoint_ok:
            print("🎉 Service is working! New endpoint deployed successfully.")
        else:
            print("⚠️  Service accessible but new endpoint not deployed yet.")
            print("Wait a few minutes for Render to redeploy.")
    else:
        print("\n❌ Service is not accessible.")
        print("Check your Render dashboard for deployment status.")

if __name__ == "__main__":
    main() 