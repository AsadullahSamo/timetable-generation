#!/usr/bin/env python3
"""
COMPLETE DATABASE CLEANUP SCRIPT
===============================
Wipes out ALL data from the database including:
- Teachers
- Subjects
- Classrooms
- Batches (except the default ones)
- Teacher Assignments
- Timetable Entries
- All other data

⚠️  WARNING: This will delete ALL data! Use with caution!

Usage: python cleanup_all.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import (
    Teacher, Subject, Classroom, Batch, 
    TeacherSubjectAssignment, TimetableEntry,
    ScheduleConfig, Config, ClassGroup
)

def cleanup_all_data():
    """Delete all data from the database"""
    print('⚠️  WARNING: This will delete ALL data from the database!')
    print('This includes:')
    print('  - All Teachers')
    print('  - All Subjects')
    print('  - All Classrooms')
    print('  - All Teacher Assignments')
    print('  - All Timetable Entries')
    print('  - All Configurations')
    print('  - All Class Groups')
    print('  - Custom Batches (keeping default 21SW, 22SW, 23SW, 24SW)')
    
    # Ask for confirmation
    confirm = input('\nAre you sure you want to proceed? Type "DELETE ALL" to confirm: ')
    
    if confirm != "DELETE ALL":
        print('❌ Operation cancelled.')
        return
    
    print('\n🗑️  STARTING COMPLETE DATABASE CLEANUP')
    print('=' * 50)
    
    # Count before deletion
    counts_before = {
        'Teachers': Teacher.objects.count(),
        'Subjects': Subject.objects.count(),
        'Classrooms': Classroom.objects.count(),
        'Teacher Assignments': TeacherSubjectAssignment.objects.count(),
        'Timetable Entries': TimetableEntry.objects.count(),
        'Schedule Configs': ScheduleConfig.objects.count(),
        'Configs': Config.objects.count(),
        'Class Groups': ClassGroup.objects.count(),
        'Custom Batches': Batch.objects.exclude(name__in=['21SW', '22SW', '23SW', '24SW']).count(),
    }
    
    print('📊 Data before cleanup:')
    for model, count in counts_before.items():
        print(f'   {model}: {count}')
    
    print('\n🗑️  Deleting data...')
    
    # Delete in reverse dependency order
    print('   🗑️  Deleting Timetable Entries...')
    TimetableEntry.objects.all().delete()
    
    print('   🗑️  Deleting Teacher Assignments...')
    TeacherSubjectAssignment.objects.all().delete()
    
    print('   🗑️  Deleting Teachers...')
    Teacher.objects.all().delete()
    
    print('   🗑️  Deleting Subjects...')
    Subject.objects.all().delete()
    
    print('   🗑️  Deleting Classrooms...')
    Classroom.objects.all().delete()
    
    print('   🗑️  Deleting Schedule Configurations...')
    ScheduleConfig.objects.all().delete()
    
    print('   🗑️  Deleting Configs...')
    Config.objects.all().delete()
    
    print('   🗑️  Deleting Class Groups...')
    ClassGroup.objects.all().delete()
    
    print('   🗑️  Deleting Custom Batches (keeping default ones)...')
    Batch.objects.exclude(name__in=['21SW', '22SW', '23SW', '24SW']).delete()
    
    # Count after deletion
    counts_after = {
        'Teachers': Teacher.objects.count(),
        'Subjects': Subject.objects.count(),
        'Classrooms': Classroom.objects.count(),
        'Teacher Assignments': TeacherSubjectAssignment.objects.count(),
        'Timetable Entries': TimetableEntry.objects.count(),
        'Schedule Configs': ScheduleConfig.objects.count(),
        'Configs': Config.objects.count(),
        'Class Groups': ClassGroup.objects.count(),
        'Remaining Batches': Batch.objects.count(),
    }
    
    print('\n📊 Data after cleanup:')
    for model, count in counts_after.items():
        print(f'   {model}: {count}')
    
    print('\n' + '=' * 50)
    print('✅ COMPLETE DATABASE CLEANUP FINISHED!')
    print('🎯 Database is now empty and ready for fresh data population.')
    
    # Show remaining batches
    remaining_batches = Batch.objects.all()
    if remaining_batches.exists():
        print(f'\n📋 Remaining batches:')
        for batch in remaining_batches:
            print(f'   - {batch.name}: {batch.description}')

def main():
    """Main function"""
    try:
        cleanup_all_data()
    except KeyboardInterrupt:
        print('\n❌ Operation cancelled by user.')
    except Exception as e:
        print(f'\n❌ Error during cleanup: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
