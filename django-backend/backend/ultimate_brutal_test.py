#!/usr/bin/env python
"""
ULTIMATE BRUTAL TEST: USER DATA vs TERMINAL DATA
Tests if user-entered data generates SAME quality timetables as script data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry
from timetable.algorithms.advanced_scheduler import AdvancedTimetableScheduler
from django.test import Client
import json
import time

def create_user_data_via_api():
    """Create data exactly as user would through frontend"""
    print("👤 CREATING USER DATA VIA FRONTEND API...")
    
    client = Client()
    created_ids = {'subjects': [], 'teachers': [], 'classrooms': [], 'configs': []}
    
    # Create subjects via API
    user_subjects = [
        {'name': 'User Programming Fundamentals', 'code': 'UPF101', 'credits': 3},
        {'name': 'User Database Systems', 'code': 'UDB201', 'credits': 3},
        {'name': 'User Software Engineering', 'code': 'USE301', 'credits': 4}
    ]
    
    for subject_data in user_subjects:
        response = client.post('/api/timetable/subjects/', 
                              data=json.dumps(subject_data),
                              content_type='application/json')
        if response.status_code == 201:
            created_ids['subjects'].append(response.json()['id'])
            print(f"✅ Created subject: {subject_data['name']}")
        else:
            print(f"❌ Failed to create subject: {subject_data['name']}")
            return None
    
    # Create classrooms via API
    user_classrooms = [
        {'name': 'User Lab 01', 'capacity': 30, 'building': 'User Building A'},
        {'name': 'User Room 02', 'capacity': 40, 'building': 'User Building B'},
        {'name': 'User Lab 03', 'capacity': 25, 'building': 'User Building A'}
    ]
    
    for classroom_data in user_classrooms:
        response = client.post('/api/timetable/classrooms/', 
                              data=json.dumps(classroom_data),
                              content_type='application/json')
        if response.status_code == 201:
            created_ids['classrooms'].append(response.json()['id'])
            print(f"✅ Created classroom: {classroom_data['name']}")
        else:
            print(f"❌ Failed to create classroom: {classroom_data['name']}")
            return None
    
    # Create teachers via API
    user_teachers = [
        {
            'name': 'User Dr. Ahmed',
            'email': 'user.ahmed@muet.edu.pk',
            'subjects': created_ids['subjects'][:2],  # First 2 subjects
            'max_lessons_per_day': 4,
            'unavailable_periods': {'Monday': [1], 'Friday': [7]}
        },
        {
            'name': 'User Prof. Khan',
            'email': 'user.khan@muet.edu.pk',
            'subjects': created_ids['subjects'][1:],  # Last 2 subjects
            'max_lessons_per_day': 5,
            'unavailable_periods': {'Tuesday': [1, 2]}
        }
    ]
    
    for teacher_data in user_teachers:
        response = client.post('/api/timetable/teachers/', 
                              data=json.dumps(teacher_data),
                              content_type='application/json')
        if response.status_code == 201:
            created_ids['teachers'].append(response.json()['id'])
            print(f"✅ Created teacher: {teacher_data['name']}")
        else:
            print(f"❌ Failed to create teacher: {teacher_data['name']}")
            return None
    
    # Create schedule config via API
    user_config = {
        'name': 'USER-ENTERED-CONFIG-24SW-TEST',
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        'periods': ['1', '2', '3', '4', '5', '6', '7'],
        'start_time': '08:00:00',
        'lesson_duration': 60,
        'class_groups': [
            {'name': 'USER-24SW-I', 'students': 35, 'subjects': ['UPF101', 'UDB201']},
            {'name': 'USER-24SW-II', 'students': 30, 'subjects': ['UDB201', 'USE301']}
        ],
        'constraints': {},
        'semester': 'User Test Semester',
        'academic_year': '2024-2025'
    }
    
    response = client.post('/api/timetable/schedule-configs/', 
                          data=json.dumps(user_config),
                          content_type='application/json')
    if response.status_code == 201:
        created_ids['configs'].append(response.json()['id'])
        print(f"✅ Created config: {user_config['name']}")
    else:
        print(f"❌ Failed to create config: {user_config['name']}")
        return None
    
    return created_ids

def test_timetable_quality(config, label):
    """Test timetable generation quality"""
    print(f"\n🧪 TESTING {label}...")
    
    try:
        scheduler = AdvancedTimetableScheduler(config)
        
        # Generate timetable
        start_time = time.time()
        result = scheduler.generate_timetable()
        generation_time = time.time() - start_time
        
        if not result or 'entries' not in result:
            return {
                'success': False,
                'error': 'Generation failed',
                'entries': 0,
                'fitness': 0,
                'violations': 999,
                'time': generation_time
            }
        
        entries = result['entries']
        fitness = result.get('fitness_score', 0)
        violations = result.get('constraint_violations', [])
        
        # Analyze quality metrics
        quality_metrics = {
            'success': True,
            'entries': len(entries),
            'fitness': fitness,
            'violations': len(violations),
            'time': generation_time,
            'teacher_conflicts': 0,
            'classroom_conflicts': 0,
            'capacity_violations': 0,
            'constraint_satisfaction': 0
        }
        
        # Check for conflicts in generated entries
        teacher_schedule = {}
        classroom_schedule = {}
        
        for entry in entries:
            time_key = f"{entry['day']}_P{entry['period']}"
            
            # Teacher conflicts
            teacher = entry['teacher']
            if teacher in teacher_schedule:
                if time_key in teacher_schedule[teacher]:
                    quality_metrics['teacher_conflicts'] += 1
                else:
                    teacher_schedule[teacher][time_key] = entry
            else:
                teacher_schedule[teacher] = {time_key: entry}
            
            # Classroom conflicts
            classroom = entry['classroom']
            if classroom in classroom_schedule:
                if time_key in classroom_schedule[classroom]:
                    quality_metrics['classroom_conflicts'] += 1
                else:
                    classroom_schedule[classroom][time_key] = entry
            else:
                classroom_schedule[classroom] = {time_key: entry}
        
        # Calculate constraint satisfaction rate
        total_possible_violations = len(entries) * 5  # Rough estimate
        satisfaction_rate = max(0, (total_possible_violations - len(violations)) / total_possible_violations * 100)
        quality_metrics['constraint_satisfaction'] = satisfaction_rate
        
        print(f"📊 {label} Results:")
        print(f"   Entries: {quality_metrics['entries']}")
        print(f"   Fitness: {quality_metrics['fitness']:.2f}")
        print(f"   Violations: {quality_metrics['violations']}")
        print(f"   Teacher conflicts: {quality_metrics['teacher_conflicts']}")
        print(f"   Classroom conflicts: {quality_metrics['classroom_conflicts']}")
        print(f"   Constraint satisfaction: {quality_metrics['constraint_satisfaction']:.1f}%")
        print(f"   Generation time: {quality_metrics['time']:.2f}s")
        
        return quality_metrics
        
    except Exception as e:
        print(f"❌ {label} failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'entries': 0,
            'fitness': 0,
            'violations': 999,
            'time': 0
        }

def compare_quality(user_metrics, terminal_metrics):
    """Compare quality between user and terminal data"""
    print(f"\n🔍 QUALITY COMPARISON:")
    print("=" * 50)
    
    comparisons = []
    
    # Compare entries generated
    if user_metrics['entries'] >= terminal_metrics['entries'] * 0.8:
        print(f"✅ Entries: User={user_metrics['entries']}, Terminal={terminal_metrics['entries']} - ACCEPTABLE")
        comparisons.append(True)
    else:
        print(f"❌ Entries: User={user_metrics['entries']}, Terminal={terminal_metrics['entries']} - USER SIGNIFICANTLY LOWER")
        comparisons.append(False)
    
    # Compare fitness scores
    if user_metrics['fitness'] >= terminal_metrics['fitness'] * 0.8:
        print(f"✅ Fitness: User={user_metrics['fitness']:.2f}, Terminal={terminal_metrics['fitness']:.2f} - ACCEPTABLE")
        comparisons.append(True)
    else:
        print(f"❌ Fitness: User={user_metrics['fitness']:.2f}, Terminal={terminal_metrics['fitness']:.2f} - USER SIGNIFICANTLY LOWER")
        comparisons.append(False)
    
    # Compare violations
    if user_metrics['violations'] <= terminal_metrics['violations'] * 1.2:
        print(f"✅ Violations: User={user_metrics['violations']}, Terminal={terminal_metrics['violations']} - ACCEPTABLE")
        comparisons.append(True)
    else:
        print(f"❌ Violations: User={user_metrics['violations']}, Terminal={terminal_metrics['violations']} - USER SIGNIFICANTLY HIGHER")
        comparisons.append(False)
    
    # Compare conflicts
    if user_metrics['teacher_conflicts'] <= terminal_metrics['teacher_conflicts']:
        print(f"✅ Teacher Conflicts: User={user_metrics['teacher_conflicts']}, Terminal={terminal_metrics['teacher_conflicts']} - ACCEPTABLE")
        comparisons.append(True)
    else:
        print(f"❌ Teacher Conflicts: User={user_metrics['teacher_conflicts']}, Terminal={terminal_metrics['teacher_conflicts']} - USER HIGHER")
        comparisons.append(False)
    
    # Compare constraint satisfaction
    if user_metrics['constraint_satisfaction'] >= terminal_metrics['constraint_satisfaction'] * 0.9:
        print(f"✅ Constraint Satisfaction: User={user_metrics['constraint_satisfaction']:.1f}%, Terminal={terminal_metrics['constraint_satisfaction']:.1f}% - ACCEPTABLE")
        comparisons.append(True)
    else:
        print(f"❌ Constraint Satisfaction: User={user_metrics['constraint_satisfaction']:.1f}%, Terminal={terminal_metrics['constraint_satisfaction']:.1f}% - USER SIGNIFICANTLY LOWER")
        comparisons.append(False)
    
    success_rate = sum(comparisons) / len(comparisons) * 100
    return success_rate, comparisons

def cleanup_user_data(created_ids):
    """Clean up user-created data"""
    print(f"\n🧹 CLEANING UP USER DATA...")
    
    try:
        # Delete in reverse order to avoid foreign key issues
        for config_id in created_ids['configs']:
            ScheduleConfig.objects.filter(id=config_id).delete()
        
        for teacher_id in created_ids['teachers']:
            Teacher.objects.filter(id=teacher_id).delete()
        
        for classroom_id in created_ids['classrooms']:
            Classroom.objects.filter(id=classroom_id).delete()
        
        for subject_id in created_ids['subjects']:
            Subject.objects.filter(id=subject_id).delete()
        
        print("✅ User data cleaned up")
        
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def main():
    print("🔥 ULTIMATE BRUTAL TEST: USER DATA vs TERMINAL DATA")
    print("=" * 70)
    
    # Step 1: Create user data via API
    created_ids = create_user_data_via_api()
    if not created_ids:
        print("💥 FAILED: Could not create user data via API")
        return
    
    # Step 2: Test user data timetable generation
    user_config = ScheduleConfig.objects.get(id=created_ids['configs'][0])
    user_metrics = test_timetable_quality(user_config, "USER DATA")
    
    # Step 3: Test terminal/script data timetable generation
    terminal_config = ScheduleConfig.objects.filter(
        name__icontains='21SW'
    ).first()
    
    if not terminal_config:
        print("💥 FAILED: No terminal/script config found")
        cleanup_user_data(created_ids)
        return
    
    terminal_metrics = test_timetable_quality(terminal_config, "TERMINAL DATA")
    
    # Step 4: Compare quality
    if user_metrics['success'] and terminal_metrics['success']:
        success_rate, comparisons = compare_quality(user_metrics, terminal_metrics)
        
        print(f"\n" + "=" * 70)
        print("🎯 FINAL BRUTAL VERDICT")
        print("=" * 70)
        
        if success_rate >= 80:
            print(f"🎉 SUCCESS: {success_rate:.1f}% quality match")
            print("✅ USER DATA generates SAME QUALITY timetables as TERMINAL DATA")
            print("🚀 SYSTEM IS PRODUCTION READY!")
        else:
            print(f"💥 FAILURE: Only {success_rate:.1f}% quality match")
            print("❌ USER DATA generates INFERIOR timetables compared to TERMINAL DATA")
            print("🚫 SYSTEM NEEDS FIXES!")
    else:
        print(f"\n💥 CRITICAL FAILURE:")
        if not user_metrics['success']:
            print(f"❌ User data generation failed: {user_metrics.get('error', 'Unknown')}")
        if not terminal_metrics['success']:
            print(f"❌ Terminal data generation failed: {terminal_metrics.get('error', 'Unknown')}")
    
    # Cleanup
    cleanup_user_data(created_ids)
    print(f"\n" + "=" * 70)

if __name__ == "__main__":
    main()
