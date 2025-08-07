import requests
import json
import time

def test_ngrok_postman():
    """Test the ngrok URL for Postman usage"""
    
    # Get ngrok URL
    try:
        import subprocess
        result = subprocess.run(['powershell', '-Command', '(Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" | ConvertFrom-Json).tunnels[0].public_url'], 
                              capture_output=True, text=True)
        ngrok_url = result.stdout.strip()
        print(f"🌐 Ngrok URL: {ngrok_url}")
    except:
        ngrok_url = "https://770651557b95.ngrok-free.app"  # Fallback URL
        print(f"🌐 Using fallback URL: {ngrok_url}")
    
    # API endpoint
    url = f"{ngrok_url}/hackrx/run"
    
    # Test payload
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
        ]
    }
    
    print("🚀 Testing Ngrok URL for Postman")
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
            timeout=60
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
                print("\n📋 Answers:")
                print("=" * 80)
                
                for i, (question, answer) in enumerate(zip(payload["questions"], answers)):
                    print(f"\nQ{i+1}: {question}")
                    print(f"A{i+1}: {answer}")
                
                if response_time <= 30:
                    print(f"\n⚡ SPEED: EXCELLENT - {response_time:.2f}s (under 30s)")
                else:
                    print(f"\n🐌 SPEED: ACCEPTABLE - {response_time:.2f}s")
                    
            else:
                print("❌ No answers received")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n📋 POSTMAN SETUP:")
    print(f"URL: {url}")
    print(f"Method: POST")
    print(f"Headers:")
    print(f"  Content-Type: application/json")
    print(f"  Authorization: Bearer my_hackrx_token")
    print(f"Body (JSON):")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    test_ngrok_postman() 