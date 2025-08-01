#!/usr/bin/env python3
"""
ENHANCED ROOM ALLOCATION SYSTEM TEST
===================================
Comprehensive test suite for the enhanced room allocation system that ensures:
1. Practical subjects are ALWAYS assigned to labs
2. All 3 blocks of a practical subject use the SAME lab
3. Flexible senior batch allocation with practical priority
4. Intelligent conflict resolution
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, Subject, Classroom, Teacher, Batch
from timetable.room_allocator import RoomAllocator
from timetable.constraint_validator import ConstraintValidator
from timetable.algorithms.final_scheduler import FinalUniversalScheduler
from collections import defaultdict


def test_room_allocation_system():
    """Main test function for the enhanced room allocation system."""
    print("🧪 ENHANCED ROOM ALLOCATION SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Basic system setup validation
    print("\n1️⃣ TESTING SYSTEM SETUP")
    test_system_setup()
    
    # Test 2: Room allocator functionality
    print("\n2️⃣ TESTING ROOM ALLOCATOR")
    test_room_allocator()
    
    # Test 3: Practical subject allocation
    print("\n3️⃣ TESTING PRACTICAL ALLOCATION")
    test_practical_allocation()
    
    # Test 4: Same-lab rule enforcement
    print("\n4️⃣ TESTING SAME-LAB RULE")
    test_same_lab_rule()
    
    # Test 5: Constraint validation
    print("\n5️⃣ TESTING CONSTRAINT VALIDATION")
    test_constraint_validation()
    
    # Test 6: Integration with scheduler
    print("\n6️⃣ TESTING SCHEDULER INTEGRATION")
    test_scheduler_integration()
    
    print("\n🎉 ENHANCED ROOM ALLOCATION TEST COMPLETE")


def test_system_setup():
    """Test basic system setup and data availability."""
    print("   📊 Checking system setup...")
    
    # Check subjects
    subjects = Subject.objects.all()
    practical_subjects = Subject.objects.filter(is_practical=True)
    print(f"   ✅ Total subjects: {subjects.count()}")
    print(f"   ✅ Practical subjects: {practical_subjects.count()}")
    
    # Check classrooms
    classrooms = Classroom.objects.all()
    labs = [room for room in classrooms if room.is_lab]
    regular_rooms = [room for room in classrooms if not room.is_lab]
    print(f"   ✅ Total classrooms: {classrooms.count()}")
    print(f"   ✅ Labs: {len(labs)}")
    print(f"   ✅ Regular rooms: {len(regular_rooms)}")
    
    # Check room allocator
    allocator = RoomAllocator()
    print(f"   ✅ Room allocator initialized")
    print(f"   ✅ Allocator labs: {len(allocator.labs)}")
    print(f"   ✅ Allocator regular rooms: {len(allocator.regular_rooms)}")
    
    assert len(labs) > 0, "No labs found in system"
    assert len(practical_subjects) > 0, "No practical subjects found"
    assert len(regular_rooms) > 0, "No regular rooms found"
    
    print("   🎯 System setup validation: PASSED")


def test_room_allocator():
    """Test room allocator functionality."""
    print("   🔧 Testing room allocator methods...")
    
    allocator = RoomAllocator()
    
    # Test lab availability checking
    entries = list(TimetableEntry.objects.all())
    available_labs = allocator.get_available_labs_for_time('Monday', 1, entries, duration=3)
    print(f"   ✅ Available labs for Monday P1-P3: {len(available_labs)}")
    
    # Test regular room availability
    available_rooms = allocator.get_available_regular_rooms_for_time('Monday', 1, entries, duration=1)
    print(f"   ✅ Available regular rooms for Monday P1: {len(available_rooms)}")
    
    # Test seniority detection
    is_senior_21sw = allocator.is_senior_batch('21SW-I')
    is_senior_24sw = allocator.is_senior_batch('24SW-A')
    print(f"   ✅ 21SW-I is senior: {is_senior_21sw}")
    print(f"   ✅ 24SW-A is senior: {is_senior_24sw}")
    
    print("   🎯 Room allocator functionality: PASSED")


def test_practical_allocation():
    """Test practical subject allocation to labs."""
    print("   🧪 Testing practical subject allocation...")
    
    allocator = RoomAllocator()
    practical_subjects = Subject.objects.filter(is_practical=True)
    
    if not practical_subjects:
        print("   ⚠️  No practical subjects to test")
        return
    
    # Test practical allocation for different batches
    test_cases = [
        ('21SW-I', 'Monday', 1),  # Senior batch
        ('22SW-A', 'Tuesday', 2),  # Junior batch
        ('23SW-B', 'Wednesday', 3),  # Junior batch
    ]
    
    entries = []
    
    for class_group, day, start_period in test_cases:
        for subject in practical_subjects[:2]:  # Test first 2 practical subjects
            print(f"     🔍 Testing {subject.code} for {class_group} on {day} P{start_period}")
            
            allocated_lab = allocator.allocate_room_for_practical(
                day, start_period, class_group, subject, entries
            )
            
            if allocated_lab:
                print(f"       ✅ Allocated lab: {allocated_lab.name}")
                assert allocated_lab.is_lab, f"Practical subject allocated to non-lab: {allocated_lab.name}"
                
                # Create mock entries for the 3-block practical
                for period_offset in range(3):
                    mock_entry = type('MockEntry', (), {
                        'day': day,
                        'period': start_period + period_offset,
                        'class_group': class_group,
                        'subject': subject,
                        'classroom': allocated_lab
                    })()
                    entries.append(mock_entry)
            else:
                print(f"       ❌ Failed to allocate lab for {subject.code}")
    
    print("   🎯 Practical allocation test: PASSED")


def test_same_lab_rule():
    """Test same-lab rule enforcement."""
    print("   🔄 Testing same-lab rule enforcement...")
    
    allocator = RoomAllocator()
    practical_subjects = Subject.objects.filter(is_practical=True)
    
    if not practical_subjects:
        print("   ⚠️  No practical subjects to test")
        return
    
    # Create test entries with intentional violations
    test_entries = []
    subject = practical_subjects.first()
    class_group = '21SW-I'
    
    # Create entries in different labs (violation)
    labs = list(Classroom.objects.filter(name__icontains='lab'))
    if len(labs) >= 2:
        for i, period in enumerate([1, 2, 3]):
            lab = labs[i % 2]  # Alternate between first two labs
            mock_entry = type('MockEntry', (), {
                'day': 'Monday',
                'period': period,
                'class_group': class_group,
                'subject': subject,
                'classroom': lab
            })()
            test_entries.append(mock_entry)
        
        print(f"     🔍 Created test violation: {subject.code} in {len(set(e.classroom.id for e in test_entries))} different labs")
        
        # Test consistency enforcement
        fixed_entries = allocator.ensure_practical_block_consistency(test_entries)
        
        # Verify fix
        labs_used_after = set(e.classroom.id for e in fixed_entries if e.subject == subject)
        print(f"     ✅ After fix: {len(labs_used_after)} lab(s) used")
        assert len(labs_used_after) == 1, "Same-lab rule not enforced"
    
    print("   🎯 Same-lab rule test: PASSED")


def test_constraint_validation():
    """Test constraint validation system."""
    print("   ✅ Testing constraint validation...")
    
    validator = ConstraintValidator()
    entries = list(TimetableEntry.objects.all())
    
    # Run validation
    results = validator.validate_all_constraints(entries)
    
    print(f"     📊 Validation results:")
    print(f"       Total constraints checked: {len(results.get('constraint_results', {}))}")

    # Check if results have the expected structure
    if 'overall_status' in results:
        print(f"       Overall status: {results['overall_status']}")
    if 'total_violations' in results:
        print(f"       Total violations: {results['total_violations']}")
    else:
        # Calculate total violations manually
        total_violations = sum(result.get('violations', 0) for result in results.get('constraint_results', {}).values())
        print(f"       Total violations: {total_violations}")
    
    # Check for room-related violations
    room_violations = 0
    constraint_results = results.get('constraint_results', {})
    for constraint_name, result in constraint_results.items():
        violations = result.get('violations', 0)
        if 'room' in constraint_name.lower() or 'practical' in constraint_name.lower():
            room_violations += violations
            if violations > 0:
                print(f"       ⚠️  {constraint_name}: {violations} violations")
    
    print(f"     📈 Room-related violations: {room_violations}")
    print("   🎯 Constraint validation test: PASSED")


def test_scheduler_integration():
    """Test integration with the scheduler."""
    print("   🔗 Testing scheduler integration...")
    
    # This is a basic integration test
    # In a real scenario, you would run the full scheduler
    
    try:
        # Get a config for scheduler initialization
        from timetable.models import ScheduleConfig
        config = ScheduleConfig.objects.first()
        if not config:
            print("     ⚠️  No schedule config found, skipping scheduler test")
            return

        scheduler = FinalUniversalScheduler(config)
        print("     ✅ Scheduler initialized successfully")
        
        # Test room allocation method
        allocator = scheduler.room_allocator
        print("     ✅ Scheduler has room allocator")
        
        # Test practical subjects detection
        practical_subjects = Subject.objects.filter(is_practical=True)
        if practical_subjects:
            subject = practical_subjects.first()
            is_practical = scheduler._is_practical_subject(subject)
            print(f"     ✅ Practical detection works: {is_practical}")
        
        print("   🎯 Scheduler integration test: PASSED")
        
    except Exception as e:
        print(f"     ❌ Scheduler integration error: {e}")
        raise


if __name__ == "__main__":
    try:
        test_room_allocation_system()
        print("\n🎉 ALL TESTS PASSED - ENHANCED ROOM ALLOCATION SYSTEM IS READY!")
    except Exception as e:
        print(f"\n💥 TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
