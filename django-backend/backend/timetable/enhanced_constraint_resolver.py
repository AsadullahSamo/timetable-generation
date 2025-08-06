"""
ENHANCED CONSTRAINT RESOLVER
============================
Resolves constraint violations while maintaining the enhanced room allocation system.
Focuses on the specific issues mentioned by the client:
- Room allocation conflicts
- Practical session management
- Constraint conflicts during resolution
- NEW: Same theory subject distribution
- NEW: Breaks between classes
- NEW: Teacher breaks after 2 consecutive classes
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import time, timedelta
import random

from .models import TimetableEntry, Subject, Teacher, Classroom, ScheduleConfig, Batch
from .enhanced_constraint_validator import EnhancedConstraintValidator
from .enhanced_room_allocator import EnhancedRoomAllocator


class EnhancedConstraintResolver:
    """
    Enhanced constraint resolver that works with the enhanced room allocation system.
    """
    
    def __init__(self):
        self.validator = EnhancedConstraintValidator()  # Use enhanced validator
        self.room_allocator = EnhancedRoomAllocator()
        self.max_iterations = 30
        self.schedule_config = None
        
        # Resolution strategies
        self.resolution_strategies = {
            'Subject Frequency': self._resolve_subject_frequency,
            'Practical Blocks': self._resolve_practical_blocks,
            'Teacher Conflicts': self._resolve_teacher_conflicts,
            'Room Conflicts': self._resolve_room_conflicts,
            'Friday Time Limits': self._resolve_friday_time_limits,
            'Minimum Daily Classes': self._resolve_minimum_daily_classes,
            'Thesis Day Constraint': self._resolve_thesis_day,
            'Compact Scheduling': self._resolve_compact_scheduling,
            'Cross Semester Conflicts': self._resolve_cross_semester_conflicts,
            'Teacher Assignments': self._resolve_teacher_assignments,
            'Friday Aware Scheduling': self._resolve_friday_aware_scheduling,
            'Empty Friday Fix': self._resolve_empty_fridays,
            # NEW CONSTRAINTS
            'Same Theory Subject Distribution': self._resolve_same_theory_subject_distribution,
            'Breaks Between Classes': self._resolve_breaks_between_classes,
            'Teacher Breaks': self._resolve_teacher_breaks,
        }
    
    def _get_schedule_config(self):
        """Get the current schedule configuration."""
        if not self.schedule_config:
            self.schedule_config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
        return self.schedule_config
    
    def resolve_all_violations(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        """
        Resolve all constraint violations with enhanced room allocation support.
        """
        print("🔧 ENHANCED CONSTRAINT RESOLUTION")
        print("=" * 50)
        
        current_entries = list(entries)
        iteration = 0
        resolution_log = []
        initial_violations = self.validator.validate_all_constraints(current_entries)['total_violations']
        
        print(f"📊 Initial violations: {initial_violations}")
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n🔄 Resolution Iteration {iteration}")
            
            # Validate current state
            validation_result = self.validator.validate_all_constraints(current_entries)
            current_violations = validation_result['total_violations']
            
            if current_violations == 0:
                print(f"🎉 All constraints satisfied in {iteration} iterations!")
                break
            
            print(f"Found {current_violations} violations to resolve...")
            
            # Apply resolution strategies
            current_entries = self._apply_resolution_strategies(current_entries, validation_result)
            
            # Log resolution progress
            resolution_log.append({
                'iteration': iteration,
                'violations': current_violations,
                'strategies_applied': len(validation_result['violations_by_constraint'])
            })
        
        final_violations = self.validator.validate_all_constraints(current_entries)['total_violations']
        
        return {
            'initial_violations': initial_violations,
            'final_violations': final_violations,
            'iterations_completed': iteration,
            'resolution_log': resolution_log,
            'overall_success': final_violations == 0,
            'entries': current_entries
        }
    
    def _apply_resolution_strategies(self, entries: List[TimetableEntry], 
                                   validation_result: Dict) -> List[TimetableEntry]:
        """Apply resolution strategies for all violation types."""
        current_entries = list(entries)
        
        # Sort violations by priority (room conflicts first, then practical blocks, etc.)
        priority_order = [
            'Room Conflicts',
            'Practical Blocks', 
            'Subject Frequency',
            'Teacher Conflicts',
            'Friday Time Limits',
            'Minimum Daily Classes',
            'Empty Friday Fix',
            'Compact Scheduling',
            'Cross Semester Conflicts',
            'Teacher Assignments',
            'Friday Aware Scheduling',
            'Thesis Day Constraint',
            # NEW CONSTRAINTS - Add to priority order
            'Same Theory Subject Distribution',
            'Breaks Between Classes',
            'Teacher Breaks'
        ]
        
        for constraint_name in priority_order:
            violations = validation_result['violations_by_constraint'].get(constraint_name, [])
            if violations:
                print(f"  🔧 Resolving {constraint_name}: {len(violations)} violations")
                current_entries = self._resolve_constraint_type(current_entries, constraint_name, violations)
        
        return current_entries
    
    def _resolve_constraint_type(self, entries: List[TimetableEntry], constraint_name: str, 
                               violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve a specific type of constraint violation."""
        if constraint_name in self.resolution_strategies:
            return self.resolution_strategies[constraint_name](entries, violations)
        else:
            print(f"  ⚠️ No resolution strategy for {constraint_name}")
            return entries
    
    # NEW CONSTRAINT RESOLUTION METHODS
    
    def _resolve_same_theory_subject_distribution(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve same theory subject distribution violations."""
        print("  📚 Resolving same theory subject distribution violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            subject_code = violation.get('subject', '')
            class_group = violation.get('class_group', '')
            
            # Find all entries for this subject and class group
            subject_entries = [entry for entry in current_entries 
                             if entry.subject and entry.subject.code == subject_code 
                             and entry.class_group == class_group and not entry.is_practical]
            
            if len(subject_entries) > 1:
                print(f"    🔧 Fixing {subject_code} for {class_group}: {len(subject_entries)} classes")
                # More aggressive distribution across different days
                current_entries = self._distribute_theory_subject_across_days_aggressive(current_entries, subject_entries)
        
        return current_entries
    
    def _distribute_theory_subject_across_days_aggressive(self, entries: List[TimetableEntry], subject_entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Aggressively distribute theory subject classes across different days."""
        if len(subject_entries) <= 1:
            return entries
        
        # Get available days
        config = self._get_schedule_config()
        if not config:
            return entries
        
        available_days = config.days.copy()
        class_group = subject_entries[0].class_group
        
        # Group entries by day to see current distribution
        day_entries = defaultdict(list)
        for entry in subject_entries:
            day_entries[entry.day].append(entry)
        
        print(f"    📅 Current distribution: {dict(day_entries)}")
        
        # Find days with multiple classes of this subject
        problematic_days = [day for day, day_entries_list in day_entries.items() if len(day_entries_list) > 1]
        
        for day in problematic_days:
            day_entries_list = day_entries[day]
            # Keep first entry, move the rest
            entries_to_move = day_entries_list[1:]
            
            for entry in entries_to_move:
                # Find a better day for this entry
                better_day = self._find_better_day_for_subject(entries, class_group, entry.subject, day)
                
                if better_day:
                    # Find available period on better day
                    available_period = self._find_available_period_on_day(entries, class_group, better_day)
                    
                    if available_period:
                        # Check if this slot is actually available
                        if self._is_slot_available(entries, class_group, better_day, available_period):
                            entry.day = better_day
                            entry.period = available_period
                            print(f"    ✅ Moved {entry.subject.code} from {day} to {better_day} P{available_period}")
                        else:
                            # Try to find another available slot
                            alternative_slot = self._find_alternative_slot_for_entry(entries, entry, better_day)
                            if alternative_slot:
                                entry.day = alternative_slot[0]
                                entry.period = alternative_slot[1]
                                print(f"    ✅ Moved {entry.subject.code} to alternative slot {alternative_slot[0]} P{alternative_slot[1]}")
                            else:
                                # Force move to any available day
                                forced_day = self._find_any_available_day(entries, class_group, entry.subject, day)
                                if forced_day:
                                    forced_period = self._find_any_available_period(entries, class_group, forced_day)
                                    if forced_period:
                                        entry.day = forced_day
                                        entry.period = forced_period
                                        print(f"    ⚡ Force moved {entry.subject.code} to {forced_day} P{forced_period}")
        
        return entries
    
    def _find_better_day_for_subject(self, entries: List[TimetableEntry], class_group: str, subject: Subject, exclude_day: str) -> str:
        """Find a better day for a subject that doesn't have this subject yet."""
        config = self._get_schedule_config()
        if not config:
            return None
        
        # Get all days except the excluded day
        available_days = [day for day in config.days if day != exclude_day]
        
        # Check which days don't have this subject for this class group
        for day in available_days:
            day_entries = [entry for entry in entries 
                          if entry.class_group == class_group 
                          and entry.day == day 
                          and entry.subject == subject 
                          and not entry.is_practical]
            
            if len(day_entries) == 0:
                return day
        
        return None
    
    def _find_alternative_slot_for_entry(self, entries: List[TimetableEntry], entry: TimetableEntry, target_day: str) -> Tuple[str, int]:
        """Find an alternative slot for an entry on a specific day."""
        config = self._get_schedule_config()
        if not config:
            return None
        
        # Try all periods on the target day
        for period in config.periods:
            if self._is_slot_available(entries, entry.class_group, target_day, period):
                return (target_day, period)
        
        return None
    
    def _find_any_available_day(self, entries: List[TimetableEntry], class_group: str, subject: Subject, exclude_day: str) -> str:
        """Find any available day for a subject."""
        config = self._get_schedule_config()
        if not config:
            return None
        
        for day in config.days:
            if day != exclude_day:
                # Check if this day has fewer classes of this subject
                day_entries = [entry for entry in entries 
                              if entry.class_group == class_group 
                              and entry.day == day 
                              and entry.subject == subject 
                              and not entry.is_practical]
                
                if len(day_entries) == 0:
                    return day
        
        return None
    
    def _find_any_available_period(self, entries: List[TimetableEntry], class_group: str, day: str) -> int:
        """Find any available period on a day."""
        config = self._get_schedule_config()
        if not config:
            return None
        
        for period in config.periods:
            if self._is_slot_available(entries, class_group, day, period):
                return period
        
        return None
    
    def _resolve_breaks_between_classes(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve breaks between classes violations."""
        print("  ⏱️ Resolving breaks between classes violations...")
        
        current_entries = list(entries)
        
        # Group entries by class group and day
        class_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in current_entries:
            class_day_entries[entry.class_group][entry.day].append(entry)
        
        # Check for breaks between classes for each class group
        for class_group, day_entries in class_day_entries.items():
            for day, day_entries_list in day_entries.items():
                # Sort by period
                day_entries_list.sort(key=lambda x: x.period)
                
                # Check for gaps between consecutive classes
                for i in range(len(day_entries_list) - 1):
                    current_entry = day_entries_list[i]
                    next_entry = day_entries_list[i + 1]
                    
                    # If there's a gap of more than 1 period, try to fill it
                    if next_entry.period - current_entry.period > 1:
                        # Try to move next entry to fill the gap
                        if self._can_move_entry_to_period(next_entry, current_entries, day, current_entry.period + 1):
                            next_entry.period = current_entry.period + 1
                            print(f"    ✅ Filled gap for {class_group} on {day}")
        
        return current_entries
    
    def _resolve_teacher_breaks(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve teacher breaks violations (after 2 consecutive theory classes)."""
        print("  👨‍🏫 Resolving teacher breaks violations...")
        
        current_entries = list(entries)
        
        # Group entries by teacher and day
        teacher_day_entries = defaultdict(lambda: defaultdict(list))
        for entry in current_entries:
            if entry.teacher and not entry.is_practical:  # Only theory classes
                teacher_day_entries[entry.teacher.id][entry.day].append(entry)
        
        # Check for teachers with more than 2 consecutive theory classes
        for teacher_id, day_entries in teacher_day_entries.items():
            for day, day_entries_list in day_entries.items():
                # Sort by period
                day_entries_list.sort(key=lambda x: x.period)
                
                # Find consecutive sequences
                consecutive_sequences = self._find_consecutive_sequences(day_entries_list)
                
                for sequence in consecutive_sequences:
                    if len(sequence) > 2:
                        # Need to break up this sequence
                        current_entries = self._break_teacher_consecutive_sequence(current_entries, sequence)
        
        return current_entries
    
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
    
    def _break_teacher_consecutive_sequence(self, entries: List[TimetableEntry], sequence: List[TimetableEntry]) -> List[TimetableEntry]:
        """Break up a consecutive sequence of teacher classes."""
        if len(sequence) <= 2:
            return entries
        
        # Keep first 2 entries, move the rest
        entries_to_move = sequence[2:]
        
        for entry in entries_to_move:
            # Try to move to a different day
            config = self._get_schedule_config()
            if not config:
                continue
            
            for day in config.days:
                if day == entry.day:
                    continue
                
                # Find available period on different day
                available_period = self._find_available_period_on_day(entries, entry.class_group, day)
                
                if available_period:
                    entry.day = day
                    entry.period = available_period
                    print(f"    ✅ Moved teacher {entry.teacher.name} class to {day} P{available_period} to avoid consecutive sequence")
                    break
        
        return entries
    
    def _find_available_period_on_day(self, entries: List[TimetableEntry], class_group: str, day: str) -> int:
        """Find available period on a specific day for a class group."""
        config = self._get_schedule_config()
        if not config:
            return None
        
        # Get all periods used by this class group on this day
        used_periods = set(entry.period for entry in entries 
                          if entry.class_group == class_group and entry.day == day)
        
        # Find first available period
        for period in config.periods:
            if period not in used_periods:
                return period
        
        return None
    
    # EXISTING RESOLUTION METHODS (keep all existing ones)
    
    def _resolve_room_conflicts(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve room conflicts using enhanced room allocation."""
        print("  🏫 Resolving room conflicts...")
        
        current_entries = list(entries)
        
        for violation in violations:
            if violation['type'] == 'Room Double Booking':
                # Find the conflicting entries
                conflicting_entries = self._find_conflicting_entries(current_entries, violation)
                
                for entry in conflicting_entries:
                    # Try to find an alternative room
                    alternative_room = self._find_alternative_room_for_entry(entry, current_entries)
                    if alternative_room:
                        entry.classroom = alternative_room
                        print(f"    ✅ Moved {entry.subject.code} to {alternative_room.name}")
                    else:
                        print(f"    ❌ Could not find alternative room for {entry.subject.code}")
            
            elif violation['type'] == 'Practical Not in Lab':
                # Move practical to lab
                entry = self._find_entry_by_violation(current_entries, violation)
                if entry:
                    lab = self._find_available_lab_for_entry(entry, current_entries)
                    if lab:
                        entry.classroom = lab
                        print(f"    ✅ Moved practical {entry.subject.code} to lab {lab.name}")
                    else:
                        print(f"    ❌ Could not find available lab for {entry.subject.code}")
            
            elif violation['type'] == 'Practical Multiple Labs':
                # Consolidate practical blocks to same lab
                current_entries = self._consolidate_practical_blocks(current_entries, violation)
        
        return current_entries
    
    def _resolve_practical_blocks(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve practical block violations."""
        print("  🧪 Resolving practical block violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            if 'consecutive' in violation.get('description', '').lower():
                # Make practical periods consecutive
                current_entries = self._make_practical_consecutive(current_entries, violation)
            elif 'same lab' in violation.get('description', '').lower():
                # Ensure same lab for practical blocks
                current_entries = self._ensure_same_lab_for_practical(current_entries, violation)
        
        return current_entries
    
    def _resolve_subject_frequency(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve subject frequency violations."""
        print("  📚 Resolving subject frequency violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            subject_code = violation.get('subject', '')
            class_group = violation.get('class_group', '')
            expected = violation.get('expected', 0)
            actual = violation.get('actual', 0)
            
            if actual < expected:
                # Add missing classes
                classes_to_add = expected - actual
                current_entries = self._add_missing_classes(current_entries, class_group, subject_code, classes_to_add)
            elif actual > expected:
                # Remove excess classes
                classes_to_remove = actual - expected
                current_entries = self._remove_excess_classes(current_entries, class_group, subject_code, classes_to_remove)
        
        return current_entries
    
    def _resolve_teacher_conflicts(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve teacher conflict violations."""
        print("  👨‍🏫 Resolving teacher conflicts...")
        
        current_entries = list(entries)
        
        for violation in violations:
            # Find alternative teacher or reschedule
            entry = self._find_entry_by_violation(current_entries, violation)
            if entry:
                alternative_teacher = self._find_alternative_teacher_for_subject(entry.subject, entry.day, entry.period, current_entries)
                if alternative_teacher:
                    entry.teacher = alternative_teacher
                    print(f"    ✅ Assigned alternative teacher {alternative_teacher.name} for {entry.subject.code}")
                else:
                    # Try to reschedule the class
                    if self._reschedule_entry(entry, current_entries):
                        print(f"    ✅ Rescheduled {entry.subject.code} to avoid teacher conflict")
        
        return current_entries
    
    def _resolve_friday_time_limits(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve Friday time limit violations."""
        print("  🕐 Resolving Friday time limit violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            entry = self._find_entry_by_violation(current_entries, violation)
            if entry and entry.day == 'Friday':
                # Try to move to earlier period on Friday
                if self._move_to_earlier_friday_period(entry, current_entries):
                    print(f"    ✅ Moved {entry.subject.code} to earlier Friday period")
                else:
                    # Try to move to another day
                    if self._move_to_another_day(entry, current_entries):
                        print(f"    ✅ Moved {entry.subject.code} to another day")
        
        return current_entries
    
    def _resolve_minimum_daily_classes(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve minimum daily classes violations."""
        print("  📅 Resolving minimum daily classes violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            class_group = violation.get('class_group', '')
            day = violation.get('day', '')
            
            # Add classes to meet minimum daily requirement
            current_entries = self._add_classes_for_daily_minimum(current_entries, class_group, day)
        
        return current_entries
    
    def _resolve_thesis_day(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve thesis day constraint violations."""
        print("  📝 Resolving thesis day violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            # Move non-thesis classes from Wednesday
            entry = self._find_entry_by_violation(current_entries, violation)
            if entry and entry.day == 'Wednesday':
                if self._move_to_another_day(entry, current_entries):
                    print(f"    ✅ Moved non-thesis class {entry.subject.code} from Wednesday")
        
        return current_entries
    
    def _resolve_compact_scheduling(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve compact scheduling violations."""
        print("  ⏱️ Resolving compact scheduling violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            entry = self._find_entry_by_violation(current_entries, violation)
            if entry:
                # Try to move to a more compact slot
                if self._move_to_compact_slot(entry, current_entries):
                    print(f"    ✅ Moved {entry.subject.code} to more compact slot")
        
        return current_entries
    
    def _resolve_cross_semester_conflicts(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve cross-semester conflict violations."""
        print("  🔄 Resolving cross-semester conflicts...")
        
        current_entries = list(entries)
        
        for violation in violations:
            entry = self._find_entry_by_violation(current_entries, violation)
            if entry:
                # Try to reschedule to avoid cross-semester conflict
                if self._reschedule_entry(entry, current_entries):
                    print(f"    ✅ Rescheduled {entry.subject.code} to avoid cross-semester conflict")
        
        return current_entries
    
    def _resolve_teacher_assignments(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve teacher assignment violations."""
        print("  👨‍🏫 Resolving teacher assignment violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            entry = self._find_entry_by_violation(current_entries, violation)
            if entry:
                # Find appropriate teacher for the subject
                appropriate_teacher = self._find_appropriate_teacher_for_subject(entry.subject, entry.class_group)
                if appropriate_teacher:
                    entry.teacher = appropriate_teacher
                    print(f"    ✅ Assigned appropriate teacher {appropriate_teacher.name} for {entry.subject.code}")
        
        return current_entries
    
    def _resolve_friday_aware_scheduling(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve Friday-aware scheduling violations."""
        print("  📅 Resolving Friday-aware scheduling violations...")
        
        current_entries = list(entries)
        
        for violation in violations:
            entry = self._find_entry_by_violation(current_entries, violation)
            if entry:
                # Move classes to earlier in the week to leave room for Friday
                if self._move_to_earlier_week_slot(entry, current_entries):
                    print(f"    ✅ Moved {entry.subject.code} to earlier week slot")
        
        return current_entries
    
    def _resolve_empty_fridays(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve empty Friday violations by adding classes to empty Fridays."""
        print("  📅 Resolving empty Friday violations...")
        
        current_entries = list(entries)
        
        # Get all class groups
        all_class_groups = set(entry.class_group for entry in current_entries)
        
        # Check each class group for empty Friday
        for class_group in all_class_groups:
            friday_entries = [entry for entry in current_entries 
                             if entry.class_group == class_group and entry.day == 'Friday']
            
            if not friday_entries:
                print(f"    🔧 Adding classes to empty Friday for {class_group}")
                current_entries = self._add_classes_to_empty_friday(current_entries, class_group)
        
        return current_entries
    
    def _add_classes_to_empty_friday(self, entries: List[TimetableEntry], class_group: str) -> List[TimetableEntry]:
        """Add classes to an empty Friday for a class group."""
        # Get subjects that need more classes for this class group
        subjects_needing = self._get_subjects_needing_more_classes(entries, class_group)
        
        if not subjects_needing:
            return entries
        
        # Get available periods on Friday
        available_periods = self._find_available_periods_on_day(entries, class_group, 'Friday')
        
        if not available_periods:
            return entries
        
        # Add classes to Friday
        classes_added = 0
        max_classes_to_add = min(3, len(available_periods))  # Add up to 3 classes to Friday
        
        for subject_code, needed_count in subjects_needing.items():
            if classes_added >= max_classes_to_add:
                break
            
            if needed_count > 0:
                # Find subject and teacher
                subject = Subject.objects.filter(code=subject_code).first()
                if subject:
                    teacher = self._find_appropriate_teacher_for_subject(subject, class_group)
                    
                    if teacher:
                        # Find available period
                        for period in available_periods:
                            if self._is_slot_available(entries, class_group, 'Friday', period):
                                # Allocate room
                                if subject.is_practical:
                                    room = self.room_allocator.allocate_room_for_practical(
                                        'Friday', period, class_group, subject, entries
                                    )
                                else:
                                    room = self.room_allocator.allocate_room_for_theory(
                                        'Friday', period, class_group, subject, entries
                                    )
                                
                                if room:
                                    # Create entry
                                    new_entry = self._create_entry('Friday', period, subject, teacher, room, class_group, subject.is_practical)
                                    entries.append(new_entry)
                                    available_periods.remove(period)
                                    classes_added += 1
                                    print(f"    ✅ Added {subject_code} to Friday P{period} for {class_group}")
                                    break
        
        return entries
    
    # Helper methods (keep all existing ones)
    
    def _find_conflicting_entries(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Find entries involved in a room conflict."""
        room_id = violation.get('room_id')
        day = violation.get('day')
        
        return [entry for entry in entries 
                if entry.classroom and entry.classroom.id == room_id and entry.day == day]
    
    def _find_entry_by_violation(self, entries: List[TimetableEntry], violation: Dict) -> TimetableEntry:
        """Find a specific entry based on violation details."""
        entry_id = violation.get('entry_id')
        if entry_id:
            for entry in entries:
                if entry.id == entry_id:
                    return entry
        
        # Fallback: find by subject and class group
        subject_code = violation.get('subject', '')
        class_group = violation.get('class_group', '')
        day = violation.get('day', '')
        
        for entry in entries:
            if (entry.subject and entry.subject.code == subject_code and
                entry.class_group == class_group and entry.day == day):
                return entry
        
        return None
    
    def _find_alternative_room_for_entry(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> Classroom:
        """Find an alternative room for an entry."""
        if entry.is_practical:
            return self.room_allocator.allocate_room_for_practical(
                entry.day, entry.period, entry.class_group, entry.subject, entries
            )
        else:
            return self.room_allocator.allocate_room_for_theory(
                entry.day, entry.period, entry.class_group, entry.subject, entries
            )
    
    def _find_available_lab_for_entry(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> Classroom:
        """Find an available lab for a practical entry."""
        available_labs = self.room_allocator.get_available_labs_for_time(
            entry.day, entry.period, 1, entries
        )
        return available_labs[0] if available_labs else None
    
    def _consolidate_practical_blocks(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Consolidate practical blocks to use the same lab."""
        subject_code = violation.get('subject', '')
        class_group = violation.get('class_group', '')
        day = violation.get('day', '')
        
        # Find all practical entries for this subject on this day
        practical_entries = [entry for entry in entries 
                           if entry.is_practical and entry.subject.code == subject_code 
                           and entry.class_group == class_group and entry.day == day]
        
        if len(practical_entries) >= 3:
            # Find a lab that can accommodate all 3 periods
            periods = sorted([entry.period for entry in practical_entries])
            start_period = periods[0]
            
            lab = self.room_allocator.allocate_room_for_practical(
                day, start_period, class_group, practical_entries[0].subject, entries
            )
            
            if lab:
                # Assign all practical entries to the same lab
                for entry in practical_entries:
                    entry.classroom = lab
                print(f"    ✅ Consolidated practical {subject_code} to lab {lab.name}")
        
        return entries
    
    def _make_practical_consecutive(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Make practical periods consecutive."""
        subject_code = violation.get('subject', '')
        class_group = violation.get('class_group', '')
        day = violation.get('day', '')
        
        # Find practical entries for this subject on this day
        practical_entries = [entry for entry in entries 
                           if entry.is_practical and entry.subject.code == subject_code 
                           and entry.class_group == class_group and entry.day == day]
        
        if len(practical_entries) >= 3:
            # Sort by period and make consecutive
            practical_entries.sort(key=lambda x: x.period)
            
            # Ensure they are consecutive starting from the first period
            start_period = practical_entries[0].period
            for i, entry in enumerate(practical_entries[:3]):
                entry.period = start_period + i
            
            print(f"    ✅ Made practical {subject_code} consecutive on {day}")
        
        return entries
    
    def _ensure_same_lab_for_practical(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Ensure all practical blocks use the same lab."""
        subject_code = violation.get('subject', '')
        class_group = violation.get('class_group', '')
        day = violation.get('day', '')
        
        # Find practical entries for this subject on this day
        practical_entries = [entry for entry in entries 
                           if entry.is_practical and entry.subject.code == subject_code 
                           and entry.class_group == class_group and entry.day == day]
        
        if len(practical_entries) >= 3:
            # Find a lab that can accommodate all periods
            periods = sorted([entry.period for entry in practical_entries])
            start_period = periods[0]
            
            lab = self.room_allocator.allocate_room_for_practical(
                day, start_period, class_group, practical_entries[0].subject, entries
            )
            
            if lab:
                # Assign all practical entries to the same lab
                for entry in practical_entries:
                    entry.classroom = lab
                print(f"    ✅ Ensured same lab for practical {subject_code}")
        
        return entries
    
    def _add_missing_classes(self, entries: List[TimetableEntry], class_group: str, 
                            subject_code: str, count: int) -> List[TimetableEntry]:
        """Add missing classes for a subject."""
        subject = Subject.objects.filter(code=subject_code).first()
        if not subject:
            return entries
        
        # Find available slots
        available_slots = self._find_available_slots(entries, class_group, count)
        
        for i, (day, period) in enumerate(available_slots[:count]):
            # Find appropriate teacher
            teacher = self._find_appropriate_teacher_for_subject(subject, class_group)
            
            # Allocate room
            if subject.is_practical:
                room = self.room_allocator.allocate_room_for_practical(
                    day, period, class_group, subject, entries
                )
            else:
                room = self.room_allocator.allocate_room_for_theory(
                    day, period, class_group, subject, entries
                )
            
            if room and teacher:
                # Create new entry
                new_entry = self._create_entry(day, period, subject, teacher, room, class_group, subject.is_practical)
                entries.append(new_entry)
                print(f"    ✅ Added missing class for {subject_code} on {day} P{period}")
        
        return entries
    
    def _remove_excess_classes(self, entries: List[TimetableEntry], class_group: str, 
                              subject_code: str, count: int) -> List[TimetableEntry]:
        """Remove excess classes for a subject."""
        # Find entries for this subject and class group
        subject_entries = [entry for entry in entries 
                          if entry.subject and entry.subject.code == subject_code 
                          and entry.class_group == class_group]
        
        # Remove the last few entries (prefer removing later periods)
        subject_entries.sort(key=lambda x: (x.day, x.period))
        
        for entry in subject_entries[-count:]:
            entries.remove(entry)
            print(f"    ✅ Removed excess class for {subject_code}")
        
        return entries
    
    def _find_alternative_teacher_for_subject(self, subject: Subject, day: str, period: int, 
                                            entries: List[TimetableEntry]) -> Teacher:
        """Find an alternative teacher for a subject."""
        # Get all teachers for this subject
        teachers = Teacher.objects.filter(teachersubjectassignment__subject=subject)
        
        for teacher in teachers:
            # Check if teacher is available at this time
            if self._is_teacher_available(teacher, day, period, entries):
                return teacher
        
        return None
    
    def _find_appropriate_teacher_for_subject(self, subject: Subject, class_group: str) -> Teacher:
        """Find an appropriate teacher for a subject and class group."""
        # Get teachers assigned to this subject for this batch
        batch_name = class_group.split('-')[0] if '-' in class_group else class_group
        batch = Batch.objects.filter(name=batch_name).first()
        
        if batch:
            assignments = subject.teachersubjectassignment_set.filter(batch=batch)
            for assignment in assignments:
                return assignment.teacher
        
        # Fallback: get any teacher for this subject
        teachers = Teacher.objects.filter(teachersubjectassignment__subject=subject)
        return teachers.first() if teachers else None
    
    def _is_teacher_available(self, teacher: Teacher, day: str, period: int, 
                             entries: List[TimetableEntry]) -> bool:
        """Check if a teacher is available at a specific time."""
        return not any(
            entry.teacher and entry.teacher.id == teacher.id and
            entry.day == day and entry.period == period
            for entry in entries
        )
    
    def _find_available_slots(self, entries: List[TimetableEntry], class_group: str, 
                             count: int) -> List[Tuple[str, int]]:
        """Find available time slots for a class group."""
        config = self._get_schedule_config()
        if not config:
            return []
        
        days = config.days
        periods = config.periods
        
        available_slots = []
        
        for day in days:
            for period in periods:
                # Check if slot is available
                if self._is_slot_available(entries, class_group, day, period):
                    available_slots.append((day, period))
        
        return available_slots[:count]
    
    def _is_slot_available(self, entries: List[TimetableEntry], class_group: str, 
                          day: str, period: int) -> bool:
        """Check if a time slot is available for a class group."""
        return not any(
            entry.class_group == class_group and entry.day == day and entry.period == period
            for entry in entries
        )
    
    def _create_entry(self, day: str, period: int, subject: Subject, teacher: Teacher,
                     classroom: Classroom, class_group: str, is_practical: bool) -> TimetableEntry:
        """Create a new timetable entry."""
        config = self._get_schedule_config()
        if not config:
            raise ValueError("No schedule configuration found")
        
        # Calculate start and end times
        start_time = config.start_time
        lesson_duration = timedelta(minutes=config.lesson_duration)
        
        # Calculate actual start time for this period
        total_minutes = (period - 1) * (config.lesson_duration + 15)  # 15 min break
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
            lesson_duration
        )
        end_total_seconds = int(end_time_obj.total_seconds())
        end_hours = end_total_seconds // 3600
        end_minutes = (end_total_seconds % 3600) // 60
        end_time_obj = time(end_hours % 24, end_minutes)
        
        return TimetableEntry(
            day=day,
            period=period,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            class_group=class_group,
            start_time=start_time_obj,
            end_time=end_time_obj,
            is_practical=is_practical,
            schedule_config=config,
            semester=getattr(config, 'semester', 'Fall 2024'),
            academic_year=getattr(config, 'academic_year', '2024-2025')
        )
    
    def _move_to_earlier_friday_period(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> bool:
        """Move an entry to an earlier period on Friday."""
        if entry.day != 'Friday':
            return False
        
        # Try earlier periods on Friday
        for period in range(1, entry.period):
            if self._can_move_entry_to_period(entry, entries, 'Friday', period):
                entry.period = period
                return True
        
        return False
    
    def _move_to_another_day(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> bool:
        """Move an entry to another day."""
        config = self._get_schedule_config()
        if not config:
            return False
        
        for day in config.days:
            if day == entry.day:
                continue
            
            for period in config.periods:
                if self._can_move_entry_to_period(entry, entries, day, period):
                    entry.day = day
                    entry.period = period
                    return True
        
        return False
    
    def _can_move_entry_to_period(self, entry: TimetableEntry, entries: List[TimetableEntry], 
                                 day: str, period: int) -> bool:
        """Check if an entry can be moved to a specific period."""
        # Check if the slot is available
        if not self._is_slot_available(entries, entry.class_group, day, period):
            return False
        
        # Check if teacher is available
        if entry.teacher and not self._is_teacher_available(entry.teacher, day, period, entries):
            return False
        
        # Check if room is available
        if entry.classroom:
            room_available = not any(
                e.classroom and e.classroom.id == entry.classroom.id and
                e.day == day and e.period == period
                for e in entries
            )
            if not room_available:
                return False
        
        return True
    
    def _add_classes_for_daily_minimum(self, entries: List[TimetableEntry], class_group: str, 
                                      day: str) -> List[TimetableEntry]:
        """Add classes to meet minimum daily requirement."""
        # Count current classes for this class group on this day
        day_entries = [entry for entry in entries 
                      if entry.class_group == class_group and entry.day == day]
        
        if len(day_entries) < 2:  # Minimum 2 classes per day
            # Find subjects that need more classes
            subjects_needing_classes = self._get_subjects_needing_more_classes(entries, class_group)
            
            for subject_code, needed_count in subjects_needing_classes.items():
                if needed_count > 0:
                    # Find available slot on this day
                    available_periods = self._find_available_periods_on_day(entries, class_group, day)
                    
                    if available_periods:
                        period = available_periods[0]
                        subject = Subject.objects.filter(code=subject_code).first()
                        teacher = self._find_appropriate_teacher_for_subject(subject, class_group)
                        
                        if subject and teacher:
                            # Allocate room
                            if subject.is_practical:
                                room = self.room_allocator.allocate_room_for_practical(
                                    day, period, class_group, subject, entries
                                )
                            else:
                                room = self.room_allocator.allocate_room_for_theory(
                                    day, period, class_group, subject, entries
                                )
                            
                            if room:
                                new_entry = self._create_entry(day, period, subject, teacher, room, class_group, subject.is_practical)
                                entries.append(new_entry)
                                print(f"    ✅ Added class for {subject_code} on {day} to meet minimum")
                                break
        
        return entries
    
    def _get_subjects_needing_more_classes(self, entries: List[TimetableEntry], class_group: str) -> Dict[str, int]:
        """Get subjects that need more classes for a class group."""
        # Count current classes per subject
        subject_counts = defaultdict(int)
        for entry in entries:
            if entry.class_group == class_group and entry.subject:
                subject_counts[entry.subject.code] += 1
        
        # Check against expected counts
        subjects_needing = {}
        for subject in Subject.objects.filter(batch=class_group.split('-')[0] if '-' in class_group else class_group):
            expected_count = subject.credits
            actual_count = subject_counts.get(subject.code, 0)
            
            if actual_count < expected_count:
                subjects_needing[subject.code] = expected_count - actual_count
        
        return subjects_needing
    
    def _find_available_periods_on_day(self, entries: List[TimetableEntry], class_group: str, day: str) -> List[int]:
        """Find available periods on a specific day for a class group."""
        config = self._get_schedule_config()
        if not config:
            return []
        
        available_periods = []
        for period in config.periods:
            if self._is_slot_available(entries, class_group, day, period):
                available_periods.append(period)
        
        return available_periods
    
    def _move_to_compact_slot(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> bool:
        """Move an entry to a more compact slot."""
        config = self._get_schedule_config()
        if not config:
            return False
        
        # Try to move to earlier periods on the same day
        for period in range(1, entry.period):
            if self._can_move_entry_to_period(entry, entries, entry.day, period):
                entry.period = period
                return True
        
        return False
    
    def _reschedule_entry(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> bool:
        """Reschedule an entry to avoid conflicts."""
        config = self._get_schedule_config()
        if not config:
            return False
        
        # Try different days and periods
        for day in config.days:
            for period in config.periods:
                if self._can_move_entry_to_period(entry, entries, day, period):
                    entry.day = day
                    entry.period = period
                    return True
        
        return False
    
    def _move_to_earlier_week_slot(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> bool:
        """Move an entry to an earlier slot in the week."""
        config = self._get_schedule_config()
        if not config:
            return False
        
        # Prefer earlier days and periods
        for day in config.days:
            if day == 'Friday':  # Skip Friday to leave room
                continue
            
            for period in config.periods:
                if self._can_move_entry_to_period(entry, entries, day, period):
                    entry.day = day
                    entry.period = period
                    return True
        
        return False 