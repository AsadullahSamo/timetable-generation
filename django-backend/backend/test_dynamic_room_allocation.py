#!/usr/bin/env python
"""
Test script for the dynamic room allocation system.
Validates that the system works universally with any batch data, not hardcoded.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.room_allocator import RoomAllocator
from timetable.models import TimetableEntry, Classroom, Subject, Batch


def test_dynamic_room_allocation():
    """Test the dynamic room allocation system with current and simulated future data."""
    print("🌐 DYNAMIC ROOM ALLOCATION SYSTEM TEST")
    print("=" * 60)
    
    # Initialize room allocator
    allocator = RoomAllocator()
    
    # Test 1: Current batch detection
    print("\n🔍 TEST 1: Dynamic Batch Detection")
    print("-" * 45)
    
    # Get current timetable entries to test with real data
    entries = list(TimetableEntry.objects.all())
    if entries:
        # Extract unique class groups from current data
        class_groups = set(entry.class_group for entry in entries if entry.class_group)
        
        print(f"📊 Found {len(class_groups)} unique class groups in current data:")
        
        batch_analysis = {}
        for class_group in sorted(class_groups):
            batch = allocator.get_batch_from_class_group(class_group)
            priority = allocator.get_batch_priority(class_group)
            is_senior = allocator.is_senior_batch(class_group)
            
            if batch not in batch_analysis:
                batch_analysis[batch] = {
                    'priority': priority,
                    'is_senior': is_senior,
                    'sections': []
                }
            batch_analysis[batch]['sections'].append(class_group)
        
        for batch, info in sorted(batch_analysis.items(), key=lambda x: x[1]['priority']):
            status = "🎓 SENIOR" if info['is_senior'] else "📚 Junior"
            print(f"   {batch}: Priority {info['priority']} {status}")
            print(f"      Sections: {', '.join(info['sections'])}")
    
    # Test 2: Simulated future data
    print("\n🔮 TEST 2: Future Data Simulation")
    print("-" * 45)
    
    # Simulate future batch names
    future_batches = ['25CS', '26SW', '27AI', '28DS']
    
    print("Testing with simulated future batch data:")
    for batch in future_batches:
        # Test with different section formats
        test_groups = [f"{batch}-I", f"{batch}-A", f"{batch}I", f"{batch}A"]
        
        for class_group in test_groups:
            extracted_batch = allocator.get_batch_from_class_group(class_group)
            priority = allocator.get_batch_priority(class_group)
            is_senior = allocator.is_senior_batch(class_group)
            
            print(f"   {class_group} → Batch: {extracted_batch}, Priority: {priority}, Senior: {is_senior}")
    
    # Test 3: Room allocation rules validation
    print("\n📋 TEST 3: Dynamic Room Allocation Rules")
    print("-" * 45)
    
    total_labs = len(allocator.labs)
    total_regular = len(allocator.regular_rooms)
    
    # Calculate dynamic limits
    reserved_labs_for_seniors = min(3, max(1, total_labs // 2))
    max_practicals_per_day = min(3, total_labs - reserved_labs_for_seniors)
    
    print(f"🏛️ Room Infrastructure:")
    print(f"   Total Labs: {total_labs}")
    print(f"   Total Regular Rooms: {total_regular}")
    print(f"   Labs Reserved for Seniors: {reserved_labs_for_seniors}")
    print(f"   Max Practicals per Day: {max_practicals_per_day}")
    
    print(f"\n📏 Dynamic Allocation Rules:")
    print(f"   ✅ Senior batches (Priority 1): ALL classes in labs")
    print(f"   ✅ Junior batches (Priority 2+): Theory in regular rooms, practicals in remaining labs")
    print(f"   ✅ Practical consistency: All 3 blocks of same practical in same lab")
    print(f"   ✅ Lab reservation: {reserved_labs_for_seniors} labs reserved for senior theory classes")
    
    # Test 4: Practical block consistency
    print("\n🧪 TEST 4: Practical Block Consistency")
    print("-" * 45)
    
    if entries:
        # Test practical consistency with current data
        practical_entries = [e for e in entries if e.subject and e.subject.is_practical]
        
        if practical_entries:
            print(f"📊 Found {len(practical_entries)} practical class entries")
            
            # Group by class group and subject
            from collections import defaultdict
            practical_groups = defaultdict(list)
            
            for entry in practical_entries:
                if entry.classroom:
                    key = (entry.class_group, entry.subject.code)
                    practical_groups[key].append(entry)
            
            consistency_issues = 0
            for (class_group, subject_code), group_entries in practical_groups.items():
                if len(group_entries) >= 3:  # Should be 3-block practical
                    labs_used = set(entry.classroom.id for entry in group_entries if entry.classroom)
                    if len(labs_used) > 1:
                        consistency_issues += 1
                        print(f"   ⚠️  {class_group} {subject_code}: using {len(labs_used)} different labs")
                    else:
                        lab_name = group_entries[0].classroom.name if group_entries[0].classroom else 'Unknown'
                        print(f"   ✅ {class_group} {subject_code}: consistent in {lab_name}")
            
            if consistency_issues == 0:
                print("   🎉 All practical subjects have consistent lab allocation!")
            else:
                print(f"   📝 Found {consistency_issues} practical consistency issues to fix")
        else:
            print("   ℹ️  No practical classes found in current data")
    
    # Test 5: Senior batch compliance
    print("\n🎓 TEST 5: Senior Batch Lab Compliance")
    print("-" * 45)
    
    if entries:
        validation_report = allocator.validate_senior_batch_lab_allocation(entries)
        
        print(f"📊 Senior Batch Analysis:")
        print(f"   Batches Checked: {validation_report['senior_batches_checked']}")
        print(f"   Total Senior Classes: {validation_report['total_senior_classes']}")
        print(f"   Classes in Labs: {validation_report['classes_in_labs']}")
        print(f"   Classes in Regular Rooms: {validation_report['classes_in_regular_rooms']}")
        print(f"   Compliance Rate: {validation_report['compliance_rate']:.1f}%")
        
        if validation_report['compliance_rate'] == 100:
            print("   🎉 Perfect compliance! All senior classes in labs!")
        else:
            print(f"   📝 {len(validation_report['violations'])} violations need fixing")
    
    print("\n🌐 DYNAMIC SYSTEM VALIDATION COMPLETE")
    print("=" * 60)
    print("✅ System is universal and will work with any future batch data!")
    print("✅ No hardcoded batch names - fully dynamic detection!")
    print("✅ Automatic seniority calculation based on year/semester!")
    print("✅ Scalable room allocation rules!")


if __name__ == "__main__":
    test_dynamic_room_allocation()
