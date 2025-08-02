#!/usr/bin/env python3
"""
Deployment Environment Check
Verifies if all required environment variables are set on Render
"""

import requests
import json
import time

# Configuration
RENDER_URL = "https://policy-2.onrender.com"

def test_environment_variables():
    """Test if environment variables are set correctly"""
    print("🔍 Testing environment variables...")
    
    # Test basic connectivity first
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test if embeddings are working (this will fail if env vars are missing)
    try:
        response = requests.get(f"{RENDER_URL}/debug/pinecone", timeout=10)
        print(f"✅ Debug pinecone: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Total vectors: {result.get('total_vectors', 0)}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Debug pinecone failed: {e}")
        return False

def test_simple_query():
    """Test if simple query works (tests LLM env vars)"""
    print("\n🔍 Testing simple query...")
    
    test_data = {
        "query": "What is the grace period for premium payment?",
        "k": 1
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
        else:
            print(f"   Error: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Query simple: Timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Query simple failed: {e}")
        return False

def test_hackrx_run_simple():
    """Test the main endpoint"""
    print("\n🤖 Testing hackrx/run-simple...")
    
    test_data = {
        "documents": "test_document.pdf",
        "questions": ["What is the grace period for premium payment?"]
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{RENDER_URL}/hackrx/run-simple",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        end_time = time.time()
        
        print(f"✅ Hackrx run simple: {response.status_code}")
        print(f"   Response time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return True
        elif response.status_code == 502:
            print("❌ Still getting 502 Bad Gateway")
            return False
        else:
            print(f"❌ Unexpected status: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run environment checks"""
    print("🚀 Deployment Environment Check")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Simple Query", test_simple_query),
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
    
    # Analysis
    print("\n" + "=" * 50)
    print("📊 ENVIRONMENT ANALYSIS")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result["success"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name} ({result['time']:.2f}s)")
    
    print(f"\n🎯 {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Environment is correctly configured.")
    else:
        print("\n🔧 DEPLOYMENT ISSUES DETECTED:")
        if not results["Environment Variables"]["success"]:
            print("• Missing or incorrect environment variables")
            print("  - Check PINECONE_API_KEY, PINECONE_ENVIRONMENT")
            print("  - Check OPENAI_API_KEY or OPENROUTER_API_KEY")
        if not results["Simple Query"]["success"]:
            print("• LLM/API key issues")
            print("  - Check OPENAI_API_KEY or OPENROUTER_API_KEY")
        if not results["Hackrx Run Simple"]["success"]:
            print("• Processing timeout issues")
            print("  - Check Render resource limits")
            print("  - Check if all dependencies are installed")

if __name__ == "__main__":
    main() 