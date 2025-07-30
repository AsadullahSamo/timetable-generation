#!/usr/bin/env python3
"""
Test the constraint resolution API endpoint directly.
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_constraint_resolution_api():
    """Test the constraint resolution API endpoint."""
    print("🧪 Testing Constraint Resolution API")
    print("=" * 50)
    
    # API endpoint
    url = "http://127.0.0.1:8001/api/timetable/resolve-constraints/"
    
    # Test data
    data = {
        "max_iterations": 10,
        "target_violations": 0
    }
    
    try:
        print("📡 Sending POST request to constraint resolution API...")
        response = requests.post(url, json=data, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"📈 Success: {result.get('success', False)}")
            print(f"📝 Message: {result.get('message', 'No message')}")
            
            if 'resolution_result' in result:
                res = result['resolution_result']
                print(f"🔢 Initial violations: {res.get('initial_violations', 'N/A')}")
                print(f"🔢 Final violations: {res.get('final_violations', 'N/A')}")
                print(f"🔢 Violations fixed: {res.get('violations_fixed', 'N/A')}")
                print(f"📊 Improvement: {res.get('improvement_percentage', 'N/A')}%")
                print(f"🔄 Iterations: {res.get('iterations', 'N/A')}")
                
            return result.get('success', False)
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Test")
    print("=" * 50)
    
    success = test_constraint_resolution_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ API test passed! Constraint resolution is working.")
    else:
        print("❌ API test failed. Check the logs above.")
    
    print("🏁 Test completed.")
