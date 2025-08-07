#!/usr/bin/env python3
"""
Test First Two Questions Only
Focuses on grace period and waiting period questions
"""

import requests
import time

def test_first_two_questions():
    """Test only the first 2 questions"""
    
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
    print(f"🎯 Testing First Two Questions Only")
    print(f"📡 API Endpoint: {API_ENDPOINT}")
    
    # Test only the first 2 questions
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
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
            
            # Expected answers
            expected_answers = [
                "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
                "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
            ]
            
            print(f"\n📋 First Two Questions Analysis:")
            print(f"{'='*80}")
            
            for i, (answer, expected) in enumerate(zip(answers, expected_answers)):
                print(f"\nQ{i+1}: {payload['questions'][i]}")
                print(f"Expected: {expected}")
                print(f"Actual:   {answer}")
                
                # Check for key terms
                answer_lower = answer.lower()
                if i == 0:  # Grace period
                    key_terms = ['thirty days', '30 days', 'grace period']
                    found_terms = [term for term in key_terms if term in answer_lower]
                    print(f"Key terms found: {found_terms}")
                    
                    if 'thirty days' in answer_lower or '30 days' in answer_lower:
                        print(f"✅ SUCCESS: Grace period information found!")
                    else:
                        print(f"❌ FAILED: No grace period information found")
                        
                elif i == 1:  # Waiting period
                    key_terms = ['36 months', 'thirty-six months', 'waiting period']
                    found_terms = [term for term in key_terms if term in answer_lower]
                    print(f"Key terms found: {found_terms}")
                    
                    if '36 months' in answer_lower or 'thirty-six' in answer_lower:
                        print(f"✅ SUCCESS: Waiting period information found!")
                    else:
                        print(f"❌ FAILED: No waiting period information found")
            
            # Check if under 1 minute
            if response_time < 60:
                print(f"\n⚡ SPEED: UNDER 1 MINUTE - {response_time:.2f}s")
            else:
                print(f"\n🐌 SPEED: OVER 1 MINUTE - {response_time:.2f}s")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing first two questions: {e}")

if __name__ == "__main__":
    test_first_two_questions() 