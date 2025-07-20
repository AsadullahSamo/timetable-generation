#!/usr/bin/env python
"""
Fix duplicate teacher names and optimize the database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Teacher
from collections import Counter

def fix_duplicates():
    """Fix duplicate teacher names"""
    print("🔧 Fixing duplicate teacher names...")
    
    # Find duplicates
    teacher_names = [t.name for t in Teacher.objects.all()]
    duplicates = [name for name, count in Counter(teacher_names).items() if count > 1]
    
    if not duplicates:
        print("✅ No duplicates found!")
        return
    
    for name in duplicates:
        teachers = Teacher.objects.filter(name=name)
        print(f"📋 Fixing {name}: {teachers.count()} instances")
        
        for i, teacher in enumerate(teachers):
            if i > 0:  # Keep first, rename others
                new_name = f"{name} (Duplicate {i})"
                teacher.name = new_name
                teacher.save()
                print(f"  ✅ Renamed to: {new_name}")
    
    print("✅ Duplicates fixed!")

if __name__ == "__main__":
    fix_duplicates()
