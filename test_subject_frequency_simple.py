#!/usr/bin/env python3
"""
Simple test for Subject Frequency constraint.
"""

import sys
import os
sys.path.append('django-backend/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from timetable.views import ConstraintTestingView
from timetable.models import TimetableEntry

def test_subject_frequency():
    print("🧪 Testing Subject Frequency Constraint")
    print("=" * 50)
    
    entries = TimetableEntry.objects.all()
    print(f"📊 Found {entries.count()} timetable entries")
    
    if not entries.exists():
        print("❌ No timetable entries found")
        return False
    
    view = ConstraintTestingView()
    analysis = view._analyze_subject_frequency(entries)
    
    print(f"📈 Analysis Results:")
    print(f"  Total violations: {analysis['total_violations']}")
    print(f"  Status: {analysis['status']}")
    
    if analysis['violations']:
        print(f"❌ Found violations:")
        for i, violation in enumerate(analysis['violations'][:3]):
            print(f"  {i+1}. {violation.get('subject_code', 'Unknown')} in {violation.get('class_group', 'Unknown')}")
            print(f"     Expected: {violation.get('expected_count', 'N/A')}, Actual: {violation.get('actual_count', 'N/A')}")
        return True  # Has violations to resolve
    else:
        print("✅ No violations found!")
        return False  # No violations

if __name__ == "__main__":
    has_violations = test_subject_frequency()
    print(f"\n{'✅' if has_violations else '❌'} Test completed - {'Has violations to resolve' if has_violations else 'No violations found'}")
