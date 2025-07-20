#!/usr/bin/env python3
"""
MUET Real Timetable Entries Population Script
Based on actual timetable images from MUET Software Engineering Department
"""

import os
import sys
import django
from datetime import time

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry
from django.db import transaction

def get_time_from_slot(time_str):
    """Convert time string like '8 to 8.45' to time objects"""
    if 'to' in time_str:
        start_str, end_str = time_str.split(' to ')
        start_str = start_str.strip()
        end_str = end_str.strip()
        
        # Handle formats like "8.45" or "8:45"
        if '.' in start_str:
            hour, minute = start_str.split('.')
        elif ':' in start_str:
            hour, minute = start_str.split(':')
        else:
            hour, minute = start_str, "0"
            
        start_time = time(int(hour), int(minute))
        
        if '.' in end_str:
            hour, minute = end_str.split('.')
        elif ':' in end_str:
            hour, minute = end_str.split(':')
        else:
            hour, minute = end_str, "0"
            
        end_time = time(int(hour), int(minute))
        
        return start_time, end_time
    
    return None, None

def create_timetable_entries():
    """Create actual timetable entries based on MUET images"""
    
    print("📅 Creating real MUET timetable entries...")
    
    # Clear existing timetable entries
    TimetableEntry.objects.all().delete()
    
    # Get all objects
    subjects = {s.code: s for s in Subject.objects.all()}
    teachers = {t.name: t for t in Teacher.objects.all()}
    classrooms = {c.name: c for c in Classroom.objects.all()}
    configs = {c.name: c for c in ScheduleConfig.objects.all()}
    
    # 21SW-BATCH SECTION-I (7th Semester Final YEAR) Timetable
    print("\n📚 Creating 21SW Final Year timetable...")
    
    config_21sw = configs.get("21SW-BATCH SECTION-I (7th Semester Final YEAR)")
    if config_21sw:
        # Monday Schedule for 21SW
        monday_21sw = [
            ("1st [8 to 8.45]", "WE", "Lab. No. 02", None),
            ("2nd [8.45 to 9.30]", "WE", None, None),
            ("3rd [9.30 to 10.15]", "MC", None, None),
            ("4th [10.15 to 11]", "FMSE", "SERE [Lab.03]", None),
            ("5th [11 to 11.45]", "FMSE", None, None),
            ("6th [11.45 to 12.30]", "SERE [Lab.03]", "FMSE", None),
            ("7th [12.30 to 1.15]", None, "WE (PR)", None),
            ("8th [1.15 to 2]", None, "WE (PR)", None),
            ("9th [2 to 2.45]", None, "WE (PR)", None),
        ]
        
        # Tuesday Schedule for 21SW
        tuesday_21sw = [
            ("1st [8 to 8.45]", None, "WE (PR)", "SERE", "Lab. No. 03"),
            ("2nd [8.45 to 9.30]", "WE (PR)", "MC", "SERE", "MC"),
            ("3rd [9.30 to 10.15]", "WE (PR)", "WE (PR)", "FMSE", "FMSE"),
            ("4th [10.15 to 11]", "WE", "MC", "MC", "SERE"),
            ("5th [11 to 11.45]", "MC", "THESIS", "MC", None),
            ("6th [11.45 to 12.30]", "FMSE", "THESIS", "WE[Lab.01]", "Career counseling"),
            ("7th [12.30 to 1.15]", None, "WE (PR)", "THESIS", "MC (PR)"),
            ("8th [1.15 to 2]", None, "WE (PR)", "THESIS", "MC (PR)"),
            ("9th [2 to 2.45]", None, "WE (PR)", "THESIS", "MC (PR)"),
        ]
        
        # Create entries for Monday
        for i, (period, subject_code, classroom_name, teacher_name) in enumerate(monday_21sw):
            if subject_code and subject_code in subjects:
                start_time = time(8 + i // 2, (i % 2) * 45)
                end_time = time(8 + (i + 1) // 2, ((i + 1) % 2) * 45)
                
                entry = TimetableEntry.objects.create(
                    schedule_config=config_21sw,
                    subject=subjects[subject_code],
                    teacher=teachers.get("Dr. Sania Bhatti") if not teacher_name else teachers.get(teacher_name),
                    classroom=classrooms.get(classroom_name) if classroom_name else classrooms.get("C.R. NO. 01"),
                    day="Monday",
                    period=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    class_group="21SW Section I",
                    is_practical="Lab" in subject_code or "PR" in subject_code
                )
                print(f"  ✓ Monday {period}: {subject_code}")
    
    # 23SW-BATCH SECTION-I (5th Semester 3rd YEAR) Timetable
    print("\n📚 Creating 23SW 5th Semester timetable...")

    config_23sw_5th = configs.get("23SW-BATCH SECTION-I (5th Semester 3rd YEAR)")
    if config_23sw_5th:
        # Monday Schedule for 23SW Section I (from the image)
        monday_23sw_5th = [
            ("1st [8 to 8.45]", "SW316", "C. R. NO. 01", "Dr. Kamran Ahsan"),  # Information Security
            ("2nd [8.45 to 9.30]", "SW317", "C. R. NO. 01", "Ms. Shafya Qadeer"),  # HCI
            ("3rd [9.30 to 10.15]", "SW318", "C. R. NO. 01", "Mr. Sajid Ali"),  # ABIS
            ("4th [10.15 to 11]", "SW315", "C. R. NO. 01", "Dr. Anoud Shaikh"),  # SCD
            ("5th [11 to 11.45]", "MTH317", "C. R. NO. 01", "Mr. Arsalan"),  # Statistics & Probability
            ("6th [11.45 to 12.30]", None, None, None),  # Career counseling
            ("7th [12.30 to 1.15]", "IS", "LAB. NO. 01", "Dr. Kamran Ahsan"),  # IS Lab
            ("8th [1.15 to 2]", "HCI", "LAB. NO. 02", "Ms. Shafya Qadeer"),  # HCI Lab
            ("9th [2 to 2.45]", "ABIS", "LAB. NO. 03", "Mr. Sajid Ali"),  # ABIS Lab
        ]

        # Tuesday Schedule for 23SW Section I
        tuesday_23sw_5th = [
            ("1st [8 to 8.45]", "SW317", "C. R. NO. 02", "Ms. Shafya Qadeer"),  # HCI
            ("2nd [8.45 to 9.30]", "SW316", "C. R. NO. 02", "Dr. Kamran Ahsan"),  # IS
            ("3rd [9.30 to 10.15]", "MTH317", "C. R. NO. 02", "Mr. Arsalan"),  # SP
            ("4th [10.15 to 11]", "SW318", "C. R. NO. 02", "Mr. Sajid Ali"),  # ABIS
            ("5th [11 to 11.45]", "SW315", "C. R. NO. 02", "Dr. Anoud Shaikh"),  # SCD
            ("6th [11.45 to 12.30]", None, None, None),  # Career counseling
            ("7th [12.30 to 1.15]", "SCD", "LAB. NO. 01", "Dr. Anoud Shaikh"),  # SCD Lab
            ("8th [1.15 to 2]", "SP", "LAB. NO. 02", "Mr. Arsalan"),  # SP Lab
            ("9th [2 to 2.45]", None, None, None),
        ]

        # Create entries for Monday 23SW 5th Semester
        for i, (period, subject_code, classroom_name, teacher_name) in enumerate(monday_23sw_5th):
            if subject_code and subject_code in subjects:
                start_time = time(8 + i // 2, (i % 2) * 45)
                end_time = time(8 + (i + 1) // 2, ((i + 1) % 2) * 45)

                entry = TimetableEntry.objects.create(
                    schedule_config=config_23sw_5th,
                    subject=subjects[subject_code],
                    teacher=teachers.get(teacher_name) if teacher_name else teachers.get("Dr. Kamran Ahsan"),
                    classroom=classrooms.get(classroom_name) if classroom_name else classrooms.get("C.R. NO. 01"),
                    day="Monday",
                    period=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    class_group="23SW Section I",
                    is_practical="Lab" in subject_code or subject_code in ["IS", "HCI", "ABIS", "SCD", "SP"]
                )
                print(f"  ✓ Monday {period}: {subject_code}")

        # Create entries for Tuesday 23SW 5th Semester
        for i, (period, subject_code, classroom_name, teacher_name) in enumerate(tuesday_23sw_5th):
            if subject_code and subject_code in subjects:
                start_time = time(8 + i // 2, (i % 2) * 45)
                end_time = time(8 + (i + 1) // 2, ((i + 1) % 2) * 45)

                entry = TimetableEntry.objects.create(
                    schedule_config=config_23sw_5th,
                    subject=subjects[subject_code],
                    teacher=teachers.get(teacher_name) if teacher_name else teachers.get("Dr. Kamran Ahsan"),
                    classroom=classrooms.get(classroom_name) if classroom_name else classrooms.get("C.R. NO. 02"),
                    day="Tuesday",
                    period=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    class_group="23SW Section I",
                    is_practical="Lab" in subject_code or subject_code in ["IS", "HCI", "ABIS", "SCD", "SP"]
                )
                print(f"  ✓ Tuesday {period}: {subject_code}")

    # 22SW-BATCH SECTION-I (2nd Semester 3rd YEAR) Timetable
    print("\n📚 Creating 22SW 3rd Year timetable...")

    config_22sw = configs.get("22SW-BATCH SECTION-I (2nd Semester 3rd YEAR)")
    if config_22sw:
        # Monday Schedule for 22SW (from the image)
        monday_22sw = [
            ("1st [8 to 8.45]", "SPM-322", "C. R. NO. 01", "Mr. Salahuddin Saddar"),
            ("2nd [8.45 to 9.30]", "DS&A-326", "C. R. NO. 01", "Dr. Areej Fatemah"),
            ("3rd [9.30 to 10.15]", "MAD-327", "C. R. NO. 01", "Ms. Aisha Esani"),
            ("4th [10.15 to 11]", "DS-325", "C. R. NO. 01", "Ms. Mariam Memon"),
            ("5th [11 to 11.45]", "TSW-ENG301", "C. R. NO. 01", "Mr. Umar Farooq"),
            ("6th [11.45 to 12.30]", None, None, None),  # Career counseling
            ("7th [12.30 to 1.15]", "SPM", "LAB. NO. 01", "Mr. Salahuddin Saddar"),
            ("8th [1.15 to 2]", "DS&A", "LAB. NO. 02", "Dr. Areej Fatemah"),
            ("9th [2 to 2.45]", "MAD", "LAB. NO. 03", "Ms. Aisha Esani"),
        ]

        # Create entries for Monday 22SW
        for i, (period, subject_code, classroom_name, teacher_name) in enumerate(monday_22sw):
            if subject_code and subject_code in subjects:
                start_time = time(8 + i // 2, (i % 2) * 45)
                end_time = time(8 + (i + 1) // 2, ((i + 1) % 2) * 45)

                entry = TimetableEntry.objects.create(
                    schedule_config=config_22sw,
                    subject=subjects[subject_code],
                    teacher=teachers.get(teacher_name) if teacher_name else teachers.get("Mr. Salahuddin Saddar"),
                    classroom=classrooms.get(classroom_name) if classroom_name else classrooms.get("C.R. NO. 01"),
                    day="Monday",
                    period=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    class_group="22SW Section I",
                    is_practical="Lab" in subject_code or "PR" in subject_code or subject_code in ["SPM", "DS&A", "MAD"]
                )
                print(f"  ✓ Monday {period}: {subject_code}")

    # 23SW-BATCH SECTION-I (2nd Semester 2nd YEAR) Timetable
    print("\n📚 Creating 23SW 2nd Year timetable...")
    
    config_23sw = configs.get("23SW-BATCH SECTION-I (2nd Semester 2nd YEAR)")
    if config_23sw:
        # Monday Schedule for 23SW
        monday_23sw = [
            ("1st [8 to 8.45]", "SDA", "C. R. NO. 01", None),
            ("2nd [8.45 to 9.30]", "CS", "OS", None),
            ("3rd [9.30 to 10.15]", "DWH", "DWH", None),
            ("4th [10.15 to 11]", "CN", "DWH", None),
            ("5th [11 to 11.45]", "CN", "CN", None),
            ("6th [11.45 to 12.30]", "CS", "SDA", None),
            ("7th [12.30 to 1.15]", "OS (PR)", "SDA (PR)", None),
            ("8th [1.15 to 2]", "OS (PR)", "SDA (PR)", None),
            ("9th [2 to 2.45]", "OS (PR)", "SDA (PR)", None),
        ]
        
        # Create entries for Monday 23SW
        for i, (period, subject_code, classroom_name, teacher_name) in enumerate(monday_23sw):
            if subject_code and subject_code in subjects:
                start_time = time(8 + i // 2, (i % 2) * 45)
                end_time = time(8 + (i + 1) // 2, ((i + 1) % 2) * 45)
                
                entry = TimetableEntry.objects.create(
                    schedule_config=config_23sw,
                    subject=subjects[subject_code],
                    teacher=teachers.get("Dr. Naeem Ahmed") if not teacher_name else teachers.get(teacher_name),
                    classroom=classrooms.get(classroom_name) if classroom_name else classrooms.get("C.R. NO. 01"),
                    day="Monday",
                    period=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    class_group="23SW Section I",
                    is_practical="Lab" in subject_code or "PR" in subject_code
                )
                print(f"  ✓ Monday {period}: {subject_code}")
    
    # 24SW-BATCH SECTION-I (3rd Semester 1st YEAR) Timetable
    print("\n📚 Creating 24SW 3rd Semester timetable...")
    
    config_24sw_3rd = configs.get("24SW-BATCH SECTION-I (3rd Semester 1st YEAR)")
    if config_24sw_3rd:
        # Monday Schedule for 24SW 3rd Semester
        monday_24sw_3rd = [
            ("1st [8 to 8.45]", "PS", None, None),
            ("2nd [8.45 to 9.30]", "OOP", None, None),
            ("3rd [9.30 to 10.15]", "PP", None, None),
            ("4th [10.15 to 11]", "PP", None, None),
            ("5th [11 to 11.45]", "ISE", None, None),
            ("6th [11.45 to 12.30]", "PS", None, None),
            ("7th [12.30 to 1.15]", "LAAG", None, None),
            ("8th [1.15 to 2]", "LAAG", None, None),
            ("9th [2 to 2.45]", None, None, None),
        ]
        
        # Create entries for Monday 24SW 3rd Semester
        for i, (period, subject_code, classroom_name, teacher_name) in enumerate(monday_24sw_3rd):
            if subject_code and subject_code in subjects:
                start_time = time(8 + i // 2, (i % 2) * 45)
                end_time = time(8 + (i + 1) // 2, ((i + 1) % 2) * 45)
                
                entry = TimetableEntry.objects.create(
                    schedule_config=config_24sw_3rd,
                    subject=subjects[subject_code],
                    teacher=teachers.get("Dr. Naeem Ahmed") if not teacher_name else teachers.get(teacher_name),
                    classroom=classrooms.get(classroom_name) if classroom_name else classrooms.get("C.R. NO. 01"),
                    day="Monday",
                    period=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    class_group="24SW Section I",
                    is_practical="Lab" in subject_code or "PR" in subject_code
                )
                print(f"  ✓ Monday {period}: {subject_code}")
    
    # 24SW-BATCH SECTION-I (1st Semester 1st YEAR) Timetable
    print("\n📚 Creating 24SW 1st Semester timetable...")
    
    config_24sw_1st = configs.get("24SW-BATCH SECTION-I (1st Semester 1st YEAR)")
    if config_24sw_1st:
        # This batch has only 5 subjects as shown in the image
        monday_24sw_1st = [
            ("1st [8 to 8.45]", "PF", None, "Dr. Naeem Ahmed"),
            ("2nd [8.45 to 9.30]", "ICT", None, "Dr. Anoud Shaikh"),
            ("3rd [9.30 to 10.15]", "AC", None, "Mr. Saleem Memon"),
            ("4th [10.15 to 11]", "AP", None, "Mr. Jabbar Memon"),
            ("5th [11 to 11.45]", "FE", None, "Ms. Uma Rubab"),
        ]
        
        # Create entries for Monday 24SW 1st Semester
        for i, (period, subject_code, classroom_name, teacher_name) in enumerate(monday_24sw_1st):
            if subject_code and subject_code in subjects:
                start_time = time(8 + i // 2, (i % 2) * 45)
                end_time = time(8 + (i + 1) // 2, ((i + 1) % 2) * 45)
                
                entry = TimetableEntry.objects.create(
                    schedule_config=config_24sw_1st,
                    subject=subjects[subject_code],
                    teacher=teachers.get(teacher_name) if teacher_name else teachers.get("Dr. Qasim Ali"),
                    classroom=classrooms.get(classroom_name) if classroom_name else classrooms.get("C.R. NO. 01"),
                    day="Monday",
                    period=i + 1,
                    start_time=start_time,
                    end_time=end_time,
                    class_group="24SW Section I",
                    is_practical="Lab" in subject_code or "PR" in subject_code
                )
                print(f"  ✓ Monday {period}: {subject_code}")
    
    print(f"\n✅ Created timetable entries for all batches")

if __name__ == "__main__":
    create_timetable_entries()
    print("\n🎉 MUET Real Timetable Entries populated successfully!")
    print("All batches now have their Monday schedules populated based on real data!")
