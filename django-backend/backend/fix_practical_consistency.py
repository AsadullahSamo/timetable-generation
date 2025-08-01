#!/usr/bin/env python
"""
Comprehensive fix for practical block consistency.
Ensures ALL practical subjects have their 3 consecutive blocks in the SAME lab.
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
from collections import defaultdict


def analyze_practical_consistency():
    """Analyze current practical block consistency issues."""
    print("🧪 ANALYZING PRACTICAL BLOCK CONSISTENCY")
    print("=" * 55)
    
    allocator = RoomAllocator()
    entries = list(TimetableEntry.objects.all())
    
    # Group practical entries by class group and subject
    practical_groups = defaultdict(list)
    
    for entry in entries:
        if entry.subject and entry.subject.is_practical and entry.classroom:
            key = (entry.class_group, entry.subject.code)
            practical_groups[key].append(entry)
    
    print(f"📊 Found {len(practical_groups)} practical subject groups")
    
    consistency_issues = []
    consistent_groups = []
    
    for (class_group, subject_code), group_entries in practical_groups.items():
        # Sort by day and period to check consecutive blocks
        group_entries.sort(key=lambda e: (e.day, e.period))
        
        if len(group_entries) >= 3:
            # Check if all entries are in the same lab
            labs_used = set(entry.classroom.id for entry in group_entries)
            
            if len(labs_used) > 1:
                # Inconsistency found
                lab_details = []
                for entry in group_entries:
                    lab_details.append(f"{entry.day} P{entry.period}: {entry.classroom.name}")
                
                consistency_issues.append({
                    'class_group': class_group,
                    'subject': subject_code,
                    'labs_used': len(labs_used),
                    'entries': group_entries,
                    'details': lab_details
                })
                
                print(f"❌ {class_group} {subject_code}: {len(labs_used)} different labs")
                for detail in lab_details:
                    print(f"   {detail}")
            else:
                consistent_groups.append((class_group, subject_code))
                lab_name = group_entries[0].classroom.name
                print(f"✅ {class_group} {subject_code}: consistent in {lab_name}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Consistent groups: {len(consistent_groups)}")
    print(f"   ❌ Inconsistent groups: {len(consistency_issues)}")
    
    return consistency_issues, consistent_groups


def fix_practical_consistency():
    """Fix ALL practical consistency issues."""
    print("\n🔧 FIXING PRACTICAL BLOCK CONSISTENCY")
    print("=" * 55)
    
    allocator = RoomAllocator()
    consistency_issues, _ = analyze_practical_consistency()
    
    if not consistency_issues:
        print("✅ No consistency issues found!")
        return
    
    fixes_made = 0
    
    with transaction.atomic():
        for issue in consistency_issues:
            class_group = issue['class_group']
            subject_code = issue['subject']
            entries = issue['entries']
            
            print(f"\n🔧 Fixing {class_group} {subject_code}:")
            
            # Strategy 1: Find the most frequently used lab
            lab_counts = defaultdict(int)
            for entry in entries:
                lab_counts[entry.classroom.id] += 1
            
            # Choose the lab used most frequently, or the first lab if tie
            target_lab_id = max(lab_counts.keys(), key=lambda x: lab_counts[x])
            target_lab = next(lab for lab in allocator.labs if lab.id == target_lab_id)
            
            print(f"   📍 Target lab: {target_lab.name}")
            
            # Check if target lab is available for all required periods
            all_periods_available = True
            for entry in entries:
                if not allocator._is_lab_available_for_duration(target_lab, entry.day, entry.period, 1, 
                                                               [e for e in TimetableEntry.objects.all() if e != entry]):
                    # Check if the conflict is with the same practical group
                    conflicting_entry = next((e for e in TimetableEntry.objects.all() 
                                            if e.classroom and e.classroom.id == target_lab.id and
                                            e.day == entry.day and e.period == entry.period and e != entry), None)
                    
                    if conflicting_entry and conflicting_entry in entries:
                        # Conflict is within the same practical group - this is fine
                        continue
                    else:
                        all_periods_available = False
                        break
            
            if all_periods_available:
                # Move all entries to target lab
                for entry in entries:
                    if entry.classroom.id != target_lab_id:
                        old_lab = entry.classroom.name
                        entry.classroom = target_lab
                        entry.save()
                        print(f"   ✅ Moved {entry.day} P{entry.period} from {old_lab} to {target_lab.name}")
                        fixes_made += 1
            else:
                # Strategy 2: Find a completely available lab for all periods
                print(f"   ⚠️  Target lab not available, finding alternative...")
                
                for lab in allocator.labs:
                    lab_available_for_all = True
                    
                    for entry in entries:
                        if not allocator._is_lab_available_for_duration(lab, entry.day, entry.period, 1,
                                                                       [e for e in TimetableEntry.objects.all() if e not in entries]):
                            lab_available_for_all = False
                            break
                    
                    if lab_available_for_all:
                        # Move all entries to this lab
                        print(f"   📍 Alternative lab: {lab.name}")
                        for entry in entries:
                            old_lab = entry.classroom.name
                            entry.classroom = lab
                            entry.save()
                            print(f"   ✅ Moved {entry.day} P{entry.period} from {old_lab} to {lab.name}")
                            fixes_made += 1
                        break
                else:
                    print(f"   ❌ Could not find available lab for all periods")
    
    print(f"\n✅ PRACTICAL CONSISTENCY FIX COMPLETE")
    print(f"📊 Total fixes made: {fixes_made}")
    
    # Re-analyze to verify fixes
    print(f"\n🔍 VERIFICATION:")
    new_issues, new_consistent = analyze_practical_consistency()
    
    if not new_issues:
        print("🎉 ALL PRACTICAL SUBJECTS NOW HAVE CONSISTENT LAB ALLOCATION!")
    else:
        print(f"⚠️  {len(new_issues)} issues remain - may need manual intervention")


def enforce_practical_3_block_rule():
    """Enforce the universal rule: ALL 3 blocks of a practical in the SAME lab."""
    print("🎯 ENFORCING UNIVERSAL PRACTICAL 3-BLOCK RULE")
    print("=" * 55)
    
    # Step 1: Analyze current state
    analyze_practical_consistency()
    
    # Step 2: Fix all issues
    fix_practical_consistency()
    
    # Step 3: Final verification
    print(f"\n🏁 FINAL VERIFICATION:")
    issues, consistent = analyze_practical_consistency()
    
    if not issues:
        print("🎉 SUCCESS: Universal practical 3-block rule enforced!")
        print("✅ Every practical subject has all 3 blocks in the same lab!")
    else:
        print(f"⚠️  {len(issues)} practical subjects still have consistency issues")
        print("📝 These may require additional manual review")


if __name__ == "__main__":
    enforce_practical_3_block_rule()
