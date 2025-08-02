#!/usr/bin/env python3
"""
Deployment Verification Script
Tests the complete workflow after deployment
"""

import requests
import json
import time

# Configuration
RENDER_URL = "https://policy-2.onrender.com"  # Update with your actual URL

def test_basic_endpoints():
    """Test basic server functionality"""
    print("🔍 Testing Basic Endpoints...")
    
    # Test health
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        print(f"✅ Health: {response.status_code}")
    except Exception as e:
        print(f"❌ Health failed: {e}")
        return False
    
    # Test ping
    try:
        response = requests.get(f"{RENDER_URL}/ping", timeout=10)
        print(f"✅ Ping: {response.status_code}")
    except Exception as e:
        print(f"❌ Ping failed: {e}")
        return False
    
    return True

def test_hackrx_test():
    """Test the simple test endpoint"""
    print("\n🤖 Testing /hackrx/test...")
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/test",
            json={"test": True},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Test endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Test endpoint failed: {e}")
        return False

def test_query_simple():
    """Test simple query functionality"""
    print("\n🔍 Testing /query-simple...")
    
    test_data = {
        "query": "What is the grace period for premium payment?",
        "k": 2
    }
    
    try:
        response = requests.post(
            f"{RENDER_URL}/query-simple",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"✅ Query simple: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Found {result.get('count', 0)} results")
        return True
    except requests.exceptions.Timeout:
        print("❌ Query simple: Timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Query simple failed: {e}")
        return False

def test_hackrx_run_simple():
    """Test the main hackrx/run-simple endpoint"""
    print("\n🤖 Testing /hackrx/run-simple...")
    
    test_data = {
        "documents": "test_document.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?"
        ]
    }
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/run-simple",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"✅ Hackrx run simple: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Processed {len(result.get('data', []))} questions")
        elif response.status_code == 502:
            print("❌ Hackrx run simple: 502 Bad Gateway - still timing out")
            return False
        return True
    except requests.exceptions.Timeout:
        print("❌ Hackrx run simple: Timeout after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Hackrx run simple failed: {e}")
        return False

def test_debug_pinecone():
    """Test debug endpoint to check embeddings"""
    print("\n🧠 Testing /debug/pinecone...")
    
    try:
        response = requests.get(f"{RENDER_URL}/debug/pinecone", timeout=10)
        print(f"✅ Debug pinecone: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Total vectors: {result.get('total_vectors', 0)}")
        return True
    except Exception as e:
        print(f"❌ Debug pinecone failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 Deployment Verification")
    print("=" * 50)
    
    tests = [
        ("Basic Endpoints", test_basic_endpoints),
        ("Hackrx Test", test_hackrx_test),
        ("Debug Pinecone", test_debug_pinecone),
        ("Query Simple", test_query_simple),
        ("Hackrx Run Simple", test_hackrx_run_simple),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        
        results[test_name] = {
            "success": success,
            "time": end_time - start_time
        }
        
        if success:
            print(f"✅ {test_name} PASSED ({end_time - start_time:.2f}s)")
        else:
            print(f"❌ {test_name} FAILED ({end_time - start_time:.2f}s)")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result["success"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name} ({result['time']:.2f}s)")
    
    print(f"\n🎯 {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your deployment is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Upload a PDF file using /upload-fast")
        print("2. Test queries with /query-simple")
        print("3. Test multiple questions with /hackrx/run-simple")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure your changes are deployed")
        print("2. Check Render logs for errors")
        print("3. Verify environment variables are set")

if __name__ == "__main__":
    main() 