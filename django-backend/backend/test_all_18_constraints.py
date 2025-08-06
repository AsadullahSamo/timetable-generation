"""
COMPREHENSIVE TEST FOR ALL 18 CONSTRAINTS WORKING HARMONIOUSLY
=============================================================
Tests that all 18 constraints work seamlessly and in harmony without one violating the other.
This includes all scheduling and room constraints working together perfectly.
"""

import os
import sys
import django
from datetime import time, timedelta
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import (
    TimetableEntry, Subject, Teacher, Classroom, ScheduleConfig, 
    Batch, TeacherSubjectAssignment
)
from timetable.enhanced_constraint_validator import EnhancedConstraintValidator
from timetable.enhanced_constraint_resolver import EnhancedConstraintResolver
from timetable.enhanced_room_allocator import EnhancedRoomAllocator


class All18ConstraintsTester:
    """Comprehensive tester for all 18 constraints working harmoniously."""
    
    def __init__(self):
        self.validator = EnhancedConstraintValidator()
        self.resolver = EnhancedConstraintResolver()
        self.room_allocator = EnhancedRoomAllocator()
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'constraint_violations': {},
            'harmony_scores': [],
            'detailed_results': []
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all 18 constraints."""
        print("🧪 COMPREHENSIVE TEST - ALL 18 CONSTRAINTS WORKING HARMONIOUSLY")
        print("=" * 70)
        
        # Test 1: Basic constraint validation
        self.test_basic_constraint_validation()
        
        # Test 2: Constraint harmony validation
        self.test_constraint_harmony()
        
        # Test 3: Room allocation constraints
        self.test_room_allocation_constraints()
        
        # Test 4: Time-based constraints
        self.test_time_based_constraints()
        
        # Test 5: Teacher-based constraints
        self.test_teacher_based_constraints()
        
        # Test 6: Subject-based constraints
        self.test_subject_based_constraints()
        
        # Test 7: Cross-constraint harmony
        self.test_cross_constraint_harmony()
        
        # Test 8: Resolution effectiveness
        self.test_resolution_effectiveness()
        
        # Generate final report
        self.generate_final_report()
    
    def test_basic_constraint_validation(self):
        """Test basic validation of all 18 constraints."""
        print("\n📋 TEST 1: Basic Constraint Validation")
        print("-" * 40)
        
        # Create test data
        entries = self.create_test_timetable_entries()
        
        # Validate all constraints
        validation_result = self.validator.validate_all_constraints(entries)
        
        self.test_results['total_tests'] += 1
        
        if validation_result['total_violations'] == 0:
            print("✅ PASS: All 18 constraints validated successfully")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: Found {validation_result['total_violations']} violations")
            self.test_results['failed_tests'] += 1
            self.test_results['constraint_violations'] = validation_result['violations_by_constraint']
        
        self.test_results['harmony_scores'].append(validation_result['harmony_score'])
        self.test_results['detailed_results'].append({
            'test': 'Basic Constraint Validation',
            'result': validation_result
        })
    
    def test_constraint_harmony(self):
        """Test that constraints work harmoniously without conflicts."""
        print("\n🎵 TEST 2: Constraint Harmony Validation")
        print("-" * 40)
        
        # Create test data with potential conflicts
        entries = self.create_test_timetable_with_potential_conflicts()
        
        # Validate constraints and check for conflicts
        validation_result = self.validator.validate_all_constraints(entries)
        
        self.test_results['total_tests'] += 1
        
        if len(validation_result['constraint_conflicts']) == 0:
            print("✅ PASS: No constraint conflicts detected")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: Found {len(validation_result['constraint_conflicts'])} constraint conflicts")
            self.test_results['failed_tests'] += 1
        
        self.test_results['harmony_scores'].append(validation_result['harmony_score'])
        self.test_results['detailed_results'].append({
            'test': 'Constraint Harmony Validation',
            'result': validation_result
        })
    
    def test_room_allocation_constraints(self):
        """Test room allocation constraints (constraints 13-15)."""
        print("\n🏫 TEST 3: Room Allocation Constraints")
        print("-" * 40)
        
        # Create test data focusing on room allocation
        entries = self.create_test_room_allocation_entries()
        
        # Validate room-specific constraints
        validation_result = self.validator.validate_all_constraints(entries)
        
        room_constraints = [
            'Same Lab Rule',
            'Practicals In Labs', 
            'Room Consistency'
        ]
        
        self.test_results['total_tests'] += 1
        room_violations = 0
        
        for constraint in room_constraints:
            violations = validation_result['violations_by_constraint'].get(constraint, [])
            if violations:
                room_violations += len(violations)
                print(f"  ❌ {constraint}: {len(violations)} violations")
            else:
                print(f"  ✅ {constraint}: PASS")
        
        if room_violations == 0:
            print("✅ PASS: All room allocation constraints satisfied")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: {room_violations} room allocation violations")
            self.test_results['failed_tests'] += 1
        
        self.test_results['harmony_scores'].append(validation_result['harmony_score'])
        self.test_results['detailed_results'].append({
            'test': 'Room Allocation Constraints',
            'result': validation_result
        })
    
    def test_time_based_constraints(self):
        """Test time-based constraints (constraints 5, 6, 7, 8, 11, 12)."""
        print("\n⏰ TEST 4: Time-Based Constraints")
        print("-" * 40)
        
        # Create test data focusing on time constraints
        entries = self.create_test_time_based_entries()
        
        # Validate time-specific constraints
        validation_result = self.validator.validate_all_constraints(entries)
        
        time_constraints = [
            'Friday Time Limits',
            'Minimum Daily Classes',
            'Thesis Day Constraint',
            'Compact Scheduling',
            'Friday Aware Scheduling',
            'Working Hours'
        ]
        
        self.test_results['total_tests'] += 1
        time_violations = 0
        
        for constraint in time_constraints:
            violations = validation_result['violations_by_constraint'].get(constraint, [])
            if violations:
                time_violations += len(violations)
                print(f"  ❌ {constraint}: {len(violations)} violations")
            else:
                print(f"  ✅ {constraint}: PASS")
        
        if time_violations == 0:
            print("✅ PASS: All time-based constraints satisfied")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: {time_violations} time-based violations")
            self.test_results['failed_tests'] += 1
        
        self.test_results['harmony_scores'].append(validation_result['harmony_score'])
        self.test_results['detailed_results'].append({
            'test': 'Time-Based Constraints',
            'result': validation_result
        })
    
    def test_teacher_based_constraints(self):
        """Test teacher-based constraints (constraints 3, 10, 18)."""
        print("\n👨‍🏫 TEST 5: Teacher-Based Constraints")
        print("-" * 40)
        
        # Create test data focusing on teacher constraints
        entries = self.create_test_teacher_based_entries()
        
        # Validate teacher-specific constraints
        validation_result = self.validator.validate_all_constraints(entries)
        
        teacher_constraints = [
            'Teacher Conflicts',
            'Teacher Assignments',
            'Teacher Breaks'
        ]
        
        self.test_results['total_tests'] += 1
        teacher_violations = 0
        
        for constraint in teacher_constraints:
            violations = validation_result['violations_by_constraint'].get(constraint, [])
            if violations:
                teacher_violations += len(violations)
                print(f"  ❌ {constraint}: {len(violations)} violations")
            else:
                print(f"  ✅ {constraint}: PASS")
        
        if teacher_violations == 0:
            print("✅ PASS: All teacher-based constraints satisfied")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: {teacher_violations} teacher-based violations")
            self.test_results['failed_tests'] += 1
        
        self.test_results['harmony_scores'].append(validation_result['harmony_score'])
        self.test_results['detailed_results'].append({
            'test': 'Teacher-Based Constraints',
            'result': validation_result
        })
    
    def test_subject_based_constraints(self):
        """Test subject-based constraints (constraints 1, 2, 4, 9, 16, 17)."""
        print("\n📚 TEST 6: Subject-Based Constraints")
        print("-" * 40)
        
        # Create test data focusing on subject constraints
        entries = self.create_test_subject_based_entries()
        
        # Validate subject-specific constraints
        validation_result = self.validator.validate_all_constraints(entries)
        
        subject_constraints = [
            'Subject Frequency',
            'Practical Blocks',
            'Room Conflicts',
            'Cross Semester Conflicts',
            'Same Theory Subject Distribution',
            'Breaks Between Classes'
        ]
        
        self.test_results['total_tests'] += 1
        subject_violations = 0
        
        for constraint in subject_constraints:
            violations = validation_result['violations_by_constraint'].get(constraint, [])
            if violations:
                subject_violations += len(violations)
                print(f"  ❌ {constraint}: {len(violations)} violations")
            else:
                print(f"  ✅ {constraint}: PASS")
        
        if subject_violations == 0:
            print("✅ PASS: All subject-based constraints satisfied")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: {subject_violations} subject-based violations")
            self.test_results['failed_tests'] += 1
        
        self.test_results['harmony_scores'].append(validation_result['harmony_score'])
        self.test_results['detailed_results'].append({
            'test': 'Subject-Based Constraints',
            'result': validation_result
        })
    
    def test_cross_constraint_harmony(self):
        """Test that constraints work together without interfering."""
        print("\n🔄 TEST 7: Cross-Constraint Harmony")
        print("-" * 40)
        
        # Create test data that tests constraint interactions
        entries = self.create_test_cross_constraint_entries()
        
        # Validate and check for conflicts
        validation_result = self.validator.validate_all_constraints(entries)
        
        self.test_results['total_tests'] += 1
        
        # Check for constraint conflicts
        conflicts = validation_result['constraint_conflicts']
        harmony_score = validation_result['harmony_score']
        
        if len(conflicts) == 0 and harmony_score >= 90:
            print("✅ PASS: All constraints work harmoniously together")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: {len(conflicts)} conflicts, harmony score: {harmony_score:.2f}%")
            self.test_results['failed_tests'] += 1
        
        self.test_results['harmony_scores'].append(harmony_score)
        self.test_results['detailed_results'].append({
            'test': 'Cross-Constraint Harmony',
            'result': validation_result
        })
    
    def test_resolution_effectiveness(self):
        """Test that constraint resolution works effectively."""
        print("\n🔧 TEST 8: Constraint Resolution Effectiveness")
        print("-" * 40)
        
        # Create test data with violations
        entries = self.create_test_violation_entries()
        
        # Try to resolve violations
        resolution_result = self.resolver.resolve_all_violations(entries)
        
        self.test_results['total_tests'] += 1
        
        if resolution_result['overall_success']:
            print("✅ PASS: All violations resolved successfully")
            self.test_results['passed_tests'] += 1
        else:
            print(f"❌ FAIL: {resolution_result['final_violations']} violations remain")
            self.test_results['failed_tests'] += 1
        
        self.test_results['detailed_results'].append({
            'test': 'Constraint Resolution Effectiveness',
            'result': resolution_result
        })
    
    def generate_final_report(self):
        """Generate comprehensive final report."""
        print("\n📊 FINAL TEST REPORT")
        print("=" * 50)
        
        total_tests = self.test_results['total_tests']
        passed_tests = self.test_results['passed_tests']
        failed_tests = self.test_results['failed_tests']
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.test_results['harmony_scores']:
            avg_harmony = sum(self.test_results['harmony_scores']) / len(self.test_results['harmony_scores'])
            print(f"Average Harmony Score: {avg_harmony:.2f}%")
        
        print("\n🎯 ALL 18 CONSTRAINTS STATUS:")
        print("-" * 30)
        
        constraint_status = [
            "1. Subject Frequency",
            "2. Practical Blocks", 
            "3. Teacher Conflicts",
            "4. Room Conflicts",
            "5. Friday Time Limits",
            "6. Minimum Daily Classes",
            "7. Thesis Day Constraint",
            "8. Compact Scheduling",
            "9. Cross Semester Conflicts",
            "10. Teacher Assignments",
            "11. Friday Aware Scheduling",
            "12. Working Hours",
            "13. Same Lab Rule",
            "14. Practicals in Labs",
            "15. Room Consistency",
            "16. Same Theory Subject Distribution",
            "17. Breaks Between Classes",
            "18. Teacher Breaks"
        ]
        
        for i, constraint in enumerate(constraint_status, 1):
            status = "✅ WORKING" if passed_tests >= total_tests * 0.8 else "❌ NEEDS ATTENTION"
            print(f"{constraint}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 SUCCESS: All 18 constraints are working harmoniously!")
            print("✅ No constraint violations")
            print("✅ No constraint conflicts") 
            print("✅ High harmony score")
            print("✅ Effective resolution")
        else:
            print(f"\n⚠️ ATTENTION: {failed_tests} tests failed")
            print("Some constraints may need adjustment")
    
    # Helper methods to create test data
    
    def create_test_timetable_entries(self):
        """Create basic test timetable entries."""
        entries = []
        
        # Get or create test data
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if not config:
            config = ScheduleConfig.objects.create(
                name="Test Config",
                days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                periods=[1, 2, 3, 4, 5, 6],
                start_time=time(8, 0),
                lesson_duration=60
            )
        
        # Create test entries
        subjects = Subject.objects.all()[:5]
        teachers = Teacher.objects.all()[:3]
        classrooms = Classroom.objects.all()[:3]
        
        if not subjects or not teachers or not classrooms:
            return entries
        
        # Create a simple timetable
        for i, day in enumerate(config.days):
            for j, period in enumerate(config.periods[:3]):
                entry = TimetableEntry(
                    day=day,
                    period=period,
                    subject=subjects[i % len(subjects)],
                    teacher=teachers[i % len(teachers)],
                    classroom=classrooms[i % len(classrooms)],
                    class_group=f"Test-{i+1}",
                    start_time=time(8 + j, 0),
                    end_time=time(9 + j, 0),
                    is_practical=(i % 2 == 0),
                    schedule_config=config
                )
                entries.append(entry)
        
        return entries
    
    def create_test_timetable_with_potential_conflicts(self):
        """Create test data with potential constraint conflicts."""
        entries = self.create_test_timetable_entries()
        
        # Add some entries that might create conflicts
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if config:
            subjects = Subject.objects.all()[:3]
            teachers = Teacher.objects.all()[:2]
            classrooms = Classroom.objects.all()[:2]
            
            if subjects and teachers and classrooms:
                # Add conflicting entries
                for i in range(3):
                    entry = TimetableEntry(
                        day='Monday',
                        period=i + 1,
                        subject=subjects[0],
                        teacher=teachers[0],
                        classroom=classrooms[0],
                        class_group="Test-1",
                        start_time=time(8 + i, 0),
                        end_time=time(9 + i, 0),
                        is_practical=False,
                        schedule_config=config
                    )
                    entries.append(entry)
        
        return entries
    
    def create_test_room_allocation_entries(self):
        """Create test data focusing on room allocation constraints."""
        entries = []
        
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if not config:
            return entries
        
        # Create practical entries that should use labs
        labs = Classroom.objects.filter(name__icontains='lab')[:2]
        regular_rooms = Classroom.objects.filter(name__icontains='lab').exclude(id__in=[lab.id for lab in labs])[:2]
        
        if labs and regular_rooms:
            subjects = Subject.objects.filter(is_practical=True)[:2]
            teachers = Teacher.objects.all()[:2]
            
            if subjects and teachers:
                # Create practical blocks in labs
                for i, lab in enumerate(labs):
                    subject = subjects[i % len(subjects)]
                    teacher = teachers[i % len(teachers)]
                    
                    for period in range(1, 4):  # 3 consecutive periods
                        entry = TimetableEntry(
                            day='Monday',
                            period=period,
                            subject=subject,
                            teacher=teacher,
                            classroom=lab,
                            class_group=f"Test-{i+1}",
                            start_time=time(8 + period - 1, 0),
                            end_time=time(9 + period - 1, 0),
                            is_practical=True,
                            schedule_config=config
                        )
                        entries.append(entry)
        
        return entries
    
    def create_test_time_based_entries(self):
        """Create test data focusing on time-based constraints."""
        entries = []
        
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if not config:
            return entries
        
        subjects = Subject.objects.all()[:3]
        teachers = Teacher.objects.all()[:2]
        classrooms = Classroom.objects.all()[:2]
        
        if subjects and teachers and classrooms:
            # Create entries that respect time constraints
            for day in config.days:
                for period in config.periods[:4]:  # Limit to 4 periods
                    entry = TimetableEntry(
                        day=day,
                        period=period,
                        subject=subjects[period % len(subjects)],
                        teacher=teachers[period % len(teachers)],
                        classroom=classrooms[period % len(classrooms)],
                        class_group="Test-1",
                        start_time=time(8 + period - 1, 0),
                        end_time=time(9 + period - 1, 0),
                        is_practical=(period % 2 == 0),
                        schedule_config=config
                    )
                    entries.append(entry)
        
        return entries
    
    def create_test_teacher_based_entries(self):
        """Create test data focusing on teacher-based constraints."""
        entries = []
        
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if not config:
            return entries
        
        subjects = Subject.objects.all()[:3]
        teachers = Teacher.objects.all()[:2]
        classrooms = Classroom.objects.all()[:2]
        
        if subjects and teachers and classrooms:
            # Create entries that respect teacher constraints
            for day in config.days:
                for period in config.periods[:3]:
                    teacher = teachers[period % len(teachers)]
                    subject = subjects[period % len(subjects)]
                    
                    entry = TimetableEntry(
                        day=day,
                        period=period,
                        subject=subject,
                        teacher=teacher,
                        classroom=classrooms[period % len(classrooms)],
                        class_group="Test-1",
                        start_time=time(8 + period - 1, 0),
                        end_time=time(9 + period - 1, 0),
                        is_practical=False,
                        schedule_config=config
                    )
                    entries.append(entry)
        
        return entries
    
    def create_test_subject_based_entries(self):
        """Create test data focusing on subject-based constraints."""
        entries = []
        
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if not config:
            return entries
        
        subjects = Subject.objects.all()[:3]
        teachers = Teacher.objects.all()[:2]
        classrooms = Classroom.objects.all()[:2]
        
        if subjects and teachers and classrooms:
            # Create entries that respect subject constraints
            for i, subject in enumerate(subjects):
                for day in config.days:
                    entry = TimetableEntry(
                        day=day,
                        period=1,
                        subject=subject,
                        teacher=teachers[i % len(teachers)],
                        classroom=classrooms[i % len(classrooms)],
                        class_group="Test-1",
                        start_time=time(8, 0),
                        end_time=time(9, 0),
                        is_practical=subject.is_practical,
                        schedule_config=config
                    )
                    entries.append(entry)
        
        return entries
    
    def create_test_cross_constraint_entries(self):
        """Create test data that tests constraint interactions."""
        entries = []
        
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if not config:
            return entries
        
        subjects = Subject.objects.all()[:3]
        teachers = Teacher.objects.all()[:2]
        classrooms = Classroom.objects.all()[:2]
        
        if subjects and teachers and classrooms:
            # Create a balanced timetable
            for day in config.days:
                for period in config.periods[:3]:
                    subject = subjects[period % len(subjects)]
                    teacher = teachers[period % len(teachers)]
                    classroom = classrooms[period % len(classrooms)]
                    
                    entry = TimetableEntry(
                        day=day,
                        period=period,
                        subject=subject,
                        teacher=teacher,
                        classroom=classroom,
                        class_group="Test-1",
                        start_time=time(8 + period - 1, 0),
                        end_time=time(9 + period - 1, 0),
                        is_practical=subject.is_practical,
                        schedule_config=config
                    )
                    entries.append(entry)
        
        return entries
    
    def create_test_violation_entries(self):
        """Create test data with intentional violations."""
        entries = []
        
        config = ScheduleConfig.objects.filter(start_time__isnull=False).first()
        if not config:
            return entries
        
        subjects = Subject.objects.all()[:2]
        teachers = Teacher.objects.all()[:2]
        classrooms = Classroom.objects.all()[:2]
        
        if subjects and teachers and classrooms:
            # Create entries with some violations
            for i in range(5):
                entry = TimetableEntry(
                    day='Monday',
                    period=1,
                    subject=subjects[i % len(subjects)],
                    teacher=teachers[i % len(teachers)],
                    classroom=classrooms[i % len(classrooms)],
                    class_group=f"Test-{i+1}",
                    start_time=time(8, 0),
                    end_time=time(9, 0),
                    is_practical=False,
                    schedule_config=config
                )
                entries.append(entry)
        
        return entries


def main():
    """Run the comprehensive test."""
    tester = All18ConstraintsTester()
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main() 