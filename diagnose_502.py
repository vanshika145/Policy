#!/usr/bin/env python3
"""
502 Error Diagnostic Script
Identifies the exact cause of 502 Bad Gateway errors
"""

import requests
import json
import time

# Configuration
RENDER_URL = "https://policy-2.onrender.com"

def test_basic_connectivity():
    """Test basic server connectivity"""
    print("🔍 Testing basic connectivity...")
    
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        print(f"✅ Health check: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_echo_endpoint():
    """Test the echo endpoint"""
    print("\n🔄 Testing echo endpoint...")
    
    test_data = {"test": True, "message": "Diagnostic test"}
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/echo",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"✅ Echo endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
        return True
    except Exception as e:
        print(f"❌ Echo endpoint failed: {e}")
        return False

def test_diagnostic_endpoint():
    """Test the diagnostic endpoint"""
    print("\n🔍 Testing diagnostic endpoint...")
    
    test_data = {
        "documents": "test_document.pdf",
        "questions": ["What is the grace period for premium payment?"]
    }
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/diagnose",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for diagnostic
        )
        print(f"✅ Diagnostic endpoint: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            
            data = result.get('data', {})
            if 'step' in data:
                print(f"   Failed at step: {data['step']}")
                if 'error' in data:
                    print(f"   Error: {data['error']}")
                if 'traceback' in data:
                    print(f"   Traceback: {data['traceback']}")
            elif 'search_time' in data:
                print(f"   Search time: {data['search_time']:.2f}s")
                print(f"   LLM time: {data['llm_time']:.2f}s")
                print(f"   Total time: {data['total_time']:.2f}s")
                print(f"   Results count: {data['results_count']}")
            
            return True
        else:
            print(f"❌ Diagnostic failed: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Diagnostic timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        return False

def test_hackrx_run_simple():
    """Test the main endpoint with timing"""
    print("\n🤖 Testing hackrx/run-simple with timing...")
    
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
            print(f"   Data count: {len(result.get('data', []))}")
            return True
        elif response.status_code == 502:
            print("❌ Still getting 502 Bad Gateway")
            print("   This indicates the request is timing out on the server side")
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
    """Run diagnostic tests"""
    print("🚀 502 Error Diagnostic")
    print("=" * 50)
    
    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("Echo Endpoint", test_echo_endpoint),
        ("Diagnostic Endpoint", test_diagnostic_endpoint),
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
    print("📊 DIAGNOSTIC ANALYSIS")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result["success"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name} ({result['time']:.2f}s)")
    
    print(f"\n🎯 {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The issue might be resolved.")
    else:
        print("\n🔧 TROUBLESHOOTING RECOMMENDATIONS:")
        if not results["Basic Connectivity"]["success"]:
            print("• Server connectivity issue - check if server is running")
        if not results["Echo Endpoint"]["success"]:
            print("• Basic endpoint issue - check server logs")
        if not results["Diagnostic Endpoint"]["success"]:
            print("• Specific functionality issue - check diagnostic output above")
        if not results["Hackrx Run Simple"]["success"]:
            print("• Main endpoint timeout - check server logs and timing")

if __name__ == "__main__":
    main() 