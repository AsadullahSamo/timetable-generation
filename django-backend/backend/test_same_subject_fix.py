#!/usr/bin/env python3
"""
Test script to verify the same theory subject distribution constraint fix.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, Subject, Teacher, Classroom, ScheduleConfig
from timetable.enhanced_constraint_validator import EnhancedConstraintValidator
from timetable.enhanced_constraint_resolver import EnhancedConstraintResolver

def test_same_subject_distribution():
    """Test that the same theory subject distribution constraint is working."""
    print("🧪 Testing Same Theory Subject Distribution Fix")
    print("=" * 60)
    
    # Initialize enhanced validator
    validator = EnhancedConstraintValidator()
    
    # Get timetable entries
    entries = list(TimetableEntry.objects.all())
    
    if not entries:
        print("❌ No timetable entries found. Please generate a timetable first.")
        return False
    
    print(f"📊 Testing with {len(entries)} timetable entries")
    
    # Test validation
    validation_result = validator.validate_all_constraints(entries)
    
    # Check specifically for same theory subject distribution violations
    same_subject_violations = validation_result['violations_by_constraint'].get('Same Theory Subject Distribution', [])
    
    print(f"\n📋 Same Theory Subject Distribution Results:")
    print(f"   • Total violations: {len(same_subject_violations)}")
    
    if len(same_subject_violations) == 0:
        print("   ✅ PASS: No same theory subject distribution violations!")
    else:
        print("   ❌ FAIL: Found same theory subject distribution violations:")
        for violation in same_subject_violations[:5]:  # Show first 5 violations
            print(f"      - {violation['description']}")
    
    # Test resolution if there are violations
    if same_subject_violations:
        print(f"\n🔧 Testing Enhanced Constraint Resolution...")
        resolver = EnhancedConstraintResolver()
        resolution_result = resolver.resolve_all_violations(entries)
        
        print(f"\n📊 Resolution Results:")
        print(f"   • Initial violations: {resolution_result['initial_violations']}")
        print(f"   • Final violations: {resolution_result['final_violations']}")
        print(f"   • Iterations completed: {resolution_result['iterations_completed']}")
        
        # Re-validate after resolution
        final_validation = validator.validate_all_constraints(resolution_result['entries'])
        final_same_subject_violations = final_validation['violations_by_constraint'].get('Same Theory Subject Distribution', [])
        
        print(f"\n📋 Final Same Theory Subject Distribution Results:")
        print(f"   • Final violations: {len(final_same_subject_violations)}")
        
        if len(final_same_subject_violations) == 0:
            print("   ✅ PASS: All same theory subject distribution violations resolved!")
        else:
            print("   ❌ FAIL: Some violations remain:")
            for violation in final_same_subject_violations[:3]:
                print(f"      - {violation['description']}")
    
    return len(same_subject_violations) == 0

def main():
    """Run the test."""
    print("🚀 TESTING SAME THEORY SUBJECT DISTRIBUTION FIX")
    print("=" * 60)
    
    success = test_same_subject_distribution()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ Same theory subject distribution constraint is working correctly!")
    else:
        print("❌ Same theory subject distribution constraint still has issues.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 