#!/usr/bin/env python3
"""
Test script to verify the timeout fix for hackrx/run-simple endpoint
"""

import asyncio
import httpx
import json

async def test_timeout_fix():
    """Test the hackrx/run-simple endpoint with timeout optimizations"""
    
    # Test data with 10 questions to test the increased limit
    test_data = {
        "documents": "Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1 - Copy.pdf",
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
    
    try:
        print("🧪 Testing /hackrx/run-simple endpoint with timeout fix...")
        
        # Test with Render URL
        render_url = "https://policy-2.onrender.com/hackrx/run-simple"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                render_url,
                json=test_data,
                timeout=120.0  # Increased timeout for 10 questions
            )
            
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Response: {json.dumps(response_data, indent=2)}")
                
                # Check if we got actual answers
                if response_data.get("status") == "success":
                    data = response_data.get("data", [])
                    if data and isinstance(data, list):
                        for i, item in enumerate(data):
                            if "answer" in item:
                                answer = item["answer"]
                                if answer != "No relevant information found in the documents." and "timeout" not in answer.lower():
                                    print(f"✅ Question {i+1}: Got meaningful answer")
                                else:
                                    print(f"⚠️  Question {i+1}: {answer}")
                            else:
                                print(f"❌ Question {i+1}: No answer field")
                    else:
                        print("❌ No data returned")
                else:
                    print(f"❌ Error: {response_data.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except httpx.TimeoutException:
        print("❌ Request timed out - the fix didn't work")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_timeout_fix()) 