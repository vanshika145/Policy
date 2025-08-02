#!/usr/bin/env python3
"""
Simple Environment Variables Test
"""

import requests
import time

RENDER_URL = "https://policy-2.onrender.com"

def test_basic_endpoints():
    """Test basic endpoints that don't require env vars"""
    print("🔍 Testing basic endpoints...")
    
    # Test health
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=5)
        print(f"✅ Health: {response.status_code}")
    except Exception as e:
        print(f"❌ Health failed: {e}")
        return False
    
    # Test ping
    try:
        response = requests.get(f"{RENDER_URL}/ping", timeout=5)
        print(f"✅ Ping: {response.status_code}")
    except Exception as e:
        print(f"❌ Ping failed: {e}")
        return False
    
    return True

def test_env_dependent_endpoints():
    """Test endpoints that require environment variables"""
    print("\n🔍 Testing environment-dependent endpoints...")
    
    # Test debug pinecone (requires Pinecone env vars)
    try:
        response = requests.get(f"{RENDER_URL}/debug/pinecone", timeout=10)
        print(f"✅ Debug pinecone: {response.status_code}")
        if response.status_code == 200:
            print("   Pinecone environment variables are working")
            return True
        else:
            print(f"   Pinecone error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Debug pinecone failed: {e}")
        print("   This suggests Pinecone environment variables are missing")
        return False

def main():
    """Run environment variable tests"""
    print("🚀 Environment Variables Test")
    print("=" * 40)
    
    # Test basic endpoints
    basic_ok = test_basic_endpoints()
    
    # Test environment-dependent endpoints
    env_ok = test_env_dependent_endpoints()
    
    print("\n" + "=" * 40)
    print("📊 RESULTS")
    print("=" * 40)
    
    if basic_ok and env_ok:
        print("🎉 All tests passed! Environment variables are correctly set.")
    elif basic_ok and not env_ok:
        print("⚠️  Basic connectivity works, but environment variables are missing.")
        print("\n🔧 FIX REQUIRED:")
        print("1. Go to Render Dashboard")
        print("2. Select your service")
        print("3. Go to 'Environment' tab")
        print("4. Add these environment variables:")
        print("   - PINECONE_API_KEY")
        print("   - PINECONE_ENVIRONMENT")
        print("   - OPENAI_API_KEY or OPENROUTER_API_KEY")
    else:
        print("❌ Basic connectivity issues detected.")
        print("Check if your service is deployed correctly.")

if __name__ == "__main__":
    main() 