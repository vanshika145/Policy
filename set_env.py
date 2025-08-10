#!/usr/bin/env python3
"""
Set environment variables for local development
"""
import os

# Set environment variables
os.environ["HACKRX_TOKEN"] = "166bca9fd80e1ae7e91af903f98706d993a4b9d36e07e7c9db70a67b12342e4b"
os.environ["PINECONE_API_KEY"] = "your_pinecone_api_key_here"  # You need to replace this
os.environ["PINECONE_INDEX"] = "policy-documents"
os.environ["OPENROUTER_API_KEY"] = "your_openrouter_api_key_here"  # You need to replace this

print("✅ Environment variables set:")
print(f"   HACKRX_TOKEN: {os.environ.get('HACKRX_TOKEN')}")
print(f"   PINECONE_API_KEY: {'Set' if os.environ.get('PINECONE_API_KEY') else 'NOT SET'}")
print(f"   PINECONE_INDEX: {os.environ.get('PINECONE_INDEX')}")
print(f"   OPENROUTER_API_KEY: {'Set' if os.environ.get('OPENROUTER_API_KEY') else 'NOT SET'}")
print()
print("⚠️  You need to replace 'your_pinecone_api_key_here' with your actual Pinecone API key")
print("⚠️  You need to replace 'your_openrouter_api_key_here' with your actual OpenRouter API key") 