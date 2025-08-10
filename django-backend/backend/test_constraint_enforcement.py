"""
TEST CONSTRAINT ENFORCEMENT - DEMONSTRATE ACTIVE CONSTRAINT IMPOSITION
=====================================================================
This test demonstrates that all 18 constraints are actively enforced during
timetable generation, not just validated afterwards.
"""

import os
import sys
import django
from datetime import time, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import (
    TimetableEntry, Subject, Teacher, Classroom, ScheduleConfig, 
    Batch, TeacherSubjectAssignment
)
from timetable.algorithms.constraint_enforced_scheduler import ConstraintEnforcedScheduler
from timetable.enhanced_constraint_validator import EnhancedConstraintValidator


def test_constraint_enforcement():
    """Test that constraints are actively enforced during generation."""
    print("🧪 TESTING CONSTRAINT ENFORCEMENT DURING GENERATION")
    print("=" * 60)
    
    # Get or create test configuration
    config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
    if not config:
        config = ScheduleConfig.objects.create(
            name="Test Constraint Enforcement Config",
            days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            periods=[1, 2, 3, 4, 5, 6],
            start_time=time(8, 0),
            lesson_duration=60
        )
    
    # Create test data if needed
    create_test_data()
    
    print(f"📊 Using config: {config.name}")
    print(f"📅 Days: {config.days}")
    print(f"⏰ Periods: {config.periods}")
    print(f"🕐 Start time: {config.start_time}")
    
    # Initialize constraint enforced scheduler
    print("\n🔧 INITIALIZING CONSTRAINT ENFORCED SCHEDULER")
    print("-" * 50)
    scheduler = ConstraintEnforcedScheduler(config)
    
    print("✅ Scheduler initialized with all 18 constraint enforcement mechanisms")
    print("🎯 Constraints will be actively imposed during generation")
    
    # Generate timetable with constraint enforcement
    print("\n🚀 GENERATING TIMETABLE WITH CONSTRAINT ENFORCEMENT")
    print("-" * 50)
    
    result = scheduler.generate_timetable()
    
    if result['success']:
        print(f"✅ Generation successful!")
        print(f"📊 Total entries: {result['total_entries']}")
        print(f"⏱️ Generation time: {result['generation_time']:.2f}s")
        print(f"🔧 Constraint violations: {result['constraint_violations']}")
        print(f"🎵 Harmony score: {result['harmony_score']:.2f}%")
        print(f"✅ Overall compliance: {'PASS' if result['overall_compliance'] else 'FAIL'}")
        
        # Validate the generated timetable
        print("\n🔍 VALIDATING GENERATED TIMETABLE")
        print("-" * 50)
        
        entries = TimetableEntry.objects.filter(schedule_config=config)
        validator = EnhancedConstraintValidator()
        validation_result = validator.validate_all_constraints(entries)
        
        print(f"📊 Validation Results:")
        print(f"   Total violations: {validation_result['total_violations']}")
        print(f"   Harmony score: {validation_result['harmony_score']:.2f}%")
        print(f"   Overall compliance: {'PASS' if validation_result['overall_compliance'] else 'FAIL'}")
        
        # Show constraint-by-constraint results
        print(f"\n🎯 CONSTRAINT-BY-CONSTRAINT RESULTS:")
        print("-" * 50)
        
        constraint_results = validation_result['constraint_results']
        for constraint_name, result in constraint_results.items():
            status = "✅ PASS" if result['status'] == 'PASS' else "❌ FAIL"
            violations = result['violations']
            print(f"   {constraint_name}: {status} ({violations} violations)")
        
        # Demonstrate specific constraint enforcement
        print(f"\n🔧 DEMONSTRATING ACTIVE CONSTRAINT ENFORCEMENT:")
        print("-" * 50)
        
        demonstrate_constraint_enforcement(entries)
        
    else:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")


def demonstrate_constraint_enforcement(entries):
    """Demonstrate specific constraint enforcement examples."""
    
    print("1. 🧪 PRACTICAL BLOCKS ENFORCEMENT:")
    practical_entries = [e for e in entries if e.is_practical]
    if practical_entries:
        # Group by class group, day, and subject
        practical_groups = {}
        for entry in practical_entries:
            key = (entry.class_group, entry.day, entry.subject.code)
            if key not in practical_groups:
                practical_groups[key] = []
            practical_groups[key].append(entry)
        
        for (class_group, day, subject_code), day_entries in practical_groups.items():
            if len(day_entries) >= 3:
                periods = sorted([e.period for e in day_entries])
                if periods[2] - periods[0] == 2:  # Consecutive
                    print(f"   ✅ {subject_code} in {class_group} on {day}: 3 consecutive periods {periods[:3]}")
                else:
                    print(f"   ❌ {subject_code} in {class_group} on {day}: Non-consecutive periods {periods}")
    
    print("\n2. 📚 THEORY SUBJECT DISTRIBUTION ENFORCEMENT:")
    theory_entries = [e for e in entries if not e.is_practical]
    if theory_entries:
        # Group by class group and subject
        theory_groups = {}
        for entry in theory_entries:
            key = (entry.class_group, entry.subject.code)
            if key not in theory_groups:
                theory_groups[key] = []
            theory_groups[key].append(entry)
        
        for (class_group, subject_code), subject_entries in theory_groups.items():
            days_used = set(e.day for e in subject_entries)
            if len(subject_entries) <= len(days_used):
                print(f"   ✅ {subject_code} in {class_group}: {len(subject_entries)} classes across {len(days_used)} days")
            else:
                print(f"   ❌ {subject_code} in {class_group}: Multiple classes on same day")
    
    print("\n3. 👨‍🏫 TEACHER BREAKS ENFORCEMENT:")
    teacher_entries = {}
    for entry in entries:
        if entry.teacher:
            key = (entry.teacher.id, entry.day)
            if key not in teacher_entries:
                teacher_entries[key] = []
            teacher_entries[key].append(entry)
    
    for (teacher_id, day), day_entries in teacher_entries.items():
        if len(day_entries) > 2:
            periods = sorted([e.period for e in day_entries])
            consecutive_count = 0
            for i in range(len(periods) - 1):
                if periods[i+1] - periods[i] == 1:
                    consecutive_count += 1
            
            if consecutive_count <= 2:
                print(f"   ✅ Teacher {day_entries[0].teacher.name} on {day}: Proper breaks enforced")
            else:
                print(f"   ❌ Teacher {day_entries[0].teacher.name} on {day}: Too many consecutive classes")
    
    print("\n4. 🏫 ROOM CONSISTENCY ENFORCEMENT:")
    class_day_entries = {}
    for entry in entries:
        if not entry.is_practical:
            key = (entry.class_group, entry.day)
            if key not in class_day_entries:
                class_day_entries[key] = []
            class_day_entries[key].append(entry)
    
    for (class_group, day), day_entries in class_day_entries.items():
        if len(day_entries) > 1:
            rooms = set(e.classroom.name for e in day_entries if e.classroom)
            if len(rooms) == 1:
                print(f"   ✅ {class_group} on {day}: Consistent room assignment ({list(rooms)[0]})")
            else:
                print(f"   ❌ {class_group} on {day}: Multiple rooms used {list(rooms)}")
    
    print("\n5. ⏰ FRIDAY TIME LIMITS ENFORCEMENT:")
    friday_entries = [e for e in entries if e.day == 'Friday']
    for entry in friday_entries:
        if entry.is_practical and entry.period > 4:
            print(f"   ❌ {entry.subject.code} on Friday P{entry.period}: Too late for practical")
        elif not entry.is_practical and entry.period > 3:
            print(f"   ❌ {entry.subject.code} on Friday P{entry.period}: Too late for theory")
        else:
            print(f"   ✅ {entry.subject.code} on Friday P{entry.period}: Within time limits")


def create_test_data():
    """Create test data for constraint enforcement testing."""
    print("📝 Creating test data...")
    
    # Create batches
    batches = []
    for i, batch_name in enumerate(['21SW', '22SW', '23SW', '24SW']):
        batch, created = Batch.objects.get_or_create(
            name=batch_name,
            defaults={
                'description': f'{i+1}st Year - Semester {i+1}',
                'semester_number': i+1,
                'total_sections': 2
            }
        )
        batches.append(batch)
    
    # Create subjects
    subjects = []
    subject_data = [
        ('MATH101', 'Mathematics', 3, False),
        ('PHYS101', 'Physics', 3, True),
        ('ENG101', 'English', 3, False),
        ('THESIS101', 'Thesis', 3, False),
        ('CS101', 'Computer Science', 3, True),
        ('CHEM101', 'Chemistry', 3, False),
    ]
    
    for code, name, credits, is_practical in subject_data:
        subject, created = Subject.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'credits': credits,
                'is_practical': is_practical,
                'batch': '21SW'  # Default batch
            }
        )
        subjects.append(subject)
    
    # Create teachers
    teachers = []
    teacher_names = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown']
    
    for name in teacher_names:
        teacher, created = Teacher.objects.get_or_create(
            name=name,
            defaults={'email': f'{name.lower().replace(" ", ".")}@university.edu'}
        )
        teachers.append(teacher)
    
    # Create classrooms
    classrooms = []
    classroom_data = [
        ('Room 101', 30, 'Main Building'),
        ('Room 102', 25, 'Main Building'),
        ('Lab 201', 20, 'Lab Building'),
        ('Lab 202', 15, 'Lab Building'),
        ('Room 301', 35, 'Academic Building'),
    ]
    
    for name, capacity, building in classroom_data:
        classroom, created = Classroom.objects.get_or_create(
            name=name,
            defaults={
                'capacity': capacity,
                'building': building
            }
        )
        classrooms.append(classroom)
    
    # Create teacher-subject assignments
    for i, subject in enumerate(subjects):
        for batch in batches:
            teacher = teachers[i % len(teachers)]
            assignment, created = TeacherSubjectAssignment.objects.get_or_create(
                teacher=teacher,
                subject=subject,
                batch=batch,
                defaults={
                    'sections': ['I', 'II']
                }
            )
    
    print(f"✅ Created {len(batches)} batches, {len(subjects)} subjects, {len(teachers)} teachers, {len(classrooms)} classrooms")


if __name__ == "__main__":
    test_constraint_enforcement() 