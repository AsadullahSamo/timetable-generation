#!/usr/bin/env python3
"""
Test the constraint validation system.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('backend')
django.setup()

from timetable.models import TimetableEntry
from timetable.constraint_validator import ConstraintValidator

def test_constraint_validation():
    """Test the constraint validation system."""
    print("🧪 Testing Constraint Validation System")
    print("=" * 50)
    
    # Get all timetable entries
    entries = TimetableEntry.objects.all()
    print(f"📊 Found {entries.count()} timetable entries")
    
    if not entries.exists():
        print("❌ No timetable entries found. Please generate a timetable first.")
        return
    
    # Initialize constraint validator
    validator = ConstraintValidator()
    
    # Run comprehensive validation
    print("\n🔍 Running comprehensive constraint validation...")
    results = validator.validate_all_constraints(list(entries))
    
    # Display results
    print(f"\n📈 VALIDATION RESULTS")
    print(f"Total violations: {results['total_violations']}")
    print(f"Overall compliance: {results['overall_compliance']}")
    
    print(f"\n📋 CONSTRAINT BREAKDOWN:")
    for constraint_name, result in results['constraint_results'].items():
        status = result['status']
        violations = result['violations']
        status_icon = "✅" if status == 'PASS' else "❌"
        print(f"  {status_icon} {constraint_name}: {status} ({violations} violations)")
    
    # Show some violation details
    if results['total_violations'] > 0:
        print(f"\n🔍 VIOLATION DETAILS (first 5):")
        violation_count = 0
        for constraint_name, violations in results['violations_by_constraint'].items():
            if violations and violation_count < 5:
                print(f"\n  {constraint_name}:")
                for violation in violations[:2]:  # Show first 2 violations per constraint
                    print(f"    - {violation.get('description', str(violation))}")
                    violation_count += 1
                    if violation_count >= 5:
                        break
    
    print(f"\n✅ Constraint validation test completed!")
    return results

if __name__ == "__main__":
    test_constraint_validation()
