#!/usr/bin/env python3
"""
Test script to verify the constraint resolution fix.
This script tests the infinite loop issue with practical blocks.
"""

import os
import sys
import django

# Add the Django backend to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, Subject, Teacher, Classroom
from timetable.constraint_validator import ConstraintValidator
from timetable.constraint_resolver import IntelligentConstraintResolver

def test_practical_constraint_resolution():
    """Test that practical block constraints don't cause infinite loops."""
    print("🧪 Testing Practical Block Constraint Resolution")
    print("=" * 60)
    
    # Get some test data
    entries = list(TimetableEntry.objects.all()[:50])  # Get first 50 entries
    
    if not entries:
        print("❌ No timetable entries found. Please generate a timetable first.")
        return False
    
    print(f"📊 Testing with {len(entries)} timetable entries")
    
    # Run initial validation
    validator = ConstraintValidator()
    initial_result = validator.validate_all_constraints(entries)
    
    print(f"🔍 Initial violations: {initial_result['total_violations']}")
    
    if initial_result['total_violations'] == 0:
        print("✅ No violations found - timetable is already compliant!")
        return True
    
    # Show violation breakdown
    print("\n📋 Violation Breakdown:")
    for constraint, violations in initial_result['violations_by_constraint'].items():
        if violations:
            print(f"  • {constraint}: {len(violations)} violations")
    
    # Test the constraint resolver
    print(f"\n🔧 Testing Intelligent Constraint Resolution...")
    resolver = IntelligentConstraintResolver()
    resolver.max_iterations = 5  # Limit iterations for testing
    
    try:
        resolution_result = resolver.resolve_all_violations(entries)
        
        print(f"\n📊 Resolution Results:")
        print(f"  • Initial violations: {resolution_result.get('initial_violations', 'N/A')}")
        print(f"  • Final violations: {resolution_result.get('final_violations', 'N/A')}")
        print(f"  • Iterations completed: {len(resolution_result.get('resolution_log', []))}")
        print(f"  • Overall success: {resolution_result.get('overall_success', False)}")
        
        # Check if we avoided infinite loops
        iterations = len(resolution_result.get('resolution_log', []))
        if iterations < resolver.max_iterations:
            print(f"✅ Resolution completed in {iterations} iterations (no infinite loop)")
            return True
        else:
            print(f"⚠️ Resolution hit max iterations ({resolver.max_iterations}) - may indicate issues")
            return False
            
    except Exception as e:
        print(f"❌ Error during resolution: {str(e)}")
        return False

def test_practical_session_counting():
    """Test the new practical session counting logic."""
    print("\n🧪 Testing Practical Session Counting Logic")
    print("=" * 60)
    
    validator = ConstraintValidator()
    
    # Get some practical entries
    practical_entries = list(TimetableEntry.objects.filter(is_practical=True)[:10])
    
    if not practical_entries:
        print("❌ No practical entries found.")
        return False
    
    print(f"📊 Testing with {len(practical_entries)} practical entries")
    
    # Test the frequency validation
    violations = validator._check_subject_frequency(practical_entries)
    
    print(f"🔍 Subject frequency violations: {len(violations)}")
    
    for violation in violations[:3]:  # Show first 3 violations
        print(f"  • {violation['description']}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Constraint Resolution Tests")
    print("=" * 60)
    
    success1 = test_practical_constraint_resolution()
    success2 = test_practical_session_counting()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed! Constraint resolution fix appears to be working.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    print("🏁 Test completed.")
