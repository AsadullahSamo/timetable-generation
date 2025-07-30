"""
Minimal Impact Constraint Fixer
Makes the smallest possible changes to achieve zero violations.
"""

from typing import List, Dict, Set, Tuple, Optional
from .models import TimetableEntry, Subject, Teacher, Classroom, TeacherSubjectAssignment
from .constraint_validator import ConstraintValidator


class MinimalConstraintFixer:
    """Minimal impact constraint fixer that makes the smallest changes possible."""
    
    def __init__(self):
        self.validator = ConstraintValidator()
    
    def fix_with_minimal_impact(self, entries: List[TimetableEntry]) -> Dict:
        """Fix constraints with minimal impact on the existing timetable."""
        print("🎯 MINIMAL IMPACT CONSTRAINT FIXER")
        print("=" * 50)
        
        current_entries = list(entries)
        initial_result = self.validator.validate_all_constraints(current_entries)
        initial_violations = initial_result['total_violations']
        
        print(f"📊 Initial violations: {initial_violations}")
        
        # Show initial violation breakdown
        for constraint, violations in initial_result['violations_by_constraint'].items():
            if violations:
                print(f"  • {constraint}: {len(violations)} violations")
        
        if initial_violations == 0:
            print("🎉 Already perfect! No violations found.")
            return {
                'initial_violations': 0,
                'final_violations': 0,
                'overall_success': True,
                'entries': current_entries
            }
        
        # Strategy 1: Fix compact scheduling by micro-adjustments
        compact_violations = initial_result['violations_by_constraint'].get('Compact Scheduling', [])
        if compact_violations:
            print(f"\n🔧 Micro-fixing {len(compact_violations)} compact scheduling violations...")
            current_entries = self._micro_fix_compact_scheduling(current_entries, compact_violations)
        
        # Strategy 2: Fix minimum daily classes by smart period swaps
        daily_violations = initial_result['violations_by_constraint'].get('Minimum Daily Classes', [])
        if daily_violations:
            print(f"\n🔧 Smart-fixing {len(daily_violations)} minimum daily class violations...")
            current_entries = self._smart_fix_daily_classes(current_entries, daily_violations)
        
        # Final validation
        final_result = self.validator.validate_all_constraints(current_entries)
        final_violations = final_result['total_violations']
        
        print(f"\n📊 Final violations: {final_violations}")
        
        if final_violations == 0:
            print("🎉 SUCCESS: Zero violations achieved with minimal impact!")
        else:
            print(f"⚠️ Reduced violations from {initial_violations} to {final_violations}")
            # Show remaining violations
            for constraint, violations in final_result['violations_by_constraint'].items():
                if violations:
                    print(f"  • {constraint}: {len(violations)} violations")
        
        return {
            'initial_violations': initial_violations,
            'final_violations': final_violations,
            'overall_success': final_violations == 0,
            'entries': current_entries,
            'improvement_percentage': ((initial_violations - final_violations) / initial_violations * 100) if initial_violations > 0 else 0
        }
    
    def _micro_fix_compact_scheduling(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Fix compact scheduling with micro-adjustments that don't disrupt other days."""
        print("  📍 Micro-adjusting periods for compact scheduling...")
        
        current_entries = list(entries)
        fixes_made = 0
        
        for violation in violations:
            class_group = violation.get('class_group')
            day = violation.get('day')
            
            if not class_group or not day:
                continue
            
            # Get all entries for this class group on this day
            day_entries = [e for e in current_entries 
                          if e.class_group == class_group and e.day == day]
            
            if len(day_entries) < 2:
                continue
            
            # Sort by period
            day_entries.sort(key=lambda e: e.period)
            periods = [e.period for e in day_entries]
            
            # Find the gap
            for i in range(len(periods) - 1):
                if periods[i+1] - periods[i] > 1:
                    # Found a gap, try to shift classes to close it
                    gap_start = periods[i] + 1
                    gap_end = periods[i+1] - 1
                    
                    # Try to shift the later class backward
                    later_entry = day_entries[i+1]
                    new_period = periods[i] + 1
                    
                    if self._can_shift_to_period(current_entries, later_entry, new_period):
                        later_entry.period = new_period
                        fixes_made += 1
                        print(f"    ✅ Micro-shift: {class_group} {day} P{periods[i+1]} → P{new_period}")
                        break
        
        print(f"  📊 Micro-fixes made: {fixes_made}")
        return current_entries
    
    def _smart_fix_daily_classes(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Fix daily class violations by smart period swaps within the same class group."""
        print("  📍 Smart period swaps for daily classes...")
        
        current_entries = list(entries)
        fixes_made = 0
        
        for violation in violations:
            class_group = violation.get('class_group')
            problem_day = violation.get('day')
            
            if not class_group or not problem_day:
                continue
            
            # Get entries for this class group on the problem day
            problem_day_entries = [e for e in current_entries 
                                  if e.class_group == class_group and e.day == problem_day]
            
            # If only one class and it's practical, try to find a theory class to swap
            if len(problem_day_entries) == 1 and problem_day_entries[0].is_practical:
                if self._smart_swap_for_daily_minimum(current_entries, class_group, problem_day):
                    fixes_made += 1
                    print(f"    ✅ Smart swap: Added theory class to {class_group} {problem_day}")
        
        print(f"  📊 Smart fixes made: {fixes_made}")
        return current_entries
    
    def _can_shift_to_period(self, entries: List[TimetableEntry], entry: TimetableEntry, new_period: int) -> bool:
        """Check if an entry can be shifted to a new period without conflicts."""
        
        # Check if the new period is already occupied by this class group
        for e in entries:
            if (e.class_group == entry.class_group and 
                e.day == entry.day and 
                e.period == new_period and 
                e != entry):
                return False
        
        # Check teacher availability
        for e in entries:
            if (e.teacher and entry.teacher and 
                e.teacher.id == entry.teacher.id and 
                e.day == entry.day and 
                e.period == new_period and 
                e != entry):
                return False
        
        # Check classroom availability
        for e in entries:
            if (e.classroom and entry.classroom and 
                e.classroom.id == entry.classroom.id and 
                e.day == entry.day and 
                e.period == new_period and 
                e != entry):
                return False
        
        # Check Friday constraints
        if entry.day.lower() == 'friday' and new_period > 4:
            return False
        
        return True
    
    def _smart_swap_for_daily_minimum(self, entries: List[TimetableEntry], 
                                     class_group: str, problem_day: str) -> bool:
        """Smart swap to fix daily minimum by finding a theory class to move to problem day."""
        
        # Find theory classes for this class group on other days
        theory_classes = [e for e in entries 
                         if (e.class_group == class_group and 
                             e.day != problem_day and 
                             not e.is_practical)]
        
        # Find days with multiple theory classes that can spare one
        day_counts = {}
        for entry in theory_classes:
            day_counts[entry.day] = day_counts.get(entry.day, 0) + 1
        
        # Look for days with multiple theory classes
        for entry in theory_classes:
            if day_counts[entry.day] > 1:  # This day has multiple theory classes
                # Try to move this class to the problem day
                available_period = self._find_available_period_smart(entries, class_group, problem_day)
                if available_period and self._can_shift_to_period(entries, entry, available_period):
                    # Check that moving this class won't create a compact scheduling violation
                    remaining_classes = [e for e in entries 
                                       if (e.class_group == class_group and 
                                           e.day == entry.day and e != entry)]
                    
                    if len(remaining_classes) >= 1:  # Still have at least one class on the original day
                        entry.day = problem_day
                        entry.period = available_period
                        return True
        
        return False
    
    def _find_available_period_smart(self, entries: List[TimetableEntry], 
                                    class_group: str, day: str) -> Optional[int]:
        """Find an available period that maintains compact scheduling."""
        
        # Get occupied periods for this class group on this day
        occupied_periods = set(e.period for e in entries 
                             if e.class_group == class_group and e.day == day)
        
        if not occupied_periods:
            return 1  # Start with period 1 if no classes
        
        # Try to place adjacent to existing classes for compactness
        min_period = min(occupied_periods)
        max_period = max(occupied_periods)
        
        # Try before first class
        if min_period > 1:
            candidate = min_period - 1
            if self._is_period_available(entries, class_group, day, candidate):
                return candidate
        
        # Try after last class
        max_allowed = 4 if day.lower() == 'friday' else 6
        if max_period < max_allowed:
            candidate = max_period + 1
            if self._is_period_available(entries, class_group, day, candidate):
                return candidate
        
        # Try any available period
        for period in range(1, max_allowed + 1):
            if (period not in occupied_periods and 
                self._is_period_available(entries, class_group, day, period)):
                return period
        
        return None
    
    def _is_period_available(self, entries: List[TimetableEntry], 
                           class_group: str, day: str, period: int) -> bool:
        """Check if a period is available for the class group."""
        
        # Check if period is already occupied by this class group
        for e in entries:
            if (e.class_group == class_group and 
                e.day == day and e.period == period):
                return False
        
        return True
