#!/usr/bin/env python3
"""
Deployment configuration for HackRx webhook integration
"""

import os
from typing import Dict, Any

# Webhook Configuration
WEBHOOK_CONFIG = {
    "endpoint": "/hackrx/run",
    "method": "POST",
    "content_type": "application/json",
    "timeout": 180,  # 3 minutes timeout
    "max_questions": 20,  # Maximum questions per request
    "max_document_size": "50MB"
}

# API Response Format
RESPONSE_FORMAT = {
    "answers": [
        "Based on the policy document, the grace period is 15 days for premium payment.",
        "The waiting period for pre-existing diseases is 36 months of continuous coverage.",
        "Yes, the policy covers maternity expenses under specific conditions."
    ]
}

# Error Response Format
ERROR_FORMAT = {
    "detail": "Questions array is required"
}

# Required Environment Variables
REQUIRED_ENV_VARS = [
    "OPENROUTER_API_KEY",
    "PINECONE_API_KEY", 
    "PINECONE_INDEX_NAME",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_PRIVATE_KEY_ID",
    "FIREBASE_PRIVATE_KEY",
    "FIREBASE_CLIENT_EMAIL",
    "FIREBASE_CLIENT_ID"
]

# Optional Environment Variables
OPTIONAL_ENV_VARS = [
    "OPENAI_API_KEY",  # For OpenAI embeddings fallback
    "DATABASE_URL",    # For PostgreSQL database
    "HACKRX_TOKEN"     # For webhook authentication
]

def validate_deployment_config() -> Dict[str, Any]:
    """
    Validate that all required configuration is present for deployment
    
    Returns:
        Dict with validation results
    """
    validation_result = {
        "ready_for_deployment": True,
        "missing_vars": [],
        "optional_vars": [],
        "recommendations": []
    }
    
    # Check required environment variables
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            validation_result["missing_vars"].append(var)
            validation_result["ready_for_deployment"] = False
    
    # Check optional environment variables
    for var in OPTIONAL_ENV_VARS:
        if not os.getenv(var):
            validation_result["optional_vars"].append(var)
    
    # Add recommendations
    if not validation_result["ready_for_deployment"]:
        validation_result["recommendations"].append(
            "Set all required environment variables before deployment"
        )
    
    if validation_result["optional_vars"]:
        validation_result["recommendations"].append(
            "Consider setting optional environment variables for enhanced functionality"
        )
    
    return validation_result

def get_webhook_url(domain: str) -> str:
    """
    Generate the webhook URL for the given domain
    
    Args:
        domain: Your deployed domain (e.g., "https://your-api.com")
    
    Returns:
        Complete webhook URL
    """
    return f"{domain}/hackrx/run"

def get_test_payload() -> Dict[str, Any]:
    """
    Get a sample test payload for webhook testing
    
    Returns:
        Sample request payload
    """
    return {
        "documents": "Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?",
            "What is the sub-limit for cataract treatment?",
            "Are organ donor medical expenses covered?"
        ]
    }

if __name__ == "__main__":
    print("🔍 Validating deployment configuration...")
    config = validate_deployment_config()
    
    print(f"✅ Ready for deployment: {config['ready_for_deployment']}")
    
    if config['missing_vars']:
        print(f"❌ Missing required environment variables: {config['missing_vars']}")
    
    if config['optional_vars']:
        print(f"⚠️  Optional environment variables not set: {config['optional_vars']}")
    
    if config['recommendations']:
        print("💡 Recommendations:")
        for rec in config['recommendations']:
            print(f"   - {rec}")
    
    print("\n🌐 Webhook URL examples:")
    print(f"   - Local: http://localhost:8000/hackrx/run")
    print(f"   - Production: https://your-domain.com/hackrx/run")
    
    print("\n📋 Test payload:")
    print(get_test_payload()) 