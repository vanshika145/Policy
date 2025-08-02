#!/usr/bin/env python3
"""
Quick Manual Test Script
For testing individual endpoints manually
"""

import requests
import json

# Configuration
RENDER_URL = "https://policy-2.onrender.com"  # Update with your actual URL

def test_health():
    """Test health endpoint"""
    print("🏥 Testing /health...")
    try:
        response = requests.get(f"{RENDER_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_ping():
    """Test ping endpoint"""
    print("\n🏓 Testing /ping...")
    try:
        response = requests.get(f"{RENDER_URL}/ping")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_hackrx_test():
    """Test hackrx/test endpoint"""
    print("\n🤖 Testing /hackrx/test...")
    try:
        response = requests.post(
            f"{RENDER_URL}/hackrx/test",
            json={"test": True},
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_hackrx_run_simple():
    """Test hackrx/run-simple endpoint"""
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
            timeout=60  # 60 second timeout
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_query_simple():
    """Test query-simple endpoint"""
    print("\n🔍 Testing /query-simple...")
    
    test_data = {
        "query": "What is the grace period for premium payment?",
        "k": 3
    }
    
    try:
        response = requests.post(
            f"{RENDER_URL}/query-simple",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all quick tests"""
    print("🚀 Quick Manual Tests")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health),
        ("Ping", test_ping),
        ("Hackrx Test", test_hackrx_test),
        ("Query Simple", test_query_simple),
        ("Hackrx Run Simple", test_hackrx_run_simple),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        
        success = test_func()
        results[test_name] = success
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 {passed}/{total} tests passed")

if __name__ == "__main__":
    main() 