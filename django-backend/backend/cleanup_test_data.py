#!/usr/bin/env python
"""
Clean up test data created during cross-semester conflict testing.
This script removes all test data to prepare for real data population.
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


def cleanup_all_test_data():
    """Remove all test data from the database."""
    print("Cleaning up test data...")
    
    # Get counts before deletion
    timetable_count = TimetableEntry.objects.count()
    config_count = ScheduleConfig.objects.count()
    subject_count = Subject.objects.count()
    teacher_count = Teacher.objects.count()
    classroom_count = Classroom.objects.count()
    old_config_count = Config.objects.count()
    classgroup_count = ClassGroup.objects.count()
    
    print(f"Before cleanup:")
    print(f"  - Timetable entries: {timetable_count}")
    print(f"  - Schedule configs: {config_count}")
    print(f"  - Subjects: {subject_count}")
    print(f"  - Teachers: {teacher_count}")
    print(f"  - Classrooms: {classroom_count}")
    print(f"  - Old configs: {old_config_count}")
    print(f"  - Class groups: {classgroup_count}")
    
    # Delete all data
    TimetableEntry.objects.all().delete()
    ScheduleConfig.objects.all().delete()
    Subject.objects.all().delete()
    Teacher.objects.all().delete()
    Classroom.objects.all().delete()
    Config.objects.all().delete()
    ClassGroup.objects.all().delete()
    
    print(f"\n✅ All test data cleaned up successfully!")
    print("Database is now ready for real data population.")


if __name__ == "__main__":
    cleanup_all_test_data()
