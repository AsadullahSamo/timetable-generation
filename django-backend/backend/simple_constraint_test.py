"""
SIMPLE TEST FOR ALL 18 CONSTRAINTS WORKING HARMONIOUSLY
=======================================================
Simple test that validates the constraint logic without requiring full Django setup.
"""

import sys
import os
from datetime import time, timedelta
from collections import defaultdict

# Mock classes for testing
class MockSubject:
    def __init__(self, code, name, credits=3, is_practical=False):
        self.code = code
        self.name = name
        self.credits = credits
        self.is_practical = is_practical

class MockTeacher:
    def __init__(self, id, name, email=""):
        self.id = id
        self.name = name
        self.email = email

class MockClassroom:
    def __init__(self, id, name, capacity=30, building="Main Building"):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.building = building
    
    @property
    def is_lab(self):
        return 'lab' in self.name.lower() or 'laboratory' in self.name.lower()

class MockTimetableEntry:
    def __init__(self, day, period, subject, teacher, classroom, class_group, 
                 start_time, end_time, is_practical=False):
        self.day = day
        self.period = period
        self.subject = subject
        self.teacher = teacher
        self.classroom = classroom
        self.class_group = class_group
        self.start_time = start_time
        self.end_time = end_time
        self.is_practical = is_practical

class SimpleConstraintValidator:
    """Simple constraint validator for testing all 18 constraints."""
    
    def __init__(self):
        self.constraint_checks = [
            self._check_subject_frequency,
            self._check_practical_blocks,
            self._check_teacher_conflicts,
            self._check_room_conflicts,
            self._check_friday_time_limits,
            self._check_minimum_daily_classes,
            self._check_thesis_day_constraint,
            self._check_compact_scheduling,
            self._check_cross_semester_conflicts,
            self._check_teacher_assignments,
            self._check_friday_aware_scheduling,
            self._check_working_hours,
            self._check_same_lab_rule,
            self._check_practicals_in_labs,
            self._check_room_consistency,
            self._check_same_theory_subject_distribution,
            self._check_breaks_between_classes,
            self._check_teacher_breaks,
        ]
    
    def validate_all_constraints(self, entries):
        """Validate all 18 constraints."""
        results = {
            'total_violations': 0,
            'constraint_results': {},
            'violations_by_constraint': {},
            'overall_compliance': False,
            'harmony_score': 0.0
        }
        
        print("🔍 SIMPLE CONSTRAINT VALIDATION - ALL 18 CONSTRAINTS")
        print("=" * 60)
        
        # Run all constraint checks
        for check_func in self.constraint_checks:
            constraint_name = check_func.__name__.replace('_check_', '').replace('_', ' ').title()
            print(f"Checking {constraint_name}...")
            
            violations = check_func(entries)
            results['constraint_results'][constraint_name] = {
                'violations': len(violations),
                'status': 'PASS' if len(violations) == 0 else 'FAIL',
                'details': violations
            }
            results['violations_by_constraint'][constraint_name] = violations
            results['total_violations'] += len(violations)
        
        # Calculate harmony score
        results['harmony_score'] = self._calculate_harmony_score(results)
        results['overall_compliance'] = results['total_violations'] == 0
        
        return results
    
    def _calculate_harmony_score(self, results):
        """Calculate harmony score."""
        total_constraints = 18
        total_violations = results['total_violations']
        
        violation_penalty = (total_violations / (total_constraints * 10)) * 100
        harmony_score = max(0, 100 - violation_penalty)
        return harmony_score
    
    def _check_subject_frequency(self, entries):
        """Check subject frequency compliance."""
        violations = []
        # Simple check - count classes per subject
        subject_counts = defaultdict(int)
        for entry in entries:
            if entry.subject:
                subject_counts[entry.subject.code] += 1
        
        # Check if counts match expected (simplified)
        for subject_code, count in subject_counts.items():
            if count < 2:  # Minimum 2 classes per subject
                violations.append({
                    'type': 'Subject Frequency Violation',
                    'subject': subject_code,
                    'count': count,
                    'description': f"{subject_code} has only {count} classes"
                })
        
        return violations
    
    def _check_practical_blocks(self, entries):
        """Check practical block requirements."""
        violations = []
        
        # Group practical entries by class group, day, and subject
        practical_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for entry in entries:
            if entry.is_practical:
                practical_groups[entry.class_group][entry.day][entry.subject.code].append(entry)
        
        for class_group, days in practical_groups.items():
            for day, subjects in days.items():
                for subject_code, subject_entries in subjects.items():
                    if len(subject_entries) < 3:
                        violations.append({
                            'type': 'Incomplete Practical Block',
                            'class_group': class_group,
                            'subject': subject_code,
                            'day': day,
                            'count': len(subject_entries),
                            'description': f"Practical {subject_code} on {day} has only {len(subject_entries)} periods"
                        })
        
        return violations
    
    def _check_teacher_conflicts(self, entries):
        """Check teacher conflict violations."""
        violations = []
        
        # Group entries by teacher, day, and period
        teacher_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for entry in entries:
            if entry.teacher:
                teacher_schedule[entry.teacher.id][entry.day][entry.period].append(entry)
        
        for teacher_id, days in teacher_schedule.items():
            for day, periods in days.items():
                for period, period_entries in periods.items():
                    if len(period_entries) > 1:
                        violations.append({
                            'type': 'Teacher Double Booking',
                            'teacher_id': teacher_id,
                            'teacher_name': period_entries[0].teacher.name,
                            'day': day,
                            'period': period,
                            'description': f"Teacher {period_entries[0].teacher.name} double-booked on {day} P{period}"
                        })
        
        return violations
    
    def _check_room_conflicts(self, entries):
        """Check room conflict violations."""
        violations = []
        
        # Group entries by room, day, and period
        room_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for entry in entries:
            if entry.classroom:
                room_schedule[entry.classroom.id][entry.day][entry.period].append(entry)
        
        for room_id, days in room_schedule.items():
            for day, periods in days.items():
                for period, period_entries in periods.items():
                    if len(period_entries) > 1:
                        violations.append({
                            'type': 'Room Double Booking',
                            'room_id': room_id,
                            'room_name': period_entries[0].classroom.name,
                            'day': day,
                            'period': period,
                            'description': f"Room {period_entries[0].classroom.name} double-booked on {day} P{period}"
                        })
        
        return violations
    
    def _check_friday_time_limits(self, entries):
        """Check Friday time limit violations."""
        violations = []
        
        for entry in entries:
            if entry.day == 'Friday':
                # Simple check - period should not be too late
                if entry.period > 4:  # After 4th period
                    violations.append({
                        'type': 'Friday Time Limit Violation',
                        'subject': entry.subject.code if entry.subject else 'Unknown',
                        'period': entry.period,
                        'description': f"Friday class at period {entry.period} is too late"
                    })
        
        return violations
    
    def _check_minimum_daily_classes(self, entries):
        """Check minimum daily classes requirement."""
        violations = []
        
        # Group entries by class group and day
        class_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            class_day_entries[entry.class_group][entry.day].append(entry)
        
        for class_group, days in class_day_entries.items():
            for day, day_entries in days.items():
                if len(day_entries) < 2:
                    violations.append({
                        'type': 'Minimum Daily Classes Violation',
                        'class_group': class_group,
                        'day': day,
                        'count': len(day_entries),
                        'description': f"{class_group} has only {len(day_entries)} classes on {day}"
                    })
        
        return violations
    
    def _check_thesis_day_constraint(self, entries):
        """Check thesis day constraint violations."""
        violations = []
        
        for entry in entries:
            if entry.day == 'Wednesday':
                if entry.subject and not entry.subject.code.startswith('THESIS'):
                    violations.append({
                        'type': 'Thesis Day Constraint Violation',
                        'subject': entry.subject.code,
                        'description': f"Non-thesis class {entry.subject.code} on Wednesday"
                    })
        
        return violations
    
    def _check_compact_scheduling(self, entries):
        """Check compact scheduling violations."""
        violations = []
        
        # Group entries by class group and day
        class_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            class_day_entries[entry.class_group][entry.day].append(entry)
        
        for class_group, days in class_day_entries.items():
            for day, day_entries in days.items():
                if len(day_entries) < 2:
                    continue
                
                # Sort by period
                day_entries.sort(key=lambda x: x.period)
                
                # Check for large gaps
                for i in range(len(day_entries) - 1):
                    gap = day_entries[i + 1].period - day_entries[i].period
                    if gap > 2:
                        violations.append({
                            'type': 'Compact Scheduling Violation',
                            'class_group': class_group,
                            'day': day,
                            'gap': gap,
                            'description': f"{class_group} has {gap} period gap on {day}"
                        })
        
        return violations
    
    def _check_cross_semester_conflicts(self, entries):
        """Check cross-semester conflict violations."""
        violations = []
        
        # Group entries by day and period
        time_slots = defaultdict(list)
        for entry in entries:
            time_slots[(entry.day, entry.period)].append(entry)
        
        for (day, period), slot_entries in time_slots.items():
            if len(slot_entries) > 1:
                # Check for conflicts between different class groups
                class_groups = set(entry.class_group for entry in slot_entries)
                if len(class_groups) > 1:
                    violations.append({
                        'type': 'Cross Semester Conflict',
                        'day': day,
                        'period': period,
                        'class_groups': list(class_groups),
                        'description': f"Multiple class groups scheduled on {day} P{period}"
                    })
        
        return violations
    
    def _check_teacher_assignments(self, entries):
        """Check teacher assignment violations."""
        violations = []
        
        for entry in entries:
            if entry.subject and entry.teacher:
                # Simple check - teacher should have a name
                if not entry.teacher.name:
                    violations.append({
                        'type': 'Invalid Teacher Assignment',
                        'subject': entry.subject.code,
                        'description': f"Teacher without name assigned to {entry.subject.code}"
                    })
        
        return violations
    
    def _check_friday_aware_scheduling(self, entries):
        """Check Friday-aware scheduling violations."""
        violations = []
        
        # Group entries by class group
        class_group_entries = defaultdict(list)
        for entry in entries:
            class_group_entries[entry.class_group].append(entry)
        
        for class_group, class_entries in class_group_entries.items():
            # Count classes per day
            day_counts = defaultdict(int)
            for entry in class_entries:
                day_counts[entry.day] += 1
            
            # Check if Friday is overloaded
            friday_count = day_counts.get('Friday', 0)
            weekday_total = sum(count for day, count in day_counts.items() if day != 'Friday')
            
            if weekday_total < 8 and friday_count > 2:
                violations.append({
                    'type': 'Friday Overload Violation',
                    'class_group': class_group,
                    'friday_count': friday_count,
                    'description': f"{class_group} has {friday_count} Friday classes"
                })
        
        return violations
    
    def _check_working_hours(self, entries):
        """Check working hours constraint."""
        violations = []
        
        for entry in entries:
            # Simple check - period should be within reasonable range
            if entry.period < 1 or entry.period > 8:
                violations.append({
                    'type': 'Working Hours Violation',
                    'subject': entry.subject.code if entry.subject else 'Unknown',
                    'period': entry.period,
                    'description': f"Class at period {entry.period} outside working hours"
                })
        
        return violations
    
    def _check_same_lab_rule(self, entries):
        """Check same lab rule for practical blocks."""
        violations = []
        
        # Group practical entries by class group, day, and subject
        practical_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for entry in entries:
            if entry.is_practical:
                practical_groups[entry.class_group][entry.day][entry.subject.code].append(entry)
        
        for class_group, days in practical_groups.items():
            for day, subjects in days.items():
                for subject_code, subject_entries in subjects.items():
                    if len(subject_entries) >= 3:
                        # Check if all use same lab
                        labs = set(e.classroom.name for e in subject_entries[:3] if e.classroom)
                        if len(labs) > 1:
                            violations.append({
                                'type': 'Same Lab Rule Violation',
                                'class_group': class_group,
                                'subject': subject_code,
                                'day': day,
                                'labs': list(labs),
                                'description': f"Practical {subject_code} uses multiple labs on {day}"
                            })
        
        return violations
    
    def _check_practicals_in_labs(self, entries):
        """Check that practical subjects are scheduled in labs only."""
        violations = []
        
        for entry in entries:
            if entry.is_practical and entry.classroom:
                if not entry.classroom.is_lab:
                    violations.append({
                        'type': 'Practical Not in Lab',
                        'subject': entry.subject.code if entry.subject else 'Unknown',
                        'room': entry.classroom.name,
                        'description': f"Practical {entry.subject.code if entry.subject else 'Unknown'} in non-lab room {entry.classroom.name}"
                    })
        
        return violations
    
    def _check_room_consistency(self, entries):
        """Check consistent room assignment for theory classes per section."""
        violations = []
        
        # Group theory entries by class group and day
        theory_groups = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            if not entry.is_practical:
                theory_groups[entry.class_group][entry.day].append(entry)
        
        for class_group, days in theory_groups.items():
            for day, day_entries in days.items():
                if len(day_entries) > 1:
                    # Check if all use same room
                    rooms = set(e.classroom.name for e in day_entries if e.classroom)
                    if len(rooms) > 1:
                        violations.append({
                            'type': 'Room Consistency Violation',
                            'class_group': class_group,
                            'day': day,
                            'rooms': list(rooms),
                            'description': f"{class_group} uses multiple rooms on {day}"
                        })
        
        return violations
    
    def _check_same_theory_subject_distribution(self, entries):
        """Check same theory subject distribution."""
        violations = []
        
        # Group entries by class group and subject
        class_subject_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            if entry.subject and not entry.is_practical:
                class_subject_entries[entry.class_group][entry.subject.code].append(entry)
        
        for class_group, subjects in class_subject_entries.items():
            for subject_code, subject_entries in subjects.items():
                # Check if more than 1 class per day
                day_counts = defaultdict(int)
                for entry in subject_entries:
                    day_counts[entry.day] += 1
                
                for day, count in day_counts.items():
                    if count > 1:
                        violations.append({
                            'type': 'Same Theory Subject Multiple Classes Per Day',
                            'class_group': class_group,
                            'subject': subject_code,
                            'day': day,
                            'count': count,
                            'description': f"{subject_code} has {count} classes on {day}"
                        })
        
        return violations
    
    def _check_breaks_between_classes(self, entries):
        """Check for breaks between classes."""
        violations = []
        
        # Group entries by class group and day
        class_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            class_day_entries[entry.class_group][entry.day].append(entry)
        
        for class_group, day_entries in class_day_entries.items():
            for day, day_entries_list in day_entries.items():
                # Sort by period
                day_entries_list.sort(key=lambda x: x.period)
                
                # Check for gaps between consecutive classes
                for i in range(len(day_entries_list) - 1):
                    current_entry = day_entries_list[i]
                    next_entry = day_entries_list[i + 1]
                    
                    gap = next_entry.period - current_entry.period
                    if gap > 1:
                        violations.append({
                            'type': 'Break Between Classes',
                            'class_group': class_group,
                            'day': day,
                            'gap': gap,
                            'description': f"{class_group} has {gap} period gap on {day}"
                        })
        
        return violations
    
    def _check_teacher_breaks(self, entries):
        """Check teacher breaks after 2 consecutive theory classes."""
        violations = []
        
        # Group entries by teacher and day
        teacher_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            if entry.teacher and not entry.is_practical:
                teacher_day_entries[entry.teacher.id][entry.day].append(entry)
        
        for teacher_id, day_entries in teacher_day_entries.items():
            for day, day_entries_list in day_entries.items():
                # Sort by period
                day_entries_list.sort(key=lambda x: x.period)
                
                # Find consecutive sequences
                consecutive_sequences = self._find_consecutive_sequences(day_entries_list)
                
                for sequence in consecutive_sequences:
                    if len(sequence) > 2:
                        violations.append({
                            'type': 'Teacher No Break After Consecutive Classes',
                            'teacher_id': teacher_id,
                            'teacher_name': sequence[0].teacher.name,
                            'day': day,
                            'sequence_length': len(sequence),
                            'description': f"Teacher {sequence[0].teacher.name} has {len(sequence)} consecutive classes on {day}"
                        })
        
        return violations
    
    def _find_consecutive_sequences(self, entries):
        """Find consecutive sequences of entries."""
        if not entries:
            return []
        
        sequences = []
        current_sequence = [entries[0]]
        
        for i in range(1, len(entries)):
            if entries[i].period == entries[i-1].period + 1:
                current_sequence.append(entries[i])
            else:
                if current_sequence:
                    sequences.append(current_sequence)
                current_sequence = [entries[i]]
        
        if current_sequence:
            sequences.append(current_sequence)
        
        return sequences


def create_test_data():
    """Create test data for validation."""
    entries = []
    
    # Create test subjects
    subjects = [
        MockSubject("MATH101", "Mathematics", 3, False),
        MockSubject("PHYS101", "Physics", 3, True),
        MockSubject("THESIS101", "Thesis", 3, False),
        MockSubject("ENG101", "English", 3, False),
    ]
    
    # Create test teachers
    teachers = [
        MockTeacher(1, "Dr. Smith"),
        MockTeacher(2, "Dr. Johnson"),
        MockTeacher(3, "Dr. Williams"),
    ]
    
    # Create test classrooms
    classrooms = [
        MockClassroom(1, "Room 101", 30, "Main Building"),
        MockClassroom(2, "Lab 201", 20, "Lab Building"),
        MockClassroom(3, "Room 301", 25, "Academic Building"),
    ]
    
    # Create test timetable entries
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for i, day in enumerate(days):
        for j, period in enumerate([1, 2, 3, 4]):
            subject = subjects[j % len(subjects)]
            teacher = teachers[j % len(teachers)]
            classroom = classrooms[j % len(classrooms)]
            
            entry = MockTimetableEntry(
                day=day,
                period=period,
                subject=subject,
                teacher=teacher,
                classroom=classroom,
                class_group=f"Test-{i+1}",
                start_time=time(8 + j, 0),
                end_time=time(9 + j, 0),
                is_practical=subject.is_practical
            )
            entries.append(entry)
    
    return entries


def main():
    """Run the simple constraint test."""
    print("🧪 SIMPLE TEST - ALL 18 CONSTRAINTS WORKING HARMONIOUSLY")
    print("=" * 70)
    
    # Create test data
    entries = create_test_data()
    
    # Create validator
    validator = SimpleConstraintValidator()
    
    # Validate constraints
    results = validator.validate_all_constraints(entries)
    
    # Print results
    print(f"\n📊 RESULTS:")
    print(f"   Total Violations: {results['total_violations']}")
    print(f"   Harmony Score: {results['harmony_score']:.2f}%")
    print(f"   Overall Compliance: {'✅ PASS' if results['overall_compliance'] else '❌ FAIL'}")
    
    print(f"\n🎯 ALL 18 CONSTRAINTS STATUS:")
    print("-" * 30)
    
    constraint_names = [
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
    
    for i, constraint_name in enumerate(constraint_names):
        constraint_key = constraint_name.split('. ')[1].replace(' ', ' ').title()
        violations = results['violations_by_constraint'].get(constraint_key, [])
        status = "✅ WORKING" if len(violations) == 0 else "❌ NEEDS ATTENTION"
        print(f"{constraint_name}: {status}")
    
    if results['overall_compliance']:
        print("\n🎉 SUCCESS: All 18 constraints are working harmoniously!")
        print("✅ No constraint violations")
        print("✅ High harmony score")
    else:
        print(f"\n⚠️ ATTENTION: {results['total_violations']} violations found")
        print("Some constraints may need adjustment")


if __name__ == "__main__":
    main() 