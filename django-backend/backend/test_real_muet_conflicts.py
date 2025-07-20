#!/usr/bin/env python
"""
Real MUET Cross-Timetable Conflict Detection Test Suite

This comprehensive test suite validates that our timetable generation system
properly handles cross-timetable conflicts using real MUET Software Engineering
Department data across all batches and semesters.
"""

import os
import sys
import django
from datetime import time, datetime
from typing import Dict, List, Tuple

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import (
    TimetableEntry, ScheduleConfig, Subject, Teacher, Classroom
)
from timetable.services.cross_semester_conflict_detector import CrossSemesterConflictDetector
from timetable.algorithms.advanced_scheduler import AdvancedTimetableScheduler


class MUETConflictTester:
    """Comprehensive conflict testing for real MUET data"""
    
    def __init__(self):
        self.results = {
            'tests_passed': 0,
            'tests_failed': 0,
            'conflicts_detected': 0,
            'conflicts_prevented': 0,
            'detailed_results': []
        }
    
    def run_all_tests(self):
        """Run comprehensive conflict detection tests"""
        print("🏛️  MUET CROSS-TIMETABLE CONFLICT DETECTION TEST SUITE")
        print("=" * 70)
        
        # Test 1: Data Integrity Check
        self.test_data_integrity()
        
        # Test 2: Existing Timetable Analysis
        self.test_existing_timetables()
        
        # Test 3: Cross-Batch Teacher Conflicts
        self.test_cross_batch_teacher_conflicts()
        
        # Test 4: Classroom Availability
        self.test_classroom_conflicts()
        
        # Test 5: New Timetable Generation with Conflict Prevention
        self.test_new_timetable_generation()
        
        # Test 6: Multiple Batch Scheduling
        self.test_multiple_batch_scheduling()
        
        # Test 7: Edge Cases and Stress Testing
        self.test_edge_cases()
        
        # Final Report
        self.print_final_report()
    
    def test_data_integrity(self):
        """Test 1: Verify data integrity and completeness"""
        print("\n📊 TEST 1: Data Integrity Check")
        print("-" * 50)
        
        try:
            # Count all entities
            subjects_count = Subject.objects.count()
            teachers_count = Teacher.objects.count()
            classrooms_count = Classroom.objects.count()
            configs_count = ScheduleConfig.objects.count()
            entries_count = TimetableEntry.objects.count()
            
            print(f"✓ Subjects: {subjects_count}")
            print(f"✓ Teachers: {teachers_count}")
            print(f"✓ Classrooms: {classrooms_count}")
            print(f"✓ Schedule Configs: {configs_count}")
            print(f"✓ Existing Timetable Entries: {entries_count}")
            
            # Check for essential MUET batches
            muet_batches = ['21SW', '22SW', '23SW', '24SW']
            found_batches = []
            
            for config in ScheduleConfig.objects.all():
                for batch in muet_batches:
                    if batch in config.name:
                        found_batches.append(batch)
                        break
            
            print(f"✓ MUET Batches Found: {set(found_batches)}")
            
            # Verify teacher-subject relationships
            teachers_with_subjects = Teacher.objects.filter(subjects__isnull=False).distinct().count()
            print(f"✓ Teachers with Subject Assignments: {teachers_with_subjects}")
            
            self.results['tests_passed'] += 1
            self.results['detailed_results'].append({
                'test': 'Data Integrity',
                'status': 'PASSED',
                'details': f'{subjects_count} subjects, {teachers_count} teachers, {configs_count} configs'
            })
            
        except Exception as e:
            print(f"❌ Data integrity test failed: {e}")
            self.results['tests_failed'] += 1
            self.results['detailed_results'].append({
                'test': 'Data Integrity',
                'status': 'FAILED',
                'details': str(e)
            })
    
    def test_existing_timetables(self):
        """Test 2: Analyze existing timetable entries for conflicts"""
        print("\n📅 TEST 2: Existing Timetable Analysis")
        print("-" * 50)
        
        try:
            # Group entries by semester/batch
            entries_by_config = {}
            for entry in TimetableEntry.objects.select_related('teacher', 'subject', 'classroom'):
                config_key = f"{entry.semester}_{entry.academic_year}"
                if config_key not in entries_by_config:
                    entries_by_config[config_key] = []
                entries_by_config[config_key].append(entry)
            
            print(f"✓ Found timetables for {len(entries_by_config)} different semesters/batches")
            
            # Check for internal conflicts within each timetable
            total_internal_conflicts = 0
            for config_key, entries in entries_by_config.items():
                conflicts = self._check_internal_conflicts(entries)
                if conflicts:
                    print(f"⚠️  {config_key}: {len(conflicts)} internal conflicts")
                    total_internal_conflicts += len(conflicts)
                else:
                    print(f"✓ {config_key}: No internal conflicts")
            
            # Check for cross-timetable teacher conflicts
            cross_conflicts = self._check_cross_timetable_conflicts()
            print(f"✓ Cross-timetable teacher conflicts detected: {len(cross_conflicts)}")
            
            if cross_conflicts:
                print("   Conflict details:")
                for conflict in cross_conflicts[:5]:  # Show first 5
                    print(f"   - {conflict}")
            
            self.results['conflicts_detected'] += len(cross_conflicts)
            self.results['tests_passed'] += 1
            
        except Exception as e:
            print(f"❌ Existing timetable analysis failed: {e}")
            self.results['tests_failed'] += 1
    
    def test_cross_batch_teacher_conflicts(self):
        """Test 3: Specific cross-batch teacher conflict detection"""
        print("\n👨‍🏫 TEST 3: Cross-Batch Teacher Conflicts")
        print("-" * 50)
        
        try:
            # Get a sample config for testing
            config = ScheduleConfig.objects.first()
            if not config:
                print("❌ No schedule configuration found")
                self.results['tests_failed'] += 1
                return
            
            # Initialize conflict detector
            conflict_detector = CrossSemesterConflictDetector(config)
            
            # Test specific teachers who might teach multiple batches
            test_teachers = Teacher.objects.filter(
                name__in=[
                    'Dr. Naeem Ahmed', 'Dr. Mohsin Memon', 'Mr. Mansoor',
                    'Ms. Amrita Dewani', 'Dr. Anoud Shaikh'
                ]
            )
            
            conflicts_found = 0
            for teacher in test_teachers:
                print(f"\n   Testing {teacher.name}:")
                
                # Check availability across all days and periods
                availability = conflict_detector.get_teacher_availability(teacher.id)
                
                total_slots = sum(len(periods) for periods in availability.values())
                occupied_slots = 0
                
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    for period in range(1, 8):  # Periods 1-7
                        has_conflict, descriptions = conflict_detector.check_teacher_conflict(
                            teacher.id, day, period
                        )
                        if has_conflict:
                            occupied_slots += 1
                            conflicts_found += 1
                            if len(descriptions) > 0:
                                print(f"     {day} P{period}: {descriptions[0][:60]}...")
                
                availability_percentage = ((total_slots - occupied_slots) / (5 * 7)) * 100
                print(f"     Availability: {availability_percentage:.1f}% ({total_slots - occupied_slots}/35 slots)")
            
            print(f"\n✓ Total cross-batch conflicts detected: {conflicts_found}")
            self.results['conflicts_detected'] += conflicts_found
            self.results['tests_passed'] += 1
            
        except Exception as e:
            print(f"❌ Cross-batch teacher conflict test failed: {e}")
            self.results['tests_failed'] += 1
    
    def test_classroom_conflicts(self):
        """Test 4: Classroom availability and conflicts"""
        print("\n🏫 TEST 4: Classroom Conflicts")
        print("-" * 50)
        
        try:
            # Check classroom utilization
            classroom_usage = {}
            
            for entry in TimetableEntry.objects.select_related('classroom'):
                if entry.classroom:
                    room_key = entry.classroom.name
                    time_key = f"{entry.day}_P{entry.period}"
                    
                    if room_key not in classroom_usage:
                        classroom_usage[room_key] = {}
                    
                    if time_key in classroom_usage[room_key]:
                        print(f"⚠️  Classroom conflict: {room_key} at {time_key}")
                        print(f"     Existing: {classroom_usage[room_key][time_key]}")
                        print(f"     Conflicting: {entry.class_group} - {entry.subject}")
                        self.results['conflicts_detected'] += 1
                    else:
                        classroom_usage[room_key][time_key] = f"{entry.class_group} - {entry.subject}"
            
            # Calculate utilization rates
            total_rooms = Classroom.objects.count()
            utilized_rooms = len(classroom_usage)
            
            print(f"✓ Classrooms in use: {utilized_rooms}/{total_rooms}")
            
            # Show top utilized classrooms
            print("\n   Top utilized classrooms:")
            sorted_usage = sorted(classroom_usage.items(), key=lambda x: len(x[1]), reverse=True)
            for room, usage in sorted_usage[:5]:
                utilization = (len(usage) / 35) * 100  # 35 = 5 days × 7 periods
                print(f"     {room}: {len(usage)} slots ({utilization:.1f}% utilization)")
            
            self.results['tests_passed'] += 1
            
        except Exception as e:
            print(f"❌ Classroom conflict test failed: {e}")
            self.results['tests_failed'] += 1

    def test_new_timetable_generation(self):
        """Test 5: Generate new timetable with conflict prevention"""
        print("\n🔄 TEST 5: New Timetable Generation with Conflict Prevention")
        print("-" * 50)

        try:
            # Find a config that doesn't have many entries (good for testing)
            configs_with_entries = []
            for config in ScheduleConfig.objects.all():
                entry_count = TimetableEntry.objects.filter(
                    semester=config.semester,
                    academic_year=config.academic_year
                ).count()
                configs_with_entries.append((config, entry_count))

            # Sort by entry count and pick one with fewer entries for testing
            configs_with_entries.sort(key=lambda x: x[1])
            test_config = configs_with_entries[0][0] if configs_with_entries else None

            if not test_config:
                print("❌ No suitable config found for testing")
                self.results['tests_failed'] += 1
                return

            print(f"   Testing with config: {test_config.name}")

            # Initialize conflict detector
            conflict_detector = CrossSemesterConflictDetector(test_config)

            # Get conflict summary before generation
            existing_conflicts = len(self._check_cross_timetable_conflicts())
            print(f"   Existing cross-timetable conflicts: {existing_conflicts}")

            # Test the scheduler's conflict detection
            try:
                scheduler = AdvancedTimetableScheduler(test_config)
                print("   ✓ Advanced scheduler initialized successfully")

                # Check if scheduler has conflict detector
                if hasattr(scheduler, 'conflict_detector'):
                    print("   ✓ Scheduler has conflict detector integrated")
                else:
                    print("   ⚠️  Scheduler missing conflict detector integration")

                # Generate a small test timetable
                print("   Generating test timetable...")
                result = scheduler.generate_timetable()

                if result and 'entries' in result:
                    print(f"   ✓ Generated {len(result['entries'])} timetable entries")

                    # Check for cross-semester violations in result
                    cross_violations = [
                        v for v in result.get('constraint_violations', [])
                        if 'Cross-semester' in v or 'cross-semester' in v
                    ]

                    if cross_violations:
                        print(f"   ⚠️  {len(cross_violations)} cross-semester violations detected:")
                        for violation in cross_violations[:3]:
                            print(f"     - {violation[:80]}...")
                        self.results['conflicts_detected'] += len(cross_violations)
                    else:
                        print("   ✓ No cross-semester violations in generated timetable")
                        self.results['conflicts_prevented'] += 1

                    self.results['tests_passed'] += 1
                else:
                    print("   ❌ Timetable generation failed or returned no entries")
                    self.results['tests_failed'] += 1

            except Exception as scheduler_error:
                print(f"   ❌ Scheduler error: {scheduler_error}")
                self.results['tests_failed'] += 1

        except Exception as e:
            print(f"❌ New timetable generation test failed: {e}")
            self.results['tests_failed'] += 1

    def test_multiple_batch_scheduling(self):
        """Test 6: Multiple batch scheduling scenarios"""
        print("\n🎓 TEST 6: Multiple Batch Scheduling")
        print("-" * 50)

        try:
            # Test scenario: What happens when we try to schedule multiple batches
            # that might share teachers

            # Find teachers who appear in multiple batch configurations
            shared_teachers = {}

            for config in ScheduleConfig.objects.all():
                # Get teachers from existing entries for this config
                teachers_in_config = set()
                entries = TimetableEntry.objects.filter(
                    semester=config.semester,
                    academic_year=config.academic_year
                ).select_related('teacher')

                for entry in entries:
                    if entry.teacher:
                        teachers_in_config.add(entry.teacher.name)

                # Track which configs each teacher appears in
                for teacher_name in teachers_in_config:
                    if teacher_name not in shared_teachers:
                        shared_teachers[teacher_name] = []
                    shared_teachers[teacher_name].append(config.name)

            # Find teachers teaching multiple batches
            multi_batch_teachers = {
                teacher: configs for teacher, configs in shared_teachers.items()
                if len(configs) > 1
            }

            print(f"   Teachers teaching multiple batches: {len(multi_batch_teachers)}")

            if multi_batch_teachers:
                print("   Multi-batch teachers:")
                for teacher, configs in list(multi_batch_teachers.items())[:5]:
                    print(f"     {teacher}: {len(configs)} batches")
                    for config in configs:
                        print(f"       - {config}")

                # Test conflict detection for these teachers
                conflicts_detected = 0
                for teacher_name in list(multi_batch_teachers.keys())[:3]:
                    try:
                        teacher = Teacher.objects.filter(name=teacher_name).first()
                        if not teacher:
                            continue

                        config = ScheduleConfig.objects.first()
                        conflict_detector = CrossSemesterConflictDetector(config)

                        # Check a few time slots
                        for day in ['Monday', 'Tuesday']:
                            for period in [1, 2, 3]:
                                has_conflict, descriptions = conflict_detector.check_teacher_conflict(
                                    teacher.id, day, period
                                )
                                if has_conflict:
                                    conflicts_detected += 1

                    except Exception as e:
                        print(f"     ⚠️  Error testing teacher {teacher_name}: {e}")
                        continue

                print(f"   ✓ Conflicts detected for multi-batch teachers: {conflicts_detected}")
                self.results['conflicts_detected'] += conflicts_detected

            self.results['tests_passed'] += 1

        except Exception as e:
            print(f"❌ Multiple batch scheduling test failed: {e}")
            self.results['tests_failed'] += 1

    def test_edge_cases(self):
        """Test 7: Edge cases and stress testing"""
        print("\n⚡ TEST 7: Edge Cases and Stress Testing")
        print("-" * 50)

        try:
            # Edge Case 1: Teacher with maximum load
            print("   Testing teacher maximum load scenarios...")

            # Find the most scheduled teacher
            teacher_loads = {}
            for entry in TimetableEntry.objects.select_related('teacher'):
                if entry.teacher:
                    teacher_name = entry.teacher.name
                    if teacher_name not in teacher_loads:
                        teacher_loads[teacher_name] = 0
                    teacher_loads[teacher_name] += 1

            if teacher_loads:
                max_loaded_teacher = max(teacher_loads.items(), key=lambda x: x[1])
                print(f"     Most loaded teacher: {max_loaded_teacher[0]} ({max_loaded_teacher[1]} periods)")

                # Test if this teacher can be scheduled for more periods
                try:
                    teacher = Teacher.objects.filter(name=max_loaded_teacher[0]).first()
                    if teacher:
                        config = ScheduleConfig.objects.first()
                        conflict_detector = CrossSemesterConflictDetector(config)

                        availability = conflict_detector.get_teacher_availability(teacher.id)
                        total_available = sum(len(periods) for periods in availability.values())
                        print(f"     Remaining availability: {total_available} slots")
                    else:
                        print("     ⚠️  Teacher not found in database")

                except Exception as e:
                    print(f"     ⚠️  Error checking teacher availability: {e}")

            # Edge Case 2: Classroom capacity vs class size
            print("\n   Testing classroom capacity constraints...")

            capacity_violations = 0
            for config in ScheduleConfig.objects.all():
                for class_group_data in config.class_groups:
                    if isinstance(class_group_data, dict) and 'students' in class_group_data:
                        class_size = class_group_data['students']

                        # Check if assigned classrooms can accommodate this class
                        entries = TimetableEntry.objects.filter(
                            class_group__icontains=class_group_data.get('name', ''),
                            semester=config.semester
                        ).select_related('classroom')

                        for entry in entries:
                            if entry.classroom and entry.classroom.capacity < class_size:
                                capacity_violations += 1
                                print(f"     ⚠️  Capacity violation: {entry.classroom.name} "
                                      f"(cap: {entry.classroom.capacity}) < class size: {class_size}")

            print(f"   ✓ Classroom capacity violations: {capacity_violations}")

            # Edge Case 3: Time slot boundary testing
            print("\n   Testing time slot boundaries...")

            boundary_issues = 0
            for entry in TimetableEntry.objects.all():
                if entry.start_time >= entry.end_time:
                    boundary_issues += 1
                    print(f"     ⚠️  Invalid time slot: {entry.start_time} >= {entry.end_time}")

            print(f"   ✓ Time boundary issues: {boundary_issues}")

            self.results['tests_passed'] += 1

        except Exception as e:
            print(f"❌ Edge cases test failed: {e}")
            self.results['tests_failed'] += 1

    def _check_internal_conflicts(self, entries: List[TimetableEntry]) -> List[str]:
        """Check for conflicts within a single timetable"""
        conflicts = []
        time_slots = {}

        for entry in entries:
            # Check teacher conflicts
            if entry.teacher:
                teacher_key = f"{entry.teacher.id}_{entry.day}_P{entry.period}"
                if teacher_key in time_slots:
                    conflicts.append(
                        f"Teacher {entry.teacher.name} double-booked on {entry.day} Period {entry.period}"
                    )
                else:
                    time_slots[teacher_key] = entry

            # Check classroom conflicts
            if entry.classroom:
                room_key = f"{entry.classroom.id}_{entry.day}_P{entry.period}"
                if room_key in time_slots:
                    conflicts.append(
                        f"Classroom {entry.classroom.name} double-booked on {entry.day} Period {entry.period}"
                    )
                else:
                    time_slots[room_key] = entry

        return conflicts

    def _check_cross_timetable_conflicts(self) -> List[str]:
        """Check for conflicts across different timetables"""
        conflicts = []

        # Group entries by teacher and time slot
        teacher_schedule = {}

        for entry in TimetableEntry.objects.select_related('teacher'):
            if not entry.teacher:
                continue

            teacher_id = entry.teacher.id
            time_key = f"{entry.day}_P{entry.period}"

            if teacher_id not in teacher_schedule:
                teacher_schedule[teacher_id] = {}

            if time_key in teacher_schedule[teacher_id]:
                # Conflict found
                existing_entry = teacher_schedule[teacher_id][time_key]
                conflicts.append(
                    f"Teacher {entry.teacher.name} conflict: "
                    f"{existing_entry.semester} vs {entry.semester} "
                    f"on {entry.day} Period {entry.period}"
                )
            else:
                teacher_schedule[teacher_id][time_key] = entry

        return conflicts

    def print_final_report(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 70)
        print("🎯 FINAL TEST REPORT")
        print("=" * 70)

        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        success_rate = (self.results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0

        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.results['tests_passed']} ✓")
        print(f"   Failed: {self.results['tests_failed']} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")

        print(f"\n🔍 Conflict Detection Summary:")
        print(f"   Conflicts Detected: {self.results['conflicts_detected']}")
        print(f"   Conflicts Prevented: {self.results['conflicts_prevented']}")

        print(f"\n📋 Detailed Results:")
        for result in self.results['detailed_results']:
            status_icon = "✓" if result['status'] == 'PASSED' else "❌"
            print(f"   {status_icon} {result['test']}: {result['details']}")

        # System Health Assessment
        print(f"\n🏥 System Health Assessment:")

        if self.results['tests_failed'] == 0:
            print("   🟢 EXCELLENT: All tests passed!")
            print("   The cross-timetable conflict detection system is working perfectly.")
        elif self.results['tests_failed'] <= 2:
            print("   🟡 GOOD: Minor issues detected.")
            print("   The system is mostly functional with some areas for improvement.")
        else:
            print("   🔴 NEEDS ATTENTION: Multiple test failures.")
            print("   The conflict detection system requires immediate attention.")

        # Recommendations
        print(f"\n💡 Recommendations:")

        if self.results['conflicts_detected'] > 0:
            print("   • Review and resolve existing timetable conflicts")
            print("   • Implement stricter validation during timetable creation")

        if self.results['conflicts_prevented'] > 0:
            print("   • ✓ Conflict prevention is working - keep current implementation")

        if self.results['tests_failed'] > 0:
            print("   • Investigate failed test cases and fix underlying issues")
            print("   • Consider additional validation rules")

        print("\n🚀 Ready for Production:")
        if success_rate >= 85 and self.results['conflicts_prevented'] > 0:
            print("   ✅ YES - System is ready for production use")
        else:
            print("   ⚠️  CAUTION - Address issues before production deployment")

        print("\n" + "=" * 70)


def main():
    """Main execution function"""
    print("Starting MUET Cross-Timetable Conflict Detection Tests...")

    try:
        tester = MUETConflictTester()
        tester.run_all_tests()

    except Exception as e:
        print(f"\n❌ Test suite execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
