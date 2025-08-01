#!/usr/bin/env python
"""
Test script for the comprehensive room allocation system.
Validates that senior batches get labs for ALL classes and junior batches use regular rooms for theory.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.room_allocator import RoomAllocator
from timetable.models import TimetableEntry, Classroom, Subject
from timetable.constraint_resolver import IntelligentConstraintResolver


def test_room_allocation_system():
    """Test the comprehensive room allocation system."""
    print("🎓 COMPREHENSIVE ROOM ALLOCATION SYSTEM TEST")
    print("=" * 60)
    
    # Initialize components
    allocator = RoomAllocator()
    resolver = IntelligentConstraintResolver()
    
    # Get current timetable entries
    entries = list(TimetableEntry.objects.all())
    print(f"📊 Testing with {len(entries)} timetable entries")
    
    if not entries:
        print("⚠️  No timetable entries found. Please generate a timetable first.")
        return
    
    # Test 1: Validate current allocation
    print("\n🔍 TEST 1: Current Room Allocation Analysis")
    print("-" * 45)
    
    validation_report = allocator.validate_senior_batch_lab_allocation(entries)
    
    print(f"📊 Senior Batches Checked: {validation_report['senior_batches_checked']}")
    print(f"📊 Total Senior Classes: {validation_report['total_senior_classes']}")
    print(f"🏛️ Classes in Labs: {validation_report['classes_in_labs']}")
    print(f"🏢 Classes in Regular Rooms: {validation_report['classes_in_regular_rooms']}")
    print(f"📈 Compliance Rate: {validation_report['compliance_rate']:.1f}%")
    
    if validation_report['violations']:
        print(f"\n❌ Found {len(validation_report['violations'])} violations:")
        for i, violation in enumerate(validation_report['violations'][:5], 1):
            print(f"   {i}. {violation['description']}")
        if len(validation_report['violations']) > 5:
            print(f"   ... and {len(validation_report['violations']) - 5} more")
    else:
        print("\n✅ No violations found - senior batches properly allocated to labs!")
    
    # Test 2: Enforce senior batch lab priority
    print("\n🔧 TEST 2: Enforcing Senior Batch Lab Priority")
    print("-" * 45)
    
    if validation_report['violations']:
        print("Applying room optimization to fix violations...")
        optimized_entries = allocator.enforce_senior_batch_lab_priority(entries)
        
        # Re-validate after optimization
        new_validation = allocator.validate_senior_batch_lab_allocation(optimized_entries)
        print(f"\n📈 New Compliance Rate: {new_validation['compliance_rate']:.1f}%")
        print(f"📊 Remaining Violations: {len(new_validation['violations'])}")
        
        if new_validation['compliance_rate'] > validation_report['compliance_rate']:
            print("✅ Room optimization improved senior batch lab allocation!")
        else:
            print("⚠️  Room optimization did not improve allocation significantly")
    else:
        print("✅ No optimization needed - allocation already compliant!")
    
    # Test 3: Room allocation rules verification
    print("\n📋 TEST 3: Room Allocation Rules Verification")
    print("-" * 45)
    
    senior_batches = ['21SW', '22SW']
    junior_batches = ['23SW', '24SW']
    
    for batch in senior_batches:
        batch_entries = [e for e in entries if e.class_group.startswith(batch) and e.classroom]
        lab_count = sum(1 for e in batch_entries if e.classroom.is_lab)
        regular_count = sum(1 for e in batch_entries if not e.classroom.is_lab)
        
        print(f"🎓 {batch} (Senior): {lab_count} in labs, {regular_count} in regular rooms")
        if regular_count > 0:
            print(f"   ❌ {regular_count} classes should be moved to labs")
        else:
            print(f"   ✅ All classes properly in labs")
    
    for batch in junior_batches:
        batch_entries = [e for e in entries if e.class_group.startswith(batch) and e.classroom]
        theory_in_labs = sum(1 for e in batch_entries 
                           if e.classroom.is_lab and e.subject and not e.subject.is_practical)
        practical_in_labs = sum(1 for e in batch_entries 
                              if e.classroom.is_lab and e.subject and e.subject.is_practical)
        theory_in_regular = sum(1 for e in batch_entries 
                              if not e.classroom.is_lab and e.subject and not e.subject.is_practical)
        
        print(f"📚 {batch} (Junior): {theory_in_regular} theory in regular, {practical_in_labs} practicals in labs")
        if theory_in_labs > 0:
            print(f"   ❌ {theory_in_labs} theory classes should be moved to regular rooms")
        else:
            print(f"   ✅ Theory classes properly in regular rooms")
    
    # Test 4: Lab utilization analysis
    print("\n📊 TEST 4: Lab Utilization Analysis")
    print("-" * 45)
    
    total_labs = len(allocator.labs)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for day in days:
        day_entries = [e for e in entries if e.day == day and e.classroom and e.classroom.is_lab]
        periods_with_labs = {}
        
        for period in range(1, 8):
            period_entries = [e for e in day_entries if e.period == period]
            occupied_labs = len(set(e.classroom.id for e in period_entries))
            periods_with_labs[period] = occupied_labs
        
        max_usage = max(periods_with_labs.values()) if periods_with_labs else 0
        reserved_labs = total_labs - max_usage
        
        print(f"📅 {day}: Max {max_usage}/{total_labs} labs used, {reserved_labs} reserved")
        
        if reserved_labs >= 3:
            print(f"   ✅ Adequate lab reservation ({reserved_labs} labs)")
        else:
            print(f"   ⚠️  Insufficient lab reservation (need 3-4, have {reserved_labs})")
    
    print("\n🎯 ROOM ALLOCATION SYSTEM TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_room_allocation_system()
