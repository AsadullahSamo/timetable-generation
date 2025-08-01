"""
Comprehensive Constraint Validation and Resolution System
Checks all constraints and provides intelligent fixing mechanisms.
"""

from typing import List, Dict, Any, Tuple
from timetable.models import TimetableEntry, Subject, Teacher, Classroom
from collections import defaultdict


class ConstraintValidator:
    """Comprehensive constraint validation and intelligent resolution system."""
    
    def __init__(self):
        self.violations = []
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
            self._check_friday_aware_scheduling
        ]
    
    def validate_all_constraints(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        """
        Comprehensive validation of all constraints.
        Returns detailed report of violations and compliance status.
        """
        self.violations = []
        results = {
            'total_violations': 0,
            'constraint_results': {},
            'violations_by_constraint': {},
            'overall_compliance': False,
            'detailed_report': []
        }
        
        print("🔍 COMPREHENSIVE CONSTRAINT VALIDATION")
        print("=" * 50)
        
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
        
        results['overall_compliance'] = results['total_violations'] == 0
        
        # Generate detailed report
        results['detailed_report'] = self._generate_detailed_report(results)
        
        return results
    
    def _check_subject_frequency(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check if subjects have correct number of classes per week based on credits."""
        violations = []

        # Group entries by class group and subject
        class_subject_counts = defaultdict(lambda: defaultdict(int))
        class_practical_sessions = defaultdict(lambda: defaultdict(int))

        # Count regular classes and practical sessions separately
        for entry in entries:
            if entry.is_practical:
                # For practical subjects, we'll count sessions later
                continue
            else:
                class_subject_counts[entry.class_group][entry.subject.code] += 1

        # Count practical sessions (3-hour blocks)
        practical_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for entry in entries:
            if entry.is_practical:
                practical_groups[entry.class_group][entry.day][entry.subject.code].append(entry)

        # Count complete practical sessions
        for class_group, days in practical_groups.items():
            for day, subjects in days.items():
                for subject_code, subject_entries in subjects.items():
                    if len(subject_entries) >= 3:
                        # Check if they are consecutive
                        periods = sorted([e.period for e in subject_entries])
                        if self._are_periods_consecutive(periods[:3]):
                            class_practical_sessions[class_group][subject_code] += 1

        # Check each class group for theory subjects
        for class_group, subject_counts in class_subject_counts.items():
            for subject_code, actual_count in subject_counts.items():
                subject = Subject.objects.filter(code=subject_code).first()
                if subject and not subject.is_practical:
                    expected_count = subject.credits

                    if actual_count != expected_count:
                        violations.append({
                            'type': 'Subject Frequency Violation',
                            'class_group': class_group,
                            'subject': subject_code,
                            'expected': expected_count,
                            'actual': actual_count,
                            'severity': 'HIGH',
                            'description': f"{subject_code} in {class_group}: expected {expected_count} classes/week, got {actual_count}"
                        })

        # Check each class group for practical subjects
        for class_group, session_counts in class_practical_sessions.items():
            for subject_code, actual_sessions in session_counts.items():
                subject = Subject.objects.filter(code=subject_code).first()
                if subject and subject.is_practical:
                    expected_sessions = 1  # Practical subjects: 1 session per week

                    if actual_sessions != expected_sessions:
                        violations.append({
                            'type': 'Subject Frequency Violation',
                            'class_group': class_group,
                            'subject': subject_code,
                            'expected': expected_sessions,
                            'actual': actual_sessions,
                            'severity': 'HIGH',
                            'description': f"{subject_code} in {class_group}: expected {expected_sessions} sessions/week, got {actual_sessions}"
                        })

        return violations

    def _are_periods_consecutive(self, periods: List[int]) -> bool:
        """Check if periods are consecutive."""
        if len(periods) < 2:
            return True

        sorted_periods = sorted(periods)
        for i in range(1, len(sorted_periods)):
            if sorted_periods[i] != sorted_periods[i-1] + 1:
                return False
        return True
    
    def _check_practical_blocks(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check if practical subjects have proper 3-hour consecutive blocks."""
        violations = []
        
        # Group practical entries by class group, day, and subject
        practical_groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for entry in entries:
            if entry.is_practical:
                practical_groups[entry.class_group][entry.day][entry.subject.code].append(entry)
        
        # Check each practical group
        for class_group, days in practical_groups.items():
            for day, subjects in days.items():
                for subject_code, subject_entries in subjects.items():
                    if len(subject_entries) != 3:
                        violations.append({
                            'type': 'Practical Block Violation',
                            'class_group': class_group,
                            'subject': subject_code,
                            'day': day,
                            'expected': 3,
                            'actual': len(subject_entries),
                            'severity': 'HIGH',
                            'description': f"Practical {subject_code} in {class_group} on {day}: expected 3 consecutive periods, got {len(subject_entries)}"
                        })
                    else:
                        # Check if periods are consecutive
                        periods = sorted([e.period for e in subject_entries])
                        for i in range(1, len(periods)):
                            if periods[i] != periods[i-1] + 1:
                                violations.append({
                                    'type': 'Practical Block Violation',
                                    'class_group': class_group,
                                    'subject': subject_code,
                                    'day': day,
                                    'periods': periods,
                                    'severity': 'HIGH',
                                    'description': f"Practical {subject_code} in {class_group} on {day}: periods not consecutive {periods}"
                                })
                                break
        
        return violations
    
    def _check_teacher_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check for teacher scheduling conflicts."""
        violations = []
        
        # Group entries by day and period
        schedule_slots = defaultdict(list)
        
        for entry in entries:
            if entry.teacher:  # Skip entries without teachers (like Thesis)
                schedule_slots[(entry.day, entry.period)].append(entry)
        
        # Check for conflicts
        for (day, period), slot_entries in schedule_slots.items():
            teacher_counts = defaultdict(int)
            for entry in slot_entries:
                if entry.teacher:
                    teacher_counts[entry.teacher.id] += 1
            
            for teacher_id, count in teacher_counts.items():
                if count > 1:
                    teacher = Teacher.objects.get(id=teacher_id)
                    conflicting_entries = [e for e in slot_entries if e.teacher and e.teacher.id == teacher_id]
                    violations.append({
                        'type': 'Teacher Conflict',
                        'teacher': teacher.name,
                        'day': day,
                        'period': period,
                        'conflicts': count,
                        'severity': 'CRITICAL',
                        'description': f"Teacher {teacher.name} scheduled for {count} classes at {day} P{period}",
                        'entries': [f"{e.class_group}-{e.subject.code}" for e in conflicting_entries]
                    })
        
        return violations
    
    def _check_room_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """
        Comprehensive room conflict detection including:
        - Double-booking conflicts
        - Room type mismatches (practicals not in labs)
        - Capacity violations
        - Seniority-based allocation violations
        """
        violations = []

        # Import room allocator for enhanced checking
        from .room_allocator import RoomAllocator
        room_allocator = RoomAllocator()

        # 1. Check for double-booking conflicts
        schedule_slots = defaultdict(list)
        for entry in entries:
            if entry.classroom:
                schedule_slots[(entry.day, entry.period, entry.classroom.id)].append(entry)

        for (day, period, classroom_id), slot_entries in schedule_slots.items():
            if len(slot_entries) > 1:
                classroom = Classroom.objects.get(id=classroom_id)
                violations.append({
                    'type': 'Room Conflict',
                    'subtype': 'double_booking',
                    'classroom': classroom.name,
                    'day': day,
                    'period': period,
                    'conflicts': len(slot_entries),
                    'severity': 'CRITICAL',
                    'description': f"Classroom {classroom.name} double-booked at {day} P{period} ({len(slot_entries)} classes)",
                    'entries': [f"{e.class_group}-{e.subject.code if e.subject else 'Unknown'}" for e in slot_entries]
                })

        # 2. ENHANCED: Check for room type mismatches and same-lab violations
        for entry in entries:
            if entry.classroom and entry.subject:
                # CRITICAL: Practical subjects MUST be in labs
                if entry.subject.is_practical and not entry.classroom.is_lab:
                    violations.append({
                        'type': 'Room Conflict',
                        'subtype': 'practical_not_in_lab',
                        'classroom': entry.classroom.name,
                        'day': entry.day,
                        'period': entry.period,
                        'severity': 'CRITICAL',
                        'description': f"VIOLATION: Practical subject {entry.subject.code} scheduled in non-lab room {entry.classroom.name}",
                        'class_group': entry.class_group,
                        'subject': entry.subject.code
                    })

        # 2b. ENHANCED: Check same-lab rule for practical subjects
        self._check_practical_same_lab_violations(entries, violations)

        # 3. Check for seniority-based allocation violations
        for entry in entries:
            if (entry.classroom and entry.classroom.is_lab and
                entry.subject and not entry.subject.is_practical):
                # Theory class in lab - check if junior batch
                is_senior = room_allocator.is_senior_batch(entry.class_group)
                if not is_senior:
                    violations.append({
                        'type': 'Room Conflict',
                        'subtype': 'seniority_violation',
                        'classroom': entry.classroom.name,
                        'day': entry.day,
                        'period': entry.period,
                        'severity': 'MEDIUM',
                        'description': f"Junior batch {entry.class_group} assigned lab {entry.classroom.name} for theory class",
                        'class_group': entry.class_group,
                        'subject': entry.subject.code if entry.subject else 'Unknown'
                    })

        # 4. Check lab reservation violations (too many practicals, not enough labs for theory)
        self._check_lab_reservation_violations(entries, violations, room_allocator)

        # 5. Check room capacity violations
        self._check_room_capacity_violations(entries, violations)

        return violations

    def _check_lab_reservation_violations(self, entries: List[TimetableEntry],
                                        violations: List[Dict], room_allocator):
        """Check if lab reservation constraints are violated."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        total_labs = len(room_allocator.labs)
        min_reserved_labs = min(4, max(3, total_labs - 2))

        for day in days:
            for period in range(1, 8):
                # Count labs occupied by practicals at this time
                practical_labs = set()
                theory_in_labs = 0

                for entry in entries:
                    if (entry.day == day and entry.period == period and
                        entry.classroom and entry.classroom.is_lab):
                        if entry.subject and entry.subject.is_practical:
                            practical_labs.add(entry.classroom.id)
                        else:
                            theory_in_labs += 1

                occupied_labs = len(practical_labs) + theory_in_labs
                available_labs = total_labs - occupied_labs

                if available_labs < min_reserved_labs:
                    violations.append({
                        'type': 'Room Conflict',
                        'subtype': 'lab_reservation_violation',
                        'day': day,
                        'period': period,
                        'severity': 'HIGH',
                        'description': f"Only {available_labs}/{min_reserved_labs} labs reserved for senior theory on {day} P{period}",
                        'occupied_labs': occupied_labs,
                        'total_labs': total_labs,
                        'required_reserved': min_reserved_labs
                    })

    def _check_room_capacity_violations(self, entries: List[TimetableEntry], violations: List[Dict]):
        """Check if room capacity can accommodate section sizes."""
        # Assume 30 students per section as default (this could be made configurable)
        default_section_size = 30

        for entry in entries:
            if entry.classroom:
                # Check if room capacity is sufficient
                if not entry.classroom.can_accommodate_section_size(default_section_size):
                    violations.append({
                        'type': 'Room Conflict',
                        'subtype': 'capacity_violation',
                        'classroom': entry.classroom.name,
                        'day': entry.day,
                        'period': entry.period,
                        'severity': 'HIGH',
                        'description': f"Room {entry.classroom.name} (capacity {entry.classroom.capacity}) cannot accommodate section {entry.class_group} (estimated {default_section_size} students)",
                        'class_group': entry.class_group,
                        'subject': entry.subject.code if entry.subject else 'Unknown',
                        'room_capacity': entry.classroom.capacity,
                        'required_capacity': default_section_size
                    })
    
    def _check_friday_time_limits(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check Friday time limit constraints."""
        violations = []
        
        # Group Friday entries by class group
        friday_entries = defaultdict(list)
        for entry in entries:
            if entry.day.lower().startswith('fri'):
                friday_entries[entry.class_group].append(entry)
        
        # Check each class group's Friday schedule
        for class_group, group_entries in friday_entries.items():
            practical_count = len([e for e in group_entries if e.is_practical])
            theory_entries = [e for e in group_entries if not e.is_practical]
            
            if practical_count > 0:
                # Has practical - theory should not exceed period 4 (12:00 PM)
                for entry in theory_entries:
                    if entry.period > 4:
                        violations.append({
                            'type': 'Friday Time Limit Violation',
                            'class_group': class_group,
                            'subject': entry.subject.code,
                            'period': entry.period,
                            'limit': 4,
                            'severity': 'HIGH',
                            'description': f"{class_group} has theory class {entry.subject.code} at P{entry.period} on Friday with practical present (limit: P4)"
                        })
            else:
                # No practical - should not exceed period 3 (11:00 AM)
                for entry in group_entries:
                    if entry.period > 3:
                        violations.append({
                            'type': 'Friday Time Limit Violation',
                            'class_group': class_group,
                            'subject': entry.subject.code,
                            'period': entry.period,
                            'limit': 3,
                            'severity': 'HIGH',
                            'description': f"{class_group} has class {entry.subject.code} at P{entry.period} on Friday without practical (limit: P3)"
                        })
        
        return violations

    def _check_minimum_daily_classes(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check minimum daily classes constraint."""
        violations = []

        # Group entries by class group and day
        daily_entries = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            daily_entries[entry.class_group][entry.day].append(entry)

        # Check each class group's daily schedule
        for class_group, days in daily_entries.items():
            for day, day_entries in days.items():
                if not day_entries:
                    continue

                practical_count = len([e for e in day_entries if e.is_practical])
                theory_count = len([e for e in day_entries if not e.is_practical])
                total_count = len(day_entries)

                # Check for violations
                if total_count == 1:
                    violations.append({
                        'type': 'Minimum Daily Classes Violation',
                        'class_group': class_group,
                        'day': day,
                        'issue': 'Only one class',
                        'count': total_count,
                        'severity': 'MEDIUM',
                        'description': f"{class_group} has only 1 class on {day}"
                    })
                elif practical_count > 0 and theory_count == 0:
                    violations.append({
                        'type': 'Minimum Daily Classes Violation',
                        'class_group': class_group,
                        'day': day,
                        'issue': 'Only practical classes',
                        'practical_count': practical_count,
                        'severity': 'MEDIUM',
                        'description': f"{class_group} has only practical classes on {day}"
                    })

        return violations

    def _check_thesis_day_constraint(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check Thesis Day constraint for final year batches."""
        violations = []

        # Find Thesis entries
        thesis_entries = [e for e in entries if 'thesis' in e.subject.code.lower() or 'thesis' in e.subject.name.lower()]

        # Check Thesis entries
        for entry in thesis_entries:
            # Check if on Wednesday
            if not entry.day.lower().startswith('wed'):
                violations.append({
                    'type': 'Thesis Day Violation',
                    'class_group': entry.class_group,
                    'subject': entry.subject.code,
                    'day': entry.day,
                    'issue': 'Not on Wednesday',
                    'severity': 'HIGH',
                    'description': f"Thesis {entry.subject.code} for {entry.class_group} scheduled on {entry.day} instead of Wednesday"
                })

            # Check if has teacher (should not)
            if entry.teacher is not None:
                violations.append({
                    'type': 'Thesis Day Violation',
                    'class_group': entry.class_group,
                    'subject': entry.subject.code,
                    'issue': 'Has teacher assigned',
                    'teacher': entry.teacher.name,
                    'severity': 'MEDIUM',
                    'description': f"Thesis {entry.subject.code} for {entry.class_group} has teacher {entry.teacher.name} (should be None)"
                })

        # Check Wednesday dedication for final year batches
        final_year_batches = ['21SW-I', '21SW-II', '21SW-III']

        for class_group in final_year_batches:
            wednesday_entries = [e for e in entries if e.class_group == class_group and e.day.lower().startswith('wed')]
            thesis_count = len([e for e in wednesday_entries if 'thesis' in e.subject.code.lower() or 'thesis' in e.subject.name.lower()])
            non_thesis_count = len(wednesday_entries) - thesis_count

            if thesis_count > 0 and non_thesis_count > 0:
                non_thesis_subjects = [e.subject.code for e in wednesday_entries if not ('thesis' in e.subject.code.lower() or 'thesis' in e.subject.name.lower())]
                violations.append({
                    'type': 'Thesis Day Violation',
                    'class_group': class_group,
                    'issue': 'Wednesday not dedicated to Thesis',
                    'thesis_count': thesis_count,
                    'non_thesis_count': non_thesis_count,
                    'non_thesis_subjects': non_thesis_subjects,
                    'severity': 'HIGH',
                    'description': f"{class_group} has {non_thesis_count} non-Thesis subjects on Wednesday: {non_thesis_subjects}"
                })

        return violations

    def _check_compact_scheduling(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check compact scheduling (wrap up quickly)."""
        violations = []

        # Group entries by class group and day
        daily_schedules = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            daily_schedules[entry.class_group][entry.day].append(entry.period)

        # Check each class group's compactness
        for class_group, days in daily_schedules.items():
            total_end_periods = []

            for day, periods in days.items():
                if periods:
                    max_period = max(periods)
                    total_end_periods.append(max_period)

                    # Check for gaps in schedule (non-compact)
                    sorted_periods = sorted(set(periods))
                    for i in range(1, len(sorted_periods)):
                        if sorted_periods[i] - sorted_periods[i-1] > 1:
                            violations.append({
                                'type': 'Compact Scheduling Violation',
                                'class_group': class_group,
                                'day': day,
                                'issue': 'Schedule gap',
                                'periods': sorted_periods,
                                'gap': f"Gap between P{sorted_periods[i-1]} and P{sorted_periods[i]}",
                                'severity': 'LOW',
                                'description': f"{class_group} has schedule gap on {day}: {sorted_periods}"
                            })

            # Check average end time
            if total_end_periods:
                avg_end_period = sum(total_end_periods) / len(total_end_periods)
                if avg_end_period > 5:  # Classes ending after period 5 (2:00 PM)
                    violations.append({
                        'type': 'Compact Scheduling Violation',
                        'class_group': class_group,
                        'issue': 'Late end times',
                        'avg_end_period': round(avg_end_period, 1),
                        'severity': 'LOW',
                        'description': f"{class_group} average end period: {avg_end_period:.1f} (should be ≤5)"
                    })

        return violations

    def _check_cross_semester_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check for cross-semester conflicts."""
        # For now, return empty as this is handled by teacher/room conflicts
        return []

    def _check_teacher_assignments(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check if teachers are assigned to their designated subjects."""
        violations = []

        for entry in entries:
            if entry.teacher and entry.subject:
                # Check if teacher is assigned to this subject
                from timetable.models import TeacherSubjectAssignment

                assignments = TeacherSubjectAssignment.objects.filter(
                    teacher=entry.teacher,
                    subject=entry.subject
                )

                if not assignments.exists():
                    violations.append({
                        'type': 'Teacher Assignment Violation',
                        'teacher': entry.teacher.name,
                        'subject': entry.subject.code,
                        'class_group': entry.class_group,
                        'severity': 'MEDIUM',
                        'description': f"Teacher {entry.teacher.name} not assigned to subject {entry.subject.code}"
                    })

        return violations

    def _check_friday_aware_scheduling(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check Friday-aware scheduling principles."""
        # This is more of a quality check - return empty for now
        return []

    def _generate_detailed_report(self, results: Dict[str, Any]) -> List[str]:
        """Generate a detailed human-readable report."""
        report = []

        report.append(f"🔍 CONSTRAINT VALIDATION REPORT")
        report.append(f"=" * 40)
        report.append(f"Total Violations: {results['total_violations']}")
        report.append(f"Overall Compliance: {'✅ PASS' if results['overall_compliance'] else '❌ FAIL'}")
        report.append("")

        # Constraint-by-constraint breakdown
        for constraint_name, constraint_result in results['constraint_results'].items():
            status_icon = "✅" if constraint_result['status'] == 'PASS' else "❌"
            report.append(f"{status_icon} {constraint_name}: {constraint_result['violations']} violations")

            if constraint_result['violations'] > 0:
                for violation in constraint_result['details'][:3]:  # Show first 3 violations
                    report.append(f"   - {violation['description']}")
                if len(constraint_result['details']) > 3:
                    report.append(f"   - ... and {len(constraint_result['details']) - 3} more")

        return report

    def _check_practical_same_lab_violations(self, entries: List[TimetableEntry], violations: List[Dict]):
        """
        ENHANCED: Check that all 3 blocks of each practical subject use the same lab.
        This enforces the universal same-lab rule for practical subjects.
        """
        from collections import defaultdict

        # Group practical entries by class group and subject
        practical_groups = defaultdict(list)

        for entry in entries:
            if (entry.subject and entry.subject.is_practical and
                entry.classroom and entry.classroom.is_lab):
                key = (entry.class_group, entry.subject.code)
                practical_groups[key].append(entry)

        # Check each practical group for same-lab compliance
        for (class_group, subject_code), group_entries in practical_groups.items():
            if len(group_entries) >= 2:  # Need at least 2 entries to check consistency
                # Get all unique labs used by this practical
                labs_used = set(entry.classroom.id for entry in group_entries)

                if len(labs_used) > 1:
                    # VIOLATION: Multiple labs used for same practical
                    lab_details = []
                    for entry in group_entries:
                        lab_details.append(f"{entry.day} P{entry.period}: {entry.classroom.name}")

                    violations.append({
                        'type': 'Room Conflict',
                        'subtype': 'practical_different_labs',
                        'severity': 'CRITICAL',
                        'description': f"VIOLATION: Practical {subject_code} uses {len(labs_used)} different labs - {', '.join(lab_details)}",
                        'class_group': class_group,
                        'subject': subject_code,
                        'labs_used': len(labs_used),
                        'details': lab_details
                    })
