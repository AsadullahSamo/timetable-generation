#!/usr/bin/env python3
"""
Simple test script for the enhanced timetable generation system.
Demonstrates the enhanced room allocation and constraint resolution.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, Subject, Teacher, Classroom, ScheduleConfig, Batch
from timetable.enhanced_room_allocator import EnhancedRoomAllocator
from timetable.enhanced_constraint_resolver import EnhancedConstraintResolver
from timetable.algorithms.enhanced_scheduler import EnhancedScheduler
from timetable.constraint_validator import ConstraintValidator

def test_enhanced_room_allocation():
    """Test the enhanced room allocation system."""
    print("🧪 Testing Enhanced Room Allocation System")
    print("=" * 60)
    
    try:
        # Initialize enhanced room allocator
        room_allocator = EnhancedRoomAllocator()
        
        print(f"📊 Room Allocation Report:")
        report = room_allocator.get_allocation_report()
        for key, value in report.items():
            if key != 'room_usage':
                print(f"   • {key}: {value}")
        
        # Test room allocation for different sections
        test_sections = ['21SW-I', '22SW-II', '23SW-III', '24SW-I']
        
        for section in test_sections:
            is_second_year = room_allocator.is_second_year_section(section)
            preferred_rooms = room_allocator.get_preferred_rooms_for_section(section)
            
            print(f"\n📋 Section: {section}")
            print(f"   • Is 2nd year: {is_second_year}")
            print(f"   • Preferred rooms: {len(preferred_rooms)} rooms")
            if preferred_rooms:
                print(f"   • First preferred: {preferred_rooms[0].name} ({preferred_rooms[0].building})")
        
        return True
    except Exception as e:
        print(f"❌ Error in room allocation test: {str(e)}")
        return False

def test_enhanced_constraint_resolution():
    """Test the enhanced constraint resolution system."""
    print("\n🧪 Testing Enhanced Constraint Resolution System")
    print("=" * 60)
    
    try:
        # Initialize enhanced constraint resolver
        constraint_resolver = EnhancedConstraintResolver()
        
        # Get some test entries
        entries = list(TimetableEntry.objects.all()[:20])
        
        if not entries:
            print("❌ No timetable entries found. Please generate a timetable first.")
            return False
        
        print(f"📊 Testing with {len(entries)} timetable entries")
        
        # Test constraint validation
        validator = ConstraintValidator()
        validation_result = validator.validate_all_constraints(entries)
        
        print(f"🔍 Initial validation:")
        print(f"   • Total violations: {validation_result['total_violations']}")
        print(f"   • Overall compliance: {validation_result['overall_compliance']}")
        
        # Show violation breakdown
        print("\n📋 Violation Breakdown:")
        for constraint, violations in validation_result['violations_by_constraint'].items():
            if violations:
                print(f"   • {constraint}: {len(violations)} violations")
        
        # Test constraint resolution
        print(f"\n🔧 Testing Enhanced Constraint Resolution...")
        resolution_result = constraint_resolver.resolve_all_violations(entries)
        
        print(f"\n📊 Resolution Results:")
        print(f"   • Initial violations: {resolution_result['initial_violations']}")
        print(f"   • Final violations: {resolution_result['final_violations']}")
        print(f"   • Iterations completed: {resolution_result['iterations_completed']}")
        print(f"   • Overall success: {resolution_result['overall_success']}")
        
        return resolution_result['overall_success']
    except Exception as e:
        print(f"❌ Error in constraint resolution test: {str(e)}")
        return False

def test_room_allocation_validation():
    """Test room allocation validation."""
    print("\n🧪 Testing Room Allocation Validation")
    print("=" * 60)
    
    try:
        # Get some test entries
        entries = list(TimetableEntry.objects.all()[:50])
        
        if not entries:
            print("❌ No timetable entries found.")
            return False
        
        # Initialize room allocator
        room_allocator = EnhancedRoomAllocator()
        
        # Validate room allocation
        violations = room_allocator.validate_room_allocation(entries)
        
        print(f"🔍 Room Allocation Validation:")
        print(f"   • Total violations: {len(violations)}")
        
        if violations:
            print(f"\n📋 Violations Found:")
            for violation in violations[:5]:  # Show first 5 violations
                print(f"   • {violation['type']}: {violation['description']}")
        else:
            print(f"   ✅ No room allocation violations found!")
        
        return len(violations) == 0
    except Exception as e:
        print(f"❌ Error in room allocation validation test: {str(e)}")
        return False

def test_practical_session_management():
    """Test practical session management."""
    print("\n🧪 Testing Practical Session Management")
    print("=" * 60)
    
    try:
        # Get practical entries
        practical_entries = list(TimetableEntry.objects.filter(is_practical=True)[:20])
        
        if not practical_entries:
            print("❌ No practical entries found.")
            return False
        
        print(f"📊 Testing with {len(practical_entries)} practical entries")
        
        # Group practical entries by subject and class group
        practical_groups = {}
        for entry in practical_entries:
            key = (entry.class_group, entry.subject.code, entry.day)
            if key not in practical_groups:
                practical_groups[key] = []
            practical_groups[key].append(entry)
        
        print(f"📋 Practical Groups Found:")
        for key, group_entries in practical_groups.items():
            class_group, subject_code, day = key
            periods = sorted([entry.period for entry in group_entries])
            
            print(f"   • {subject_code} ({class_group}) on {day}: {periods}")
            
            # Check if consecutive
            is_consecutive = all(periods[i] == periods[i-1] + 1 for i in range(1, len(periods)))
            print(f"     - Consecutive: {is_consecutive}")
            
            # Check if same lab
            labs_used = set(entry.classroom.id for entry in group_entries if entry.classroom)
            same_lab = len(labs_used) == 1
            print(f"     - Same lab: {same_lab}")
            
            # Check if in lab
            in_lab = all(entry.classroom.is_lab for entry in group_entries if entry.classroom)
            print(f"     - In lab: {in_lab}")
        
        return True
    except Exception as e:
        print(f"❌ Error in practical session management test: {str(e)}")
        return False

def test_enhanced_scheduler():
    """Test the enhanced scheduler system."""
    print("\n🧪 Testing Enhanced Scheduler System")
    print("=" * 60)
    
    try:
        # Get the latest schedule config
        config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
        
        if not config:
            print("❌ No schedule configuration found. Please create a schedule config first.")
            return False
        
        print(f"📋 Using schedule config: {config.name}")
        print(f"   • Days: {config.days}")
        print(f"   • Periods: {config.periods}")
        print(f"   • Start time: {config.start_time}")
        print(f"   • Lesson duration: {config.lesson_duration} minutes")
        
        # Initialize enhanced scheduler
        scheduler = EnhancedScheduler(config)
        
        # Test timetable generation
        print(f"\n🚀 Testing Enhanced Timetable Generation...")
        result = scheduler.generate_timetable()
        
        print(f"\n📊 Generation Results:")
        print(f"   • Success: {result['success']}")
        if result['success']:
            print(f"   • Entries generated: {result['entries_generated']}")
            print(f"   • Entries saved: {result['entries_saved']}")
            print(f"   • Generation time: {result['generation_time']:.2f} seconds")
            print(f"   • Initial violations: {result['initial_violations']}")
            print(f"   • Final violations: {result['final_violations']}")
            print(f"   • Iterations completed: {result['iterations_completed']}")
            
            # Show room allocation report
            room_report = result.get('room_allocation_report', {})
            print(f"\n🏛️ Room Allocation Report:")
            for key, value in room_report.items():
                if key != 'room_usage':
                    print(f"   • {key}: {value}")
        else:
            print(f"   • Error: {result.get('error', 'Unknown error')}")
        
        return result['success']
    except Exception as e:
        print(f"❌ Error in enhanced scheduler test: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 ENHANCED TIMETABLE SYSTEM TESTING")
    print("=" * 60)
    
    tests = [
        ("Enhanced Room Allocation", test_enhanced_room_allocation),
        ("Enhanced Constraint Resolution", test_enhanced_constraint_resolution),
        ("Enhanced Scheduler", test_enhanced_scheduler),
        ("Room Allocation Validation", test_room_allocation_validation),
        ("Practical Session Management", test_practical_session_management),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 