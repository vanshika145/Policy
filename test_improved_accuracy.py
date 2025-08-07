#!/usr/bin/env python3
"""
Test improved accuracy with the same questions as the user's sample
"""
import requests
import json

def test_improved_accuracy():
    """Test the improved accuracy with sample questions"""
    base_url = "https://c860474c0351.ngrok-free.app"
    
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXEZOgeT%2FjUHNO7HzQ%3D",
        "questions": [
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
    }
    
    headers = {
        "Authorization": "Bearer my_hackrx_token",
        "Content-Type": "application/json"
    }
    
    print("🧪 Testing improved accuracy with sample questions:")
    try:
        response = requests.post(f"{base_url}/hackrx/run", json=test_data, headers=headers, timeout=120)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ SUCCESS!")
            result = response.json()
            print(f"   Number of answers: {len(result['answers'])}")
            for i, answer in enumerate(result['answers'], 1):
                print(f"   {i}. {answer[:100]}...")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_improved_accuracy() 