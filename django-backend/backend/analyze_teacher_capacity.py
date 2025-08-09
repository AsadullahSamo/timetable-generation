#!/usr/bin/env python3

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import Subject, Teacher, TimetableEntry

def analyze_teacher_capacity():
    print('=== PRACTICAL SCHEDULING CAPACITY ANALYSIS ===')
    print()

    # Get practical subjects and class groups
    practical_subjects = Subject.objects.filter(is_practical=True)
    all_entries = TimetableEntry.objects.all()
    class_groups = set(entry.class_group for entry in all_entries)

    print(f'📚 Practical subjects: {practical_subjects.count()}')
    print(f'📋 Class groups: {len(class_groups)} → {sorted(class_groups)}')
    print(f'🎯 Total practical sessions needed: {practical_subjects.count() * len(class_groups)} sessions')
    print()

    # Check teacher capacity
    print('👨‍🏫 TEACHER CAPACITY ANALYSIS:')
    total_overloaded = 0
    
    for subject in practical_subjects:
        assigned_teachers = subject.teachersubjectassignment_set.all()
        teacher_count = assigned_teachers.count()
        sessions_needed = len(class_groups)  # One session per class group
        
        print(f'  {subject.code}:')
        print(f'    Teachers assigned: {teacher_count}')
        print(f'    Sessions needed: {sessions_needed}')
        
        if teacher_count > 0:
            ratio = sessions_needed / teacher_count
            print(f'    Capacity ratio: {ratio:.1f} sessions per teacher')
        else:
            print(f'    Capacity ratio: ∞ sessions per teacher')
        
        if teacher_count == 0:
            print(f'    ❌ CRITICAL: No teachers assigned!')
            total_overloaded += 1
        elif sessions_needed > teacher_count * 5:  # Assuming max 5 time slots per teacher per week
            print(f'    ⚠️  OVERLOADED: Not enough teachers for capacity')
            total_overloaded += 1
        elif sessions_needed > teacher_count:
            print(f'    ⚠️  TIGHT: Teachers need to teach multiple sessions')
        else:
            print(f'    ✅ OK: Sufficient teacher capacity')
        print()

    print('💡 ANALYSIS SUMMARY:')
    print(f'   - {total_overloaded} out of {practical_subjects.count()} practical subjects are overloaded')
    print(f'   - Each teacher needs to handle multiple class groups simultaneously')
    print(f'   - This causes scheduling conflicts when trying to assign same time slots')
    print()
    
    print('🔧 RECOMMENDED SOLUTIONS:')
    print('1. Add more teachers to practical subjects (assign multiple teachers per subject)')
    print('2. Improve scheduling algorithm to better distribute time slots across the week')
    print('3. Consider staggered scheduling (different practical subjects on different days)')
    
    return total_overloaded

if __name__ == "__main__":
    analyze_teacher_capacity()
