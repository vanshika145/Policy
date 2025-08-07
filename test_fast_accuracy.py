import requests
import json
import time

def test_fast_accuracy():
    """Test speed and accuracy of the optimized system"""
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Get ngrok URL
    try:
        import subprocess
        result = subprocess.run(['powershell', '-Command', '(Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" | ConvertFrom-Json).tunnels[0].public_url'], 
                              capture_output=True, text=True)
        ngrok_url = result.stdout.strip()
        if not ngrok_url.startswith('http'):
            ngrok_url = "http://localhost:8000"
    except:
        ngrok_url = "http://localhost:8000"
    
    # API endpoint - use localhost to avoid auth issues
    url = "http://localhost:8000/hackrx/run"
    
    # Test payload - just 2 questions for speed test
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
        ]
    }
    
    print("🚀 Testing Fast Accuracy System")
    print(f"📡 API Endpoint: {url}")
    print("⚡ Sending request to API...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer my_hackrx_token"
            },
            timeout=60  # Reduced timeout
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
                print("\n📋 Accuracy Analysis:")
                print("=" * 80)
                
                expected_answers = [
                    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
                    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
                ]
                
                for i, (question, answer, expected) in enumerate(zip(payload["questions"], answers, expected_answers)):
                    print(f"\nQ{i+1}: {question}")
                    print(f"Expected: {expected}")
                    print(f"Actual:   {answer}")
                    
                    # Check accuracy
                    if expected.lower() in answer.lower() or answer.lower() in expected.lower():
                        print("✅ ACCURATE: Answer matches expected!")
                    else:
                        print("❌ INACCURATE: Answer doesn't match expected")
                
                # Speed analysis
                if response_time <= 30:
                    print(f"\n⚡ SPEED: EXCELLENT - {response_time:.2f}s (under 30s)")
                elif response_time <= 60:
                    print(f"\n🐌 SPEED: ACCEPTABLE - {response_time:.2f}s (under 1min)")
                else:
                    print(f"\n🐌 SPEED: TOO SLOW - {response_time:.2f}s (over 1min)")
                    
            else:
                print("❌ No answers received")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fast_accuracy() 