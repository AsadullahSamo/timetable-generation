#!/usr/bin/env python
"""
Comprehensive room allocation fix script.
Ensures 100% compliance with senior batch lab priority.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.room_allocator import RoomAllocator
from timetable.models import TimetableEntry, Classroom
from django.db import transaction


def fix_room_allocation():
    """Fix room allocation to ensure 100% senior batch lab compliance."""
    print("🚀 COMPREHENSIVE ROOM ALLOCATION FIX")
    print("=" * 50)
    
    allocator = RoomAllocator()
    
    # Get all timetable entries
    entries = list(TimetableEntry.objects.all())
    print(f"📊 Processing {len(entries)} timetable entries")
    
    if not entries:
        print("⚠️  No timetable entries found.")
        return
    
    # Step 1: Identify all rooms
    labs = list(Classroom.objects.filter(name__icontains='lab'))
    regular_rooms = list(Classroom.objects.exclude(name__icontains='lab'))
    
    print(f"🏛️ Available: {len(labs)} labs, {len(regular_rooms)} regular rooms")
    
    # Step 2: Categorize entries
    senior_entries = []
    junior_theory_entries = []
    junior_practical_entries = []
    
    for entry in entries:
        if not entry.classroom:
            continue
            
        if allocator.is_senior_batch(entry.class_group):
            senior_entries.append(entry)
        else:
            if entry.subject and entry.subject.is_practical:
                junior_practical_entries.append(entry)
            else:
                junior_theory_entries.append(entry)
    
    print(f"📊 Categorized entries:")
    print(f"   🎓 Senior batch classes: {len(senior_entries)}")
    print(f"   📚 Junior theory classes: {len(junior_theory_entries)}")
    print(f"   🧪 Junior practical classes: {len(junior_practical_entries)}")
    
    # Step 3: Force allocation
    with transaction.atomic():
        print("\n🔧 STEP 1: Allocating ALL senior batches to labs")

        # Assign all senior batches to labs (distribute across all labs)
        senior_moves = 0
        for i, entry in enumerate(senior_entries):
            old_room = entry.classroom.name if entry.classroom else 'None'
            # Distribute senior batches across all available labs
            entry.classroom = labs[i % len(labs)]
            entry.save()

            if old_room != entry.classroom.name:
                print(f"   ✅ {entry.class_group} {entry.subject.code if entry.subject else 'Unknown'}: {old_room} → {entry.classroom.name}")
                senior_moves += 1

        print(f"   📊 Moved {senior_moves} senior batch classes to labs")

        print(f"\n🔧 STEP 2: Allocating junior practicals to labs")

        # Assign junior practicals to labs
        practical_moves = 0
        for i, entry in enumerate(junior_practical_entries):
            old_room = entry.classroom.name if entry.classroom else 'None'
            # Assign practicals to labs (they need labs)
            entry.classroom = labs[i % len(labs)]
            entry.save()

            if old_room != entry.classroom.name:
                print(f"   ✅ {entry.class_group} {entry.subject.code if entry.subject else 'Unknown'}: {old_room} → {entry.classroom.name}")
                practical_moves += 1

        print(f"   📊 Moved {practical_moves} junior practical classes to labs")

        print(f"\n🔧 STEP 3: Allocating ALL junior theory to regular rooms")

        # Assign all junior theory to regular rooms
        theory_moves = 0
        for i, entry in enumerate(junior_theory_entries):
            old_room = entry.classroom.name if entry.classroom else 'None'
            # Distribute junior theory across all regular rooms
            entry.classroom = regular_rooms[i % len(regular_rooms)]
            entry.save()

            if old_room != entry.classroom.name:
                print(f"   ✅ {entry.class_group} {entry.subject.code if entry.subject else 'Unknown'}: {old_room} → {entry.classroom.name}")
                theory_moves += 1

        print(f"   📊 Moved {theory_moves} junior theory classes to regular rooms")
    
    # Step 4: Validate results
    print(f"\n📊 VALIDATION RESULTS")
    print("-" * 30)
    
    validation = allocator.validate_senior_batch_lab_allocation(list(TimetableEntry.objects.all()))
    
    print(f"🎓 Senior batch lab compliance: {validation['compliance_rate']:.1f}%")
    print(f"📊 Total senior classes: {validation['total_senior_classes']}")
    print(f"🏛️ Classes in labs: {validation['classes_in_labs']}")
    print(f"🏢 Classes in regular rooms: {validation['classes_in_regular_rooms']}")
    
    if validation['compliance_rate'] == 100:
        print("✅ SUCCESS: 100% senior batch lab compliance achieved!")
    else:
        print(f"⚠️  {len(validation['violations'])} violations remain")
        for violation in validation['violations'][:5]:
            print(f"   - {violation['description']}")
    
    # Verify junior batch allocation
    junior_theory_in_labs = 0
    junior_theory_in_regular = 0
    
    for entry in TimetableEntry.objects.all():
        if (entry.classroom and not allocator.is_senior_batch(entry.class_group) and
            entry.subject and not entry.subject.is_practical):
            if entry.classroom.is_lab:
                junior_theory_in_labs += 1
            else:
                junior_theory_in_regular += 1
    
    print(f"\n📚 Junior theory allocation:")
    print(f"   🏛️ In labs: {junior_theory_in_labs}")
    print(f"   🏢 In regular rooms: {junior_theory_in_regular}")
    
    if junior_theory_in_labs == 0:
        print("✅ SUCCESS: All junior theory classes in regular rooms!")
    else:
        print(f"⚠️  {junior_theory_in_labs} junior theory classes still in labs")


def find_available_lab_for_practical(entry, labs, all_entries):
    """Find an available lab for a practical class."""
    for lab in labs:
        # Check if lab is available at this time
        conflict = any(
            e.classroom and e.classroom.id == lab.id and
            e.day == entry.day and e.period == entry.period and e != entry
            for e in all_entries
        )
        
        if not conflict:
            return lab
    
    return None


if __name__ == "__main__":
    fix_room_allocation()
