#!/usr/bin/env python3
"""
Simple Analysis of Your Dynamic Prompt System
"""

# Your actual answers from the real policy document
YOUR_ANSWERS = [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
    "The policy has a specific waiting period of two (2) years for cataract surgery.",
    "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
    "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
    "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
    "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
    "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
    "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
]

def analyze_accuracy():
    print("🎯 YOUR DYNAMIC PROMPT SYSTEM ANALYSIS")
    print("="*60)
    
    # Key details that should be extracted
    key_details = [
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
    
    total_score = 0
    
    for i, (answer, expected_details) in enumerate(zip(YOUR_ANSWERS, key_details)):
        answer_lower = answer.lower()
        matches = sum(1 for detail in expected_details if detail.lower() in answer_lower)
        score = matches / len(expected_details)
        total_score += score
        
        status = "✅" if score >= 0.8 else "⚠️" if score >= 0.5 else "❌"
        print(f"{status} Q{i+1}: {matches}/{len(expected_details)} details found")
    
    overall_accuracy = (total_score / len(YOUR_ANSWERS)) * 100
    print(f"\n🎯 Overall Accuracy: {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 90:
        print("🏆 RATING: EXCELLENT - Dynamic prompts working perfectly!")
    elif overall_accuracy >= 80:
        print("🏆 RATING: GOOD - Dynamic prompts working well!")
    elif overall_accuracy >= 70:
        print("🏆 RATING: FAIR - Dynamic prompts need some improvement")
    else:
        print("🏆 RATING: NEEDS IMPROVEMENT")

if __name__ == "__main__":
    analyze_accuracy() 