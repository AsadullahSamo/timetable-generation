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

def populate_teachers():
    """Create all teachers"""
    print('=== CREATING TEACHERS ===')
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
        {'name': 'Ms.Memona Sami', 'email': 'memona.sami@faculty.muet.edu.pk'},
    ]

    for teacher_data in teachers_data:
        teacher, created = Teacher.objects.get_or_create(
            email=teacher_data['email'],
            defaults=teacher_data
        )
        if created:
            print(f'   ✅ Created: {teacher.name}')
        else:
            print(f'   ⚪ Exists: {teacher.name}')

    print(f'Total teachers: {Teacher.objects.count()}')

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

def populate_subjects():
    """Create all subjects and assign them to batches"""
    print('\n=== CREATING SUBJECTS ===')
    
    # 21SW - 8th Semester (Final Year)
    subjects_21sw = [
        ('SM', 'Simulation and Modeling', 3, False),
        ('SQE', 'Software Quality Engineering', 3, False),
        ('SQE2', 'Software Quality Engineering (PR)', 1, True),
        ('CC', 'Cloud Computing', 3, False),
        ('CC2', 'Cloud Computing (PR)', 1, True),
    ]
    
    # 22SW - 6th Semester (3rd Year)
    subjects_22sw = [
        ('SPM', 'Software Project Management', 3, False),
        ('TSW', 'Technical & Scientific Writing', 2, False),
        ('DS', 'Discrete Structures', 3, False),
        ('DSA2', 'Data Science & Analytics', 3, False),
        ('DSA3', 'Data Science & Analytics (PR)', 1, True),
        ('MAD', 'Mobile Application Development', 3, False),
        ('MAD2', 'Mobile Application Development (PR)', 1, True),
    ]
    
    # 23SW - 4th Semester (2nd Year)
    subjects_23sw = [
        ('ABIS', 'Agent based Intelligent Systems', 3, False),
        ('ISEC', 'Information Security', 3, False),
        ('HCI', 'Human Computer Interaction', 3, False),
        ('SP', 'Statistics & Probability', 1, False),
        ('SCD', 'Software Construction & Development', 2, False),
        ('SCD2', 'Software Construction & Development (PR)', 1, True),
    ]
    
    # 24SW - 2nd Semester (1st Year)
    subjects_24sw = [
        ('DBS', 'Database Systems', 3, False),
        ('DBS2', 'Database Systems (PR)', 1, True),
        ('DSA', 'Data Structures & Algorithm', 3, False),
        ('DSA4', 'Data Structures & Algorithm (PR)', 1, True),
        ('SRE', 'Software Requirement Engineering', 3, False),
        ('OR', 'Operations Research', 3, False),
        ('SEM', 'Software Economics & Management', 3, False),
    ]
    
    all_subjects = [
        ('21SW', subjects_21sw),
        ('22SW', subjects_22sw),
        ('23SW', subjects_23sw),
        ('24SW', subjects_24sw),
    ]
    
    for batch_name, subjects in all_subjects:
        print(f'\n--- {batch_name} Subjects ---')
        for code, name, credits, is_practical in subjects:
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'credits': credits,
                    'is_practical': is_practical,
                    'batch': batch_name
                }
            )
            if created:
                print(f'   ✅ Created: {code} - {name}')
            else:
                # Update batch if it was missing
                if not subject.batch:
                    subject.batch = batch_name
                    subject.save()
                    print(f'   🔄 Updated batch for: {code} - {name}')
                else:
                    print(f'   ⚪ Exists: {code} - {name}')

    print(f'\nTotal subjects: {Subject.objects.count()}')

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

def populate_teacher_assignments():
    """Create teacher-subject-section assignments"""
    print('\n=== CREATING TEACHER ASSIGNMENTS ===')
    
    # Teacher assignments with specific sections
    assignments_data = [
        # 21SW assignments
        ('Dr. Sania Bhatti', 'SM', '21SW', ['I', 'II']),
        ('Mr.Umar Farooq', 'SM', '21SW', ['III']),
        ('Mr. Aqib Ali', 'SQE', '21SW', ['I', 'II', 'III']),
        ('Mr. Aqib Ali', 'SQE2', '21SW', ['I', 'II', 'III']),
        ('Dr. Rabeea Jaffari', 'CC', '21SW', ['I', 'II', 'III']),
        ('Ms. Sana Faiz', 'CC2', '21SW', ['I', 'II', 'III']),
        
        # 22SW assignments
        ('Mr. Salahuddin Saddar', 'SPM', '22SW', ['I', 'II', 'III']),
        ('Ms. Shazma Memon', 'TSW', '22SW', ['I', 'II']),
        ('Mr. Sarwar Ali', 'TSW', '22SW', ['III']),
        ('Ms. Shafya Qadeer', 'DS', '22SW', ['I', 'II', 'III']),
        ('Dr.Areej Fatemah', 'DSA2', '22SW', ['I', 'II', 'III']),
        ('Ms. Aisha Esani', 'DSA3', '22SW', ['I', 'II', 'III']),
        ('Ms. Mariam Memon', 'MAD', '22SW', ['I', 'II', 'III']),
        ('Mr. Umar Farooq', 'MAD2', '22SW', ['I', 'II', 'III']),
        
        # 23SW assignments
        ('Mr. Naveen Kumar', 'ABIS', '23SW', ['I', 'II', 'III']),
        ('Prof. Dr. Qasim Ali', 'ISEC', '23SW', ['I']),
        ('Ms. Soonti Taj', 'ISEC', '23SW', ['II', 'III']),
        ('Dr. S. M. Shehram Shah', 'HCI', '23SW', ['I', 'II']),
        ('Mr. Arsalan', 'HCI', '23SW', ['III']),
        ('Mr. Mansoor Bhaagat', 'SP', '23SW', ['I', 'II', 'III']),
        ('Ms. Dua Agha', 'SCD', '23SW', ['I', 'II', 'III']),
        ('Ms. Dua Agha', 'SCD2', '23SW', ['I', 'II', 'III']),
        
        # 24SW assignments
        ('Ms. Aleena', 'DBS', '24SW', ['I', 'II', 'III']),
        ('Ms. Hina Ali', 'DBS2', '24SW', ['I', 'II', 'III']),
        ('Dr. Mohsin Memon', 'DSA', '24SW', ['I', 'II']),
        ('Mr. Mansoor', 'DSA', '24SW', ['III']),
        ('Mr. Naveen Kumar', 'DSA4', '24SW', ['I', 'II', 'III']),
        ('Ms.Memona Sami', 'SRE', '24SW', ['I', 'II', 'III']),
        ('Ms. Amirta Dewani', 'OR', '24SW', ['I', 'II', 'III']),
        ('Mr. Junaid Ahmed', 'SEM', '24SW', ['I', 'II', 'III']),
    ]
    
    for teacher_name, subject_code, batch_name, sections in assignments_data:
        try:
            teacher = Teacher.objects.get(name=teacher_name)
            subject = Subject.objects.get(code=subject_code)
            batch = Batch.objects.get(name=batch_name)
            
            assignment, created = TeacherSubjectAssignment.objects.get_or_create(
                teacher=teacher,
                subject=subject,
                batch=batch,
                defaults={'sections': sections}
            )
            
            if created:
                print(f'   ✅ Created: {teacher_name} -> {subject_code} ({batch_name} - {", ".join(sections)})')
            else:
                # Update sections if different
                if set(assignment.sections) != set(sections):
                    assignment.sections = sections
                    assignment.save()
                    print(f'   🔄 Updated: {teacher_name} -> {subject_code} ({batch_name} - {", ".join(sections)})')
                else:
                    print(f'   ⚪ Exists: {teacher_name} -> {subject_code} ({batch_name} - {", ".join(sections)})')
                    
        except Teacher.DoesNotExist:
            print(f'   ❌ Teacher not found: {teacher_name}')
        except Subject.DoesNotExist:
            print(f'   ❌ Subject not found: {subject_code}')
        except Batch.DoesNotExist:
            print(f'   ❌ Batch not found: {batch_name}')
    
    print(f'Total teacher assignments: {TeacherSubjectAssignment.objects.count()}')

def main():
    """Main function to populate all data"""
    print('🚀 STARTING DATA POPULATION')
    print('=' * 50)
    
    # Populate in order
    populate_teachers()
    populate_batches()
    populate_subjects()
    populate_classrooms()
    populate_teacher_assignments()
    
    print('\n' + '=' * 50)
    print('✅ DATA POPULATION COMPLETE!')
    print(f'📊 Final counts:')
    print(f'   Teachers: {Teacher.objects.count()}')
    print(f'   Batches: {Batch.objects.count()}')
    print(f'   Subjects: {Subject.objects.count()}')
    print(f'   Classrooms: {Classroom.objects.count()}')
    print(f'   Teacher Assignments: {TeacherSubjectAssignment.objects.count()}')
    print('\n🎯 Database is ready for timetable generation!')

if __name__ == '__main__':
    main()
