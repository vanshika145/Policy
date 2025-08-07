#!/usr/bin/env python3
"""
Accuracy Analysis: Dynamic vs Static Prompts
Tests the accuracy of our dynamic prompt system against expected answers
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
NGROK_URL = "http://localhost:4040/api/tunnels"
API_ENDPOINT = None

# Expected answers with key details to check
EXPECTED_ANSWERS = {
    "grace_period": {
        "question": "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "expected_keywords": ["thirty days", "30 days", "grace period"],
        "expected_numbers": ["30", "thirty"]
    },
    "waiting_period_ped": {
        "question": "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "expected_keywords": ["36 months", "thirty-six months", "36", "three years"],
        "expected_numbers": ["36", "3"]
    },
    "maternity": {
        "question": "Does this policy cover maternity expenses, and what are the conditions?",
        "expected_keywords": ["24 months", "two deliveries", "maternity"],
        "expected_numbers": ["24", "2"]
    },
    "cataract": {
        "question": "What is the waiting period for cataract surgery?",
        "expected_keywords": ["2 years", "two years", "cataract"],
        "expected_numbers": ["2"]
    },
    "ncd": {
        "question": "What is the No Claim Discount (NCD) offered in this policy?",
        "expected_keywords": ["5%", "five percent", "NCD"],
        "expected_numbers": ["5"]
    },
    "health_checkup": {
        "question": "Is there a benefit for preventive health check-ups?",
        "expected_keywords": ["two continuous policy years", "health check-ups"],
        "expected_numbers": ["2"]
    },
    "hospital_definition": {
        "question": "How does the policy define a 'Hospital'?",
        "expected_keywords": ["10 inpatient beds", "15 beds", "24/7"],
        "expected_numbers": ["10", "15", "24"]
    },
    "ayush": {
        "question": "What is the extent of coverage for AYUSH treatments?",
        "expected_keywords": ["AYUSH", "Sum Insured"],
        "expected_numbers": []
    },
    "room_rent": {
        "question": "Are there any sub-limits on room rent and ICU charges for Plan A?",
        "expected_keywords": ["1%", "2%", "Sum Insured"],
        "expected_numbers": ["1", "2"]
    }
}

def get_ngrok_url():
    """Get the current ngrok URL"""
    try:
        response = requests.get(NGROK_URL)
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            for tunnel in tunnels:
                if tunnel['proto'] == 'https':
                    return tunnel['public_url']
    except Exception as e:
        print(f"❌ Error getting ngrok URL: {e}")
    return None

def test_dynamic_prompt_accuracy():
    """Test the accuracy of dynamic prompts"""
    global API_ENDPOINT
    
    # Get ngrok URL
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("❌ Could not get ngrok URL")
        return
    
    API_ENDPOINT = f"{ngrok_url}/hackrx/run"
    print(f"🎯 Testing Dynamic Prompt Accuracy")
    print(f"📡 API Endpoint: {API_ENDPOINT}")
    
    # Test payload
    questions = [expected["question"] for expected in EXPECTED_ANSWERS.values()]
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
            max_score = len(EXPECTED_ANSWERS)
            
            print(f"\n📋 Accuracy Analysis:")
            print(f"{'='*80}")
            
            for i, (key, expected) in enumerate(EXPECTED_ANSWERS.items()):
                if i < len(answers):
                    answer = answers[i].lower()
                    question = expected["question"]
                    expected_keywords = expected["expected_keywords"]
                    expected_numbers = expected["expected_numbers"]
                    
                    # Check keyword matches
                    keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer)
                    number_matches = sum(1 for num in expected_numbers if num in answer)
                    
                    # Calculate score (keywords worth 70%, numbers worth 30%)
                    keyword_score = (keyword_matches / len(expected_keywords)) * 0.7 if expected_keywords else 0
                    number_score = (number_matches / len(expected_numbers)) * 0.3 if expected_numbers else 0
                    total_question_score = keyword_score + number_score
                    
                    total_score += total_question_score
                    
                    # Display results
                    status = "✅" if total_question_score >= 0.8 else "⚠️" if total_question_score >= 0.5 else "❌"
                    print(f"{status} Q{i+1}: {question[:60]}...")
                    print(f"   Score: {total_question_score:.2f} (Keywords: {keyword_matches}/{len(expected_keywords)}, Numbers: {number_matches}/{len(expected_numbers)})")
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
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing accuracy: {e}")

if __name__ == "__main__":
    test_dynamic_prompt_accuracy() 