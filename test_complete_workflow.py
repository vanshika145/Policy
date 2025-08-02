#!/usr/bin/env python3
"""
Complete Workflow Test Script
Tests the entire pipeline: upload → processing → embeddings → query
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

# Configuration
RENDER_URL = "https://policy-2.onrender.com"  # Update with your actual URL
TEST_PDF_PATH = "test_document.pdf"  # Update with your test PDF path

async def test_health_check():
    """Test if the server is running"""
    print("🏥 Testing health check...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{RENDER_URL}/health") as response:
                if response.status == 200:
                    print("✅ Health check passed - server is running")
                    return True
                else:
                    print(f"❌ Health check failed - status: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def test_ping():
    """Test ping endpoint"""
    print("🏓 Testing ping...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{RENDER_URL}/ping") as response:
                if response.status == 200:
                    print("✅ Ping successful")
                    return True
                else:
                    print(f"❌ Ping failed - status: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Ping error: {e}")
            return False

async def test_file_upload():
    """Test file upload functionality"""
    print("📤 Testing file upload...")
    
    # Check if test PDF exists
    if not Path(TEST_PDF_PATH).exists():
        print(f"⚠️  Test PDF not found at {TEST_PDF_PATH}")
        print("   Please upload a PDF file manually or create a test file")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            # Prepare file for upload
            with open(TEST_PDF_PATH, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=TEST_PDF_PATH, content_type='application/pdf')
                
                async with session.post(f"{RENDER_URL}/upload-fast", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ File upload successful")
                        print(f"   Response: {result}")
                        return True
                    else:
                        print(f"❌ File upload failed - status: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ File upload error: {e}")
            return False

async def test_query_simple():
    """Test simple query functionality"""
    print("🔍 Testing simple query...")
    
    test_query = {
        "query": "What is the grace period for premium payment?",
        "k": 3
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{RENDER_URL}/query-simple",
                json=test_query,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Simple query successful")
                    print(f"   Found {len(result.get('results', []))} results")
                    return True
                else:
                    print(f"❌ Simple query failed - status: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Simple query error: {e}")
            return False

async def test_hackrx_run_simple():
    """Test the main hackrx/run-simple endpoint"""
    print("🤖 Testing hackrx/run-simple...")
    
    test_request = {
        "documents": "test_document.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?"
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{RENDER_URL}/hackrx/run-simple",
                json=test_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ hackrx/run-simple successful")
                    print(f"   Processed {len(result.get('data', []))} questions")
                    return True
                else:
                    print(f"❌ hackrx/run-simple failed - status: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ hackrx/run-simple error: {e}")
            return False

async def test_embeddings_status():
    """Test if embeddings are working"""
    print("🧠 Testing embeddings status...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{RENDER_URL}/debug/pinecone") as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Embeddings debug endpoint accessible")
                    print(f"   Status: {result}")
                    return True
                else:
                    print(f"❌ Embeddings debug failed - status: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Embeddings debug error: {e}")
            return False

async def main():
    """Run all tests"""
    print("🚀 Starting Complete Workflow Test")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Ping", test_ping),
        ("Embeddings Status", test_embeddings_status),
        ("File Upload", test_file_upload),
        ("Simple Query", test_query_simple),
        ("Hackrx Run Simple", test_hackrx_run_simple),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        start_time = time.time()
        success = await test_func()
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
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result["success"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name} ({result['time']:.2f}s)")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your deployment is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    asyncio.run(main()) 