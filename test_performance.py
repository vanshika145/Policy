import time
import requests
import json

def test_api_performance():
    """Test the performance of the optimized API with accuracy focus"""
    
    url = "https://e9727efbf02f.ngrok-free.app/hackrx/run"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer my_hackrx_token"
    }
    
    # Test data with policy-specific questions
    payload = {
        "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "What is the waiting period for cataract surgery?",
            "What is the No Claim Discount offered?",
            "What is the coverage for AYUSH treatments?"
        ]
    }
    
    print("🚀 Testing API performance with accuracy focus...")
    print(f"📄 Document: {payload['documents']}")
    print(f"❓ Questions: {len(payload['questions'])}")
    print()
    
    # Measure response time
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Got {len(result.get('answers', []))} answers")
            
            # Show answers with focus on accuracy
            print(f"\n📋 Detailed Answers:")
            for i, answer in enumerate(result.get('answers', []), 1):
                print(f"   {i}. {answer}")
                
            print(f"\n🎯 Performance Summary:")
            print(f"   • Total time: {response_time:.2f}s")
            print(f"   • Questions processed: {len(payload['questions'])}")
            print(f"   • Average time per question: {response_time/len(payload['questions']):.2f}s")
            
            # Check for specific accuracy indicators
            answers_text = " ".join(result.get('answers', [])).lower()
            accuracy_indicators = {
                "30 days": "grace period",
                "36 months": "waiting period for PED", 
                "2 years": "cataract surgery",
                "5%": "NCD discount",
                "AYUSH": "treatment coverage"
            }
            
            print(f"\n🎯 Accuracy Check:")
            for indicator, description in accuracy_indicators.items():
                if indicator in answers_text:
                    print(f"   ✅ Found '{indicator}' - {description}")
                else:
                    print(f"   ❌ Missing '{indicator}' - {description}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (180 seconds)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_performance() 