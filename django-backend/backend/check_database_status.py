#!/usr/bin/env python
"""
Check database status to verify it's clean and ready for real data.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import (
    Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry, Config, ClassGroup
)


def check_database_status():
    """Check if database is clean and ready for real data."""
    print("=== DATABASE STATUS CHECK ===")
    
    # Count all records
    counts = {
        'TimetableEntry': TimetableEntry.objects.count(),
        'ScheduleConfig': ScheduleConfig.objects.count(),
        'Subject': Subject.objects.count(),
        'Teacher': Teacher.objects.count(),
        'Classroom': Classroom.objects.count(),
        'Config': Config.objects.count(),
        'ClassGroup': ClassGroup.objects.count(),
    }
    
    # Display counts
    for model_name, count in counts.items():
        print(f"{model_name} count: {count}")
    
    print()
    
    # Check for existing data and show samples
    warnings = []
    
    if TimetableEntry.objects.exists():
        warnings.append("TimetableEntry data exists!")
        print("⚠️  WARNING: TimetableEntry data exists!")
        for entry in TimetableEntry.objects.all()[:3]:
            print(f"  - {entry}")
    else:
        print("✅ TimetableEntry: CLEAN")
    
    if ScheduleConfig.objects.exists():
        warnings.append("ScheduleConfig data exists!")
        print("⚠️  WARNING: ScheduleConfig data exists!")
        for config in ScheduleConfig.objects.all()[:3]:
            print(f"  - {config}")
    else:
        print("✅ ScheduleConfig: CLEAN")
    
    if Subject.objects.exists():
        warnings.append("Subject data exists!")
        print("⚠️  WARNING: Subject data exists!")
        for subject in Subject.objects.all()[:3]:
            print(f"  - {subject}")
    else:
        print("✅ Subject: CLEAN")
    
    if Teacher.objects.exists():
        warnings.append("Teacher data exists!")
        print("⚠️  WARNING: Teacher data exists!")
        for teacher in Teacher.objects.all()[:3]:
            print(f"  - {teacher}")
    else:
        print("✅ Teacher: CLEAN")
    
    if Classroom.objects.exists():
        warnings.append("Classroom data exists!")
        print("⚠️  WARNING: Classroom data exists!")
        for classroom in Classroom.objects.all()[:3]:
            print(f"  - {classroom}")
    else:
        print("✅ Classroom: CLEAN")
    
    if Config.objects.exists():
        warnings.append("Config data exists!")
        print("⚠️  WARNING: Config data exists!")
        for config in Config.objects.all()[:3]:
            print(f"  - {config}")
    else:
        print("✅ Config: CLEAN")
    
    if ClassGroup.objects.exists():
        warnings.append("ClassGroup data exists!")
        print("⚠️  WARNING: ClassGroup data exists!")
        for group in ClassGroup.objects.all()[:3]:
            print(f"  - {group}")
    else:
        print("✅ ClassGroup: CLEAN")
    
    print()
    print("=== SUMMARY ===")
    
    total_records = sum(counts.values())
    
    if total_records == 0:
        print("🎉 DATABASE IS COMPLETELY CLEAN - READY FOR REAL DATA!")
        return True
    else:
        print(f"⚠️  Database contains {total_records} records - cleanup may be needed")
        print(f"   Issues found: {len(warnings)}")
        for warning in warnings:
            print(f"   - {warning}")
        return False


if __name__ == "__main__":
    is_clean = check_database_status()
    sys.exit(0 if is_clean else 1)
