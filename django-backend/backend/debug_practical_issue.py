#!/usr/bin/env python3
"""
Debug script to investigate persistent practical scheduling issues.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import ScheduleConfig, TimetableEntry, Subject
from timetable.algorithms.constraint_enforced_scheduler import ConstraintEnforcedScheduler

def analyze_current_practical_scheduling():
    print("🔍 DEBUGGING PRACTICAL SCHEDULING ISSUES")
    print("=" * 60)
    
    # Clear existing entries
    print("🗑️ Clearing existing timetable entries...")
    TimetableEntry.objects.all().delete()
    
    # Get config and generate timetable
    print("⚙️ Getting schedule configuration...")
    config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
    if not config:
        print("❌ No schedule configuration found!")
        return
    
    print("🎯 Generating new timetable...")
    scheduler = ConstraintEnforcedScheduler(config)
    result = scheduler.generate_timetable()
    
    # Get all practical subjects
    practical_subjects = Subject.objects.filter(is_practical=True)
    print(f"\n📚 PRACTICAL SUBJECTS IN DATABASE ({practical_subjects.count()})")
    print("-" * 40)
    for subject in practical_subjects:
        print(f"  {subject.code}: {subject.name} (Credits: {subject.credits})")
    
    # Analyze practical entries
    practical_entries = list(TimetableEntry.objects.filter(is_practical=True).order_by('subject__code', 'class_group', 'day', 'period'))
    
    print(f"\n🔍 PRACTICAL ENTRIES ANALYSIS ({len(practical_entries)} total)")
    print("-" * 40)
    
    # Group by subject-class combination
    practical_blocks = {}
    for entry in practical_entries:
        key = f"{entry.subject.code}-{entry.class_group}"
        if key not in practical_blocks:
            practical_blocks[key] = {}
        if entry.day not in practical_blocks[key]:
            practical_blocks[key][entry.day] = []
        practical_blocks[key][entry.day].append((entry.period, entry.classroom.name if entry.classroom else 'No Room'))
    
    # Analyze frequency and consistency
    issues = []
    valid_blocks = []
    broken_blocks = []
    
    print("\n📊 DETAILED ANALYSIS BY SUBJECT-CLASS")
    print("-" * 40)
    
    for subject_class, days in practical_blocks.items():
        subject_code, class_group = subject_class.split('-', 1)
        total_sessions = len(days)
        
        print(f"\n📚 {subject_class}:")
        print(f"  📋 Total sessions per week: {total_sessions}")
        
        if total_sessions == 0:
            issues.append(f"❌ {subject_class}: NOT SCHEDULED")
        elif total_sessions > 1:
            issues.append(f"⚠️ {subject_class}: SCHEDULED {total_sessions} TIMES (should be 1)")
        
        for day, periods_rooms in days.items():
            periods = [p[0] for p in periods_rooms]
            rooms = [p[1] for p in periods_rooms]
            periods.sort()
            
            print(f"    📅 {day}: Periods {periods}")
            
            # Check if it's a proper 3-consecutive block
            if len(periods) == 3 and periods == [periods[0], periods[0]+1, periods[0]+2]:
                same_room = len(set(rooms)) == 1
                room_status = "✅ Same room" if same_room else "❌ Different rooms"
                print(f"        ✅ Valid 3-consecutive block: P{periods[0]}-{periods[0]+2} ({room_status})")
                valid_blocks.append(subject_class)
            else:
                print(f"        ❌ BROKEN BLOCK: Periods {periods} (not 3-consecutive)")
                broken_blocks.append(f"{subject_class} on {day}")
    
    # Check for completely missing practical subjects
    all_class_groups = set()
    for entry in TimetableEntry.objects.all():
        all_class_groups.add(entry.class_group)
    
    missing_subjects = []
    for subject in practical_subjects:
        for class_group in all_class_groups:
            key = f"{subject.code}-{class_group}"
            if key not in practical_blocks:
                missing_subjects.append(key)
    
    print(f"\n🚫 MISSING PRACTICAL SUBJECTS ({len(missing_subjects)})")
    print("-" * 40)
    if missing_subjects:
        for missing in missing_subjects[:10]:  # Show first 10
            print(f"  • {missing}")
        if len(missing_subjects) > 10:
            print(f"  ... and {len(missing_subjects) - 10} more")
    else:
        print("  ✅ No missing practical subjects")
    
    print(f"\n📊 SUMMARY STATISTICS")
    print("-" * 40)
    print(f"  📚 Total practical subjects: {practical_subjects.count()}")
    print(f"  📋 Total class groups: {len(all_class_groups)}")
    print(f"  🎯 Expected practical sessions: {practical_subjects.count() * len(all_class_groups)}")
    print(f"  ✅ Valid 3-consecutive blocks: {len(set(valid_blocks))}")
    print(f"  ❌ Broken blocks: {len(broken_blocks)}")
    print(f"  🚫 Missing subjects: {len(missing_subjects)}")
    print(f"  ⚠️ Frequency issues: {len([i for i in issues if 'TIMES' in i])}")
    
    # Frequency distribution
    frequency_stats = {"not_scheduled": 0, "once": 0, "twice": 0, "more": 0}
    
    for subject_code in [s.code for s in practical_subjects]:
        for class_group in all_class_groups:
            key = f"{subject_code}-{class_group}"
            if key in practical_blocks:
                sessions = len(practical_blocks[key])
                if sessions == 1:
                    frequency_stats["once"] += 1
                elif sessions == 2:
                    frequency_stats["twice"] += 1
                else:
                    frequency_stats["more"] += 1
            else:
                frequency_stats["not_scheduled"] += 1
    
    print(f"\n🔬 FREQUENCY DISTRIBUTION")
    print("-" * 40)
    print(f"  🚫 Not scheduled: {frequency_stats['not_scheduled']}")
    print(f"  ✅ Once per week: {frequency_stats['once']}")
    print(f"  ⚠️ Twice per week: {frequency_stats['twice']}")
    print(f"  🚨 More than twice: {frequency_stats['more']}")
    
    # Final assessment
    print(f"\n🎯 CONSTRAINT COMPLIANCE ASSESSMENT")
    print("-" * 40)
    
    if frequency_stats['twice'] > 0 or frequency_stats['more'] > 0:
        print("❌ CONSTRAINT VIOLATION: Some practical subjects scheduled multiple times per week")
    elif len(broken_blocks) > 0:
        print("❌ CONSTRAINT VIOLATION: Some practical blocks are not 3-consecutive")
    else:
        print("✅ CONSTRAINT SATISFIED: All scheduled practicals are proper 3-consecutive blocks")
    
    if frequency_stats['not_scheduled'] > 0:
        print("⚠️ SCHEDULING ISSUE: Some practical subjects not scheduled (capacity/conflict issue)")
    
    return {
        'total_practicals': practical_subjects.count(),
        'total_class_groups': len(all_class_groups),
        'valid_blocks': len(set(valid_blocks)),
        'broken_blocks': len(broken_blocks),
        'missing_subjects': len(missing_subjects),
        'frequency_issues': len([i for i in issues if 'TIMES' in i]),
        'frequency_stats': frequency_stats
    }

if __name__ == "__main__":
    results = analyze_current_practical_scheduling()
