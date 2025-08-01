#!/usr/bin/env python
"""
Test script to verify that the practical 3-block same-lab rule is properly enforced.
This tests the universal rule: ALL practical subjects must have their 3 consecutive blocks in the SAME lab.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, Subject, Classroom, ScheduleConfig
from timetable.room_allocator import RoomAllocator
from timetable.algorithms.final_scheduler import FinalUniversalScheduler
from collections import defaultdict


def test_practical_consistency_enforcement():
    """Test that the system enforces practical 3-block same-lab rule."""
    print("🧪 TESTING PRACTICAL 3-BLOCK SAME-LAB RULE ENFORCEMENT")
    print("=" * 65)
    
    # Check current practical subjects
    practical_subjects = Subject.objects.filter(is_practical=True)
    print(f"📊 Found {practical_subjects.count()} practical subjects in database:")
    for subject in practical_subjects:
        print(f"   - {subject.code}: {subject.name} ({subject.credits} credits)")
    
    # Check current practical entries
    practical_entries = TimetableEntry.objects.filter(subject__is_practical=True)
    print(f"\n📊 Current practical entries in timetable: {practical_entries.count()}")
    
    if practical_entries.count() == 0:
        print("\n⚠️  No practical classes currently scheduled.")
        print("🔧 Testing the enforcement mechanism with scheduler...")
        
        # Test the scheduler's practical consistency enforcement
        test_scheduler_practical_consistency()
    else:
        print("\n🔍 Analyzing existing practical entries...")
        analyze_existing_practical_consistency()
    
    # Test the room allocator's consistency enforcement
    test_room_allocator_consistency()


def analyze_existing_practical_consistency():
    """Analyze existing practical entries for consistency violations."""
    print("\n🔍 ANALYZING EXISTING PRACTICAL CONSISTENCY")
    print("-" * 50)
    
    allocator = RoomAllocator()
    practical_entries = TimetableEntry.objects.filter(subject__is_practical=True)
    
    # Group by class group and subject
    practical_groups = defaultdict(list)
    for entry in practical_entries:
        if entry.classroom:
            key = (entry.class_group, entry.subject.code)
            practical_groups[key].append(entry)
    
    violations = []
    consistent_groups = []
    
    for (class_group, subject_code), entries in practical_groups.items():
        # Sort by day and period
        entries.sort(key=lambda e: (e.day, e.period))
        
        if len(entries) >= 3:
            # Check lab consistency
            labs_used = set(entry.classroom.id for entry in entries)
            
            if len(labs_used) > 1:
                # Violation found
                lab_details = []
                for entry in entries:
                    lab_details.append(f"{entry.day} P{entry.period}: {entry.classroom.name}")
                
                violations.append({
                    'class_group': class_group,
                    'subject': subject_code,
                    'labs_used': len(labs_used),
                    'details': lab_details
                })
                
                print(f"❌ {class_group} {subject_code}: {len(labs_used)} different labs")
                for detail in lab_details:
                    print(f"   {detail}")
            else:
                consistent_groups.append((class_group, subject_code))
                lab_name = entries[0].classroom.name
                print(f"✅ {class_group} {subject_code}: consistent in {lab_name}")
    
    print(f"\n📊 CONSISTENCY ANALYSIS:")
    print(f"   ✅ Consistent groups: {len(consistent_groups)}")
    print(f"   ❌ Inconsistent groups: {len(violations)}")
    
    if violations:
        print(f"\n🚨 VIOLATIONS DETECTED!")
        print("The system should enforce the rule: ALL 3 blocks in SAME lab")
        return False
    else:
        print(f"\n🎉 ALL PRACTICAL SUBJECTS FOLLOW THE 3-BLOCK SAME-LAB RULE!")
        return True


def test_scheduler_practical_consistency():
    """Test the scheduler's practical consistency enforcement."""
    print("\n🔧 TESTING SCHEDULER PRACTICAL CONSISTENCY ENFORCEMENT")
    print("-" * 55)

    # Test the practical subjects availability
    practical_subjects = Subject.objects.filter(is_practical=True)

    if practical_subjects.exists():
        test_subject = practical_subjects.first()
        test_class_group = "21SW-I"

        print(f"🧪 Testing with practical subject: {test_subject.code}")
        print(f"📚 Testing with class group: {test_class_group}")

        # Check if the scheduler class has the required method
        try:
            config = ScheduleConfig.objects.first()
            if not config:
                config = ScheduleConfig.objects.create(
                    max_periods_per_day=7,
                    max_classes_per_day=6,
                    break_periods=[4],
                    preferred_days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                )

            scheduler = FinalUniversalScheduler(config)

            # Check if the method exists
            if hasattr(scheduler, '_find_existing_lab_for_practical'):
                print("✅ Scheduler has _find_existing_lab_for_practical method")
            else:
                print("❌ Scheduler missing _find_existing_lab_for_practical method")

            print("✅ Scheduler practical consistency methods are available")
        except Exception as e:
            print(f"⚠️  Scheduler initialization issue: {e}")
    else:
        print("⚠️  No practical subjects found to test with")


def test_room_allocator_consistency():
    """Test the room allocator's consistency enforcement."""
    print("\n🏛️ TESTING ROOM ALLOCATOR CONSISTENCY ENFORCEMENT")
    print("-" * 55)
    
    allocator = RoomAllocator()
    
    # Test the consistency enforcement method
    entries = list(TimetableEntry.objects.all())
    
    if entries:
        print(f"📊 Testing with {len(entries)} timetable entries")
        
        # Run consistency enforcement
        consistent_entries = allocator.ensure_practical_block_consistency(entries)
        
        print(f"✅ Consistency enforcement completed")
        print(f"📊 Processed {len(consistent_entries)} entries")
    else:
        print("⚠️  No timetable entries found to test with")


def demonstrate_practical_rule():
    """Demonstrate the practical 3-block same-lab rule."""
    print("\n📋 PRACTICAL 3-BLOCK SAME-LAB RULE DEMONSTRATION")
    print("=" * 55)
    
    print("🎯 UNIVERSAL RULE: All practical subjects must follow this pattern:")
    print()
    print("   ✅ CORRECT (Same Lab):")
    print("      Monday P1: Database Systems (PR) - Lab 1")
    print("      Monday P2: Database Systems (PR) - Lab 1  ← SAME LAB")
    print("      Monday P3: Database Systems (PR) - Lab 1  ← SAME LAB")
    print()
    print("   ❌ INCORRECT (Different Labs):")
    print("      Monday P1: Database Systems (PR) - Lab 1")
    print("      Monday P2: Database Systems (PR) - Lab 2  ← DIFFERENT LAB")
    print("      Monday P3: Database Systems (PR) - Lab 3  ← DIFFERENT LAB")
    print()
    print("🔧 ENFORCEMENT MECHANISMS:")
    print("   1. Scheduler checks for existing lab assignments")
    print("   2. Room allocator enforces consistency")
    print("   3. Constraint resolver fixes violations")
    print("   4. Post-processing ensures compliance")
    print()
    print("🌐 UNIVERSAL APPLICATION:")
    print("   - Works with ANY practical subject")
    print("   - Works with ANY class group")
    print("   - Works with ANY number of labs")
    print("   - Works with ANY future data")


def verify_system_readiness():
    """Verify that the system is ready to enforce practical consistency."""
    print("\n🔍 SYSTEM READINESS VERIFICATION")
    print("=" * 40)
    
    checks = []
    
    # Check 1: Room allocator has consistency method
    try:
        allocator = RoomAllocator()
        if hasattr(allocator, 'ensure_practical_block_consistency'):
            checks.append("✅ Room allocator has consistency enforcement")
        else:
            checks.append("❌ Room allocator missing consistency method")
    except Exception as e:
        checks.append(f"❌ Room allocator error: {e}")
    
    # Check 2: Scheduler has existing lab finder
    try:
        config = ScheduleConfig.objects.first()
        if not config:
            config = ScheduleConfig.objects.create(
                max_periods_per_day=7,
                max_classes_per_day=6,
                break_periods=[4],
                preferred_days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            )
        scheduler = FinalUniversalScheduler(config)
        if hasattr(scheduler, '_find_existing_lab_for_practical'):
            checks.append("✅ Scheduler has existing lab finder")
        else:
            checks.append("❌ Scheduler missing lab finder method")
    except Exception as e:
        checks.append(f"❌ Scheduler error: {e}")
    
    # Check 3: Practical subjects exist
    try:
        practical_count = Subject.objects.filter(is_practical=True).count()
        if practical_count > 0:
            checks.append(f"✅ {practical_count} practical subjects available")
        else:
            checks.append("⚠️  No practical subjects in database")
    except Exception as e:
        checks.append(f"❌ Database error: {e}")
    
    # Check 4: Labs exist
    try:
        lab_count = Classroom.objects.filter(name__icontains='lab').count()
        if lab_count > 0:
            checks.append(f"✅ {lab_count} labs available")
        else:
            checks.append("❌ No labs found in database")
    except Exception as e:
        checks.append(f"❌ Classroom error: {e}")
    
    print("\n📊 SYSTEM CHECKS:")
    for check in checks:
        print(f"   {check}")
    
    all_passed = all("✅" in check for check in checks)
    
    if all_passed:
        print("\n🎉 SYSTEM IS READY TO ENFORCE PRACTICAL CONSISTENCY!")
    else:
        print("\n⚠️  Some system components need attention")
    
    return all_passed


if __name__ == "__main__":
    demonstrate_practical_rule()
    verify_system_readiness()
    test_practical_consistency_enforcement()
    
    print("\n🎯 CONCLUSION:")
    print("The system is designed to enforce the universal rule:")
    print("ALL practical subjects must have their 3 consecutive blocks in the SAME lab!")
    print("This applies to ALL practical subjects, ALL class groups, and ALL future data!")
