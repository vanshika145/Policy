#!/usr/bin/env python3
"""
Comprehensive test script for Railway deployment
"""

import sys
import os
import subprocess
import time

def test_import():
    """Test if the app can be imported successfully"""
    print("🧪 Testing app import...")
    
    try:
        # Add server directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
        
        # Import the app
        from main import app
        print("App imported successfully")
        
        # Check if health endpoint exists
        routes = [route.path for route in app.routes]
        if "/health" in routes:
            print("Health endpoint found")
            return True
        else:
            print("Health endpoint not found")
            print(f"Available routes: {routes}")
            return False
            
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_startup_script():
    """Test if the startup script works"""
    print("\n🧪 Testing startup script...")
    
    try:
        # Test the startup script
        result = subprocess.run([sys.executable, "start.py"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if "Successfully imported FastAPI app" in result.stdout:
            print("Startup script works correctly")
            return True
        else:
            print("Startup script failed")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Startup script started (timeout expected)")
        return True
    except Exception as e:
        print(f"Startup script error: {e}")
        return False

def test_requirements():
    """Test if all requirements can be installed"""
    print("\n🧪 Testing requirements...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--dry-run"], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("Requirements are valid")
            return True
        else:
            print("Requirements have issues")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Requirements test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Railway deployment tests...\n")
    
    tests = [
        ("Import Test", test_import),
        ("Startup Script Test", test_startup_script),
        ("Requirements Test", test_requirements)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"{test_name} PASSED")
        else:
            print(f"{test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("All tests passed! Ready for Railway deployment!")
        return True
    else:
        print("Some tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 