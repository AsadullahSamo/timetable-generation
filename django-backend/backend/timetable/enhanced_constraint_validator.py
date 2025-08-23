"""
ENHANCED CONSTRAINT VALIDATOR - ALL 19 CONSTRAINTS WORKING HARMONIOUSLY
=====================================================================
Validates all 19 constraints ensuring they work seamlessly and in harmony without one violating the other.
This includes all scheduling and room constraints working together perfectly.

THE 19 CONSTRAINTS:
1. Subject Frequency - Correct number of classes per week based on credits
2. Practical Blocks - 3-hour consecutive blocks for practical subjects
3. Teacher Conflicts - No teacher double-booking
4. Room Conflicts - No room double-booking
5. Friday Time Limits - Classes must not exceed 12:00/1:00 PM with practical, 11:00 AM without practical
6. Minimum Daily Classes - No day has only practical or only one class
7. Thesis Day Constraint - Wednesday is exclusively reserved for Thesis subjects for final year students
8. Compact Scheduling - Classes wrap up quickly while respecting Friday constraints
9. Cross Semester Conflicts - Prevents scheduling conflicts across batches
10. Teacher Assignments - Intelligent teacher assignment matching
11. Friday Aware Scheduling - Monday-Thursday scheduling considers Friday limits proactively
12. Working Hours - All classes are within 8:00 AM to 3:00 PM
13. Same Lab Rule - All 3 blocks of practical subjects must use the same lab
14. Practicals in Labs - Practical subjects must be scheduled only in laboratory rooms
15. Room Consistency - Enhanced room consistency for theory/practical separation (same room for theory, same lab for practicals)
16. Same Theory Subject Distribution - Max 1 class per day, distributed across 5 weekdays
17. Breaks Between Classes - Minimal breaks, only when needed
18. Teacher Breaks - After 2 consecutive theory classes, teacher must have a break
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import time, timedelta
from .models import TimetableEntry, Subject, Teacher, Classroom, ScheduleConfig


class EnhancedConstraintValidator:
    """Enhanced constraint validator ensuring all 18 constraints work harmoniously."""
    
    def __init__(self):
        self.violations = []
        self.constraint_checks = [
            # Core scheduling constraints
            self._check_subject_frequency,
            self._check_practical_blocks,
            self._check_teacher_conflicts,
            self._check_room_conflicts,
            self._check_friday_time_limits,
            self._check_minimum_daily_classes,
            self._check_empty_fridays,
            self._check_thesis_day_constraint,
            self._check_compact_scheduling,
            self._check_cross_semester_conflicts,
            self._check_teacher_assignments,
            self._check_friday_aware_scheduling,
            self._check_working_hours,
            
            # Room allocation constraints
            self._check_same_lab_rule,
            self._check_practicals_in_labs,
            self._check_room_consistency,

            
            # NEW CONSTRAINTS
            self._check_same_theory_subject_distribution,
            self._check_breaks_between_classes,
            self._check_teacher_breaks,
        ]
        
        # Constraint conflict detection
        self.constraint_conflicts = {
            'practical_blocks': ['breaks_between_classes', 'teacher_breaks'],
            'compact_scheduling': ['breaks_between_classes'],
            'same_theory_distribution': ['compact_scheduling'],
            'teacher_breaks': ['compact_scheduling'],
        }
    
    def validate_all_constraints(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        """Validate all 18 constraints ensuring they work harmoniously."""
        self.violations = []
        results = {
            'total_violations': 0,
            'constraint_results': {},
            'violations_by_constraint': {},
            'overall_compliance': False,
            'detailed_report': [],
            'constraint_conflicts': [],
            'harmony_score': 0.0
        }
        
        print("🔍 ENHANCED CONSTRAINT VALIDATION - ALL 19 CONSTRAINTS")
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
        
        # Check for constraint conflicts
        results['constraint_conflicts'] = self._detect_constraint_conflicts(results)
        
        # Calculate harmony score
        results['harmony_score'] = self._calculate_harmony_score(results)
        
        results['overall_compliance'] = results['total_violations'] == 0 and len(results['constraint_conflicts']) == 0
        
        print(f"\n📊 VALIDATION RESULTS:")
        print(f"   Total Violations: {results['total_violations']}")
        print(f"   Constraint Conflicts: {len(results['constraint_conflicts'])}")
        print(f"   Harmony Score: {results['harmony_score']:.2f}%")
        print(f"   Overall Compliance: {'✅ PASS' if results['overall_compliance'] else '❌ FAIL'}")
        
        return results
    
    def _detect_constraint_conflicts(self, results: Dict[str, Any]) -> List[Dict]:
        """Detect conflicts between constraints."""
        conflicts = []
        
        for constraint1, conflicting_constraints in self.constraint_conflicts.items():
            constraint1_violations = results['violations_by_constraint'].get(constraint1.replace('_', ' ').title(), [])
            
            for constraint2 in conflicting_constraints:
                constraint2_violations = results['violations_by_constraint'].get(constraint2.replace('_', ' ').title(), [])
                
                if constraint1_violations and constraint2_violations:
                    conflicts.append({
                        'constraint1': constraint1.replace('_', ' ').title(),
                        'constraint2': constraint2.replace('_', ' ').title(),
                        'description': f"Conflict between {constraint1} and {constraint2}",
                        'resolution_suggestion': self._get_conflict_resolution_suggestion(constraint1, constraint2)
                    })
        
        return conflicts
    
    def _get_conflict_resolution_suggestion(self, constraint1: str, constraint2: str) -> str:
        """Get resolution suggestion for constraint conflicts."""
        suggestions = {
            ('practical_blocks', 'breaks_between_classes'): "Prioritize practical blocks over breaks",
            ('practical_blocks', 'teacher_breaks'): "Allow teacher breaks within practical blocks",
            ('compact_scheduling', 'breaks_between_classes'): "Minimize breaks while maintaining compactness",
            ('same_theory_distribution', 'compact_scheduling'): "Distribute theory subjects while keeping compact",
            ('teacher_breaks', 'compact_scheduling'): "Schedule teacher breaks strategically"
        }
        
        key = (constraint1, constraint2)
        reverse_key = (constraint2, constraint1)
        
        return suggestions.get(key, suggestions.get(reverse_key, "Review constraint priorities"))
    
    def _calculate_harmony_score(self, results: Dict[str, Any]) -> float:
        """Calculate harmony score based on violations and conflicts."""
        total_constraints = len(self.constraint_checks)
        total_violations = results['total_violations']
        total_conflicts = len(results['constraint_conflicts'])
        
        # Base score from violations
        violation_penalty = (total_violations / (total_constraints * 10)) * 100  # Max 10 violations per constraint
        conflict_penalty = total_conflicts * 10  # 10% penalty per conflict
        
        harmony_score = max(0, 100 - violation_penalty - conflict_penalty)
        return harmony_score
    
    # CORE SCHEDULING CONSTRAINTS
    
    def _check_subject_frequency(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check if subjects have correct number of classes per week based on credits."""
        violations = []
        
        # Group entries by class group and subject
        class_subject_counts = defaultdict(lambda: defaultdict(int))
        class_practical_sessions = defaultdict(lambda: defaultdict(int))
        
        # Count regular classes and practical sessions separately
        for entry in entries:
            if entry.is_practical:
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
                        periods = sorted([e.period for e in subject_entries])
                        if self._are_periods_consecutive(periods[:3]):
                            class_practical_sessions[class_group][subject_code] += 1
        
        # Check each class group for theory subjects
        for class_group, subjects in class_subject_counts.items():
            for subject_code, count in subjects.items():
                subject = Subject.objects.filter(code=subject_code).first()
                if subject:
                    expected_count = subject.credits
                    if count != expected_count:
                        violations.append({
                            'type': 'Subject Frequency Violation',
                            'class_group': class_group,
                            'subject': subject_code,
                            'expected': expected_count,
                            'actual': count,
                            'description': f"{subject_code} in {class_group} has {count} classes (expected {expected_count})"
                        })
        
        # Check practical sessions
        for class_group, subjects in class_practical_sessions.items():
            for subject_code, count in subjects.items():
                subject = Subject.objects.filter(code=subject_code).first()
                if subject and subject.is_practical:
                    expected_sessions = subject.credits // 3  # 3-hour blocks
                    if count != expected_sessions:
                        violations.append({
                            'type': 'Practical Session Frequency Violation',
                            'class_group': class_group,
                            'subject': subject_code,
                            'expected_sessions': expected_sessions,
                            'actual_sessions': count,
                            'description': f"Practical {subject_code} in {class_group} has {count} sessions (expected {expected_sessions})"
                        })
        
        return violations
    
    def _are_periods_consecutive(self, periods: List[int]) -> bool:
        """Check if periods are consecutive."""
        if len(periods) < 2:
            return True
        return all(periods[i] + 1 == periods[i + 1] for i in range(len(periods) - 1))
    
    def _check_practical_blocks(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check practical block requirements - 3 consecutive periods in same lab."""
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
                            'description': f"Practical {subject_code} on {day} has only {len(subject_entries)} periods (need 3)"
                        })
                        continue
                    
                    # Check if periods are consecutive
                    periods = sorted([e.period for e in subject_entries])
                    if not self._are_periods_consecutive(periods[:3]):
                        violations.append({
                            'type': 'Non-Consecutive Practical Block',
                            'class_group': class_group,
                            'subject': subject_code,
                            'day': day,
                            'periods': periods[:3],
                            'description': f"Practical {subject_code} on {day} periods {periods[:3]} are not consecutive"
                        })
                    
                    # Check if all use same lab
                    labs = set(e.classroom.name for e in subject_entries[:3] if e.classroom)
                    if len(labs) > 1:
                        violations.append({
                            'type': 'Multiple Labs for Practical Block',
                            'class_group': class_group,
                            'subject': subject_code,
                            'day': day,
                            'labs': list(labs),
                            'description': f"Practical {subject_code} on {day} uses multiple labs: {labs}"
                        })
        
        return violations
    
    def _check_teacher_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check teacher conflict violations."""
        violations = []
        
        # Group entries by teacher, day, and period
        teacher_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for entry in entries:
            if entry.teacher:
                teacher_schedule[entry.teacher.id][entry.day][entry.period].append(entry)
        
        for teacher_id, days in teacher_schedule.items():
            teacher = Teacher.objects.get(id=teacher_id)
            for day, periods in days.items():
                for period, period_entries in periods.items():
                    if len(period_entries) > 1:
                        violations.append({
                            'type': 'Teacher Double Booking',
                            'teacher_id': teacher_id,
                            'teacher_name': teacher.name,
                            'day': day,
                            'period': period,
                            'entries': period_entries,
                            'description': f"Teacher {teacher.name} is double-booked on {day} P{period}"
                        })
        
        return violations
    
    def _check_room_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check room conflict violations."""
        violations = []
        
        # Group entries by room, day, and period
        room_schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for entry in entries:
            if entry.classroom:
                room_schedule[entry.classroom.id][entry.day][entry.period].append(entry)
        
        for room_id, days in room_schedule.items():
            room = Classroom.objects.get(id=room_id)
            for day, periods in days.items():
                for period, period_entries in periods.items():
                    if len(period_entries) > 1:
                        violations.append({
                            'type': 'Room Double Booking',
                            'room_id': room_id,
                            'room_name': room.name,
                            'day': day,
                            'period': period,
                            'entries': period_entries,
                            'description': f"Room {room.name} is double-booked on {day} P{period}"
                        })
        
        return violations
    
    def _check_friday_time_limits(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check Friday time limit violations."""
        violations = []
        
        for entry in entries:
            if entry.day == 'Friday':
                # Get schedule config for time calculations
                config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
                if config:
                    # Calculate actual time for this period
                    start_time = config.start_time
                    class_duration = timedelta(minutes=config.class_duration)
                    
                    # Calculate actual start time for this period
                    total_minutes = (entry.period - 1) * (config.class_duration + 15)  # 15 min break
                    actual_start_time = (
                        timedelta(hours=start_time.hour, minutes=start_time.minute) +
                        timedelta(minutes=total_minutes)
                    )
                    
                    # Convert to time object
                    total_seconds = int(actual_start_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    start_time_obj = time(hours % 24, minutes)
                    
                    # Check limits based on practical status
                    if entry.is_practical:
                        limit_time = time(13, 0)  # 1:00 PM
                    else:
                        limit_time = time(11, 0)  # 11:00 AM
                    
                    if start_time_obj >= limit_time:
                        violations.append({
                            'type': 'Friday Time Limit Violation',
                            'entry_id': entry.id,
                            'subject': entry.subject.code if entry.subject else 'Unknown',
                            'start_time': start_time_obj,
                            'limit_time': limit_time,
                            'is_practical': entry.is_practical,
                            'description': f"Friday class starts at {start_time_obj} (limit: {limit_time})"
                        })
        
        return violations
    
    def _check_minimum_daily_classes(self, entries: List[TimetableEntry]) -> List[Dict]:
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
                        'description': f"{class_group} has only {len(day_entries)} classes on {day} (minimum 2 required)"
                    })
                
                # Check if day has only practical classes
                practical_count = sum(1 for entry in day_entries if entry.is_practical)
                if practical_count == len(day_entries) and len(day_entries) > 0:
                    violations.append({
                        'type': 'Only Practical Classes Violation',
                        'class_group': class_group,
                        'day': day,
                        'practical_count': practical_count,
                        'description': f"{class_group} has only practical classes on {day}"
                    })
        
        return violations
    
    def _check_thesis_day_constraint(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check thesis day constraint violations."""
        violations = []
        
        for entry in entries:
            if entry.day == 'Wednesday':
                # Check if this is a thesis subject for final year students
                if entry.subject and entry.subject.code.startswith('THESIS'):
                    # This is allowed
                    continue
                else:
                    # Check if this is a final year batch
                    class_group = entry.class_group
                    if class_group and any(year in class_group for year in ['21SW', '22SW']):  # Final year batches
                        violations.append({
                            'type': 'Thesis Day Constraint Violation',
                            'entry_id': entry.id,
                            'subject': entry.subject.code if entry.subject else 'Unknown',
                            'class_group': class_group,
                            'description': f"Non-thesis class {entry.subject.code if entry.subject else 'Unknown'} scheduled on Wednesday for final year batch {class_group}"
                        })
        
        return violations
    
    def _check_compact_scheduling(self, entries: List[TimetableEntry]) -> List[Dict]:
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
                    if gap > 2:  # More than 2 period gap
                        violations.append({
                            'type': 'Compact Scheduling Violation',
                            'class_group': class_group,
                            'day': day,
                            'gap': gap,
                            'periods': [day_entries[i].period, day_entries[i + 1].period],
                            'description': f"{class_group} has {gap} period gap on {day} between P{day_entries[i].period} and P{day_entries[i + 1].period}"
                        })
        
        return violations
    
    def _check_cross_semester_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check cross-semester conflict violations."""
        violations = []
        
        # Group entries by day and period
        time_slots = defaultdict(list)
        for entry in entries:
            time_slots[(entry.day, entry.period)].append(entry)
        
        for (day, period), slot_entries in time_slots.items():
            if len(slot_entries) > 1:
                # Check for conflicts between different batches
                batches = set(entry.class_group.split('-')[0] for entry in slot_entries if '-' in entry.class_group)
                if len(batches) > 1:
                    violations.append({
                        'type': 'Cross Semester Conflict',
                        'day': day,
                        'period': period,
                        'batches': list(batches),
                        'entries': slot_entries,
                        'description': f"Multiple batches {batches} scheduled simultaneously on {day} P{period}"
                    })
        
        return violations
    
    def _check_teacher_assignments(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check teacher assignment violations."""
        violations = []
        
        for entry in entries:
            if entry.subject and entry.teacher:
                # Check if teacher is assigned to this subject
                teacher_assignments = entry.teacher.teachersubjectassignment_set.filter(subject=entry.subject)
                if not teacher_assignments.exists():
                    violations.append({
                        'type': 'Invalid Teacher Assignment',
                        'entry_id': entry.id,
                        'subject': entry.subject.code,
                        'teacher': entry.teacher.name,
                        'description': f"Teacher {entry.teacher.name} not assigned to subject {entry.subject.code}"
                    })
        
        return violations
    
    def _check_friday_aware_scheduling(self, entries: List[TimetableEntry]) -> List[Dict]:
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
            
            # Check if Monday-Thursday are underutilized while Friday is overloaded
            weekday_total = sum(count for day, count in day_counts.items() if day != 'Friday')
            friday_count = day_counts.get('Friday', 0)
            
            if weekday_total < 8 and friday_count > 2:  # Arbitrary thresholds
                violations.append({
                    'type': 'Friday Overload Violation',
                    'class_group': class_group,
                    'weekday_total': weekday_total,
                    'friday_count': friday_count,
                    'description': f"{class_group} has {weekday_total} weekday classes but {friday_count} Friday classes"
                })
        
        return violations
    
    def _check_working_hours(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check working hours constraint (8:00 AM to 3:00 PM)."""
        violations = []
        
        config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
        if not config:
            return violations
        
        for entry in entries:
            # Calculate actual time for this period
            start_time = config.start_time
            class_duration = timedelta(minutes=config.class_duration)
            
            # Calculate actual start time for this period
            total_minutes = (entry.period - 1) * (config.class_duration + 15)  # 15 min break
            actual_start_time = (
                timedelta(hours=start_time.hour, minutes=start_time.minute) +
                timedelta(minutes=total_minutes)
            )
            
            # Convert to time object
            total_seconds = int(actual_start_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            start_time_obj = time(hours % 24, minutes)
            
            # Calculate end time
            end_time_obj = (
                timedelta(hours=start_time_obj.hour, minutes=start_time_obj.minute) +
                class_duration
            )
            end_total_seconds = int(end_time_obj.total_seconds())
            end_hours = end_total_seconds // 3600
            end_minutes = (end_total_seconds % 3600) // 60
            end_time_obj = time(end_hours % 24, end_minutes)
            
            # Check working hours (8:00 AM to 3:00 PM)
            working_start = time(8, 0)
            working_end = time(15, 0)
            
            if start_time_obj < working_start or end_time_obj > working_end:
                violations.append({
                    'type': 'Working Hours Violation',
                    'entry_id': entry.id,
                    'subject': entry.subject.code if entry.subject else 'Unknown',
                    'start_time': start_time_obj,
                    'end_time': end_time_obj,
                    'description': f"Class {entry.subject.code if entry.subject else 'Unknown'} outside working hours: {start_time_obj} - {end_time_obj}"
                })
        
        return violations
    
    # ROOM ALLOCATION CONSTRAINTS
    
    def _check_same_lab_rule(self, entries: List[TimetableEntry]) -> List[Dict]:
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
                                'description': f"Practical {subject_code} on {day} uses multiple labs: {labs}"
                            })
        
        return violations
    
    def _check_practicals_in_labs(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check that practical subjects are scheduled in labs only."""
        violations = []
        
        for entry in entries:
            if entry.is_practical and entry.classroom:
                if not entry.classroom.is_lab:
                    violations.append({
                        'type': 'Practical Not in Lab',
                        'entry_id': entry.id,
                        'subject': entry.subject.code if entry.subject else 'Unknown',
                        'room': entry.classroom.name,
                        'description': f"Practical {entry.subject.code if entry.subject else 'Unknown'} scheduled in non-lab room {entry.classroom.name}"
                    })
        
        return violations
    
    def _check_room_consistency(self, entries: List[TimetableEntry]) -> List[Dict]:
        """
        Check enhanced room consistency for theory/practical separation.
        
        NEW CONSTRAINT: 
        - If only theory classes are scheduled for the entire day, all classes for a section should be assigned in same room
        - If both theory and practical classes are scheduled for a day, all practical classes must be in same lab (all 3 consecutive blocks) 
          and then if theory classes are scheduled in a room, all must be in same room
        """
        violations = []
        
        # Group entries by class group and day
        class_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            class_day_entries[entry.class_group][entry.day].append(entry)
        
        for class_group, days in class_day_entries.items():
            for day, day_entries in days.items():
                if len(day_entries) > 1:
                    # Separate theory and practical classes
                    theory_entries = [e for e in day_entries if not e.is_practical]
                    practical_entries = [e for e in day_entries if e.is_practical]
                    
                    # Check theory class room consistency
                    if len(theory_entries) > 1:
                        theory_rooms = set(e.classroom.name for e in theory_entries if e.classroom)
                        if len(theory_rooms) > 1:
                            violations.append({
                                'type': 'Theory Room Consistency Violation',
                                'class_group': class_group,
                                'day': day,
                                'theory_rooms': list(theory_rooms),
                                'theory_count': len(theory_entries),
                                'description': f"{class_group} uses multiple rooms for theory classes on {day}: {theory_rooms}"
                            })
                    
                    # Check practical class lab consistency
                    if len(practical_entries) > 1:
                        practical_labs = set(e.classroom.name for e in practical_entries if e.classroom)
                        if len(practical_labs) > 1:
                            violations.append({
                                'type': 'Practical Lab Consistency Violation',
                                'class_group': class_group,
                                'day': day,
                                'practical_labs': list(practical_labs),
                                'practical_count': len(practical_entries),
                                'description': f"{class_group} uses multiple labs for practical classes on {day}: {practical_labs}"
                            })
                        
                        # Check if practical classes are consecutive (3 blocks)
                        practical_periods = sorted([e.period for e in practical_entries])
                        if len(practical_periods) >= 3:
                            # Check if we have 3 consecutive periods
                            consecutive_blocks = 0
                            for i in range(len(practical_periods) - 1):
                                if practical_periods[i+1] == practical_periods[i] + 1:
                                    consecutive_blocks += 1
                                else:
                                    consecutive_blocks = 0
                            
                            if consecutive_blocks < 2:  # Need at least 2 consecutive transitions for 3 blocks
                                violations.append({
                                    'type': 'Practical Non-Consecutive Blocks',
                                    'class_group': class_group,
                                    'day': day,
                                    'practical_periods': practical_periods,
                                    'consecutive_blocks': consecutive_blocks + 1,
                                    'description': f"{class_group} practical classes on {day} are not in 3 consecutive blocks: {practical_periods}"
                                })
        
        return violations
    

    
    # NEW CONSTRAINTS
    
    def _check_same_theory_subject_distribution(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check same theory subject distribution - max 1 class per day, distributed across 5 weekdays."""
        violations = []
        
        # Group entries by class group and subject
        class_subject_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            if entry.subject and not entry.is_practical:  # Only theory subjects
                class_subject_entries[entry.class_group][entry.subject.code].append(entry)
        
        for class_group, subjects in class_subject_entries.items():
            for subject_code, subject_entries in subjects.items():
                # Check if more than 1 class per day
                day_counts = defaultdict(int)
                day_entries = defaultdict(list)
                
                for entry in subject_entries:
                    day_counts[entry.day] += 1
                    day_entries[entry.day].append(entry)
                
                for day, count in day_counts.items():
                    if count > 1:
                        # Get specific entries causing the violation
                        violating_entries = day_entries[day]
                        entry_details = [f"{entry.day} P{entry.period}" for entry in violating_entries]
                        
                        violations.append({
                            'type': 'Same Theory Subject Multiple Classes Per Day',
                            'class_group': class_group,
                            'subject': subject_code,
                            'day': day,
                            'count': count,
                            'entries': violating_entries,
                            'entry_details': entry_details,
                            'description': f"{subject_code} in {class_group} has {count} classes on {day} (max 1 allowed): {', '.join(entry_details)}"
                        })
                
                # Check distribution across weekdays
                days_used = set(entry.day for entry in subject_entries)
                total_classes = len(subject_entries)
                
                # If we have multiple classes, they should be distributed across different days
                if total_classes > 1 and len(days_used) < total_classes:
                    violations.append({
                        'type': 'Same Theory Subject Poor Distribution',
                        'class_group': class_group,
                        'subject': subject_code,
                        'total_classes': total_classes,
                        'days_used': len(days_used),
                        'days_list': list(days_used),
                        'description': f"{subject_code} in {class_group} has {total_classes} classes but only uses {len(days_used)} days ({', '.join(days_used)}) - should be distributed across different days"
                    })
        
        return violations
    
    def _check_breaks_between_classes(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check for breaks between classes - should be minimal breaks."""
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
                    if gap > 1:  # More than 1 period gap
                        violations.append({
                            'type': 'Break Between Classes',
                            'class_group': class_group,
                            'day': day,
                            'gap_size': gap,
                            'current_period': current_entry.period,
                            'next_period': next_entry.period,
                            'description': f"{class_group} has {gap} period gap on {day} between P{current_entry.period} and P{next_entry.period}"
                        })
        
        return violations
    
    def _check_teacher_breaks(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check teacher breaks - after 2 consecutive theory classes, teacher must have a break."""
        violations = []
        
        # Group entries by teacher and day
        teacher_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            if entry.teacher and not entry.is_practical:  # Only theory classes
                teacher_day_entries[entry.teacher.id][entry.day].append(entry)
        
        for teacher_id, day_entries in teacher_day_entries.items():
            teacher = Teacher.objects.get(id=teacher_id)
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
                            'teacher_name': teacher.name,
                            'day': day,
                            'sequence_length': len(sequence),
                            'periods': [entry.period for entry in sequence],
                            'description': f"Teacher {teacher.name} has {len(sequence)} consecutive theory classes on {day} (max 2 allowed)"
                        })
        
        return violations
    
    def _find_consecutive_sequences(self, entries: List[TimetableEntry]) -> List[List[TimetableEntry]]:
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
    
    def _check_empty_fridays(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check for empty Fridays - each class group should have at least one class on Friday."""
        violations = []
        
        # Get all class groups
        all_class_groups = set(entry.class_group for entry in entries)
        
        # Check each class group for empty Friday
        for class_group in all_class_groups:
            friday_entries = [entry for entry in entries 
                             if entry.class_group == class_group and entry.day == 'Friday']
            
            if not friday_entries:
                violations.append({
                    'type': 'Empty Friday',
                    'class_group': class_group,
                    'description': f"Class group {class_group} has no classes on Friday"
                })
        
        return violations 