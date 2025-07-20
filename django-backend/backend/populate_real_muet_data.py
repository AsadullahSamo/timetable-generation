#!/usr/bin/env python3
"""
Real MUET Data Population Script
Mehran University of Engineering and Technology, Jamshoro
Department of Software Engineering
"""

import os
import sys
import django
from datetime import time, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry
from django.db import transaction

def create_muet_data():
    """Create real MUET Software Engineering Department data"""
    
    print("🏛️  Populating MUET Software Engineering Department Data...")
    
    with transaction.atomic():
        # Clear existing data
        TimetableEntry.objects.all().delete()
        Subject.objects.all().delete()
        Teacher.objects.all().delete()
        Classroom.objects.all().delete()
        ScheduleConfig.objects.all().delete()
        
        print("✅ Cleared existing data")
        
        # 1. CREATE SUBJECTS
        print("\n📚 Creating subjects...")
        
        subjects_data = [
            # 7th Semester (Final Year) - 21SW
            {"code": "SW416", "name": "Multimedia Communication", "credits": 3, "is_practical": False},
            {"code": "SW415", "name": "Software Reengineering", "credits": 3, "is_practical": False},
            {"code": "SW418", "name": "Formal Methods in Software Engineering", "credits": 3, "is_practical": False},
            {"code": "SW417", "name": "Web Engineering", "credits": 3, "is_practical": False},
            {"code": "SW438", "name": "Thesis/Project", "credits": 6, "is_practical": True},
            
            # 5th Semester (3rd Year) - 23SW
            {"code": "SW316", "name": "Information Security (IS)", "credits": 3, "is_practical": False},
            {"code": "SW317", "name": "Human Computer Interaction (HCI)", "credits": 3, "is_practical": False},
            {"code": "SW318", "name": "Agent based Intelligent Systems (ABIS)", "credits": 3, "is_practical": False},
            {"code": "SW315", "name": "Software Construction & Development (SCD)", "credits": 2, "is_practical": False},
            {"code": "MTH317", "name": "Statistics & Probability (SP)", "credits": 3, "is_practical": False},

            # 2nd Semester (3rd Year) - 22SW
            {"code": "SPM-322", "name": "Software Project Management (SPM)", "credits": 3, "is_practical": False},
            {"code": "DS&A-326", "name": "Data Science & Analytics (DS&A)", "credits": 3, "is_practical": False},
            {"code": "MAD-327", "name": "Mobile Application Development (MAD)", "credits": 3, "is_practical": False},
            {"code": "DS-325", "name": "Discrete Structures (DS)", "credits": 3, "is_practical": False},
            {"code": "TSW-ENG301", "name": "Technical & Scientific Writing (TSW)", "credits": 2, "is_practical": False},

            # 2nd Semester (2nd Year) - 23SW
            {"code": "SW228", "name": "Data Warehousing (DWH)", "credits": 3, "is_practical": False},
            {"code": "SW225", "name": "Operating Systems (OS)", "credits": 3, "is_practical": False},
            {"code": "SW226", "name": "Computer Networks (CN)", "credits": 3, "is_practical": False},
            {"code": "SW227", "name": "Software Design and Architecture", "credits": 2, "is_practical": False},
            {"code": "ENG301", "name": "Communication Skills", "credits": 2, "is_practical": False},
            
            # 1st Semester (2nd Year) - 24SW
            {"code": "SW212", "name": "Data Structure & Algorithms (DSA)", "credits": 3, "is_practical": False},
            {"code": "SW217", "name": "Operations Research (OR)", "credits": 3, "is_practical": False},
            {"code": "SW216", "name": "Software Requirement Engineering (SRE)", "credits": 3, "is_practical": False},
            {"code": "SW211", "name": "Software Economics & Management (SEM)", "credits": 3, "is_practical": False},
            {"code": "SW215", "name": "Database Systems (DBS)", "credits": 3, "is_practical": False},

            # 3rd Semester (1st Year) - 24SW
            {"code": "SW121", "name": "Object Oriented Programming (OOP)", "credits": 3, "is_practical": False},
            {"code": "SW124", "name": "Introduction to Software Engineering (ISE)", "credits": 3, "is_practical": False},
            {"code": "SW123", "name": "Professional Practices (PP)", "credits": 3, "is_practical": False},
            {"code": "MTH112", "name": "Linear Algebra & Analytical Geometry (LAAG)", "credits": 3, "is_practical": False},
            {"code": "PS106", "name": "Pakistan Studies (PS)", "credits": 2, "is_practical": False},
            {"code": "SS104", "name": "Islamic Studies (IS)", "credits": 2, "is_practical": False},
            {"code": "ETHICS", "name": "Ethics", "credits": 2, "is_practical": False},
            
            # 1st Semester (1st Year) - 24SW
            {"code": "PF", "name": "Programming Fundamentals", "credits": 3, "is_practical": False},
            {"code": "ICT", "name": "Introduction to Information and Communication Technology", "credits": 2, "is_practical": False},
            {"code": "AC", "name": "Applied Calculus", "credits": 3, "is_practical": False},
            {"code": "AP", "name": "Applied Physics", "credits": 3, "is_practical": False},
            {"code": "FE", "name": "Functional English", "credits": 2, "is_practical": False},
            
            # Lab Subjects
            {"code": "MC", "name": "Multimedia Communication Lab", "credits": 1, "is_practical": True},
            {"code": "WE", "name": "Web Engineering Lab", "credits": 1, "is_practical": True},
            {"code": "SERE", "name": "Software Reengineering Lab", "credits": 1, "is_practical": True},
            {"code": "FMSE", "name": "Formal Methods in Software Engineering Lab", "credits": 1, "is_practical": True},
            {"code": "SDA", "name": "Software Design and Architecture Lab", "credits": 1, "is_practical": True},
            {"code": "OS", "name": "Operating Systems Lab", "credits": 1, "is_practical": True},
            {"code": "CN", "name": "Computer Networks Lab", "credits": 1, "is_practical": True},
            {"code": "DWH", "name": "Data Warehousing Lab", "credits": 1, "is_practical": True},
            {"code": "OOP", "name": "Object Oriented Programming Lab", "credits": 1, "is_practical": True},
            {"code": "ISE", "name": "Introduction to Software Engineering Lab", "credits": 1, "is_practical": True},
            {"code": "PP", "name": "Professional Practices Lab", "credits": 1, "is_practical": True},
            {"code": "SCP", "name": "System and Computer Programming Lab", "credits": 1, "is_practical": True},

            # 23SW Lab Subjects (5th Semester)
            {"code": "IS", "name": "Information Security Lab", "credits": 1, "is_practical": True},
            {"code": "HCI", "name": "Human Computer Interaction Lab", "credits": 1, "is_practical": True},
            {"code": "ABIS", "name": "Agent based Intelligent Systems Lab", "credits": 1, "is_practical": True},
            {"code": "SCD", "name": "Software Construction & Development Lab", "credits": 1, "is_practical": True},
            {"code": "SP", "name": "Statistics & Probability Lab", "credits": 1, "is_practical": True},

            # 22SW Lab Subjects
            {"code": "SPM", "name": "Software Project Management Lab", "credits": 1, "is_practical": True},
            {"code": "DS&A", "name": "Data Science & Analytics Lab", "credits": 1, "is_practical": True},
            {"code": "MAD", "name": "Mobile Application Development Lab", "credits": 1, "is_practical": True},
            {"code": "DS", "name": "Discrete Structures Lab", "credits": 1, "is_practical": True},
            {"code": "TSW", "name": "Technical & Scientific Writing Lab", "credits": 1, "is_practical": True},
        ]
        
        subjects = {}
        for subject_data in subjects_data:
            subject = Subject.objects.create(**subject_data)
            subjects[subject_data["code"]] = subject
            print(f"  ✓ {subject.name} ({subject.code})")
        
        # 2. CREATE TEACHERS
        print("\n👨‍🏫 Creating teachers...")
        
        teachers_data = [
            {"name": "Dr. Sania Bhatti", "email": "sania.bhatti@faculty.muet.edu.pk"},
            {"name": "Ms. Aleena", "email": "aleena@faculty.muet.edu.pk"},
            {"name": "Mr. Aqib", "email": "aqib@faculty.muet.edu.pk"},
            {"name": "Mr. Salahuddin Saddar", "email": "salahuddin@faculty.muet.edu.pk"},
            {"name": "Ms. Sana Faiz", "email": "sana.faiz@faculty.muet.edu.pk"},
            {"name": "Ms. Mariam Memon", "email": "mariam.memon@faculty.muet.edu.pk"},
            {"name": "Mr. Arsalan Aftab", "email": "arsalan@faculty.muet.edu.pk"},
            {"name": "Ms. Dua", "email": "dua@faculty.muet.edu.pk"},
            {"name": "Ms. Afifah", "email": "afifah@faculty.muet.edu.pk"},
            {"name": "Mr. Tabish", "email": "tabish@faculty.muet.edu.pk"},
            {"name": "Dr. Naeem Ahmed", "email": "naeem.mahoto@faculty.muet.edu.pk"},
            {"name": "Ms. Amrita", "email": "amrita@faculty.muet.edu.pk"},
            {"name": "Mr. Asadullah", "email": "asadullah@faculty.muet.edu.pk"},
            {"name": "Ms. Memoona Sami", "email": "memoona@faculty.muet.edu.pk"},
            {"name": "Mr. Umar", "email": "umar@faculty.muet.edu.pk"},
            {"name": "Ms. Aysha", "email": "aysha@faculty.muet.edu.pk"},
            {"name": "Ms. Mehwish Shaikh", "email": "mehwish@faculty.muet.edu.pk"},
            {"name": "Ms. Afifah", "email": "afifah2@faculty.muet.edu.pk"},
            {"name": "Mr. Sarwar Ali", "email": "sarwar@faculty.muet.edu.pk"},
            {"name": "Ms. Amna Baloch", "email": "amna@faculty.muet.edu.pk"},
            {"name": "Dr. Shafya Qadeer", "email": "shafya@faculty.muet.edu.pk"},
            {"name": "Mr. Sajid Ali", "email": "sajid@faculty.muet.edu.pk"},
            {"name": "Dr. Anoud Shaikh", "email": "anoud@faculty.muet.edu.pk"},
            {"name": "Mr. Arsalan", "email": "arsalan2@faculty.muet.edu.pk"},
            {"name": "Mr. Saleem Memon", "email": "saleem@faculty.muet.edu.pk"},
            {"name": "Mr. Jabbar Memon", "email": "jabbar@faculty.muet.edu.pk"},
            {"name": "Ms. Uma Rubab", "email": "uma@faculty.muet.edu.pk"},
            {"name": "Dr. Qasim Ali", "email": "qasim.arain@faculty.muet.edu.pk"},
            {"name": "Dr. Mohsin Memon", "email": "mohsin@faculty.muet.edu.pk"},
            {"name": "Mr. Naveen Kumar", "email": "naveen@faculty.muet.edu.pk"},
            {"name": "Mr. Junaid Ahmed", "email": "junaid@faculty.muet.edu.pk"},
            {"name": "Mr. Zulfiqar", "email": "zulfiqar@faculty.muet.edu.pk"},
            {"name": "Mr. Mansoor Ali Shaagat", "email": "mansoor@faculty.muet.edu.pk"},
            {"name": "Mr. Irshad Ali Burfat", "email": "irshad@faculty.muet.edu.pk"},
            {"name": "Mr. Hafiz Imran Junejo", "email": "hafiz@faculty.muet.edu.pk"},

            # Additional teachers from 22SW timetable
            {"name": "Mr. Salahuddin Saddar", "email": "salahuddin.saddar@faculty.muet.edu.pk"},
            {"name": "Dr. Areej Fatemah", "email": "areej@faculty.muet.edu.pk"},
            {"name": "Ms. Aisha Esani", "email": "aisha@faculty.muet.edu.pk"},
            {"name": "Ms. Mariam Memon", "email": "mariam2@faculty.muet.edu.pk"},
            {"name": "Mr. Umar Farooq", "email": "umar.farooq@faculty.muet.edu.pk"},
            {"name": "Ms. Shafya Qadeer", "email": "shafya2@faculty.muet.edu.pk"},
            {"name": "Ms. Shazma Memon", "email": "shazma@faculty.muet.edu.pk"},
            {"name": "Mr. Sarwar Ali", "email": "sarwar2@faculty.muet.edu.pk"},
            {"name": "Dr. S.M. Shehram Shah", "email": "shehram.shah@faculty.muet.edu.pk"},

            # Additional teachers from 23SW 5th Semester timetable
            {"name": "Dr. Kamran Ahsan", "email": "kamran.ahsan@faculty.muet.edu.pk"},
            {"name": "Ms. Shafya Qadeer", "email": "shafya.qadeer@faculty.muet.edu.pk"},
            {"name": "Mr. Sajid Ali", "email": "sajid.ali@faculty.muet.edu.pk"},
            {"name": "Dr. Anoud Shaikh", "email": "anoud.shaikh@faculty.muet.edu.pk"},
            {"name": "Mr. Arsalan", "email": "arsalan.aftab@faculty.muet.edu.pk"},
            {"name": "Mr. Saleem Memon", "email": "saleem.memon@faculty.muet.edu.pk"},
            {"name": "Dr. Naeem Ahmed", "email": "naeem.ahmed@faculty.muet.edu.pk"},
            {"name": "Ms. Mariam Memon", "email": "mariam.memon2@faculty.muet.edu.pk"},
            {"name": "Dr. Areej Fatemah", "email": "areej.fatemah@faculty.muet.edu.pk"},
            {"name": "Ms. Aisha Esani", "email": "aisha.esani@faculty.muet.edu.pk"},

            # Additional teachers from 24SW 1st Semester 2nd Year timetable
            {"name": "Dr. Mohsin Memon", "email": "mohsin.memon@faculty.muet.edu.pk"},
            {"name": "Mr. Mansoor", "email": "mansoor@faculty.muet.edu.pk"},
            {"name": "Mr. Naveen Kumar", "email": "naveen.kumar@faculty.muet.edu.pk"},
            {"name": "Ms. Amrita Dewani", "email": "amrita.dewani@faculty.muet.edu.pk"},
            {"name": "Ms. Memoona Sami", "email": "memoona.sami@faculty.muet.edu.pk"},
            {"name": "Mr. Junaid Ahmed", "email": "junaid.ahmed@faculty.muet.edu.pk"},
            {"name": "Ms. Aleena (Th)", "email": "aleena.th@faculty.muet.edu.pk"},
            {"name": "Ms. Hina Ali", "email": "hina.ali@faculty.muet.edu.pk"},
        ]
        
        teachers = {}
        seen_emails = set()
        for teacher_data in teachers_data:
            # Skip if email already exists
            if teacher_data["email"] in seen_emails:
                print(f"  ⚠️  Skipping duplicate email: {teacher_data['email']} for {teacher_data['name']}")
                continue

            try:
                teacher = Teacher.objects.create(**teacher_data)
                teachers[teacher_data["name"]] = teacher
                seen_emails.add(teacher_data["email"])
                print(f"  ✓ {teacher.name}")
            except Exception as e:
                print(f"  ❌ Failed to create teacher {teacher_data['name']}: {e}")
                continue
        
        # 3. CREATE CLASSROOMS
        print("\n🏫 Creating classrooms...")
        
        classrooms_data = [
            # Regular Classrooms
            {"name": "C.R. NO. 01", "capacity": 60, "building": "Software Department"},
            {"name": "C.R. NO. 02", "capacity": 60, "building": "Software Department"},
            {"name": "C.R. NO. 03", "capacity": 60, "building": "Software Department"},
            
            # Lab Rooms
            {"name": "LAB. NO. 01", "capacity": 30, "building": "Software Department"},
            {"name": "LAB. NO. 02", "capacity": 30, "building": "Software Department"},
            {"name": "LAB. NO. 03", "capacity": 30, "building": "Software Department"},
            {"name": "LAB. NO. 05", "capacity": 30, "building": "Software Department"},
            {"name": "Lab. No. 6", "capacity": 30, "building": "Software Department"},
            
            # Additional Labs from Lab Timetable
            {"name": "LAB.01", "capacity": 25, "building": "Academia Building-II"},
            {"name": "LAB.02", "capacity": 25, "building": "Academia Building-II"},
            {"name": "LAB.03", "capacity": 25, "building": "Academia Building-II"},
            {"name": "LAB.04", "capacity": 25, "building": "Academia Building-II"},
            {"name": "LAB.05", "capacity": 25, "building": "Academia Building-II"},
            {"name": "LAB.06", "capacity": 25, "building": "Academia Building-II"},
        ]
        
        classrooms = {}
        for classroom_data in classrooms_data:
            classroom = Classroom.objects.create(**classroom_data)
            classrooms[classroom_data["name"]] = classroom
            print(f"  ✓ {classroom.name} (Capacity: {classroom.capacity})")
        
        print(f"\n✅ Created {len(subjects)} subjects")
        print(f"✅ Created {len(teachers)} teachers")
        print(f"✅ Created {len(classrooms)} classrooms")

        return subjects, teachers, classrooms

def create_schedule_configs():
    """Create schedule configurations for different batches"""

    print("\n⚙️  Creating schedule configurations...")

    # Get all subjects, teachers, and classrooms
    subjects = {s.code: s for s in Subject.objects.all()}
    teachers = {t.name: t for t in Teacher.objects.all()}
    classrooms = {c.name: c for c in Classroom.objects.all()}

    # Create schedule configurations for each batch
    configs = [
        {
            "name": "21SW-BATCH SECTION-I (7th Semester Final YEAR)",
            "batch": "21SW",
            "section": "I",
            "semester": 7,
            "year": "Final Year",
            "total_students": 45,
            "subjects": ["SW416", "SW415", "SW418", "SW417", "SW438", "MC", "WE", "SERE", "FMSE"],
            "time_slots": [
                ("08:00", "08:45"),
                ("08:45", "09:30"),
                ("09:30", "10:15"),
                ("10:15", "11:00"),
                ("11:00", "11:45"),
                ("11:45", "12:30"),
                ("12:30", "01:15"),
                ("01:15", "02:00"),
                ("02:00", "02:45"),
            ]
        },
        {
            "name": "23SW-BATCH SECTION-I (5th Semester 3rd YEAR)",
            "batch": "23SW",
            "section": "I",
            "semester": 5,
            "year": "3rd Year",
            "total_students": 42,
            "subjects": ["SW316", "SW317", "SW318", "SW315", "MTH317", "IS", "HCI", "ABIS", "SCD", "SP"],
            "time_slots": [
                ("08:00", "08:45"),
                ("08:45", "09:30"),
                ("09:30", "10:15"),
                ("10:15", "11:00"),
                ("11:00", "11:45"),
                ("11:45", "12:30"),
                ("12:30", "01:15"),
                ("01:15", "02:00"),
                ("02:00", "02:45"),
            ]
        },
        {
            "name": "24SW-BATCH SECTION-I (1st Semester 2nd YEAR)",
            "batch": "24SW",
            "section": "I",
            "semester": 1,
            "year": "2nd Year",
            "total_students": 40,
            "subjects": ["SW212", "SW217", "SW216", "SW211", "SW215"],
            "time_slots": [
                ("08:00", "09:00"),
                ("09:00", "10:00"),
                ("10:00", "11:00"),
                ("11:00", "12:00"),
                ("12:00", "01:00"),
                ("01:00", "02:00"),
                ("02:00", "03:00"),
            ]
        },
        {
            "name": "24SW-BATCH SECTION-II (1st Semester 2nd YEAR)",
            "batch": "24SW",
            "section": "II",
            "semester": 1,
            "year": "2nd Year",
            "total_students": 38,
            "subjects": ["SW212", "SW217", "SW216", "SW211", "SW215"],
            "time_slots": [
                ("08:00", "09:00"),
                ("09:00", "10:00"),
                ("10:00", "11:00"),
                ("11:00", "12:00"),
                ("12:00", "01:00"),
                ("01:00", "02:00"),
                ("02:00", "03:00"),
            ]
        },
        {
            "name": "24SW-BATCH SECTION-III (1st Semester 2nd YEAR)",
            "batch": "24SW",
            "section": "III",
            "semester": 1,
            "year": "2nd Year",
            "total_students": 35,
            "subjects": ["SW212", "SW217", "SW216", "SW211", "SW215"],
            "time_slots": [
                ("08:00", "09:00"),
                ("09:00", "10:00"),
                ("10:00", "11:00"),
                ("11:00", "12:00"),
                ("12:00", "01:00"),
                ("01:00", "02:00"),
                ("02:00", "03:00"),
            ]
        },
        {
            "name": "22SW-BATCH SECTION-I (2nd Semester 3rd YEAR)",
            "batch": "22SW",
            "section": "I",
            "semester": 2,
            "year": "3rd Year",
            "total_students": 40,
            "subjects": ["SPM-322", "DS&A-326", "MAD-327", "DS-325", "TSW-ENG301"],
            "time_slots": [
                ("08:00", "08:45"),
                ("08:45", "09:30"),
                ("09:30", "10:15"),
                ("10:15", "11:00"),
                ("11:00", "11:45"),
                ("11:45", "12:30"),
                ("12:30", "01:15"),
                ("01:15", "02:00"),
                ("02:00", "02:45"),
            ]
        },
        {
            "name": "23SW-BATCH SECTION-I (2nd Semester 2nd YEAR)",
            "batch": "23SW",
            "section": "I",
            "semester": 2,
            "year": "2nd Year",
            "total_students": 50,
            "subjects": ["SW228", "SW225", "SW226", "SW227", "ENG301", "SDA", "OS", "CN", "DWH"],
            "time_slots": [
                ("08:00", "08:45"),
                ("08:45", "09:30"),
                ("09:30", "10:15"),
                ("10:15", "11:00"),
                ("11:00", "11:45"),
                ("11:45", "12:30"),
                ("12:30", "01:15"),
                ("01:15", "02:00"),
                ("02:00", "02:45"),
            ]
        },
        {
            "name": "24SW-BATCH SECTION-I (3rd Semester 1st YEAR)",
            "batch": "24SW",
            "section": "I",
            "semester": 3,
            "year": "1st Year",
            "total_students": 55,
            "subjects": ["SW121", "SW124", "SW123", "MTH112", "PS106", "SS104", "ETHICS", "OOP", "ISE", "PP"],
            "time_slots": [
                ("08:00", "08:45"),
                ("08:45", "09:30"),
                ("09:30", "10:15"),
                ("10:15", "11:00"),
                ("11:00", "11:45"),
                ("11:45", "12:30"),
                ("12:30", "01:15"),
                ("01:15", "02:00"),
                ("02:00", "02:45"),
            ]
        },
        {
            "name": "24SW-BATCH SECTION-I (1st Semester 1st YEAR)",
            "batch": "24SW",
            "section": "I",
            "semester": 1,
            "year": "1st Year",
            "total_students": 60,
            "subjects": ["PF", "ICT", "AC", "AP", "FE"],
            "time_slots": [
                ("08:00", "08:45"),
                ("08:45", "09:30"),
                ("09:30", "10:15"),
                ("10:15", "11:00"),
                ("11:00", "11:45"),
                ("11:45", "12:30"),
                ("12:30", "01:15"),
                ("01:15", "02:00"),
                ("02:00", "02:45"),
            ]
        }
    ]

    created_configs = []
    for config_data in configs:
        # Create the schedule config
        config = ScheduleConfig.objects.create(
            name=config_data["name"],
            days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            periods=[f"{slot[0]}-{slot[1]}" for slot in config_data["time_slots"]],
            start_time=time(8, 0),  # 8:00 AM
            lesson_duration=45,  # 45 minutes
            semester=f"{config_data['semester']} Semester",
            academic_year="2024-2025",
            class_groups=[{
                "name": f"{config_data['batch']} Section {config_data['section']}",
                "students": config_data["total_students"],
                "subjects": config_data["subjects"]
            }],
            constraints={
                "max_periods_per_day": 9,
                "break_after_periods": [2, 4, 6],
                "lunch_break": "12:30-13:15"
            }
        )


        created_configs.append(config)
        print(f"  ✓ {config.name}")

    print(f"\n✅ Created {len(created_configs)} schedule configurations")
    return created_configs

def create_24sw_timetable_data():
    """Create specific timetable entries for 24SW batch based on actual MUET timetable"""
    from timetable.models import TimetableEntry

    print("\n📅 Creating 24SW timetable entries...")

    # Get required objects
    subjects = {s.code: s for s in Subject.objects.all()}
    teachers = {t.name: t for t in Teacher.objects.all()}
    classrooms = {c.name: c for c in Classroom.objects.all()}

    # 24SW Section-I Timetable Data
    section_i_schedule = [
        # Monday
        {"day": "Monday", "period": "1st [8 to 9]", "subject": "SW215", "teacher": "DBS (PR)", "room": "C.R. NO. 01"},
        {"day": "Monday", "period": "2nd [9 to 10]", "subject": "SW215", "teacher": "DBS (PR)", "room": "C.R. NO. 01"},
        {"day": "Monday", "period": "3rd [10 to 11]", "subject": "SW215", "teacher": "DBS (PR)", "room": "C.R. NO. 01"},
        {"day": "Monday", "period": "4th [11 to 12]", "subject": "SW211", "teacher": "SEM", "room": "C.R. NO. 01"},

        # Tuesday
        {"day": "Tuesday", "period": "1st [8 to 9]", "subject": "SW217", "teacher": "OR", "room": "C.R. NO. 01"},
        {"day": "Tuesday", "period": "2nd [9 to 10]", "subject": "SW215", "teacher": "DBS", "room": "C.R. NO. 01"},
        {"day": "Tuesday", "period": "3rd [10 to 11]", "subject": "SW212", "teacher": "DSA", "room": "C.R. NO. 01"},
        {"day": "Tuesday", "period": "4th [11 to 12]", "subject": "SW216", "teacher": "SRE", "room": "C.R. NO. 01"},
        {"day": "Tuesday", "period": "5th [12 to 1]", "subject": "SW212", "teacher": "DSA (PR)", "room": "LAB. NO. 01"},
        {"day": "Tuesday", "period": "6th [1 to 2]", "subject": "SW212", "teacher": "DSA (PR)", "room": "LAB. NO. 01"},
        {"day": "Tuesday", "period": "7th [2 to 3]", "subject": "SW212", "teacher": "DSA (PR)", "room": "LAB. NO. 01"},

        # Wednesday
        {"day": "Wednesday", "period": "1st [8 to 9]", "subject": "SW217", "teacher": "OR*", "room": "C.R. NO. 01"},
        {"day": "Wednesday", "period": "2nd [9 to 10]", "subject": "SW212", "teacher": "DSA", "room": "C.R. NO. 01"},
        {"day": "Wednesday", "period": "3rd [10 to 11]", "subject": "SW216", "teacher": "SRE", "room": "C.R. NO. 01"},
        {"day": "Wednesday", "period": "4th [11 to 12]", "subject": "SW215", "teacher": "DBS", "room": "C.R. NO. 01"},
        {"day": "Wednesday", "period": "5th [12 to 1]", "subject": "SW211", "teacher": "SEM", "room": "C.R. NO. 01"},
        {"day": "Wednesday", "period": "6th [1 to 2]", "subject": "SW215", "teacher": "DBS*", "room": "C.R. NO. 01"},
        {"day": "Wednesday", "period": "7th [2 to 3]", "subject": "PRACTICAL", "teacher": "Practical *", "room": "LAB. NO. 01"},

        # Thursday
        {"day": "Thursday", "period": "1st [8 to 9]", "subject": "SW211", "teacher": "SEM*", "room": "C.R. NO. 01"},
        {"day": "Thursday", "period": "2nd [9 to 10]", "subject": "SW216", "teacher": "SRE", "room": "C.R. NO. 01"},
        {"day": "Thursday", "period": "3rd [10 to 11]", "subject": "SW212", "teacher": "DSA", "room": "C.R. NO. 01"},
        {"day": "Thursday", "period": "4th [11 to 12]", "subject": "SW217", "teacher": "OR", "room": "C.R. NO. 01"},
        {"day": "Thursday", "period": "5th [12 to 1]", "subject": "PRACTICAL", "teacher": "Practical *", "room": "LAB. NO. 01"},
        {"day": "Thursday", "period": "6th [1 to 2]", "subject": "PRACTICAL", "teacher": "Practical *", "room": "LAB. NO. 01"},
        {"day": "Thursday", "period": "7th [2 to 3]", "subject": "PRACTICAL", "teacher": "Practical *", "room": "LAB. NO. 01"},

        # Friday
        {"day": "Friday", "period": "1st [8 to 9]", "subject": "SW215", "teacher": "DBS", "room": "C.R. NO. 01"},
        {"day": "Friday", "period": "2nd [9 to 10]", "subject": "SW211", "teacher": "SEM", "room": "C.R. NO. 01"},
        {"day": "Friday", "period": "3rd [10 to 11]", "subject": "SW212", "teacher": "DSA", "room": "C.R. NO. 01"},
        {"day": "Friday", "period": "4th [11 to 12]", "subject": "SW216", "teacher": "SRE*", "room": "C.R. NO. 01"},
        {"day": "Friday", "period": "5th [12 to 1]", "subject": "COUNSELING", "teacher": "Carrier counseling", "room": "C.R. NO. 01"},
    ]

    # Create timetable entries for Section-I
    created_entries = []
    for entry_data in section_i_schedule:
        # Map subject codes to actual subjects
        subject_code = entry_data["subject"]
        if subject_code in subjects:
            subject = subjects[subject_code]
        else:
            # Handle special cases like PRACTICAL, COUNSELING
            subject = None

        # Find appropriate teacher (simplified mapping)
        teacher_name = None
        if "Dr. Mohsin Memon" in teachers:
            teacher_name = "Dr. Mohsin Memon"
        elif "Mr. Mansoor" in teachers:
            teacher_name = "Mr. Mansoor"
        else:
            # Use first available teacher
            teacher_name = list(teachers.keys())[0] if teachers else None

        teacher = teachers.get(teacher_name) if teacher_name else None

        # Find classroom
        room_name = entry_data["room"]
        classroom = classrooms.get(room_name) or classrooms.get("C.R. NO. 01")

        if subject and teacher and classroom:
            # Parse period to get period number
            period_num = 1  # Default
            if "1st" in entry_data["period"]:
                period_num = 1
            elif "2nd" in entry_data["period"]:
                period_num = 2
            elif "3rd" in entry_data["period"]:
                period_num = 3
            elif "4th" in entry_data["period"]:
                period_num = 4
            elif "5th" in entry_data["period"]:
                period_num = 5
            elif "6th" in entry_data["period"]:
                period_num = 6
            elif "7th" in entry_data["period"]:
                period_num = 7

            # Calculate start and end times based on period
            start_hour = 8 + (period_num - 1)  # Starting from 8:00 AM
            start_time = time(start_hour, 0)
            end_time = time(start_hour + 1, 0)

            entry = TimetableEntry.objects.create(
                subject=subject,
                teacher=teacher,
                classroom=classroom,
                day=entry_data["day"],
                period=period_num,
                class_group="24SW Section I",
                start_time=start_time,
                end_time=end_time,
                is_practical="Practical" in entry_data.get("subject", "")
            )
            created_entries.append(entry)

    print(f"  ✓ Created {len(created_entries)} timetable entries for 24SW Section-I")
    return created_entries

if __name__ == "__main__":
    create_muet_data()
    create_schedule_configs()
    create_24sw_timetable_data()
    print("\n🎉 MUET Software Engineering Department data populated successfully!")
    print("Ready for timetable generation!")
