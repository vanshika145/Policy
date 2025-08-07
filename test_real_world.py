import time
import requests
import json

def test_real_world_performance():
    """Test the API with real-world scenario - larger document, more questions"""
    
    url = "https://e9727efbf02f.ngrok-free.app/hackrx/run"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer my_hackrx_token"
    }
    
    # Real-world test data with more questions
    payload = {
        "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "What is the waiting period for cataract surgery?",
            "What is the No Claim Discount offered?",
            "What is the coverage for AYUSH treatments?",
            "What is the maternity benefit coverage?",
            "What is the room rent limit?",
            "What is the organ donor coverage?",
            "What is the preventive health check benefit?",
            "What is the definition of Hospital?"
        ]
    }
    
    print("🚀 Testing API with real-world scenario...")
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
                print(f"   {i}. {answer[:150]}...")
                
            print(f"\n🎯 Performance Summary:")
            print(f"   • Total time: {response_time:.2f}s")
            print(f"   • Questions processed: {len(payload['questions'])}")
            print(f"   • Average time per question: {response_time/len(payload['questions']):.2f}s")
            
            # Check if under 30 seconds
            if response_time < 30:
                print(f"✅ SUCCESS: Under 30 seconds ({response_time:.2f}s)")
            else:
                print(f"❌ FAILED: Over 30 seconds ({response_time:.2f}s)")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (180 seconds)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_real_world_performance() 