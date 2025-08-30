#!/usr/bin/env python3
"""
SPRING SEMESTER DATA POPULATION SCRIPT
=====================================
Populates the database with the current spring semester data including:
- Teachers (38 total)
- Batches with sections (21SW-7th, 22SW-5th, 23SW-4th, 24SW-2nd)
- Subjects (assigned to batches)
- Classrooms
- Teacher-Subject-Section assignments
- All data except timetable entries

Usage: python populate_spring_semester_data.py
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
        {'name': 'Dr. Anoud Shaikh', 'email': 'anoud.shaikh@faculty.muet.edu.pk'},
        {'name': 'Dr. Areej Fatemah', 'email': 'areej.fatemah@faculty.muet.edu.pk'},
        {'name': 'Dr. Asma Zubadi', 'email': 'asma.zubadi@faculty.muet.edu.pk'},
        {'name': 'Dr. Mohsin Memon', 'email': 'mohsin.memon@faculty.muet.edu.pk'},
        {'name': 'Dr. Naeem Ahmad', 'email': 'naeem.ahmad@faculty.muet.edu.pk'},
        {'name': 'Dr. Rabeea Jaffari', 'email': 'rabeea.jaffari@faculty.muet.edu.pk'},
        {'name': 'Dr. S.M. Shehram Shah', 'email': 'shehram.shah@faculty.muet.edu.pk'},
        {'name': 'Dr. Saba Qureshi', 'email': 'saba.qureshi@faculty.muet.edu.pk'},
        {'name': 'Dr. Sania Bhatti', 'email': 'sania.bhatti@faculty.muet.edu.pk'},
        {'name': 'Mr Hafiz Imran Junejo', 'email': 'hafiz.imran@faculty.muet.edu.pk'},
        {'name': 'Mr. Ali Asghar Sangha', 'email': 'ali.asghar@faculty.muet.edu.pk'},
        {'name': 'Mr. Aqib', 'email': 'aqib@faculty.muet.edu.pk'},
        {'name': 'Mr. Arsalan Aftab', 'email': 'arsalan.aftab@faculty.muet.edu.pk'},
        {'name': 'Mr. Asadullah', 'email': 'asadullah.channar@faculty.muet.edu.pk'},
        {'name': 'Mr. Irshad Ali Burfat', 'email': 'irshad.ali@faculty.muet.edu.pk'},
        {'name': 'Mr. Junaid Ahmad', 'email': 'junaid.ahmad@faculty.muet.edu.pk'},
        {'name': 'Mr. Mansoor Bhaagat', 'email': 'mansoor.bhaggat@faculty.muet.edu.pk'},
        {'name': 'Mr. Mansoor Samo', 'email': 'mansoor.samo@faculty.muet.edu.pk'},
        {'name': 'Mr. Naveen Kumar', 'email': 'naveen.kumar@faculty.muet.edu.pk'},
        {'name': 'Mr. Sajjad Ali', 'email': 'sajjad.ali@faculty.muet.edu.pk'},
        {'name': 'Mr. Salahuddin Saddar', 'email': 'salahuddin.saddari@faculty.muet.edu.pk'},
        {'name': 'Mr. Sarwar Ali', 'email': 'sarwar.ali@faculty.muet.edu.pk'},
        {'name': 'Mr. Tabish', 'email': 'tabish@faculty.muet.edu.pk'},
        {'name': 'Mr. Umar', 'email': 'umar@faculty.muet.edu.pk'},
        {'name': 'Mr. Zulfiqar', 'email': 'zulfiqar@faculty.muet.edu.pk'},
        {'name': 'Ms. Afifah', 'email': 'afifah@faculty.muet.edu.pk'},
        {'name': 'Ms. Aleena', 'email': 'aleena@faculty.muet.edu.pk'},
        {'name': 'Ms. Amirita', 'email': 'amirita@faculty.muet.edu.pk'},
        {'name': 'Ms. Amna Baloch', 'email': 'amna.baloch@faculty.muet.edu.pk'},
        {'name': 'Ms. Aysha', 'email': 'aysha@faculty.muet.edu.pk'},
        {'name': 'Ms. Dua Agha', 'email': 'dua.agha@faculty.muet.edu.pk'},
        {'name': 'Ms. Fatima', 'email': 'fatima@faculty.muet.edu.pk'},
        {'name': 'Ms. Hina Ali', 'email': 'hina.ali@faculty.muet.edu.pk'},
        {'name': 'Ms. Mariam Memon', 'email': 'mariam.memon@faculty.muet.edu.pk'},
        {'name': 'Ms. Mehwish Shaikh', 'email': 'mehwish@faculty.muet.edu.pk'},
        {'name': 'Ms. Memoona Sami', 'email': 'memoona.sami@faculty.muet.edu.pk'},
        {'name': 'Ms. Shafiya Qadeer', 'email': 'shafiya.qadeer@faculty.muet.edu.pk'},
        {'name': 'Prof. Dr. Qasim Ali', 'email': 'qasim.ali@faculty.muet.edu.pk'},
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
            'description': '7th Semester - Final Year',
            'semester_number': 7,
            'total_sections': 3,
            'academic_year': '2024-2025'
        },
        {
            'name': '22SW',
            'description': '5th Semester - 3rd Year',
            'semester_number': 5,
            'total_sections': 3,
            'academic_year': '2024-2025'
        },
        {
            'name': '23SW',
            'description': '4th Semester - 2nd Year',
            'semester_number': 4,
            'total_sections': 3,
            'academic_year': '2024-2025'
        },
        {
            'name': '24SW',
            'description': '2nd Semester - 1st Year',
            'semester_number': 2,
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
    
    # 21SW - 7th Semester (Final Year)
    subjects_21sw = [
        ('SERE', 'Software Reengineering', 3, False),
        ('MC', 'Multimedia Communication', 3, False),
        ('MC2', 'Multimedia Communication (PR)', 1, True),
        ('FMSE', 'Formal Methods in Software Engineering', 3, False),
        ('WE', 'Web Engineering', 3, False),
        ('WE2', 'Web Engineering (PR)', 1, True),
    ]
    
    # 22SW - 5th Semester (3rd Year)
    subjects_22sw = [
        ('IS', 'Information Security', 3, False),
        ('ABIS', 'Agent based Intelligent Systems', 3, False),
        ('HCI', 'Human Computer Interaction', 3, False),
        ('SCD', 'Software Construction & Development', 2, False),
        ('SCD2', 'Software Construction & Development (PR)', 1, True),
        ('SP', 'Statistics& Probability', 3, False),
        ('IEC', 'Introduction to Entrepreneurship & Creativity', 3, False),
    ]
    
    # 23SW - 4th Semester (2nd Year)
    subjects_23sw = [
        ('DWH', 'Data Warehousing', 3, False),
        ('OS', 'Operating Systems', 3, False),
        ('OS2', 'Operating Systems (PR)', 1, True),
        ('CN', 'Computer Networks', 3, False),
        ('CN2', 'Computer Networks (PR)', 1, True),
        ('SDA', 'Software Design and Architecture', 2, False),
        ('SDA2', 'Software Design and Architecture (PR)', 1, True),
        ('CS', 'Communication Skills', 2, False),
    ]
    
    # 24SW - 2nd Semester (1st Year)
    subjects_24sw = [
        ('OOP', 'Object Oriented Programming', 3, False),
        ('OOP2', 'Object Oriented Programming (PR)', 1, True),
        ('ISE', 'Introduction to Software Engineering', 3, False),
        ('PP', 'Professional Practices', 3, False),
        ('LAAG', 'Linear Algebra & Analytical Geometry', 3, False),
        ('PS', 'Pakistan Studies', 3, False),
        ('IST', 'Islamic Studies', 3, False),
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
        {'name': 'Room 01', 'building': 'Main Building'},
        {'name': 'Room 02', 'building': 'Main Building'},
        {'name': 'Room 03', 'building': 'Main Building'},
        {'name': 'Room 04', 'building': 'Main Building'},
        {'name': 'A.C. Room 01', 'building': 'Academic Building'},
        {'name': 'A.C. Room 02', 'building': 'Academic Building'},
        {'name': 'A.C. Room 03', 'building': 'Academic Building'},
        {'name': 'Lab 1', 'building': 'Main Building'},
        {'name': 'Lab 2', 'building': 'Main Building'},
        {'name': 'Lab 3', 'building': 'Main Building'},
        {'name': 'Lab 4', 'building': 'Main Building'},
        {'name': 'Lab 5', 'building': 'Main Building'},
        {'name': 'Lab 6', 'building': 'Main Building'},
    ]

    for classroom_data in classrooms_data:
        classroom, created = Classroom.objects.get_or_create(
            name=classroom_data['name'],
            defaults=classroom_data
        )
        if created:
            print(f'   ✅ Created: {classroom.name}')
        else:
            print(f'   ⚪ Exists: {classroom.name}')

    print(f'Total classrooms: {Classroom.objects.count()}')

def populate_teacher_assignments():
    """Create teacher-subject-section assignments"""
    print('\n=== CREATING TEACHER ASSIGNMENTS ===')
    
    # Teacher assignments with specific sections - EXACTLY as they exist in current database
    assignments_data = [
        # 21SW assignments
        ('Mr. Salahuddin Saddar', 'SERE', '21SW', ['I', 'II', 'III']),
        ('Dr. Sania Bhatti', 'MC', '21SW', ['I']),
        ('Ms. Aleena', 'MC', '21SW', ['II', 'III']),
        ('Mr. Aqib', 'MC2', '21SW', ['I', 'II', 'III']),
        ('Ms. Mariam Memon', 'FMSE', '21SW', ['I', 'II']),
        ('Mr. Arsalan Aftab', 'FMSE', '21SW', ['III']),
        ('Ms. Dua Agha', 'WE', '21SW', ['I', 'II']),
        ('Ms. Afifah', 'WE', '21SW', ['III']),
        ('Mr. Tabish', 'WE2', '21SW', ['I', 'II', 'III']),
        
        # 22SW assignments
        ('Prof. Dr. Qasim Ali', 'IS', '22SW', ['I']),
        ('Ms. Fatima', 'IS', '22SW', ['II', 'III']),
        ('Dr. Areej Fatemah', 'ABIS', '22SW', ['I', 'II']),
        ('Ms. Amirita', 'ABIS', '22SW', ['III']),
        ('Dr. S.M. Shehram Shah', 'HCI', '22SW', ['I', 'II']),
        ('Ms. Dua Agha', 'HCI', '22SW', ['III']),
        ('Dr. Rabeea Jaffari', 'SCD', '22SW', ['I', 'II', 'III']),
        ('Ms. Hina Ali', 'SCD2', '22SW', ['I', 'II', 'III']),
        ('Mr. Ali Asghar Sangha', 'SP', '22SW', ['I', 'II', 'III']),
        ('Dr. Asma Zubadi', 'IEC', '22SW', ['I']),
        ('Dr. Saba Qureshi', 'IEC', '22SW', ['II']),
        ('Mr. Mansoor Samo', 'IEC', '22SW', ['III']),
        
        # 23SW assignments
        ('Dr. Naeem Ahmad', 'DWH', '23SW', ['I', 'II']),
        ('Ms. Amirita', 'DWH', '23SW', ['III']),
        ('Ms. Shafiya Qadeer', 'OS', '23SW', ['I', 'II']),
        ('Mr. Sajjad Ali', 'OS', '23SW', ['III']),
        ('Mr. Asadullah', 'OS2', '23SW', ['I', 'II', 'III']),
        ('Ms. Memoona Sami', 'CN', '23SW', ['I', 'II']),
        ('Mr. Umar', 'CN', '23SW', ['III']),
        ('Ms. Aysha', 'CN2', '23SW', ['I', 'II', 'III']),
        ('Ms. Mehwish Shaikh', 'SDA', '23SW', ['I', 'II', 'III']),
        ('Ms. Afifah', 'SDA2', '23SW', ['I', 'II', 'III']),
        ('Mr. Sarwar Ali', 'CS', '23SW', ['I', 'III']),
        ('Ms. Amna Baloch', 'CS', '23SW', ['II']),
        
        # 24SW assignments
        ('Dr. Mohsin Memon', 'OOP', '24SW', ['I', 'II']),
        ('Mr. Naveen Kumar', 'OOP', '24SW', ['III']),
        ('Mr. Naveen Kumar', 'OOP2', '24SW', ['I', 'II', 'III']),
        ('Dr. Anoud Shaikh', 'ISE', '24SW', ['I', 'II']),
        ('Mr. Arsalan Aftab', 'ISE', '24SW', ['III']),
        ('Mr. Junaid Ahmad', 'PP', '24SW', ['I', 'II']),
        ('Mr. Zulfiqar', 'PP', '24SW', ['III']),
        ('Mr. Mansoor Bhaagat', 'LAAG', '24SW', ['I', 'II', 'III']),
        ('Mr. Irshad Ali Burfat', 'PS', '24SW', ['I', 'II', 'III']),
        ('Mr Hafiz Imran Junejo', 'IST', '24SW', ['I', 'II', 'III']),
    ]
    
    for teacher_name, subject_code, batch_name, sections in assignments_data:
        try:
            # Resolve teacher by name safely in case of duplicates
            teacher_qs = Teacher.objects.filter(name=teacher_name)
            if not teacher_qs.exists():
                print(f'   ❌ Teacher not found: {teacher_name}')
                continue
            if teacher_qs.count() > 1:
                print(f'   ⚠️ Multiple teachers named "{teacher_name}" found. Using the earliest created.')
            teacher = teacher_qs.order_by('id').first()

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

        except Subject.DoesNotExist:
            print(f'   ❌ Subject not found: {subject_code}')
        except Batch.DoesNotExist:
            print(f'   ❌ Batch not found: {batch_name}')
    
    print(f'Total teacher assignments: {TeacherSubjectAssignment.objects.count()}')

def main():
    """Main function to populate all data"""
    print('🚀 STARTING SPRING SEMESTER DATA POPULATION')
    print('=' * 50)
    
    # Populate in order
    populate_teachers()
    populate_batches()
    populate_subjects()
    populate_classrooms()
    populate_teacher_assignments()
    
    print('\n' + '=' * 50)
    print('✅ SPRING SEMESTER DATA POPULATION COMPLETE!')
    print(f'📊 Final counts:')
    print(f'   Teachers: {Teacher.objects.count()}')
    print(f'   Batches: {Batch.objects.count()}')
    print(f'   Subjects: {Subject.objects.count()}')
    print(f'   Classrooms: {Classroom.objects.count()}')
    print(f'   Teacher Assignments: {TeacherSubjectAssignment.objects.count()}')
    print('\n🎯 Database is ready for spring semester timetable generation!')

if __name__ == '__main__':
    main()
