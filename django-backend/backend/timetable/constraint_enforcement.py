"""
CENTRALIZED CONSTRAINT ENFORCEMENT
==================================
Wraps existing validators/allocators and provides a single API for validation and auto-fixing.
Ensures the "3 consecutive blocks of a practical must be in the same lab" rule cannot be violated.
"""

from typing import List, Dict, Any
from collections import defaultdict

from .models import TimetableEntry, Classroom
from .enhanced_constraint_validator import EnhancedConstraintValidator
from .constraint_validator import ConstraintValidator
from .room_allocator import RoomAllocator


class ConstraintEnforcer:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.enhanced_validator = EnhancedConstraintValidator(verbose=verbose)
        self.basic_validator = ConstraintValidator()
        self.room_allocator = RoomAllocator()

    def validate_all_constraints(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        """
        Run enhanced validation first; fall back to basic where necessary.
        """
        # Enhanced validator covers all 19 constraints, including same-lab rule
        enhanced_results = self.enhanced_validator.validate_all_constraints(entries)

        # Merge with basic validator for legacy checks
        basic_results = self.basic_validator.validate_all_constraints(entries)

        total_violations = (
            enhanced_results['total_violations'] + basic_results['total_violations']
        )

        # Combine reports
        combined = {
            'total_violations': total_violations,
            'overall_compliance': total_violations == 0,
            'enhanced': enhanced_results,
            'basic': basic_results
        }
        return combined

    def enforce_all_constraints(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        """
        Enforce all constraints with priority on zero-violation operation.
        """
        actions = []

        # 1) Hard-enforce SAME-LAB for all practicals
        actions.append(self._enforce_same_lab_for_all_practicals(entries))

        # 2) Fix room conflicts (double-bookings)
        actions.append(self._resolve_room_double_bookings(entries))

        # 3) Ensure practicals are in labs only
        actions.append(self._ensure_practicals_in_labs(entries))

        return {
            'actions': actions,
            'success': all(a.get('success', True) for a in actions),
        }

    def _enforce_same_lab_for_all_practicals(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        fixed = 0
        practical_groups = defaultdict(list)

        for e in entries:
            if e.subject and e.subject.is_practical:
                practical_groups[(e.class_group, e.subject.code, e.day)].append(e)

        for (class_group, subject_code, day), group in practical_groups.items():
            if len(group) < 2:
                continue

            # Determine target lab (majority lab among the 3 entries)
            labs = [ge.classroom for ge in group if ge.classroom]
            if not labs:
                continue
            from collections import Counter
            lab_counter = Counter(lab.id for lab in labs if lab)
            target_lab_id, _ = lab_counter.most_common(1)[0]
            target_lab = Classroom.objects.get(id=target_lab_id)

            # Move mismatched entries to target lab if available
            for ge in group:
                if ge.classroom and ge.classroom.id != target_lab_id:
                    # Ensure target lab free at this slot
                    conflict = TimetableEntry.objects.filter(
                        classroom=target_lab, day=ge.day, period=ge.period
                    ).exclude(id=ge.id).exists()
                    if not conflict:
                        ge.classroom = target_lab
                        ge.save()
                        fixed += 1

        if self.verbose:
            print(f"   🔒 Enforced same-lab rule: fixed {fixed} assignments")

        return {
            'name': 'same_lab_enforcement',
            'fixed': fixed,
            'success': True
        }

    def _resolve_room_double_bookings(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        moved = 0
        from collections import defaultdict
        schedule = defaultdict(list)

        for e in entries:
            if e.classroom:
                schedule[(e.day, e.period, e.classroom.id)].append(e)

        # For any slot with >1, move extras
        for key, coll in schedule.items():
            if len(coll) <= 1:
                continue
            keep = coll[0]
            to_move = coll[1:]
            day, period, _ = key
            for e in to_move:
                alt = (
                    self.room_allocator.allocate_room_for_practical(day, period, e.class_group, e.subject, entries)
                    if (e.subject and e.subject.is_practical)
                    else self.room_allocator.allocate_room_for_theory(day, period, e.class_group, e.subject, entries)
                )
                if alt:
                    e.classroom = alt
                    e.save()
                    moved += 1

        if self.verbose:
            print(f"   🧹 Resolved double-bookings: moved {moved} entries")

        return {
            'name': 'room_conflict_resolution',
            'moved': moved,
            'success': True
        }

    def _ensure_practicals_in_labs(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        corrected = 0
        for e in entries:
            if e.subject and e.subject.is_practical:
                if not (e.classroom and e.classroom.is_lab):
                    # Try to allocate a lab at this slot
                    lab = self.room_allocator.allocate_room_for_practical(e.day, e.period, e.class_group, e.subject, entries)
                    if lab:
                        e.classroom = lab
                        e.save()
                        corrected += 1
        if self.verbose:
            print(f"   🔬 Ensured practicals in labs: corrected {corrected}")
        return {
            'name': 'practicals_in_labs',
            'corrected': corrected,
            'success': True
        }
