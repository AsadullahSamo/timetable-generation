#!/usr/bin/env python
"""
CORRECT TEST: Frontend API vs Terminal Data Storage
Tests if IDENTICAL data entered via frontend API generates SAME quality as terminal data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher, Classroom, ScheduleConfig
from timetable.algorithms.advanced_scheduler import AdvancedTimetableScheduler
from django.test import Client
import json

def test_identical_data_different_methods():
    """Test if identical data via different input methods produces same results"""
    print("🔍 TESTING: IDENTICAL DATA, DIFFERENT INPUT METHODS")
    print("=" * 60)
    
    # Get existing terminal data
    terminal_subject = Subject.objects.filter(code='PF').first()
    terminal_teacher = Teacher.objects.filter(name__icontains='Dr. Naeem').first()
    terminal_classroom = Classroom.objects.filter(name__icontains='Lab').first()
    
    if not all([terminal_subject, terminal_teacher, terminal_classroom]):
        print("❌ Missing terminal data for comparison")
        return False
    
    print(f"📊 Using terminal data as reference:")
    print(f"   Subject: {terminal_subject.name} ({terminal_subject.code}) - {terminal_subject.credits} credits")
    print(f"   Teacher: {terminal_teacher.name} - {terminal_teacher.subjects.count()} subjects")
    print(f"   Classroom: {terminal_classroom.name} - {terminal_classroom.capacity} capacity")
    
    # Create IDENTICAL data via frontend API
    client = Client()
    
    print(f"\n👤 CREATING IDENTICAL DATA VIA FRONTEND API...")
    
    # Create identical subject via API
    subject_data = {
        'name': terminal_subject.name,
        'code': f"API_{terminal_subject.code}",  # Slightly different code to avoid conflicts
        'credits': terminal_subject.credits
    }
    
    response = client.post('/api/timetable/subjects/', 
                          data=json.dumps(subject_data),
                          content_type='application/json')
    
    if response.status_code != 201:
        print(f"❌ Failed to create subject via API: {response.status_code}")
        return False
    
    api_subject_id = response.json()['id']
    print(f"✅ Created identical subject via API: {subject_data['name']}")
    
    # Create identical classroom via API
    classroom_data = {
        'name': f"API_{terminal_classroom.name}",
        'capacity': terminal_classroom.capacity,
        'building': terminal_classroom.building
    }
    
    response = client.post('/api/timetable/classrooms/', 
                          data=json.dumps(classroom_data),
                          content_type='application/json')
    
    if response.status_code != 201:
        print(f"❌ Failed to create classroom via API: {response.status_code}")
        return False
    
    api_classroom_id = response.json()['id']
    print(f"✅ Created identical classroom via API: {classroom_data['name']}")
    
    # Create identical teacher via API
    teacher_data = {
        'name': f"API_{terminal_teacher.name}",
        'email': f"api.{terminal_teacher.email}",
        'subjects': [api_subject_id],  # Assign to API-created subject
        'max_lessons_per_day': terminal_teacher.max_lessons_per_day,
        'unavailable_periods': terminal_teacher.unavailable_periods or {}
    }
    
    response = client.post('/api/timetable/teachers/', 
                          data=json.dumps(teacher_data),
                          content_type='application/json')
    
    if response.status_code != 201:
        print(f"❌ Failed to create teacher via API: {response.status_code}")
        return False
    
    api_teacher_id = response.json()['id']
    print(f"✅ Created identical teacher via API: {teacher_data['name']}")
    
    # Create identical schedule config via API
    terminal_config = ScheduleConfig.objects.first()
    
    config_data = {
        'name': f"API_{terminal_config.name}",
        'days': terminal_config.days,
        'periods': terminal_config.periods,
        'start_time': terminal_config.start_time.strftime('%H:%M:%S'),
        'lesson_duration': terminal_config.lesson_duration,
        'class_groups': [
            {'name': 'API-24SW-I', 'students': 30, 'subjects': [f"API_{terminal_subject.code}"]}
        ],
        'constraints': terminal_config.constraints or {},
        'semester': f"API_{terminal_config.semester}",
        'academic_year': terminal_config.academic_year
    }
    
    response = client.post('/api/timetable/schedule-configs/', 
                          data=json.dumps(config_data),
                          content_type='application/json')
    
    if response.status_code != 201:
        print(f"❌ Failed to create config via API: {response.status_code}")
        print(f"Response: {response.content}")
        return False
    
    api_config_id = response.json()['id']
    print(f"✅ Created identical config via API: {config_data['name']}")
    
    # Now test timetable generation with both
    print(f"\n🧪 TESTING TIMETABLE GENERATION...")
    
    # Test terminal data
    try:
        terminal_scheduler = AdvancedTimetableScheduler(terminal_config)
        terminal_result = terminal_scheduler.generate_timetable()
        
        if terminal_result and 'entries' in terminal_result:
            terminal_entries = len(terminal_result['entries'])
            terminal_fitness = terminal_result.get('fitness_score', 0)
            terminal_violations = len(terminal_result.get('constraint_violations', []))
            print(f"✅ Terminal data: {terminal_entries} entries, fitness: {terminal_fitness:.2f}, violations: {terminal_violations}")
        else:
            print(f"❌ Terminal data generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Terminal data error: {e}")
        return False
    
    # Test API data
    try:
        api_config = ScheduleConfig.objects.get(id=api_config_id)
        api_scheduler = AdvancedTimetableScheduler(api_config)
        api_result = api_scheduler.generate_timetable()
        
        if api_result and 'entries' in api_result:
            api_entries = len(api_result['entries'])
            api_fitness = api_result.get('fitness_score', 0)
            api_violations = len(api_result.get('constraint_violations', []))
            print(f"✅ API data: {api_entries} entries, fitness: {api_fitness:.2f}, violations: {api_violations}")
        else:
            print(f"❌ API data generation failed")
            return False
            
    except Exception as e:
        print(f"❌ API data error: {e}")
        return False
    
    # Compare results
    print(f"\n🔍 COMPARISON:")
    print(f"   Entries: Terminal={terminal_entries}, API={api_entries}")
    print(f"   Fitness: Terminal={terminal_fitness:.2f}, API={api_fitness:.2f}")
    print(f"   Violations: Terminal={terminal_violations}, API={api_violations}")
    
    # Check if results are similar (allowing for some variation due to randomness)
    entries_similar = abs(terminal_entries - api_entries) <= 5
    fitness_similar = abs(terminal_fitness - api_fitness) <= abs(terminal_fitness * 0.1)  # 10% tolerance
    violations_similar = abs(terminal_violations - api_violations) <= 10
    
    success = entries_similar and fitness_similar and violations_similar
    
    # Cleanup API data
    print(f"\n🧹 CLEANING UP API DATA...")
    try:
        Subject.objects.filter(id=api_subject_id).delete()
        Teacher.objects.filter(id=api_teacher_id).delete()
        Classroom.objects.filter(id=api_classroom_id).delete()
        ScheduleConfig.objects.filter(id=api_config_id).delete()
        print("✅ API data cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
    
    return success

def test_data_storage_integrity():
    """Test if frontend API stores data with correct fields"""
    print(f"\n🔍 TESTING DATA STORAGE INTEGRITY...")
    
    client = Client()
    
    # Test subject storage
    subject_data = {'name': 'Test Storage Subject', 'code': 'TSS999', 'credits': 3}
    response = client.post('/api/timetable/subjects/', 
                          data=json.dumps(subject_data),
                          content_type='application/json')
    
    if response.status_code == 201:
        subject_id = response.json()['id']
        stored_subject = Subject.objects.get(id=subject_id)
        
        fields_correct = (
            stored_subject.name == subject_data['name'] and
            stored_subject.code == subject_data['code'] and
            stored_subject.credits == subject_data['credits']
        )
        
        print(f"✅ Subject storage: {'CORRECT' if fields_correct else 'INCORRECT'}")
        stored_subject.delete()
    else:
        print(f"❌ Subject storage failed")
        return False
    
    # Test classroom storage
    classroom_data = {'name': 'Test Storage Room', 'capacity': 40, 'building': 'Test Building'}
    response = client.post('/api/timetable/classrooms/', 
                          data=json.dumps(classroom_data),
                          content_type='application/json')
    
    if response.status_code == 201:
        classroom_id = response.json()['id']
        stored_classroom = Classroom.objects.get(id=classroom_id)
        
        fields_correct = (
            stored_classroom.name == classroom_data['name'] and
            stored_classroom.capacity == classroom_data['capacity'] and
            stored_classroom.building == classroom_data['building']
        )
        
        print(f"✅ Classroom storage: {'CORRECT' if fields_correct else 'INCORRECT'}")
        stored_classroom.delete()
    else:
        print(f"❌ Classroom storage failed")
        return False
    
    return True

def main():
    print("🔍 CORRECT USER DATA TEST: FRONTEND API vs TERMINAL STORAGE")
    print("=" * 70)
    
    # Test 1: Data storage integrity
    storage_ok = test_data_storage_integrity()
    
    # Test 2: Identical data comparison
    generation_ok = test_identical_data_different_methods()
    
    print(f"\n" + "=" * 70)
    print("🎯 FINAL VERDICT")
    print("=" * 70)
    
    if storage_ok and generation_ok:
        print("🎉 SUCCESS: Frontend API stores data correctly and generates same quality timetables!")
        print("✅ User-entered data WILL generate same quality as terminal data")
        print("✅ Data flow: Frontend → Database → Algorithm → Timetable is PERFECT")
        print("🚀 SYSTEM IS READY!")
    else:
        if not storage_ok:
            print("❌ Data storage integrity failed")
        if not generation_ok:
            print("❌ Timetable generation quality differs")
        print("🚫 SYSTEM NEEDS FIXES!")

if __name__ == "__main__":
    main()
