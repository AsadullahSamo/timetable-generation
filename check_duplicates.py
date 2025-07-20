#!/usr/bin/env python
"""
Check and fix duplicate teacher names in the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Teacher
from collections import Counter

def check_and_fix_duplicates():
    """Check for duplicate teacher names and fix them"""
    print("🔍 Checking for duplicate teacher names...")
    
    # Find duplicate teacher names
    teacher_names = [t.name for t in Teacher.objects.all()]
    duplicates = [name for name, count in Counter(teacher_names).items() if count > 1]
    
    if not duplicates:
        print("✅ No duplicate teacher names found!")
        return
    
    print(f"⚠️  Found {len(duplicates)} duplicate teacher names:")
    
    for name in duplicates:
        teachers = Teacher.objects.filter(name=name)
        print(f"\n📋 {name}: {teachers.count()} instances")
        
        # Keep the first one, remove or rename others
        for i, teacher in enumerate(teachers):
            if i == 0:
                print(f"  ✅ Keeping: ID {teacher.id}, Email: {teacher.email}")
            else:
                # Rename the duplicate
                new_name = f"{name} ({i+1})"
                print(f"  🔄 Renaming: ID {teacher.id} to '{new_name}'")
                teacher.name = new_name
                teacher.save()
    
    print("\n✅ Duplicate teacher names fixed!")

def verify_teacher_subject_assignments():
    """Verify that teachers have subject assignments"""
    print("\n🔗 Verifying teacher-subject assignments...")
    
    teachers_with_subjects = Teacher.objects.filter(subjects__isnull=False).distinct().count()
    total_teachers = Teacher.objects.count()
    
    print(f"📊 Teachers with subjects: {teachers_with_subjects}/{total_teachers}")
    
    if teachers_with_subjects == 0:
        print("⚠️  No teachers have subject assignments!")
        return False
    elif teachers_with_subjects < total_teachers * 0.5:
        print("⚠️  Less than 50% of teachers have subject assignments")
        return False
    else:
        print("✅ Good teacher-subject assignment coverage")
        return True

def main():
    """Main function"""
    print("🔧 MUET Database Cleanup and Verification")
    print("=" * 50)
    
    # Check and fix duplicates
    check_and_fix_duplicates()
    
    # Verify assignments
    verify_teacher_subject_assignments()
    
    print("\n🎉 Database cleanup completed!")

if __name__ == "__main__":
    main()
