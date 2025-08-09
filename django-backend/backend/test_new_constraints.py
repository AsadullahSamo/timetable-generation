#!/usr/bin/env python3
"""
Test script to verify the 3 new constraints are working.
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

def test_new_constraints():
    """Test that the 3 new constraints are working."""
    print("🧪 Testing 3 New Constraints")
    print("=" * 50)
    
    # Initialize enhanced validator
    validator = EnhancedConstraintValidator()
    
    # Get some test entries
    entries = list(TimetableEntry.objects.all()[:50])
    
    if not entries:
        print("❌ No timetable entries found. Please generate a timetable first.")
        return False
    
    print(f"📊 Testing with {len(entries)} timetable entries")
    
    # Test validation with enhanced validator
    validation_result = validator.validate_all_constraints(entries)
    
    print(f"\n📋 Validation Results:")
    print(f"   • Total violations: {validation_result['total_violations']}")
    print(f"   • Overall compliance: {validation_result['overall_compliance']}")
    
    # Check specifically for the 3 new constraints
    new_constraints = [
        'Same Theory Subject Distribution',
        'Breaks Between Classes', 
        'Teacher Breaks'
    ]
    
    print(f"\n🆕 NEW CONSTRAINTS CHECK:")
    for constraint in new_constraints:
        violations = validation_result['violations_by_constraint'].get(constraint, [])
        status = "✅ PASS" if len(violations) == 0 else f"❌ FAIL ({len(violations)} violations)"
        print(f"   • {constraint}: {status}")
        
        if violations:
            print(f"      - Violations found:")
            for violation in violations[:3]:  # Show first 3 violations
                print(f"        * {violation.get('description', 'Unknown violation')}")
    
    # Test constraint resolution
    print(f"\n🔧 Testing Enhanced Constraint Resolution...")
    resolver = EnhancedConstraintResolver()
    resolution_result = resolver.resolve_all_violations(entries)
    
    print(f"\n📊 Resolution Results:")
    print(f"   • Initial violations: {resolution_result['initial_violations']}")
    print(f"   • Final violations: {resolution_result['final_violations']}")
    print(f"   • Iterations completed: {resolution_result['iterations_completed']}")
    print(f"   • Overall success: {resolution_result['overall_success']}")
    
    return resolution_result['overall_success']

def main():
    """Run the test."""
    print("🚀 TESTING 3 NEW CONSTRAINTS")
    print("=" * 50)
    
    success = test_new_constraints()
    
    print(f"\n{'='*50}")
    if success:
        print("✅ All 3 new constraints are working correctly!")
    else:
        print("❌ Some issues with the 3 new constraints.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 