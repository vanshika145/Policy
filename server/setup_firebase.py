#!/usr/bin/env python3
"""
Firebase Setup Helper Script
"""

import os
import json
import sys
from pathlib import Path

def check_firebase_key():
    """Check if Firebase service account key exists and is valid"""
    key_path = Path("config/firebase-service-account-key.json")
    
    if not key_path.exists():
        print("❌ Firebase service account key not found!")
        print(f"   Expected location: {key_path.absolute()}")
        print("\n📋 To get your service account key:")
        print("1. Go to Firebase Console: https://console.firebase.google.com/")
        print("2. Select your project")
        print("3. Go to Project Settings (gear icon) > Service accounts")
        print("4. Click 'Generate new private key'")
        print("5. Save the downloaded file as 'firebase-service-account-key.json' in the config/ folder")
        return False
    
    try:
        with open(key_path, 'r') as f:
            data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"❌ Invalid service account key. Missing fields: {missing_fields}")
            return False
        
        print(f"✅ Firebase service account key found and valid")
        print(f"   Project ID: {data.get('project_id', 'Unknown')}")
        print(f"   Client Email: {data.get('client_email', 'Unknown')}")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in service account key file")
        return False
    except Exception as e:
        print(f"❌ Error reading service account key: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has Firebase configuration"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("   Run: cp env.example .env")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    if "FIREBASE_SERVICE_ACCOUNT_KEY_PATH" not in content:
        print("❌ Firebase configuration missing from .env file")
        print("   Add: FIREBASE_SERVICE_ACCOUNT_KEY_PATH=config/firebase-service-account-key.json")
        return False
    
    print("✅ .env file configured")
    return True

def create_config_dir():
    """Create config directory if it doesn't exist"""
    config_dir = Path("config")
    if not config_dir.exists():
        config_dir.mkdir()
        print("✅ Created config directory")
    else:
        print("✅ Config directory exists")

def main():
    """Main setup function"""
    print("🔥 Firebase Setup Helper")
    print("=" * 40)
    
    # Create config directory
    create_config_dir()
    
    # Check environment file
    env_ok = check_env_file()
    
    # Check Firebase key
    key_ok = check_firebase_key()
    
    print("\n" + "=" * 40)
    
    if env_ok and key_ok:
        print("🎉 Firebase setup is complete!")
        print("\nNext steps:")
        print("1. Test the setup: python test_setup.py")
        print("2. Start the server: python start.py")
    else:
        print("❌ Firebase setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 