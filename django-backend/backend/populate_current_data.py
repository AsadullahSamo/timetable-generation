#!/usr/bin/env python3
"""
Updated Timetable Data Population Script
========================================

This script populates the database with the current state of data,
using the new TeacherSubjectAssignment model structure.

Usage:
    python populate_current_data.py [--clear]
"""

import os
import sys
import django
from django.db import transaction

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher, Classroom, Batch, TeacherSubjectAssignment, Config


def clear_data():
    """Clear existing data (except structural data)."""
    print("🗑️  CLEARING EXISTING DATA...")
    print("-" * 50)
    
    assignments_deleted = TeacherSubjectAssignment.objects.count()
    teachers_deleted = Teacher.objects.count()
    subjects_deleted = Subject.objects.count()
    classrooms_deleted = Classroom.objects.count()
    
    TeacherSubjectAssignment.objects.all().delete()
    Teacher.objects.all().delete()
    Subject.objects.all().delete()
    Classroom.objects.all().delete()
    # Keep Batch and Config as they are structural
    
    print(f"✅ Deleted {teachers_deleted} teachers")
    print(f"✅ Deleted {subjects_deleted} subjects")
    print(f"✅ Deleted {classrooms_deleted} classrooms")
    print(f"✅ Deleted {assignments_deleted} teacher assignments")
    print("✅ Kept batches and configs (structural data)")
    print()


def create_batches():
    """Create batches if they don't exist."""
    print("🎓 CREATING BATCHES...")
    print("-" * 50)
    
    batches_data = [
        {
            'name': '21SW',
            'description': '8th Semester - Final Year',
            'semester_number': 8,
            'academic_year': '2024-2025',
            'total_sections': 3
        },
        {
            'name': '22SW',
            'description': '6th Semester - Third Year',
            'semester_number': 6,
            'academic_year': '2024-2025',
            'total_sections': 3
        },
        {
            'name': '23SW',
            'description': '4th Semester - Second Year',
            'semester_number': 4,
            'academic_year': '2024-2025',
            'total_sections': 2
        },
        {
            'name': '24SW',
            'description': '2nd Semester - First Year',
            'semester_number': 2,
            'academic_year': '2024-2025',
            'total_sections': 2
        }
    ]
    
    created_count = 0
    for batch_data in batches_data:
        batch, created = Batch.objects.get_or_create(
            name=batch_data['name'],
            defaults=batch_data
        )
        if created:
            created_count += 1
            print(f"✅ Created: {batch.name} - {batch.description} ({batch.total_sections} sections)")
        else:
            print(f"⚪ Exists: {batch.name}")
    
    print(f"📊 Created {created_count} new batches")
    return created_count


def create_teachers():
    """Create teachers."""
    print("\n👨‍🏫 CREATING TEACHERS...")
    print("-" * 50)
    
    teachers_data = [
        {'name': 'Dr. Areej Fatemah', 'email': 'areej.fatemah@faculty.muet.edu.pk'},
        {'name': 'Dr. Rabeea Jaffari', 'email': 'rabeea.jaffari@faculty.muet.edu.pk'},
        {'name': 'Dr. S. M. Shehram Shah', 'email': 'shehram.shah@faculty.muet.edu.pk'},
        {'name': 'Dr. Sania Bhatti', 'email': 'sania.bhatti@faculty.muet.edu.pk'},
        {'name': 'Mr. Aqib Ali', 'email': 'aqib.ali@faculty.muet.edu.pk'},
        {'name': 'Mr. Arsalan', 'email': 'arsalan@faculty.muet.edu.pk'},
        {'name': 'Mr. Mansoor Bhaagat', 'email': 'mansoor.bhaagat@faculty.muet.edu.pk'},
        {'name': 'Mr. Naveen Kumar', 'email': 'naveen.kumar@faculty.muet.edu.pk'},
        {'name': 'Mr. Salahuddin Saddar', 'email': 'salahuddin.saddar@faculty.muet.edu.pk'},
        {'name': 'Mr. Sarwar Ali', 'email': 'sarwar.ali@faculty.muet.edu.pk'},
        {'name': 'Mr. Umar Farooq', 'email': 'umar.farooq@faculty.muet.edu.pk'},
        {'name': 'Ms. Aisha Esani', 'email': 'aisha.esani@faculty.muet.edu.pk'},
        {'name': 'Ms. Dua Agha', 'email': 'dua.agha@faculty.muet.edu.pk'},
        {'name': 'Ms. Mariam Memon', 'email': 'mariam.memon@faculty.muet.edu.pk'},
        {'name': 'Ms. Sana Faiz', 'email': 'sana.faiz@faculty.muet.edu.pk'},
        {'name': 'Ms. Shafya Qadeer', 'email': 'shafya.qadeer@faculty.muet.edu.pk'},
        {'name': 'Ms. Shazma Memon', 'email': 'shazma.memon@faculty.muet.edu.pk'},
        {'name': 'Ms. Soonti Taj', 'email': 'soonti.taj@faculty.muet.edu.pk'},
        {'name': 'Prof. Dr. Qasim Ali', 'email': 'qasim.ali@faculty.muet.edu.pk'},
        {'name': 'Dr. Mohsin Memon', 'email': 'mohsin.memon@faculty.muet.edu.pk'},
        {'name': 'Mr. Mansoor', 'email': 'mansoor@faculty.muet.edu.pk'},
        {'name': 'Ms. Amirta Dewani', 'email': 'amirta.dewani@faculty.muet.edu.pk'},
        {'name': 'Mr. Junaid Ahmed', 'email': 'junaid.ahmed@faculty.muet.edu.pk'},
        {'name': 'Ms. Aleena', 'email': 'aleena@faculty.muet.edu.pk'},
        {'name': 'Ms. Hina Ali', 'email': 'hina.ali@faculty.muet.edu.pk'},
    ]
    
    created_count = 0
    for teacher_data in teachers_data:
        teacher, created = Teacher.objects.get_or_create(
            email=teacher_data['email'],
            defaults=teacher_data
        )
        if created:
            created_count += 1
            print(f"✅ Created: {teacher.name}")
        else:
            print(f"⚪ Exists: {teacher.name}")
    
    print(f"📊 Created {created_count} new teachers")
    return created_count


def create_subjects():
    """Create subjects with batch assignments."""
    print("\n📚 CREATING SUBJECTS...")
    print("-" * 50)
    
    subjects_data = [
        # 21SW - 8th Semester (Final Year) - Theory
        {"name": "Simulation and Modeling", "code": "SM", "credits": 3, "is_practical": False, "batch": "21SW"},
        {"name": "Cloud Computing", "code": "CC", "credits": 3, "is_practical": False, "batch": "21SW"},
        {"name": "Software Quality Engineering", "code": "SQE", "credits": 3, "is_practical": False, "batch": "21SW"},

        # 22SW - 6th Semester (3rd Year) - Theory
        {"name": "Software Project Management", "code": "SPM", "credits": 3, "is_practical": False, "batch": "22SW"},
        {"name": "Data Science & Analytics", "code": "DS&A", "credits": 3, "is_practical": False, "batch": "22SW"},
        {"name": "Mobile Application Development", "code": "MAD", "credits": 3, "is_practical": False, "batch": "22SW"},
        {"name": "Discrete Structures", "code": "DS", "credits": 3, "is_practical": False, "batch": "22SW"},
        {"name": "Technical & Scientific Writing", "code": "TSW", "credits": 3, "is_practical": False, "batch": "22SW"},

        # 23SW - 4th Semester (2nd Year) - Theory
        {"name": "Information Security", "code": "IS", "credits": 3, "is_practical": False, "batch": "23SW"},
        {"name": "Human Computer Interaction", "code": "HCI", "credits": 3, "is_practical": False, "batch": "23SW"},
        {"name": "Agent Based Intelligent Systems", "code": "ABIS", "credits": 3, "is_practical": False, "batch": "23SW"},
        {"name": "Software Construction & Development", "code": "SCD", "credits": 3, "is_practical": False, "batch": "23SW"},
        {"name": "Statistics & Probability", "code": "SP", "credits": 3, "is_practical": False, "batch": "23SW"},

        # 24SW - 2nd Semester (1st Year) - Theory
        {"name": "Data Structure & Algorithm", "code": "DSA", "credits": 3, "is_practical": False, "batch": "24SW"},
        {"name": "Operations Research", "code": "OR", "credits": 3, "is_practical": False, "batch": "24SW"},
        {"name": "Software Requirement Engineering", "code": "SRE", "credits": 3, "is_practical": False, "batch": "24SW"},
        {"name": "Software Economics & Management", "code": "SEM", "credits": 3, "is_practical": False, "batch": "24SW"},
        {"name": "Database Systems", "code": "DBS", "credits": 3, "is_practical": False, "batch": "24SW"},

        # Practical subjects
        # 21SW Practicals
        {"name": "Cloud Computing Practical", "code": "CC Pr", "credits": 1, "is_practical": True, "batch": "21SW"},
        {"name": "Software Quality Engineering Practical", "code": "SQE Pr", "credits": 1, "is_practical": True, "batch": "21SW"},

        # 22SW Practicals
        {"name": "Data Science & Analytics Practical", "code": "DS&A Pr", "credits": 1, "is_practical": True, "batch": "22SW"},
        {"name": "Mobile Application Development Practical", "code": "MAD Pr", "credits": 1, "is_practical": True, "batch": "22SW"},

        # 23SW Practicals
        {"name": "Software Construction & Development Practical", "code": "SCD Pr", "credits": 1, "is_practical": True, "batch": "23SW"},

        # 24SW Practicals
        {"name": "Data Structure & Algorithm Practical", "code": "DSA Pr", "credits": 1, "is_practical": True, "batch": "24SW"},
        {"name": "Database Systems Practical", "code": "DBS Pr", "credits": 1, "is_practical": True, "batch": "24SW"},
    ]
    
    created_count = 0
    for subject_data in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults=subject_data
        )
        if created:
            created_count += 1
            practical_info = " (Practical)" if subject.is_practical else ""
            print(f"✅ Created: {subject.code} - {subject.name} -> {subject.batch}{practical_info}")
        else:
            print(f"⚪ Exists: {subject.code}")
    
    print(f"📊 Created {created_count} new subjects")
    return created_count


def create_classrooms():
    """Create classrooms."""
    print("\n🏫 CREATING CLASSROOMS...")
    print("-" * 50)
    
    classrooms_data = [
        {'name': 'Room 101', 'capacity': 40, 'building': 'Main Block'},
        {'name': 'Room 102', 'capacity': 35, 'building': 'Main Block'},
        {'name': 'Room 103', 'capacity': 45, 'building': 'Main Block'},
        {'name': 'Room 201', 'capacity': 40, 'building': 'Main Block'},
        {'name': 'Room 202', 'capacity': 35, 'building': 'Main Block'},
        {'name': 'Lab 1', 'capacity': 30, 'building': 'Lab Block'},
        {'name': 'Lab 2', 'capacity': 30, 'building': 'Lab Block'},
        {'name': 'Lab 3', 'capacity': 25, 'building': 'Lab Block'},
        {'name': 'Seminar Hall', 'capacity': 100, 'building': 'Main Block'},
        {'name': 'Conference Room', 'capacity': 20, 'building': 'Admin Block'},
    ]
    
    created_count = 0
    for classroom_data in classrooms_data:
        classroom, created = Classroom.objects.get_or_create(
            name=classroom_data['name'],
            defaults=classroom_data
        )
        if created:
            created_count += 1
            print(f"✅ Created: {classroom.name} (Capacity: {classroom.capacity})")
        else:
            print(f"⚪ Exists: {classroom.name}")
    
    print(f"📊 Created {created_count} new classrooms")
    return created_count


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate timetable database with current data structure')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before populating')
    
    args = parser.parse_args()
    
    if args.clear:
        confirm = input("\n⚠️  WARNING: This will delete ALL existing teachers, subjects, and assignments!\n"
                       "Are you sure you want to continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            return
    
    print("🎓 TIMETABLE DATA POPULATION - CURRENT STRUCTURE")
    print("=" * 80)
    
    try:
        with transaction.atomic():
            if args.clear:
                clear_data()
            
            create_batches()
            create_teachers()
            create_subjects()
            create_classrooms()
            
            print(f"\n🎉 DATA POPULATION COMPLETE!")
            print("=" * 80)
            print(f"✅ Teachers: {Teacher.objects.count()}")
            print(f"✅ Subjects: {Subject.objects.count()}")
            print(f"✅ Classrooms: {Classroom.objects.count()}")
            print(f"✅ Batches: {Batch.objects.count()}")
            print(f"✅ Teacher Assignments: {TeacherSubjectAssignment.objects.count()}")
            
            print(f"\n🎯 NEXT STEPS:")
            print("1. Use Teacher Assignments component to create teacher-subject-section assignments")
            print("2. Test timetable generation")
            print("3. The Class Groups field in DepartmentConfig is now redundant - use Batches instead")
            
    except Exception as e:
        print(f"❌ ERROR DURING POPULATION: {e}")
        print("🔄 Transaction rolled back - database unchanged")
        sys.exit(1)


if __name__ == "__main__":
    main()
