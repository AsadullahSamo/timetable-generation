#!/usr/bin/env python
"""
PROPER CROSS-SEMESTER CONFLICT RESOLUTION - NO MORE LIES
"""

import os
import sys
import django
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, ScheduleConfig, Subject, Teacher, Classroom

def fix_cross_semester_properly():
    """Fix cross-semester conflicts properly"""
    print("🔧 PROPER CROSS-SEMESTER FIX")
    print("=" * 50)
    
    # Clear all existing timetables
    print("Clearing existing timetables...")
    initial_count = TimetableEntry.objects.count()
    TimetableEntry.objects.all().delete()
    print(f"Cleared {initial_count} entries")
    
    # Get all configurations
    configs = list(ScheduleConfig.objects.filter(start_time__isnull=False).order_by('name'))
    print(f"Found {len(configs)} configurations")
    
    # Track global schedules
    global_teacher_schedule = defaultdict(dict)  # teacher_id -> {(day, period): True}
    global_classroom_schedule = defaultdict(dict)  # classroom_id -> {(day, period): True}
    teacher_workloads = defaultdict(int)
    
    successful = 0
    total_entries = 0
    
    for i, config in enumerate(configs, 1):
        print(f"[{i}/{len(configs)}] Processing: {config.name}")
        
        # Get subjects for this config
        subjects_needed = []
        for class_group in config.class_groups:
            for subject_code in class_group.get('subjects', []):
                subject = Subject.objects.filter(code=subject_code).first()
                if subject:
                    subjects_needed.append((subject, class_group['name']))
        
        if not subjects_needed:
            print(f"  No subjects found")
            continue
        
        # Generate entries for this config (multiple periods per subject)
        entries = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = list(range(1, 8))

        for subject, class_group in subjects_needed:
            # Schedule multiple periods per subject (3-5 periods per week)
            periods_per_week = 4  # Standard periods per subject
            periods_scheduled = 0

            while periods_scheduled < periods_per_week:
                scheduled = False
                attempts = 0
                max_attempts = 200
            
            while not scheduled and attempts < max_attempts:
                import random
                day = random.choice(days)
                period = random.choice(periods)
                
                # Find available teacher
                qualified_teachers = list(Teacher.objects.filter(subjects=subject))
                if not qualified_teachers:
                    attempts += 1
                    continue
                
                # Sort by workload
                qualified_teachers.sort(key=lambda t: teacher_workloads[t.id])
                
                teacher = None
                for t in qualified_teachers:
                    if (day, period) not in global_teacher_schedule[t.id]:
                        teacher = t
                        break
                
                if not teacher:
                    attempts += 1
                    continue
                
                # Find available classroom
                classroom = None
                for c in Classroom.objects.all():
                    if (day, period) not in global_classroom_schedule[c.id]:
                        classroom = c
                        break
                
                if not classroom:
                    attempts += 1
                    continue
                
                # Create entry
                start_hour = 8 + (period - 1)
                entry = TimetableEntry(
                    day=day,
                    period=period,
                    subject=subject,
                    teacher=teacher,
                    classroom=classroom,
                    class_group=class_group,
                    start_time=f"{start_hour:02d}:00:00",
                    end_time=f"{start_hour + 1:02d}:00:00",
                    is_practical=False,
                    schedule_config=config,
                    semester=config.semester,
                    academic_year=config.academic_year
                )
                
                entries.append(entry)
                
                # Update global schedules
                global_teacher_schedule[teacher.id][(day, period)] = True
                global_classroom_schedule[classroom.id][(day, period)] = True
                teacher_workloads[teacher.id] += 1
                
                scheduled = True
                periods_scheduled += 1
                attempts += 1

            if not scheduled:
                attempts += 1
        
        # Save entries
        if entries:
            try:
                TimetableEntry.objects.bulk_create(entries)
                successful += 1
                total_entries += len(entries)
                print(f"  Generated {len(entries)} entries")
            except Exception as e:
                print(f"  Failed to save: {e}")
        else:
            print(f"  No entries generated")
    
    # Final analysis
    print(f"\nFINAL RESULTS:")
    print(f"Successful: {successful}/{len(configs)}")
    print(f"Total entries: {total_entries}")
    
    # Check teacher distribution
    teacher_usage = defaultdict(int)
    for entry in TimetableEntry.objects.select_related('teacher'):
        if entry.teacher:
            teacher_usage[entry.teacher.name] += 1
    
    print(f"Unique teachers used: {len(teacher_usage)}")
    print("Top teachers:")
    for teacher, count in sorted(teacher_usage.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {teacher}: {count} periods")
    
    # Check conflicts
    conflicts = 0
    teacher_schedule = defaultdict(dict)
    for entry in TimetableEntry.objects.select_related('teacher'):
        if entry.teacher:
            time_key = (entry.day, entry.period)
            if time_key in teacher_schedule[entry.teacher.id]:
                conflicts += 1
            else:
                teacher_schedule[entry.teacher.id][time_key] = entry
    
    print(f"Cross-semester conflicts: {conflicts}")
    
    if successful == len(configs) and conflicts == 0 and len(teacher_usage) > 10:
        print("\n🎉 SUCCESS: PROPERLY FIXED!")
        return True
    else:
        print("\n❌ STILL HAS ISSUES")
        return False

if __name__ == "__main__":
    success = fix_cross_semester_properly()
    if success:
        print("✅ System is now working properly")
    else:
        print("❌ System still needs work")
