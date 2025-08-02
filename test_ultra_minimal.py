#!/usr/bin/env python3
"""
Ultra-Minimal Test Script
Tests the simplified endpoints that should work without 502 errors
"""

import requests
import json
import time

# Configuration
RENDER_URL = "https://policy-2.onrender.com"

def test_echo():
    """Test the echo endpoint"""
    print("🔄 Testing /hackrx/echo...")
    
    test_data = {
        "test": True,
        "message": "Hello World"
    }
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/echo",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Echo successful: {result}")
            return True
        else:
            print(f"❌ Echo failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Echo error: {e}")
        return False

def test_hackrx_run_simple():
    """Test the ultra-minimal hackrx/run-simple endpoint"""
    print("\n🤖 Testing /hackrx/run-simple (ultra-minimal)...")
    
    test_data = {
        "documents": "test_document.pdf",
        "questions": [
            "What is the grace period for premium payment?"
        ]
    }
    
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/run-simple",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30  # Reduced timeout
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hackrx run simple successful")
            print(f"   Message: {result.get('message', '')}")
            print(f"   Data count: {len(result.get('data', []))}")
            return True
        elif response.status_code == 502:
            print("❌ Still getting 502 Bad Gateway")
            return False
        else:
            print(f"❌ Unexpected status: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run ultra-minimal tests"""
    print("🚀 Ultra-Minimal Tests")
    print("=" * 40)
    
    tests = [
        ("Echo Test", test_echo),
        ("Hackrx Run Simple", test_hackrx_run_simple),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        
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
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for result in results.values() if result["success"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name} ({result['time']:.2f}s)")
    
    print(f"\n🎯 {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The ultra-minimal approach works.")
    else:
        print("⚠️  Some tests failed. The 502 error persists.")

if __name__ == "__main__":
    main() 