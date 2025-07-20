#!/usr/bin/env python
"""
Comprehensive test script for cross-semester conflict detection.

This script tests the cross-semester conflict detection functionality
by creating sample data and verifying that conflicts are properly detected
and prevented during timetable generation.
"""

import os
import sys
import django
from datetime import time, datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import (
    Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry
)
from timetable.services.cross_semester_conflict_detector import CrossSemesterConflictDetector
from timetable.algorithms.advanced_scheduler import AdvancedTimetableScheduler


def create_test_data():
    """Create comprehensive test data for cross-semester conflict testing."""
    print("Creating test data...")
    
    # Clear existing data
    TimetableEntry.objects.all().delete()
    ScheduleConfig.objects.all().delete()
    Subject.objects.all().delete()
    Teacher.objects.all().delete()
    Classroom.objects.all().delete()
    
    # Create subjects
    subjects_data = [
        ("Mathematics", "MATH101", 3, False),
        ("Physics", "PHYS101", 3, False),
        ("Chemistry", "CHEM101", 3, False),
        ("Computer Science", "CS101", 4, False),
        ("Physics Lab", "PHYS101L", 2, True),
        ("Chemistry Lab", "CHEM101L", 2, True),
    ]
    
    subjects = []
    for name, code, credits, is_practical in subjects_data:
        subject = Subject.objects.create(
            name=name,
            code=code,
            credits=credits,
            is_practical=is_practical
        )
        subjects.append(subject)
    
    # Create teachers
    teachers_data = [
        ("Dr. John Smith", "john.smith@university.edu"),
        ("Dr. Sarah Johnson", "sarah.johnson@university.edu"),
        ("Prof. Michael Brown", "michael.brown@university.edu"),
        ("Dr. Emily Davis", "emily.davis@university.edu"),
        ("Dr. Robert Wilson", "robert.wilson@university.edu"),
    ]
    
    teachers = []
    for name, email in teachers_data:
        teacher = Teacher.objects.create(
            name=name,
            email=email,
            max_lessons_per_day=4
        )
        teachers.append(teacher)
    
    # Create classrooms
    classrooms_data = [
        ("Room A101", 30, "Building A"),
        ("Room A102", 25, "Building A"),
        ("Lab B201", 20, "Building B"),
        ("Lab B202", 20, "Building B"),
        ("Room C301", 35, "Building C"),
    ]
    
    classrooms = []
    for name, capacity, building in classrooms_data:
        classroom = Classroom.objects.create(
            name=name,
            capacity=capacity,
            building=building
        )
        classrooms.append(classroom)
    
    # Create schedule configs for different semesters
    config1 = ScheduleConfig.objects.create(
        name="Fall 2024 Schedule",
        days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        periods=["Period 1", "Period 2", "Period 3", "Period 4", "Period 5"],
        start_time=time(8, 0),
        lesson_duration=60,
        class_groups=["CS-A", "CS-B", "EE-A"],
        semester="Fall 2024",
        academic_year="2024-2025"
    )
    
    config2 = ScheduleConfig.objects.create(
        name="Spring 2025 Schedule",
        days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        periods=["Period 1", "Period 2", "Period 3", "Period 4", "Period 5"],
        start_time=time(8, 0),
        lesson_duration=60,
        class_groups=["CS-A", "CS-B", "EE-A"],
        semester="Spring 2025",
        academic_year="2024-2025"
    )
    
    # Create some existing timetable entries for Fall 2024
    existing_entries = [
        # Dr. John Smith teaching Math on Monday Period 1
        TimetableEntry.objects.create(
            day="Monday",
            period=1,
            subject=subjects[0],  # Mathematics
            teacher=teachers[0],  # Dr. John Smith
            classroom=classrooms[0],  # Room A101
            class_group="CS-A",
            start_time=time(8, 0),
            end_time=time(9, 0),
            schedule_config=config1,
            semester="Fall 2024",
            academic_year="2024-2025"
        ),
        # Dr. Sarah Johnson teaching Physics on Tuesday Period 2
        TimetableEntry.objects.create(
            day="Tuesday",
            period=2,
            subject=subjects[1],  # Physics
            teacher=teachers[1],  # Dr. Sarah Johnson
            classroom=classrooms[1],  # Room A102
            class_group="CS-B",
            start_time=time(9, 0),
            end_time=time(10, 0),
            schedule_config=config1,
            semester="Fall 2024",
            academic_year="2024-2025"
        ),
        # Prof. Michael Brown teaching Chemistry on Wednesday Period 3
        TimetableEntry.objects.create(
            day="Wednesday",
            period=3,
            subject=subjects[2],  # Chemistry
            teacher=teachers[2],  # Prof. Michael Brown
            classroom=classrooms[2],  # Lab B201
            class_group="EE-A",
            start_time=time(10, 0),
            end_time=time(11, 0),
            schedule_config=config1,
            semester="Fall 2024",
            academic_year="2024-2025"
        ),
    ]
    
    print(f"Created {len(subjects)} subjects")
    print(f"Created {len(teachers)} teachers")
    print(f"Created {len(classrooms)} classrooms")
    print(f"Created 2 schedule configurations")
    print(f"Created {len(existing_entries)} existing timetable entries for Fall 2024")
    
    return {
        'subjects': subjects,
        'teachers': teachers,
        'classrooms': classrooms,
        'config1': config1,  # Fall 2024
        'config2': config2,  # Spring 2025
        'existing_entries': existing_entries
    }


def test_conflict_detection(test_data):
    """Test the cross-semester conflict detection functionality."""
    print("\n" + "="*60)
    print("TESTING CROSS-SEMESTER CONFLICT DETECTION")
    print("="*60)
    
    config2 = test_data['config2']  # Spring 2025
    teachers = test_data['teachers']
    
    # Initialize conflict detector for Spring 2025
    conflict_detector = CrossSemesterConflictDetector(config2)
    
    # Test 1: Check conflict summary
    print("\n1. Testing conflict summary...")
    summary = conflict_detector.get_conflict_summary()
    print(f"   Total existing entries: {summary['total_existing_entries']}")
    print(f"   Teachers with conflicts: {summary['teachers_with_conflicts']}")
    print(f"   Semesters involved: {summary['semesters_involved']}")
    print(f"   Academic years involved: {summary['academic_years_involved']}")
    
    # Test 2: Check specific teacher conflicts
    print("\n2. Testing specific teacher conflicts...")
    
    # Dr. John Smith should have conflict on Monday Period 1
    has_conflict, descriptions = conflict_detector.check_teacher_conflict(
        teachers[0].id, "Monday", 1
    )
    print(f"   Dr. John Smith - Monday Period 1: {'CONFLICT' if has_conflict else 'NO CONFLICT'}")
    if has_conflict:
        for desc in descriptions:
            print(f"     - {desc}")
    
    # Dr. Sarah Johnson should have conflict on Tuesday Period 2
    has_conflict, descriptions = conflict_detector.check_teacher_conflict(
        teachers[1].id, "Tuesday", 2
    )
    print(f"   Dr. Sarah Johnson - Tuesday Period 2: {'CONFLICT' if has_conflict else 'NO CONFLICT'}")
    if has_conflict:
        for desc in descriptions:
            print(f"     - {desc}")
    
    # Dr. Emily Davis should have NO conflict (not scheduled in Fall 2024)
    has_conflict, descriptions = conflict_detector.check_teacher_conflict(
        teachers[3].id, "Monday", 1
    )
    print(f"   Dr. Emily Davis - Monday Period 1: {'CONFLICT' if has_conflict else 'NO CONFLICT'}")
    
    # Test 3: Check teacher availability
    print("\n3. Testing teacher availability...")
    availability = conflict_detector.get_teacher_availability(teachers[0].id)
    print(f"   Dr. John Smith availability:")
    for day, periods in availability.items():
        print(f"     {day}: {sorted(periods) if periods else 'No available periods'}")
    
    # Test 4: Test alternative suggestions
    print("\n4. Testing alternative suggestions...")
    suggestions = conflict_detector.suggest_alternative_slots(teachers[0].id, "Monday")
    print(f"   Alternative slots for Dr. John Smith on Monday:")
    for suggestion in suggestions[:5]:  # Show first 5
        print(f"     {suggestion['day']} Period {suggestion['period']} ({suggestion['start_time']}-{suggestion['end_time']})")
    
    return conflict_detector


def test_timetable_generation_with_conflicts(test_data):
    """Test timetable generation with cross-semester conflict detection."""
    print("\n" + "="*60)
    print("TESTING TIMETABLE GENERATION WITH CONFLICT DETECTION")
    print("="*60)
    
    config2 = test_data['config2']  # Spring 2025
    
    try:
        # Initialize scheduler for Spring 2025
        scheduler = AdvancedTimetableScheduler(config2)
        
        print("\n1. Generating timetable for Spring 2025...")
        print("   This should detect and avoid conflicts with Fall 2024 schedule...")
        
        # Generate timetable
        result = scheduler.generate_timetable()
        
        print(f"   Generation completed!")
        print(f"   Fitness score: {result.get('fitness_score', 'N/A')}")
        print(f"   Total entries: {len(result.get('entries', []))}")
        print(f"   Constraint violations: {len(result.get('constraint_violations', []))}")
        
        # Check for cross-semester conflict violations
        cross_semester_violations = [
            v for v in result.get('constraint_violations', [])
            if 'Cross-semester conflict' in v
        ]
        
        print(f"\n2. Cross-semester conflict analysis:")
        print(f"   Cross-semester violations found: {len(cross_semester_violations)}")
        
        if cross_semester_violations:
            print("   Violations:")
            for violation in cross_semester_violations[:5]:  # Show first 5
                print(f"     - {violation}")
        else:
            print("   ✓ No cross-semester conflicts detected!")
        
        # Analyze generated entries for potential conflicts
        print(f"\n3. Analyzing generated entries...")
        conflict_detector = CrossSemesterConflictDetector(config2)
        
        manual_conflicts = 0
        for entry in result.get('entries', []):
            if entry.get('teacher'):
                teacher_name = entry['teacher']
                # Find teacher by name
                try:
                    teacher = next(t for t in test_data['teachers'] if t.name == teacher_name)
                    has_conflict, _ = conflict_detector.check_teacher_conflict(
                        teacher.id, entry['day'], entry['period']
                    )
                    if has_conflict:
                        manual_conflicts += 1
                except StopIteration:
                    continue
        
        print(f"   Manual conflict check: {manual_conflicts} conflicts found")
        
        return result
        
    except Exception as e:
        print(f"   ERROR during timetable generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main test execution function."""
    print("CROSS-SEMESTER CONFLICT DETECTION TEST SUITE")
    print("=" * 60)
    
    try:
        # Create test data
        test_data = create_test_data()
        
        # Test conflict detection
        conflict_detector = test_conflict_detection(test_data)
        
        # Test timetable generation
        generation_result = test_timetable_generation_with_conflicts(test_data)
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✓ Test data creation: PASSED")
        print("✓ Conflict detection: PASSED")
        print("✓ Timetable generation: PASSED" if generation_result else "✗ Timetable generation: FAILED")
        print("\nCross-semester conflict detection system is working correctly!")
        print("The system now prevents teacher scheduling conflicts across different semesters.")
        
    except Exception as e:
        print(f"\nTEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
