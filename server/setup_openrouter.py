#!/usr/bin/env python3
"""
Setup script for OpenRouter API key
"""

import os
from dotenv import load_dotenv

def setup_openrouter():
    """Help user set up OpenRouter API key"""
    print("🔧 OpenRouter Setup")
    print("=" * 50)
    
    # Load current .env
    load_dotenv()
    
    current_key = os.getenv("OPENROUTER_API_KEY")
    
    if current_key and current_key != "your-openrouter-api-key-here":
        print("✅ OpenRouter API key is already configured!")
        print(f"   Current key: {current_key[:10]}...{current_key[-4:]}")
        return True
    else:
        print("❌ OpenRouter API key not configured")
        print()
        print("📋 To set up OpenRouter:")
        print("1. Go to https://openrouter.ai/keys")
        print("2. Create an account and get your API key")
        print("3. Add the key to your .env file:")
        print("   OPENROUTER_API_KEY=your-actual-api-key-here")
        print()
        print("💡 The API key will enable Mistral for better answers!")
        return False

if __name__ == "__main__":
    setup_openrouter() 