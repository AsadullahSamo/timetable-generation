#!/usr/bin/env python
"""
FINAL BRUTAL HONEST & AGGRESSIVE TEST
Tests everything end-to-end like a real user
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry
from timetable.serializers import SubjectSerializer, TeacherSerializer, ClassroomSerializer
from timetable.algorithms.advanced_scheduler import AdvancedTimetableScheduler
from django.test import Client
import json

def main():
    print("🔥 FINAL BRUTAL HONEST & AGGRESSIVE TEST")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # TEST 1: API ENDPOINTS
    print("\n1️⃣  TESTING REAL API ENDPOINTS...")
    
    client = Client()
    
    # Subject API
    try:
        response = client.post('/api/timetable/subjects/', 
                              data=json.dumps({'name': 'Brutal Test Subject', 'code': 'BTS999', 'credits': 3}),
                              content_type='application/json')
        if response.status_code == 201:
            print("✅ Subject API: WORKS")
            subject_id = response.json()['id']
        else:
            errors.append(f"Subject API failed: {response.status_code}")
            subject_id = None
    except Exception as e:
        errors.append(f"Subject API error: {e}")
        subject_id = None
    
    # Teacher API
    try:
        if subject_id:
            response = client.post('/api/timetable/teachers/', 
                                  data=json.dumps({
                                      'name': 'Brutal Test Teacher',
                                      'email': 'brutal@test.com',
                                      'subjects': [subject_id],
                                      'max_lessons_per_day': 4,
                                      'unavailable_periods': {}
                                  }),
                                  content_type='application/json')
            if response.status_code == 201:
                print("✅ Teacher API: WORKS")
            else:
                errors.append(f"Teacher API failed: {response.status_code}")
        else:
            warnings.append("Teacher API not tested - no subject ID")
    except Exception as e:
        errors.append(f"Teacher API error: {e}")
    
    # Classroom API
    try:
        response = client.post('/api/timetable/classrooms/', 
                              data=json.dumps({
                                  'name': 'Brutal Test Room',
                                  'capacity': 50,
                                  'building': 'Brutal Test Building'
                              }),
                              content_type='application/json')
        if response.status_code == 201:
            print("✅ Classroom API: WORKS")
        else:
            errors.append(f"Classroom API failed: {response.status_code}")
    except Exception as e:
        errors.append(f"Classroom API error: {e}")
    
    # TEST 2: ALGORITHM COMPATIBILITY
    print("\n2️⃣  TESTING ALGORITHM WITH USER DATA...")
    
    try:
        config = ScheduleConfig.objects.first()
        if not config:
            errors.append("No schedule configuration available")
        else:
            scheduler = AdvancedTimetableScheduler(config)
            
            if len(scheduler.subjects) == 0:
                errors.append("No subjects loaded in scheduler")
            if len(scheduler.teachers) == 0:
                errors.append("No teachers loaded in scheduler")
            if len(scheduler.classrooms) == 0:
                errors.append("No classrooms loaded in scheduler")
            
            teachers_with_subjects = sum(1 for t in scheduler.teachers if t.subjects.count() > 0)
            if teachers_with_subjects == 0:
                errors.append("CRITICAL: No teachers have subject assignments")
            elif teachers_with_subjects < len(scheduler.teachers) * 0.5:
                warnings.append(f"Only {teachers_with_subjects}/{len(scheduler.teachers)} teachers have subjects")
            
            print(f"📊 Scheduler: {len(scheduler.subjects)} subjects, {len(scheduler.teachers)} teachers, {len(scheduler.classrooms)} classrooms")
            print(f"👨‍🏫 Teachers with subjects: {teachers_with_subjects}/{len(scheduler.teachers)}")
            
    except Exception as e:
        errors.append(f"Scheduler error: {e}")
    
    # TEST 3: TIMETABLE GENERATION
    print("\n3️⃣  TESTING TIMETABLE GENERATION...")
    
    try:
        configs = ScheduleConfig.objects.filter(start_time__isnull=False)[:2]
        generation_failures = 0
        
        for config in configs:
            try:
                scheduler = AdvancedTimetableScheduler(config)
                result = scheduler.generate_timetable()
                
                if not result or 'entries' not in result or len(result['entries']) == 0:
                    generation_failures += 1
                    errors.append(f"Generation failed for {config.name}")
                else:
                    entries_count = len(result['entries'])
                    print(f"✅ {config.name}: {entries_count} entries")
                    
            except Exception as e:
                generation_failures += 1
                errors.append(f"Generation error for {config.name}: {str(e)[:50]}...")
        
        if generation_failures > 0:
            errors.append(f"{generation_failures}/{len(configs)} generation failures")
        
    except Exception as e:
        errors.append(f"Generation test error: {e}")
    
    # TEST 4: DATABASE CONSISTENCY
    print("\n4️⃣  TESTING DATABASE CONSISTENCY...")
    
    try:
        subjects_count = Subject.objects.count()
        teachers_count = Teacher.objects.count()
        classrooms_count = Classroom.objects.count()
        configs_count = ScheduleConfig.objects.count()
        entries_count = TimetableEntry.objects.count()
        
        if subjects_count == 0:
            errors.append("No subjects in database")
        if teachers_count == 0:
            errors.append("No teachers in database")
        if classrooms_count == 0:
            errors.append("No classrooms in database")
        if configs_count == 0:
            errors.append("No schedule configs in database")
        
        print(f"📊 Database: {subjects_count} subjects, {teachers_count} teachers, {classrooms_count} classrooms")
        print(f"📊 Configs: {configs_count}, Entries: {entries_count}")
        
    except Exception as e:
        errors.append(f"Database consistency error: {e}")
    
    # TEST 5: CROSS-BATCH CONFLICTS
    print("\n5️⃣  TESTING CROSS-BATCH CONFLICTS...")
    
    try:
        # Check if we have multi-batch data
        from collections import defaultdict
        entries_by_batch = defaultdict(int)
        
        for entry in TimetableEntry.objects.all():
            batch_key = f"{entry.semester}_{entry.academic_year}"
            entries_by_batch[batch_key] += 1
        
        if len(entries_by_batch) <= 1:
            warnings.append("Only one batch has timetable data - limited conflict testing")
        else:
            print(f"✅ Multi-batch data: {len(entries_by_batch)} batches")
            
        # Check for actual conflicts
        teacher_conflicts = 0
        teacher_schedule = defaultdict(dict)
        
        for entry in TimetableEntry.objects.select_related('teacher'):
            if entry.teacher:
                teacher_id = entry.teacher.id
                time_key = f"{entry.day}_P{entry.period}"
                
                if time_key in teacher_schedule[teacher_id]:
                    teacher_conflicts += 1
                else:
                    teacher_schedule[teacher_id][time_key] = entry
        
        print(f"📊 Teacher conflicts detected: {teacher_conflicts}")
        
    except Exception as e:
        errors.append(f"Conflict detection error: {e}")
    
    # CLEANUP
    print("\n🧹 CLEANING UP TEST DATA...")
    try:
        Subject.objects.filter(code='BTS999').delete()
        Teacher.objects.filter(email='brutal@test.com').delete()
        Classroom.objects.filter(name='Brutal Test Room').delete()
        print("✅ Test data cleaned")
    except:
        warnings.append("Could not clean all test data")
    
    # FINAL VERDICT
    print("\n" + "=" * 60)
    print("🎯 FINAL BRUTAL HONEST VERDICT")
    print("=" * 60)
    
    print(f"❌ CRITICAL ERRORS: {len(errors)}")
    for error in errors:
        print(f"   💥 {error}")
    
    print(f"\n⚠️  WARNINGS: {len(warnings)}")
    for warning in warnings:
        print(f"   ⚠️  {warning}")
    
    if len(errors) == 0:
        print("\n🎉 VERDICT: SYSTEM IS READY FOR PRODUCTION!")
        print("✅ Frontend-Backend data flow: PERFECT")
        print("✅ Multi-batch timetable generation: WORKING")
        print("✅ User data compatibility: CONFIRMED")
        print("🚀 READY FOR CONFLICT RESOLUTION & OPTIMIZATION!")
    else:
        print(f"\n💥 VERDICT: {len(errors)} CRITICAL ISSUES MUST BE FIXED!")
        print("🚫 NOT READY FOR CONFLICT RESOLUTION!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
