#!/usr/bin/env python3
"""
Test Enhanced Chunking
Checks if better chunking helps find grace period information
"""

import requests
import time

def test_enhanced_chunks():
    """Test with enhanced chunking"""
    
    # Get ngrok URL
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            for tunnel in tunnels:
                if tunnel['proto'] == 'https':
                    ngrok_url = tunnel['public_url']
                    break
        else:
            print("❌ Could not get ngrok URL")
            return
    except Exception as e:
        print(f"❌ Error getting ngrok URL: {e}")
        return
    
    API_ENDPOINT = f"{ngrok_url}/hackrx/run"
    print(f"🎯 Testing Enhanced Chunking")
    print(f"📡 API Endpoint: {API_ENDPOINT}")
    
    # Test only grace period question with enhanced chunking
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?"
        ]
    }
    
    try:
        print(f"\n🚀 Sending request to API...")
        start_time = time.time()
        
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer my_hackrx_token"
            },
            timeout=120
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get("answers", [])
            
            print(f"\n✅ Success! Got {len(answers)} answers")
            
            if answers:
                answer = answers[0]
                print(f"\n📋 Grace Period Answer with Enhanced Chunking:")
                print(f"{'='*80}")
                print(f"Question: What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?")
                print(f"Answer: {answer}")
                print(f"{'='*80}")
                
                # Check for key terms
                answer_lower = answer.lower()
                key_terms = ['thirty days', '30 days', 'grace period', 'premium payment']
                found_terms = [term for term in key_terms if term in answer_lower]
                
                print(f"\n🔍 Key Terms Found: {found_terms}")
                
                if 'thirty days' in answer_lower or '30 days' in answer_lower:
                    print(f"✅ SUCCESS: Enhanced chunking found grace period information!")
                else:
                    print(f"❌ FAILED: Enhanced chunking still didn't find grace period information")
                    print(f"💡 The document might not contain grace period information")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing enhanced chunking: {e}")

if __name__ == "__main__":
    test_enhanced_chunks() 