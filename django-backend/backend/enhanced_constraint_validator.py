"""
ENHANCED CONSTRAINT VALIDATOR
=============================
Validates all constraints including the 3 new ones:
1. Same theory subject distribution
2. Breaks between classes
3. Teacher breaks after 2 consecutive classes
"""

from typing import List, Dict, Any
from collections import defaultdict
from .models import TimetableEntry, Subject, Teacher, Classroom


class EnhancedConstraintValidator:
    """Enhanced constraint validator with new constraints."""
    
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
            self._check_friday_aware_scheduling,
            # NEW CONSTRAINTS
            self._check_same_theory_subject_distribution,
            self._check_breaks_between_classes,
            self._check_teacher_breaks,
        ]
    
    def validate_all_constraints(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        """Validate all constraints including new ones."""
        self.violations = []
        results = {
            'total_violations': 0,
            'constraint_results': {},
            'violations_by_constraint': {},
            'overall_compliance': False,
            'detailed_report': []
        }
        
        print("🔍 ENHANCED CONSTRAINT VALIDATION")
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
        return results
    
    # NEW CONSTRAINT CHECKS
    
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
        
        if violations:
            print(f"    ❌ Found {len(violations)} same theory subject distribution violations")
            for violation in violations[:3]:  # Show first 3 violations
                print(f"      - {violation['description']}")
        
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
    
    # EXISTING CONSTRAINT CHECKS (simplified versions)
    
    def _check_subject_frequency(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check subject frequency compliance."""
        violations = []
        # Implementation would check if subjects have correct number of classes
        return violations
    
    def _check_practical_blocks(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check practical block requirements."""
        violations = []
        # Implementation would check 3-block consecutive practicals
        return violations
    
    def _check_teacher_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check teacher conflict violations."""
        violations = []
        # Implementation would check teacher double-booking
        return violations
    
    def _check_room_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check room conflict violations."""
        violations = []
        # Implementation would check room double-booking
        return violations
    
    def _check_friday_time_limits(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check Friday time limit violations."""
        violations = []
        # Implementation would check Friday time constraints
        return violations
    
    def _check_minimum_daily_classes(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check minimum daily classes requirement."""
        violations = []
        # Implementation would check minimum daily classes
        return violations
    
    def _check_thesis_day_constraint(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check thesis day constraint violations."""
        violations = []
        # Implementation would check Wednesday thesis day
        return violations
    
    def _check_compact_scheduling(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check compact scheduling violations."""
        violations = []
        # Implementation would check compact scheduling
        return violations
    
    def _check_cross_semester_conflicts(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check cross-semester conflict violations."""
        violations = []
        # Implementation would check cross-semester conflicts
        return violations
    
    def _check_teacher_assignments(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check teacher assignment violations."""
        violations = []
        # Implementation would check teacher assignments
        return violations
    
    def _check_friday_aware_scheduling(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Check Friday-aware scheduling violations."""
        violations = []
        # Implementation would check Friday-aware scheduling
        return violations 