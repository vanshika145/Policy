#!/usr/bin/env python3
"""
Comprehensive Deployment Diagnostic Tool
"""

import requests
import subprocess
import sys
import time
from datetime import datetime

RENDER_URL = "https://policy-2.onrender.com"

def check_basic_connectivity():
    """Check if the service is reachable at all"""
    print("🔍 Step 1: Basic Connectivity Check")
    print("-" * 40)
    
    try:
        # Try with curl first
        result = subprocess.run(
            ["curl", "-I", RENDER_URL], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Service responds to curl")
            print(f"   Status: {result.stdout}")
        else:
            print("❌ Service doesn't respond to curl")
            print(f"   Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Curl test failed: {e}")
    
    # Try with requests
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=5)
        print(f"✅ Service responds to requests: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print("❌ Service timeout - service is down or very slow")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - service is completely down")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def check_dns_resolution():
    """Check if DNS resolves correctly"""
    print("\n🔍 Step 2: DNS Resolution Check")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            ["nslookup", "policy-2.onrender.com"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ DNS resolution works")
            print(f"   Response: {result.stdout}")
        else:
            print("❌ DNS resolution failed")
            print(f"   Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ DNS check failed: {e}")

def check_port_scan():
    """Check if port 443 is open"""
    print("\n🔍 Step 3: Port Availability Check")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            ["telnet", "policy-2.onrender.com", "443"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Port 443 is open")
        else:
            print("❌ Port 443 is closed or filtered")
            
    except Exception as e:
        print(f"❌ Port scan failed: {e}")

def check_alternative_endpoints():
    """Check if any endpoints respond"""
    print("\n🔍 Step 4: Endpoint Response Check")
    print("-" * 40)
    
    endpoints = [
        "/health",
        "/ping", 
        "/",
        "/docs",
        "/openapi.json"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{RENDER_URL}{endpoint}", timeout=3)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {type(e).__name__}")

def check_render_status():
    """Check Render service status via API"""
    print("\n🔍 Step 5: Render Service Status")
    print("-" * 40)
    
    print("⚠️  Manual check required:")
    print("1. Go to https://dashboard.render.com")
    print("2. Find your 'policy-2' service")
    print("3. Check the status:")
    print("   - 🟢 Live (green)")
    print("   - 🔴 Build Failed (red)")
    print("   - 🔴 Deploy Failed (red)")
    print("   - ⚫ Suspended (gray)")
    print("4. Click on the service and check 'Logs' tab")

def generate_fix_recommendations():
    """Generate specific fix recommendations"""
    print("\n🔧 Step 6: Fix Recommendations")
    print("-" * 40)
    
    print("🎯 MOST LIKELY ISSUES:")
    print()
    print("1. 🔴 BUILD FAILED:")
    print("   - Check requirements.txt for missing dependencies")
    print("   - Check Dockerfile if using Docker")
    print("   - Check build logs in Render dashboard")
    print()
    print("2. 🔴 DEPLOY FAILED:")
    print("   - Check startup script (start command)")
    print("   - Check port binding (should be $PORT)")
    print("   - Check environment variables")
    print()
    print("3. ⚫ SERVICE SUSPENDED:")
    print("   - Free tier limitations")
    print("   - Upgrade to paid plan")
    print("   - Check billing status")
    print()
    print("4. 🟡 ENVIRONMENT VARIABLES:")
    print("   - PINECONE_API_KEY")
    print("   - PINECONE_ENVIRONMENT") 
    print("   - OPENAI_API_KEY or OPENROUTER_API_KEY")
    print()
    print("5. 🟡 DEPENDENCIES:")
    print("   - Check if all packages are in requirements.txt")
    print("   - Check for version conflicts")

def main():
    """Main diagnostic function"""
    print("🚀 Comprehensive Deployment Diagnostic")
    print("=" * 50)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {RENDER_URL}")
    print("=" * 50)
    
    # Run all checks
    connectivity_ok = check_basic_connectivity()
    check_dns_resolution()
    check_port_scan()
    check_alternative_endpoints()
    check_render_status()
    generate_fix_recommendations()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if connectivity_ok:
        print("✅ Service is reachable but may have internal issues")
        print("🔧 Check Render logs for specific error messages")
    else:
        print("❌ Service is completely down")
        print("🔧 Check Render dashboard for deployment status")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Check Render dashboard status")
    print("2. Review build/deploy logs")
    print("3. Verify environment variables")
    print("4. Check requirements.txt and dependencies")

if __name__ == "__main__":
    main() 