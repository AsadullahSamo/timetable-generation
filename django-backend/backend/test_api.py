#!/usr/bin/env python3
"""
API Test Script
Tests that the API endpoints are working correctly with the new field names
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_api_endpoints():
    """Test various API endpoints to ensure they work with new field names"""
    base_url = "http://localhost:8000/api/timetable"
    
    print("🧪 TESTING API ENDPOINTS")
    print("=" * 50)
    
    # Test 1: Teachers endpoint
    print("\n1. Testing Teachers API...")
    try:
        response = requests.get(f"{base_url}/api/teachers/")
        if response.status_code == 200:
            teachers = response.json()
            print(f"   ✅ Teachers API working - Found {len(teachers)} teachers")
            
            # Check if the response contains the new field name
            if teachers and 'max_classes_per_day' in teachers[0]:
                print("   ✅ Response contains 'max_classes_per_day' field")
            else:
                print("   ❌ Response missing 'max_classes_per_day' field")
                print(f"   Available fields: {list(teachers[0].keys()) if teachers else 'None'}")
        else:
            print(f"   ❌ Teachers API failed with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing Teachers API: {e}")
    
    # Test 2: Configuration endpoint
    print("\n2. Testing Configuration API...")
    try:
        response = requests.get(f"{base_url}/api/config/")
        if response.status_code == 200:
            configs = response.json()
            print(f"   ✅ Configuration API working - Found {len(configs)} configs")
            
            # Check if the response contains the new field name
            if configs and 'class_duration' in configs[0]:
                print("   ✅ Response contains 'class_duration' field")
            else:
                print("   ❌ Response missing 'class_duration' field")
                print(f"   Available fields: {list(configs[0].keys()) if configs else 'None'}")
        else:
            print(f"   ❌ Configuration API failed with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing Configuration API: {e}")
    
    # Test 3: Subjects endpoint
    print("\n3. Testing Subjects API...")
    try:
        response = requests.get(f"{base_url}/api/subjects/")
        if response.status_code == 200:
            subjects = response.json()
            print(f"   ✅ Subjects API working - Found {len(subjects)} subjects")
            
            # Check if THESIS subject exists
            thesis_subject = next((s for s in subjects if s['code'] == 'THESIS'), None)
            if thesis_subject:
                print(f"   ✅ THESIS subject found: {thesis_subject['name']} (Batch: {thesis_subject['batch']})")
            else:
                print("   ❌ THESIS subject not found")
        else:
            print(f"   ❌ Subjects API failed with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing Subjects API: {e}")
    
    # Test 4: Teacher Assignments endpoint
    print("\n4. Testing Teacher Assignments API...")
    try:
        response = requests.get(f"{base_url}/api/teacher-assignments/")
        if response.status_code == 200:
            assignments = response.json()
            print(f"   ✅ Teacher Assignments API working - Found {len(assignments)} assignments")
            
            # Check if Dr. Areej Fatemah is assigned to DSA2
            areej_dsa2 = next((a for a in assignments if a['teacher_name'] == 'Dr. Areej Fatemah' and a['subject_code'] == 'DSA2'), None)
            if areej_dsa2:
                print(f"   ✅ Dr. Areej Fatemah assigned to DSA2: {areej_dsa2['sections']}")
            else:
                print("   ❌ Dr. Areej Fatemah not assigned to DSA2")
        else:
            print(f"   ❌ Teacher Assignments API failed with status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing Teacher Assignments API: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 API Testing Complete!")

if __name__ == "__main__":
    test_api_endpoints()
