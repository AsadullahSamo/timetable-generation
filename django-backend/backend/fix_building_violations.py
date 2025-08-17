#!/usr/bin/env python3
"""
Script to fix existing timetable entries that violate building rules.
This script will:
1. Find all timetable entries that violate building rules
2. Move them to the correct buildings automatically
3. Ensure 2nd year batches use Academic Building for theory classes
4. Ensure non-2nd year batches use Main Building for theory classes
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.room_allocator import RoomAllocator
from timetable.models import TimetableEntry, Classroom

def fix_building_violations():
    """Fix all building rule violations in existing timetable entries."""
    print("🔧 FIXING BUILDING RULE VIOLATIONS")
    print("=" * 50)
    
    # Initialize the room allocator
    allocator = RoomAllocator()
    
    # Get all existing timetable entries
    print("📊 Loading existing timetable entries...")
    all_entries = list(TimetableEntry.objects.all())
    print(f"Found {len(all_entries)} existing entries")
    
    if not all_entries:
        print("No timetable entries found. Nothing to fix.")
        return
    
    # Get building allocation summary to identify violations
    print("\n🔍 Analyzing current building allocation...")
    summary = allocator.get_building_allocation_summary(all_entries)
    
    print(f"2nd year batch: {summary['second_year_batch']}")
    print(f"Active batches: {summary['active_batches']}")
    
    # Show current violations
    if summary['violations']:
        print(f"\n❌ Found {len(summary['violations'])} building rule violations:")
        for violation in summary['violations']:
            print(f"  • {violation['type']}: {violation['description']}")
    else:
        print("\n✅ No building rule violations found!")
        return
    
    # Fix violations by moving classes to correct buildings
    print(f"\n🔧 Fixing {len(summary['violations'])} violations...")
    
    moves_made = 0
    for violation in summary['violations']:
        if violation['type'] == '2nd Year Wrong Building':
            # Move 2nd year batch from wrong building to Academic Building
            for entry_info in violation['entries']:
                entry = TimetableEntry.objects.get(
                    class_group=entry_info['class_group'],
                    day=entry_info['day'],
                    period=entry_info['period']
                )
                
                # Find available room in Academic Building
                target_room = allocator._find_available_room_in_building(
                    entry.day, entry.period, "Academic Building", all_entries
                )
                
                if target_room:
                    old_room = entry.classroom.name
                    entry.classroom = target_room
                    entry.save()
                    print(f"  ✅ Moved {entry.class_group} from {old_room} to {target_room.name}")
                    moves_made += 1
                else:
                    print(f"  ❌ Could not find available room in Academic Building for {entry.class_group}")
        
        elif violation['type'] == 'Non-2nd Year Wrong Building':
            # Move non-2nd year batch from Academic Building to Main Building
            for entry_info in violation['entries']:
                entry = TimetableEntry.objects.get(
                    class_group=entry_info['class_group'],
                    day=entry_info['day'],
                    period=entry_info['period']
                )
                
                # Find available room in Main Building
                target_room = allocator._find_available_room_in_building(
                    entry.day, entry.period, "Main Building", all_entries
                )
                
                if target_room:
                    old_room = entry.classroom.name
                    entry.classroom = target_room
                    entry.save()
                    print(f"  ✅ Moved {entry.class_group} from {old_room} to {target_room.name}")
                    moves_made += 1
                else:
                    print(f"  ❌ Could not find available room in Main Building for {entry.class_group}")
    
    print(f"\n✅ Building rule violations fixed: {moves_made} moves completed")
    
    # Verify that violations are fixed
    print("\n🔍 Verifying fixes...")
    updated_entries = list(TimetableEntry.objects.all())
    updated_summary = allocator.get_building_allocation_summary(updated_entries)
    
    if updated_summary['violations']:
        print(f"❌ Still have {len(updated_summary['violations'])} violations:")
        for violation in updated_summary['violations']:
            print(f"  • {violation['type']}: {violation['description']}")
    else:
        print("✅ All building rule violations have been resolved!")
    
    # Show final building allocation
    print("\n📊 Final building allocation:")
    for batch, buildings in updated_summary['building_allocation'].items():
        print(f"\n  {batch}:")
        for building, entries in buildings.items():
            theory_count = len([e for e in entries if not e['is_practical']])
            practical_count = len([e for e in entries if e['is_practical']])
            print(f"    {building}: {theory_count} theory, {practical_count} practical")

def show_building_allocation():
    """Show current building allocation without making changes."""
    print("📊 CURRENT BUILDING ALLOCATION")
    print("=" * 50)
    
    allocator = RoomAllocator()
    all_entries = list(TimetableEntry.objects.all())
    
    if not all_entries:
        print("No timetable entries found.")
        return
    
    summary = allocator.get_building_allocation_summary(all_entries)
    
    print(f"2nd year batch: {summary['second_year_batch']}")
    print(f"Active batches: {summary['active_batches']}")
    
    if summary['violations']:
        print(f"\n❌ Found {len(summary['violations'])} building rule violations:")
        for violation in summary['violations']:
            print(f"  • {violation['type']}: {violation['description']}")
    else:
        print("\n✅ No building rule violations found!")
    
    print("\n📊 Building allocation details:")
    for batch, buildings in summary['building_allocation'].items():
        print(f"\n  {batch}:")
        for building, entries in buildings.items():
            theory_count = len([e for e in entries if not e['is_practical']])
            practical_count = len([e for e in entries if e['is_practical']])
            print(f"    {building}: {theory_count} theory, {practical_count} practical")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix building rule violations in timetable')
    parser.add_argument('--show-only', action='store_true', 
                       help='Only show current allocation without fixing violations')
    
    args = parser.parse_args()
    
    if args.show_only:
        show_building_allocation()
    else:
        fix_building_violations()
