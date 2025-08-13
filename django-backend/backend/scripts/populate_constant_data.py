#!/usr/bin/env python3
"""
DATA POPULATION SCRIPT
=====================
Populates the database with all necessary data including:
- Teachers
- Batches with sections (21SW-8th, 22SW-6th, 23SW-5th, 24SW-3rd)
- Subjects (assigned to batches)
- Classrooms
- Teacher-Subject-Section assignments
- All data except timetable entries

Usage: python populate_data.py
"""

import os
import sys
import django

# Add the parent directory to Python path so we can import backend module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Teacher, Subject, Classroom, Batch, TeacherSubjectAssignment

def populate_batches():
    """Create all batches with their sections"""
    print('\n=== CREATING BATCHES ===')
    
    batches_data = [
        {
            'name': '21SW',
            'description': '8th Semester - Final Year',
            'semester_number': 8,
            'total_sections': 3,
            'academic_year': '2024-2025'
        },
        {
            'name': '22SW',
            'description': '6th Semester - 3rd Year',
            'semester_number': 6,
            'total_sections': 3,
            'academic_year': '2024-2025'
        },
        {
            'name': '23SW',
            'description': '5th Semester - 2nd Year',
            'semester_number': 5,
            'total_sections': 3,
            'academic_year': '2024-2025'
        },
        {
            'name': '24SW',
            'description': '3rd Semester - 1st Year',
            'semester_number': 3,
            'total_sections': 3,
            'academic_year': '2024-2025'
        }
    ]
    
    for batch_data in batches_data:
        batch, created = Batch.objects.get_or_create(
            name=batch_data['name'],
            defaults=batch_data
        )
        if created:
            print(f'   ✅ Created: {batch.name} - {batch.description} ({batch.total_sections} sections)')
        else:
            # Update batch data if it exists but has different values
            updated = False
            for field, value in batch_data.items():
                if field != 'name' and getattr(batch, field) != value:
                    setattr(batch, field, value)
                    updated = True
            
            if updated:
                batch.save()
                print(f'   🔄 Updated: {batch.name} - {batch.description} ({batch.total_sections} sections)')
            else:
                print(f'   ⚪ Exists: {batch.name} - {batch.description} ({batch.total_sections} sections)')
    
    print(f'Total batches: {Batch.objects.count()}')
    
    # Show all batches with their sections
    print('\n📋 Batch Details:')
    for batch in Batch.objects.all().order_by('-semester_number'):
        sections = batch.get_sections()
        print(f'   {batch.name}: {batch.description} - Sections: {", ".join(sections)}')

def populate_classrooms():
    """Create all classrooms"""
    print('\n=== CREATING CLASSROOMS ===')
    classrooms_data = [
        {'name': 'Room 01', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Room 02', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Room 03', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Room 04', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'A.C. Room 01', 'capacity': 50, 'building': 'Academic Building'},
        {'name': 'A.C. Room 02', 'capacity': 50, 'building': 'Academic Building'},
        {'name': 'A.C. Room 03', 'capacity': 50, 'building': 'Academic Building'},
        {'name': 'Lab 1', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Lab 2', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Lab 3', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Lab 4', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Lab 5', 'capacity': 50, 'building': 'Main Building'},
        {'name': 'Lab 6', 'capacity': 50, 'building': 'Main Building'},
    ]

    for classroom_data in classrooms_data:
        classroom, created = Classroom.objects.get_or_create(
            name=classroom_data['name'],
            defaults=classroom_data
        )
        if created:
            print(f'   ✅ Created: {classroom.name} (Capacity: {classroom.capacity})')
        else:
            print(f'   ⚪ Exists: {classroom.name} (Capacity: {classroom.capacity})')

    print(f'Total classrooms: {Classroom.objects.count()}')

def main():
    """Main function to populate all data"""
    print('🚀 STARTING DATA POPULATION')
    print('=' * 50)
    
    # Populate in order
    populate_batches()
    populate_classrooms()
    
    print('\n' + '=' * 50)
    print('✅ DATA POPULATION COMPLETE!')
    print(f'📊 Final counts:')
    print(f'   Batches: {Batch.objects.count()}')
    print(f'   Classrooms: {Classroom.objects.count()}')
    print('\n🎯 Populated constant data')

if __name__ == '__main__':
    main()
