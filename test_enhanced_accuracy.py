#!/usr/bin/env python3
"""
Test Enhanced Dynamic Prompt System
Tests the system with your actual policy document
"""

import requests
import time

def test_enhanced_system():
    """Test the enhanced dynamic prompt system"""
    
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
    print(f"🎯 Testing Enhanced Dynamic Prompt System")
    print(f"📡 API Endpoint: {API_ENDPOINT}")
    
    # Your actual questions
    questions = [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
    
    # Expected key details for each question
    expected_details = [
        ["thirty days", "30 days"],  # Grace period
        ["36 months", "thirty-six months"],  # Waiting period PED
        ["24 months", "two deliveries"],  # Maternity
        ["2 years", "two years"],  # Cataract
        ["Transplantation of Human Organs Act"],  # Organ donor
        ["5%", "five percent"],  # NCD
        ["two continuous policy years"],  # Health checkup
        ["10 inpatient beds", "15 beds", "24/7"],  # Hospital definition
        ["AYUSH", "Sum Insured"],  # AYUSH coverage
        ["1%", "2%", "Sum Insured"]  # Room rent limits
    ]
    
    # Test payload
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": questions
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
            
            # Analyze accuracy
            total_score = 0
            max_score = len(questions)
            
            print(f"\n📋 Enhanced Dynamic Prompt Analysis:")
            print(f"{'='*80}")
            
            for i, (answer, expected) in enumerate(zip(answers, expected_details)):
                answer_lower = answer.lower()
                matches = sum(1 for detail in expected if detail.lower() in answer_lower)
                score = matches / len(expected) if expected else 1.0
                total_score += score
                
                # Display result
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.5 else "❌"
                print(f"{status} Q{i+1}: {questions[i][:50]}...")
                print(f"   Score: {score:.2f} ({matches}/{len(expected)} details found)")
                print(f"   Answer: {answer[:100]}...")
                print()
            
            # Overall accuracy
            overall_accuracy = (total_score / max_score) * 100
            print(f"{'='*80}")
            print(f"🎯 Overall Accuracy: {overall_accuracy:.1f}%")
            print(f"📊 Total Score: {total_score:.2f}/{max_score}")
            print(f"⏱️  Response Time: {response_time:.2f}s")
            
            # Performance rating
            if overall_accuracy >= 90:
                rating = "🟢 EXCELLENT"
            elif overall_accuracy >= 80:
                rating = "🟡 GOOD"
            elif overall_accuracy >= 70:
                rating = "🟠 FAIR"
            else:
                rating = "🔴 NEEDS IMPROVEMENT"
            
            print(f"🏆 Rating: {rating}")
            
            # Check if under 1 minute
            if response_time < 60:
                print(f"⚡ SPEED: UNDER 1 MINUTE - {response_time:.2f}s")
            else:
                print(f"🐌 SPEED: OVER 1 MINUTE - {response_time:.2f}s")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing enhanced system: {e}")

if __name__ == "__main__":
    test_enhanced_system() 