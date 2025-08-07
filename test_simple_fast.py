import requests
import json
import time

def test_simple_fast():
    """Test with minimal processing for speed"""
    
    print("🚀 Testing Simple Fast System")
    print("📡 API Endpoint: http://localhost:8000/hackrx/run")
    
    # Use a much smaller test PDF
    payload = {
        "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?"
        ]
    }
    
    print("⚡ Sending request to API...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8000/hackrx/run",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer my_hackrx_token"
            },
            timeout=30  # Short timeout
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            answers = data.get("answers", [])
            
            if answers:
                print("✅ Success! Got answers")
                for i, answer in enumerate(answers):
                    print(f"Q{i+1}: {answer[:100]}...")
                
                if response_time <= 30:
                    print(f"⚡ SPEED: EXCELLENT - {response_time:.2f}s")
                else:
                    print(f"🐌 SPEED: TOO SLOW - {response_time:.2f}s")
            else:
                print("❌ No answers received")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_fast() 