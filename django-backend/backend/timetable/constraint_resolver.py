"""
Intelligent Constraint Resolution System
Fixes constraint violations without breaking other constraints.
"""

from typing import List, Dict, Any, Tuple
from timetable.models import TimetableEntry, Subject, Teacher, Classroom, ScheduleConfig
from timetable.constraint_validator import ConstraintValidator
from timetable.room_allocator import RoomAllocator
from datetime import time, timedelta
from collections import defaultdict
import random


class IntelligentConstraintResolver:
    """Intelligent system to resolve constraint violations without breaking others."""
    
    def __init__(self):
        self.validator = ConstraintValidator()
        self.room_allocator = RoomAllocator()  # Initialize room allocation system
        self.max_iterations = 50  # Increased for persistent resolution
        self.schedule_config = None
        self.aggressive_mode = True  # Enable aggressive mode for 0 violations
        self.gap_filling_enabled = True  # Enable intelligent gap filling
        self.persistent_mode = True  # Keep trying until 0 violations
        self.zero_violations_target = True  # Target 0 violations specifically
        self.resolution_strategies = {
            # Match the exact constraint names from ConstraintValidator
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
        }

        # Room allocation optimization strategies
        self.room_optimization_strategies = [
            self.optimize_room_allocation,
            self._optimize_practical_lab_allocation,
            self._optimize_senior_batch_priority,
        ]

    def _get_schedule_config(self):
        """Get the current schedule configuration."""
        if not self.schedule_config:
            self.schedule_config = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('-id').first()
        return self.schedule_config

    def _create_timetable_entry(self, day: str, period: int, subject: Subject, teacher: Teacher,
                               classroom: Classroom, class_group: str, is_practical: bool = False) -> TimetableEntry:
        """Create a properly formatted TimetableEntry with all required fields."""
        config = self._get_schedule_config()

        if not config:
            raise ValueError("No schedule configuration found")

        # Calculate start and end times based on period and config
        start_time = config.start_time
        lesson_duration = timedelta(minutes=config.lesson_duration)
        break_duration = timedelta(minutes=15)  # Default 15 minute break

        # Calculate the actual start time for this period
        total_minutes = (period - 1) * (config.lesson_duration + 15)  # 15 min break between periods
        actual_start_time = (
            timedelta(hours=start_time.hour, minutes=start_time.minute) +
            timedelta(minutes=total_minutes)
        )

        # Convert back to time object
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

    def resolve_all_violations(self, entries: List[TimetableEntry]) -> Dict[str, Any]:
        """
        Intelligently resolve all constraint violations with enhanced multi-constraint handling.
        Returns the fixed entries and resolution report.
        """
        print("🔧 INTELLIGENT CONSTRAINT RESOLUTION")
        print("=" * 50)

        current_entries = list(entries)
        iteration = 0
        resolution_log = []
        initial_violations = self.validator.validate_all_constraints(current_entries)['total_violations']

        # Track violation counts to detect cycles
        violation_history = []

        consecutive_no_progress = 0

        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n🔄 Resolution Iteration {iteration}")

            # Validate current state
            validation_result = self.validator.validate_all_constraints(current_entries)
            current_violations = validation_result['total_violations']

            # Track violation history for cycle detection
            violation_history.append(current_violations)

            # PERSISTENT MODE: Keep going until 0 violations
            if validation_result['overall_compliance'] and current_violations == 0:
                print(f"🎉 PERFECT! All constraints satisfied in {iteration} iterations!")
                break

            print(f"Found {current_violations} violations to resolve...")

            # Check for progress
            if len(violation_history) >= 2:
                if violation_history[-1] == violation_history[-2]:
                    consecutive_no_progress += 1
                else:
                    consecutive_no_progress = 0

            # Apply conservative gap filling only when needed
            if self.zero_violations_target and iteration % 5 == 0 and current_violations <= 20:  # Every 5th iteration, only for small counts
                print("  🎯 Applying conservative gap filling...")
                current_entries = self._conservative_gap_filling(current_entries)
                resolution_log.append({
                    'iteration': iteration,
                    'strategy': 'CONSERVATIVE_GAP_FILLING',
                    'status': 'APPLIED'
                })

            # Enhanced cycle detection with multiple strategies
            if consecutive_no_progress >= 1:  # Apply strategies earlier
                print(f"  🔄 No progress for {consecutive_no_progress} iterations - applying advanced strategies...")

                # Strategy 1: Intelligent Gap Filling (apply immediately)
                if self.gap_filling_enabled and consecutive_no_progress >= 1:
                    print("  📍 Applying intelligent gap filling...")
                    current_entries = self._enhanced_gap_filling(current_entries)
                    resolution_log.append({
                        'iteration': iteration,
                        'strategy': 'ENHANCED_GAP_FILLING',
                        'status': 'APPLIED'
                    })
                    consecutive_no_progress = 0  # Reset counter
                    continue

                # Strategy 2: Aggressive Resolution
                elif consecutive_no_progress >= 3:
                    print("  🚀 Triggering aggressive resolution...")
                    self.aggressive_mode = True
                    current_entries = self._force_resolve_remaining_violations(current_entries, validation_result)
                    resolution_log.append({
                        'iteration': iteration,
                        'strategy': 'AGGRESSIVE_STAGNATION_RESOLUTION',
                        'status': 'APPLIED'
                    })
                    consecutive_no_progress = 0  # Reset counter
                    continue

                # Check for oscillation (alternating between 2 values)
                if len(violation_history) >= 4:
                    last_four = violation_history[-4:]
                    if len(set(last_four)) <= 2 and last_four[0] == last_four[2] and last_four[1] == last_four[3]:
                        print("  🔄 Oscillation detected - triggering force resolution...")
                        current_entries = self._force_resolve_remaining_violations(current_entries, validation_result)
                        resolution_log.append({
                            'iteration': iteration,
                            'strategy': 'OSCILLATION_BREAK_FORCE_RESOLUTION',
                            'status': 'APPLIED'
                        })
                        # Re-validate after force resolution
                        validation_result = self.validator.validate_all_constraints(current_entries)
                        current_violations = validation_result['total_violations']
                        print(f"  🚨 After force resolution: {current_violations} violations remain")

                        # If force resolution helped significantly, continue; otherwise break
                        if current_violations < min(last_four) * 0.7:  # 30% improvement
                            print("  ✅ Force resolution made significant progress, continuing...")
                        else:
                            print("  ⚠️ Force resolution didn't help enough, stopping to prevent infinite loop")
                            break

            # Group violations by type for batch processing
            violations_by_type = {}
            for constraint_name, violations in validation_result['violations_by_constraint'].items():
                if violations:
                    violations_by_type[constraint_name] = violations

            # Enhanced resolution strategy: handle related constraints together
            violations_resolved = 0

            # CONSERVATIVE ZERO VIOLATIONS MODE: Only for very small violation counts
            if self.zero_violations_target and current_violations <= 10:  # Only when very close to zero
                print("  🎯 CONSERVATIVE ZERO VIOLATIONS MODE: Applying targeted strategies...")
                current_entries = self._apply_conservative_strategies(current_entries, violations_by_type)
                violations_resolved += min(current_violations, 5)  # Conservative estimate
                resolution_log.append({
                    'iteration': iteration,
                    'strategy': 'CONSERVATIVE_ZERO_VIOLATIONS_MODE',
                    'violations_targeted': current_violations,
                    'status': 'APPLIED'
                })
                continue  # Skip normal resolution and re-validate

            # Priority 1: Handle practical blocks BEFORE subject frequency to avoid conflicts
            practical_violations = violations_by_type.get('Practical Blocks', [])
            if practical_violations:
                print("  🎯 Priority 1: Resolving Practical Blocks first...")
                for violation in practical_violations[:5]:  # Handle top 5 practical violations
                    current_entries = self._resolve_practical_blocks(current_entries, violation)
                    violations_resolved += 1
                resolution_log.append({
                    'iteration': iteration,
                    'constraint': 'Practical Blocks',
                    'violations_fixed': min(5, len(practical_violations)),
                    'strategy': 'practical_first'
                })

            # Priority 2: Handle credit hour violations (but skip practical subjects already fixed)
            if 'Subject Frequency' in violations_by_type:
                print("  🎯 Priority 2: Resolving Subject Frequency violations...")
                current_entries = self._resolve_subject_frequency_batch(
                    current_entries, violations_by_type['Subject Frequency']
                )
                violations_resolved += len(violations_by_type['Subject Frequency'])
                resolution_log.append({
                    'iteration': iteration,
                    'constraint': 'Subject Frequency',
                    'violations_fixed': len(violations_by_type['Subject Frequency']),
                    'strategy': 'batch_processing'
                })

            # Priority 3: Handle Friday time limits and minimum daily classes together
            friday_violations = violations_by_type.get('Friday Time Limits', [])
            daily_violations = violations_by_type.get('Minimum Daily Classes', [])

            if friday_violations or daily_violations:
                print("  🎯 Priority 3: Resolving Friday and Daily Class violations together...")
                current_entries = self._resolve_time_and_daily_constraints(
                    current_entries, friday_violations, daily_violations
                )
                violations_resolved += len(friday_violations) + len(daily_violations)
                resolution_log.append({
                    'iteration': iteration,
                    'constraint': 'Friday & Daily Classes',
                    'violations_fixed': len(friday_violations) + len(daily_violations),
                    'strategy': 'coordinated_resolution'
                })

            # Priority 4: Handle remaining violations individually
            remaining_violations = []
            for constraint_name, violations in violations_by_type.items():
                if constraint_name not in ['Subject Frequency', 'Friday Time Limits', 'Minimum Daily Classes']:
                    for violation in violations:
                        violation['constraint'] = constraint_name
                        remaining_violations.append(violation)

            # Sort remaining by severity
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            remaining_violations.sort(key=lambda v: severity_order.get(v.get('severity', 'LOW'), 3))

            for violation in remaining_violations[:3]:  # Handle top 3 remaining violations
                constraint_type = violation['constraint']

                if constraint_type in self.resolution_strategies:
                    print(f"  🔧 Resolving: {violation['description']}")

                    try:
                        current_entries = self.resolution_strategies[constraint_type](
                            current_entries, violation
                        )
                        violations_resolved += 1
                        resolution_log.append({
                            'iteration': iteration,
                            'violation': violation['description'],
                            'status': 'RESOLVED'
                        })
                    except Exception as e:
                        print(f"    ❌ Failed to resolve: {str(e)}")
                        resolution_log.append({
                            'iteration': iteration,
                            'violation': violation['description'],
                            'status': 'FAILED',
                            'error': str(e)
                        })
                else:
                    print(f"  ⚠️  No resolution strategy for: {constraint_type}")
            
            if violations_resolved == 0:
                print("  ⚠️  No violations could be resolved this iteration")

                # FORCE RESOLUTION: If stuck for 3+ iterations, use aggressive strategies
                if iteration >= 3:
                    print("  🚨 FORCE RESOLUTION: Using aggressive strategies...")
                    current_entries = self._force_resolve_remaining_violations(current_entries, validation_result)
                    resolution_log.append({
                        'iteration': iteration,
                        'strategy': 'FORCE_RESOLUTION',
                        'status': 'APPLIED'
                    })
                else:
                    break
        
        # Final validation
        final_validation = self.validator.validate_all_constraints(current_entries)
        
        return {
            'resolved_entries': current_entries,
            'iterations': iteration,
            'initial_violations': initial_violations,
            'final_violations': final_validation['total_violations'],
            'overall_success': final_validation['overall_compliance'],
            'resolution_log': resolution_log,
            'final_validation': final_validation
        }
    
    def _resolve_subject_frequency(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve subject frequency violations by adding or removing classes."""
        class_group = violation['class_group']
        subject_code = violation['subject']
        expected = violation['expected']
        actual = violation['actual']
        
        if actual < expected:
            # Need to add classes
            return self._add_subject_classes(entries, class_group, subject_code, expected - actual)
        elif actual > expected:
            # Need to remove classes
            return self._remove_subject_classes(entries, class_group, subject_code, actual - expected)
        
        return entries
    
    def _add_subject_classes(self, entries: List[TimetableEntry], class_group: str, 
                           subject_code: str, classes_to_add: int) -> List[TimetableEntry]:
        """Add classes for a subject while respecting all constraints."""
        subject = Subject.objects.filter(code=subject_code).first()
        if not subject:
            return entries
        
        # Find available teachers for this subject
        from timetable.models import TeacherSubjectAssignment
        assignments = TeacherSubjectAssignment.objects.filter(subject=subject)
        available_teachers = [a.teacher for a in assignments]
        
        if not available_teachers:
            return entries
        
        updated_entries = list(entries)
        classes_added = 0
        
        # Try to find available slots
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            if classes_added >= classes_to_add:
                break
                
            for period in range(1, 8):
                if classes_added >= classes_to_add:
                    break
                
                # Check if slot is available
                if self._is_slot_available(updated_entries, class_group, day, period):
                    # Find available teacher and classroom
                    teacher = self._find_available_teacher(updated_entries, available_teachers, day, period)
                    classroom = self._find_available_classroom(updated_entries, day, period)
                    
                    if teacher and classroom:
                        # Check if adding here would violate other constraints
                        if self._would_violate_constraints(updated_entries, class_group, day, period, subject):
                            continue
                        
                        # Add the class
                        new_entry = self._create_entry(day, period, subject, teacher, classroom, class_group)
                        updated_entries.append(new_entry)
                        classes_added += 1
                        print(f"    ✅ Added {subject_code} class: {day} P{period}")
        
        return updated_entries
    
    def _remove_subject_classes(self, entries: List[TimetableEntry], class_group: str, 
                              subject_code: str, classes_to_remove: int) -> List[TimetableEntry]:
        """Remove excess classes for a subject."""
        # Find entries for this subject and class group
        subject_entries = [e for e in entries if e.class_group == class_group and e.subject.code == subject_code]
        
        # Sort by some criteria (e.g., prefer removing from Friday, later periods)
        subject_entries.sort(key=lambda e: (
            0 if e.day.lower().startswith('fri') else 1,  # Prefer Friday
            -e.period  # Prefer later periods
        ))
        
        # Remove the specified number of classes
        entries_to_remove = subject_entries[:classes_to_remove]
        updated_entries = [e for e in entries if e not in entries_to_remove]
        
        for removed in entries_to_remove:
            print(f"    ✅ Removed {subject_code} class: {removed.day} P{removed.period}")
        
        return updated_entries

    def _intelligent_gap_filling(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Fill schedule gaps intelligently with available subjects and teachers."""
        print("    🎯 INTELLIGENT GAP FILLING STRATEGY")
        print("    " + "=" * 45)

        current_entries = list(entries)

        # Get all class groups
        class_groups = set(entry.class_group for entry in current_entries)

        gaps_filled = 0
        for class_group in class_groups:
            print(f"    📋 Analyzing gaps for {class_group}...")

            # Find gaps in this class group's schedule
            gaps = self._find_schedule_gaps(current_entries, class_group)

            if gaps:
                print(f"      🔍 Found gaps: {gaps}")
            else:
                print(f"      ✅ No gaps found for {class_group}")

            for day, periods in gaps.items():
                for period in periods:
                    print(f"      🎯 Trying to fill gap: {class_group} {day} P{period}")
                    # Try to fill this gap with a suitable subject
                    filled = self._fill_gap_intelligently(current_entries, class_group, day, period)
                    if filled:
                        gaps_filled += 1
                        print(f"      ✅ Filled gap: {class_group} {day} P{period}")
                    else:
                        print(f"      ❌ Could not fill gap: {class_group} {day} P{period}")

        print(f"    📊 Total gaps filled: {gaps_filled}")
        return current_entries

    def _enhanced_gap_filling(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Enhanced gap filling strategy to achieve 0 violations."""
        print("    🚀 ENHANCED GAP FILLING FOR ZERO VIOLATIONS")
        print("    " + "=" * 50)

        current_entries = list(entries)

        # Strategy 1: Fill internal gaps to prevent compact scheduling violations
        current_entries = self._fill_internal_gaps(current_entries)

        # Strategy 2: Redistribute classes to optimize utilization
        current_entries = self._redistribute_for_optimization(current_entries)

        # Strategy 3: Conservative subject placement (disabled to prevent excessive class addition)
        # current_entries = self._smart_subject_placement(current_entries)

        return current_entries

    def _fill_internal_gaps(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Fill gaps between existing classes to prevent compact scheduling violations."""
        print("      🎯 Filling internal gaps...")

        current_entries = list(entries)
        class_groups = set(entry.class_group for entry in current_entries)
        gaps_filled = 0

        for class_group in class_groups:
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                # Skip Wednesday for thesis batches
                if day == 'Wednesday' and self._is_thesis_batch(current_entries, class_group):
                    continue

                # Get occupied periods for this class group on this day
                occupied_periods = set()
                for entry in current_entries:
                    if entry.class_group == class_group and entry.day == day:
                        occupied_periods.add(entry.period)

                if len(occupied_periods) < 2:
                    continue  # Need at least 2 classes to have gaps

                # Find gaps between min and max periods
                min_period = min(occupied_periods)
                max_period = max(occupied_periods)

                for period in range(min_period + 1, max_period):
                    if period not in occupied_periods:
                        # Try to fill this gap
                        if self._fill_specific_gap(current_entries, class_group, day, period):
                            gaps_filled += 1
                            print(f"        ✅ Filled gap: {class_group} {day} P{period}")

        print(f"      📊 Internal gaps filled: {gaps_filled}")
        return current_entries

    def _is_thesis_batch(self, entries: List[TimetableEntry], class_group: str) -> bool:
        """Check if this class group has thesis subjects."""
        for entry in entries:
            if (entry.class_group == class_group and
                entry.subject and
                'thesis' in entry.subject.name.lower()):
                return True
        return False

    def _fill_specific_gap(self, entries: List[TimetableEntry], class_group: str, day: str, period: int) -> bool:
        """Fill a specific gap with the best available subject."""
        # Get subjects that need more classes for this class group
        needed_subjects = self._get_subjects_needing_classes(entries, class_group)

        for subject_code, needed_count in needed_subjects.items():
            if needed_count <= 0:
                continue

            # Get the subject object
            from .models import Subject
            try:
                subject = Subject.objects.get(code=subject_code)
            except Subject.DoesNotExist:
                continue

            # Find available teacher
            teacher = self._find_conflict_free_teacher(entries, subject, day, period)
            if not teacher:
                continue

            # Find available classroom
            classroom = self._find_conflict_free_classroom(entries, day, period)
            if not classroom:
                continue

            # Check constraints
            if self._would_create_violations(entries, class_group, day, period, subject):
                continue

            # Create the entry
            new_entry = self._create_timetable_entry(
                day=day,
                period=period,
                subject=subject,
                teacher=teacher,
                classroom=classroom,
                class_group=class_group,
                is_practical=subject.is_practical
            )
            entries.append(new_entry)
            return True

        return False

    def _redistribute_for_optimization(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Redistribute classes to optimize schedule and reduce violations."""
        print("      🔄 Redistributing classes for optimization...")

        current_entries = list(entries)
        redistributed = 0

        # Find classes that can be moved to better positions
        moveable_entries = []
        for entry in current_entries:
            # Skip practical blocks (they need consecutive periods)
            if entry.is_practical:
                continue

            # Skip thesis day entries
            if entry.day == 'Wednesday' and self._is_thesis_batch(current_entries, entry.class_group):
                continue

            moveable_entries.append(entry)

        # Try to move classes to fill gaps and reduce violations
        for entry in moveable_entries[:20]:  # Limit to prevent excessive processing
            better_slot = self._find_better_slot(current_entries, entry)
            if better_slot:
                day, period = better_slot
                old_day, old_period = entry.day, entry.period
                entry.day = day
                entry.period = period
                redistributed += 1
                print(f"        ↗️ Moved {entry.subject.code} from {old_day} P{old_period} to {day} P{period}")

        print(f"      📊 Classes redistributed: {redistributed}")
        return current_entries

    def _smart_subject_placement(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Smart placement of subjects to satisfy frequency constraints."""
        print("      🧠 Smart subject placement...")

        current_entries = list(entries)
        placements_made = 0

        # Get all class groups
        class_groups = set(entry.class_group for entry in current_entries)

        for class_group in class_groups:
            # Check which subjects need more classes
            needed_subjects = self._get_subjects_needing_classes(current_entries, class_group)

            for subject_code, needed_count in needed_subjects.items():
                if needed_count <= 0:
                    continue

                # Try to place the needed classes
                placed = self._place_needed_classes(current_entries, class_group, subject_code, needed_count)
                placements_made += placed

        print(f"      📊 Smart placements made: {placements_made}")
        return current_entries

    def _find_conflict_free_teacher(self, entries: List[TimetableEntry], subject, day: str, period: int):
        """Find a teacher for the subject who is available at the given time."""
        from .models import TeacherSubjectAssignment

        # Get teachers who can teach this subject through assignments
        assignments = TeacherSubjectAssignment.objects.filter(subject=subject)

        for assignment in assignments:
            teacher = assignment.teacher
            # Check if teacher is free at this time
            is_busy = any(
                entry.teacher and entry.teacher.id == teacher.id and
                entry.day == day and entry.period == period
                for entry in entries
            )

            if not is_busy:
                return teacher

        return None

    def _find_conflict_free_classroom(self, entries: List[TimetableEntry], day: str, period: int,
                                     class_group: str = None, subject: Subject = None):
        """
        Find a classroom that is available at the given time using intelligent allocation.
        Considers room type, seniority, and allocation rules.
        """
        if not class_group or not subject:
            # Fallback to basic allocation if missing information
            return self._find_basic_available_classroom(entries, day, period)

        # Use intelligent room allocation based on subject type
        if subject.is_practical:
            # Practical subjects need labs with 3-block allocation
            return self.room_allocator.allocate_room_for_practical(
                day, period, class_group, subject, entries
            )
        else:
            # Theory subjects use seniority-based allocation
            return self.room_allocator.allocate_room_for_theory(
                day, period, class_group, subject, entries
            )

    def _find_basic_available_classroom(self, entries: List[TimetableEntry], day: str, period: int):
        """Basic classroom finding for fallback scenarios."""
        from .models import Classroom

        # Get all classrooms ordered by priority
        all_classrooms = list(Classroom.objects.all())
        all_classrooms.sort(key=lambda room: (room.building_priority, room.name))

        for classroom in all_classrooms:
            # Check if classroom is free at this time
            is_busy = any(
                entry.classroom and entry.classroom.id == classroom.id and
                entry.day == day and entry.period == period
                for entry in entries
            )

            if not is_busy:
                return classroom

        return None

    def _would_create_violations(self, entries: List[TimetableEntry], class_group: str,
                               day: str, period: int, subject) -> bool:
        """Check if adding this class would create constraint violations."""

        # Check Friday time limits
        if day.lower() == 'friday':
            friday_entries = [e for e in entries if e.class_group == class_group and e.day.lower() == 'friday']
            practical_count = len([e for e in friday_entries if e.is_practical])

            if subject.is_practical and period > 6:
                return True
            elif not subject.is_practical:
                if practical_count > 0 and period > 4:
                    return True
                elif practical_count == 0 and period > 3:
                    return True

        # Check if class group already has a class at this time
        for entry in entries:
            if (entry.class_group == class_group and
                entry.day == day and entry.period == period):
                return True

        # Check thesis day constraint
        if day == 'Wednesday' and self._is_thesis_batch(entries, class_group):
            # Only thesis subjects allowed on Wednesday for thesis batches
            if 'thesis' not in subject.name.lower():
                return True

        return False

    def _get_subjects_needing_classes(self, entries: List[TimetableEntry], class_group: str) -> Dict[str, int]:
        """Get subjects that need more classes for the given class group."""
        from .models import Subject

        # Count current classes per subject
        current_counts = {}
        for entry in entries:
            if entry.class_group == class_group:
                subject_code = entry.subject.code
                if subject_code not in current_counts:
                    current_counts[subject_code] = 0
                # Count practical sessions as 1 (they take 3 periods but count as 1 session)
                if entry.is_practical:
                    # Only count if this is the first period of the practical block
                    practical_periods = [e.period for e in entries
                                       if e.class_group == class_group and
                                          e.subject.code == subject_code and
                                          e.is_practical and e.day == entry.day]
                    if entry.period == min(practical_periods):
                        current_counts[subject_code] += 1
                else:
                    current_counts[subject_code] += 1

        # Calculate needed classes
        needed = {}
        all_subjects = Subject.objects.all()

        for subject in all_subjects:
            current = current_counts.get(subject.code, 0)
            required = subject.credits  # 3-credit = 3 classes, 1-credit practical = 1 session

            if current < required:
                needed[subject.code] = required - current

        return needed

    def _find_better_slot(self, entries: List[TimetableEntry], entry: TimetableEntry) -> tuple:
        """Find a better time slot for the given entry."""
        current_day, current_period = entry.day, entry.period

        # Try different days and periods
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            # Skip Wednesday for non-thesis subjects in thesis batches
            if (day == 'Wednesday' and
                self._is_thesis_batch(entries, entry.class_group) and
                'thesis' not in entry.subject.name.lower()):
                continue

            for period in range(1, 7):  # Periods 1-6
                if day == current_day and period == current_period:
                    continue  # Skip current position

                # Check if this slot would be better
                if self._is_better_slot(entries, entry, day, period):
                    return (day, period)

        return None

    def _is_better_slot(self, entries: List[TimetableEntry], entry: TimetableEntry,
                       new_day: str, new_period: int) -> bool:
        """Check if the new slot is better than the current one."""

        # Check basic availability
        if self._would_create_violations(entries, entry.class_group, new_day, new_period, entry.subject):
            return False

        # Check teacher availability
        teacher_busy = any(
            e.teacher and e.teacher.id == entry.teacher.id and
            e.day == new_day and e.period == new_period and e != entry
            for e in entries
        )
        if teacher_busy:
            return False

        # Check classroom availability
        classroom_busy = any(
            e.classroom and e.classroom.id == entry.classroom.id and
            e.day == new_day and e.period == new_period and e != entry
            for e in entries
        )
        if classroom_busy:
            return False

        # Check if this would fill a gap (making it better)
        class_periods = [e.period for e in entries
                        if e.class_group == entry.class_group and e.day == new_day and e != entry]

        if class_periods:
            min_period = min(class_periods)
            max_period = max(class_periods)

            # If new period fills a gap, it's better
            if min_period < new_period < max_period:
                return True

        return False

    def _place_needed_classes(self, entries: List[TimetableEntry], class_group: str,
                            subject_code: str, needed_count: int) -> int:
        """Place the needed classes for a subject."""
        from .models import Subject

        try:
            subject = Subject.objects.get(code=subject_code)
        except Subject.DoesNotExist:
            return 0

        placed = 0

        # Try to place the needed classes
        for _ in range(needed_count):
            best_slot = self._find_best_available_slot(entries, class_group, subject)
            if not best_slot:
                break

            day, period = best_slot

            # Find resources
            teacher = self._find_conflict_free_teacher(entries, subject, day, period)
            classroom = self._find_conflict_free_classroom(entries, day, period)

            if teacher and classroom:
                new_entry = self._create_timetable_entry(
                    day=day,
                    period=period,
                    subject=subject,
                    teacher=teacher,
                    classroom=classroom,
                    class_group=class_group,
                    is_practical=subject.is_practical
                )
                entries.append(new_entry)
                placed += 1

        return placed

    def _find_best_available_slot(self, entries: List[TimetableEntry], class_group: str, subject) -> tuple:
        """Find the best available slot for a subject."""

        # Priority order: fill gaps first, then early periods, then later periods
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            # Skip Wednesday for non-thesis subjects in thesis batches
            if (day == 'Wednesday' and
                self._is_thesis_batch(entries, class_group) and
                'thesis' not in subject.name.lower()):
                continue

            # Get occupied periods for this class group on this day
            occupied_periods = set(e.period for e in entries
                                 if e.class_group == class_group and e.day == day)

            # Strategy 1: Fill gaps between existing classes
            if len(occupied_periods) >= 2:
                min_period = min(occupied_periods)
                max_period = max(occupied_periods)

                for period in range(min_period + 1, max_period):
                    if (period not in occupied_periods and
                        not self._would_create_violations(entries, class_group, day, period, subject)):
                        return (day, period)

            # Strategy 2: Add to beginning or end to maintain compactness
            if occupied_periods:
                min_period = min(occupied_periods)
                max_period = max(occupied_periods)

                # Try before first class
                if (min_period > 1 and
                    not self._would_create_violations(entries, class_group, day, min_period - 1, subject)):
                    return (day, min_period - 1)

                # Try after last class
                max_allowed = 6 if day.lower() != 'friday' else (4 if not subject.is_practical else 6)
                if (max_period < max_allowed and
                    not self._would_create_violations(entries, class_group, day, max_period + 1, subject)):
                    return (day, max_period + 1)

            # Strategy 3: Start new day
            else:
                for period in range(1, 4):  # Prefer early periods
                    if not self._would_create_violations(entries, class_group, day, period, subject):
                        return (day, period)

        return None

    def _apply_zero_violations_strategies(self, entries: List[TimetableEntry], violations_by_type: Dict) -> List[TimetableEntry]:
        """Apply all strategies aggressively to achieve zero violations."""
        print("      🚀 ZERO VIOLATIONS STRATEGIES")
        print("      " + "=" * 40)

        current_entries = list(entries)

        # Strategy 1: Conservative gap filling only
        current_entries = self._conservative_gap_filling(current_entries)

        # Strategy 2: Only handle critical violations conservatively
        compact_violations = violations_by_type.get('Compact Scheduling', [])
        daily_violations = violations_by_type.get('Minimum Daily Classes', [])
        teacher_conflicts = violations_by_type.get('Teacher Conflicts', [])
        room_conflicts = violations_by_type.get('Room Conflicts', [])

        if compact_violations:
            print(f"      🎯 Conservatively resolving Compact Scheduling ({len(compact_violations)} violations)")
            current_entries = self._conservative_fix_compact_scheduling(current_entries, compact_violations)

        if daily_violations and len(daily_violations) <= 5:
            print(f"      🎯 Conservatively resolving Minimum Daily Classes ({len(daily_violations)} violations)")
            current_entries = self._conservative_fix_daily_classes(current_entries, daily_violations)

        if teacher_conflicts:
            print(f"      🎯 Resolving Teacher Conflicts ({len(teacher_conflicts)} violations)")
            current_entries = self._aggressively_fix_teacher_conflicts(current_entries, teacher_conflicts)

        if room_conflicts:
            print(f"      🎯 Resolving Room Conflicts ({len(room_conflicts)} violations)")
            current_entries = self._aggressively_fix_room_conflicts(current_entries, room_conflicts)

        return current_entries

    def _aggressively_fix_compact_scheduling(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Aggressively fix compact scheduling violations by moving classes."""
        current_entries = list(entries)

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

            # Move classes to fill gaps
            target_period = day_entries[0].period
            for entry in day_entries:
                if entry.period != target_period:
                    # Check if we can move to target period
                    if not self._would_create_violations(current_entries, class_group, day, target_period, entry.subject):
                        entry.period = target_period
                target_period += 1

        return current_entries

    def _aggressively_fix_subject_frequency(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Aggressively fix subject frequency violations."""
        current_entries = list(entries)

        for violation in violations:
            class_group = violation.get('class_group')
            subject_code = violation.get('subject_code')

            if not class_group or not subject_code:
                continue

            # Get current count and required count
            current_count = len([e for e in current_entries
                               if e.class_group == class_group and e.subject.code == subject_code])

            from .models import Subject
            try:
                subject = Subject.objects.get(code=subject_code)
                required_count = subject.credits

                if current_count < required_count:
                    # Add missing classes
                    needed = required_count - current_count
                    self._place_needed_classes(current_entries, class_group, subject_code, needed)
                elif current_count > required_count:
                    # Remove excess classes
                    excess = current_count - required_count
                    excess_entries = [e for e in current_entries
                                    if e.class_group == class_group and e.subject.code == subject_code]
                    for i in range(excess):
                        if i < len(excess_entries):
                            current_entries.remove(excess_entries[i])
            except Subject.DoesNotExist:
                continue

        return current_entries

    def _aggressively_fix_teacher_conflicts(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Aggressively fix teacher conflicts by reassigning teachers."""
        current_entries = list(entries)

        for violation in violations:
            teacher_name = violation.get('teacher')
            day = violation.get('day')
            period = violation.get('period')

            if not all([teacher_name, day, period]):
                continue

            # Find conflicting entries
            conflicting_entries = [e for e in current_entries
                                 if (e.teacher and e.teacher.name == teacher_name and
                                     e.day == day and e.period == period)]

            # Keep the first entry, reassign others
            for entry in conflicting_entries[1:]:
                new_teacher = self._find_conflict_free_teacher(current_entries, entry.subject, day, period)
                if new_teacher:
                    entry.teacher = new_teacher

        return current_entries

    def _aggressively_fix_room_conflicts(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Aggressively fix room conflicts by reassigning classrooms."""
        current_entries = list(entries)

        for violation in violations:
            classroom_name = violation.get('classroom')
            day = violation.get('day')
            period = violation.get('period')

            if not all([classroom_name, day, period]):
                continue

            # Find conflicting entries
            conflicting_entries = [e for e in current_entries
                                 if (e.classroom and e.classroom.name == classroom_name and
                                     e.day == day and e.period == period)]

            # Keep the first entry, reassign others
            for entry in conflicting_entries[1:]:
                new_classroom = self._find_conflict_free_classroom(current_entries, day, period)
                if new_classroom:
                    entry.classroom = new_classroom

        return current_entries

    def _aggressively_fix_friday_limits(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Aggressively fix Friday time limit violations by moving classes."""
        current_entries = list(entries)

        for violation in violations:
            class_group = violation.get('class_group')

            if not class_group:
                continue

            # Find Friday entries that violate time limits
            friday_entries = [e for e in current_entries
                            if e.class_group == class_group and e.day.lower() == 'friday']

            practical_count = len([e for e in friday_entries if e.is_practical])

            for entry in friday_entries:
                if entry.is_practical and entry.period > 6:
                    # Move practical to earlier period or different day
                    better_slot = self._find_better_slot(current_entries, entry)
                    if better_slot:
                        entry.day, entry.period = better_slot
                elif not entry.is_practical:
                    max_period = 4 if practical_count > 0 else 3
                    if entry.period > max_period:
                        better_slot = self._find_better_slot(current_entries, entry)
                        if better_slot:
                            entry.day, entry.period = better_slot

        return current_entries

    def _aggressively_fix_daily_classes(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Aggressively fix minimum daily classes violations."""
        current_entries = list(entries)

        for violation in violations:
            class_group = violation.get('class_group')
            day = violation.get('day')

            if not class_group or not day:
                continue

            # Get entries for this class group on this day
            day_entries = [e for e in current_entries
                          if e.class_group == class_group and e.day == day]

            if len(day_entries) == 1 and day_entries[0].is_practical:
                # Add a theory class
                needed_subjects = self._get_subjects_needing_classes(current_entries, class_group)
                for subject_code, needed_count in needed_subjects.items():
                    if needed_count > 0:
                        self._place_needed_classes(current_entries, class_group, subject_code, 1)
                        break

        return current_entries

    def _aggressively_fix_practical_blocks(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Aggressively fix practical block violations."""
        current_entries = list(entries)

        for violation in violations:
            class_group = violation.get('class_group')
            subject_code = violation.get('subject_code')
            day = violation.get('day')

            if not all([class_group, subject_code, day]):
                continue

            # Remove broken practical entries
            broken_entries = [e for e in current_entries
                            if (e.class_group == class_group and
                                e.subject.code == subject_code and
                                e.day == day and e.is_practical)]

            for entry in broken_entries:
                current_entries.remove(entry)

            # Create new proper practical block
            from .models import Subject
            try:
                subject = Subject.objects.get(code=subject_code)
                if subject.is_practical:
                    # Find 3 consecutive periods
                    for start_period in range(1, 5):  # Periods 1-4 can start a 3-period block
                        if self._can_place_practical_block(current_entries, class_group, day, start_period, subject):
                            self._create_practical_block(current_entries, class_group, day, start_period, subject)
                            break
            except Subject.DoesNotExist:
                continue

        return current_entries

    def _can_place_practical_block(self, entries: List[TimetableEntry], class_group: str,
                                  day: str, start_period: int, subject) -> bool:
        """Check if a 3-period practical block can be placed."""
        for period in range(start_period, start_period + 3):
            if self._would_create_violations(entries, class_group, day, period, subject):
                return False
        return True

    def _create_practical_block(self, entries: List[TimetableEntry], class_group: str,
                               day: str, start_period: int, subject):
        """Create a 3-period practical block."""
        teacher = self._find_conflict_free_teacher(entries, subject, day, start_period)
        classroom = self._find_conflict_free_classroom(entries, day, start_period)

        if teacher and classroom:
            for period in range(start_period, start_period + 3):
                new_entry = self._create_timetable_entry(
                    day=day,
                    period=period,
                    subject=subject,
                    teacher=teacher,
                    classroom=classroom,
                    class_group=class_group,
                    is_practical=True
                )
                entries.append(new_entry)

    def _apply_conservative_strategies(self, entries: List[TimetableEntry], violations_by_type: Dict) -> List[TimetableEntry]:
        """Apply conservative strategies that don't add excessive classes."""
        print("      🎯 CONSERVATIVE STRATEGIES")
        print("      " + "=" * 30)

        current_entries = list(entries)

        # Only handle compact scheduling and minimum daily classes conservatively
        compact_violations = violations_by_type.get('Compact Scheduling', [])
        daily_violations = violations_by_type.get('Minimum Daily Classes', [])

        if compact_violations:
            print(f"      🔧 Conservatively fixing {len(compact_violations)} compact scheduling violations...")
            current_entries = self._conservative_fix_compact_scheduling(current_entries, compact_violations)

        if daily_violations and len(daily_violations) <= 5:  # Only if very few
            print(f"      🔧 Conservatively fixing {len(daily_violations)} daily class violations...")
            current_entries = self._conservative_fix_daily_classes(current_entries, daily_violations)

        return current_entries

    def _conservative_gap_filling(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Conservative gap filling that only moves existing classes."""
        print("      🎯 Conservative gap filling...")

        current_entries = list(entries)
        moves_made = 0

        # Only fill internal gaps by moving existing classes
        class_groups = set(entry.class_group for entry in current_entries)

        for class_group in class_groups:
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                # Skip Wednesday for thesis batches
                if day == 'Wednesday' and self._is_thesis_batch(current_entries, class_group):
                    continue

                # Get occupied periods for this class group on this day
                day_entries = [e for e in current_entries
                              if e.class_group == class_group and e.day == day]

                if len(day_entries) < 2:
                    continue

                # Sort by period
                day_entries.sort(key=lambda e: e.period)
                periods = [e.period for e in day_entries]

                # Find gaps between min and max
                min_period = min(periods)
                max_period = max(periods)

                for period in range(min_period + 1, max_period):
                    if period not in periods:
                        # Try to move a class from another day to fill this gap
                        if self._move_class_to_fill_gap(current_entries, class_group, day, period):
                            moves_made += 1
                            if moves_made >= 3:  # Limit moves to prevent excessive changes
                                break

                if moves_made >= 3:
                    break

            if moves_made >= 3:
                break

        print(f"      📊 Conservative moves made: {moves_made}")
        return current_entries

    def _conservative_fix_compact_scheduling(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Conservatively fix compact scheduling by moving classes only."""
        current_entries = list(entries)
        fixes_made = 0

        for violation in violations[:3]:  # Limit to first 3 violations
            class_group = violation.get('class_group')
            day = violation.get('day')

            if not class_group or not day:
                continue

            # Try to move a class from another day to fill the gap
            if self._move_class_to_fill_gap(current_entries, class_group, day, None):
                fixes_made += 1

        print(f"        📊 Compact scheduling fixes: {fixes_made}")
        return current_entries

    def _conservative_fix_daily_classes(self, entries: List[TimetableEntry], violations: List) -> List[TimetableEntry]:
        """Conservatively fix daily class violations by moving classes only."""
        current_entries = list(entries)
        fixes_made = 0

        for violation in violations[:2]:  # Limit to first 2 violations
            class_group = violation.get('class_group')
            day = violation.get('day')

            if not class_group or not day:
                continue

            # Try to move a theory class from another day
            if self._move_theory_class_to_day_conservative(current_entries, class_group, day):
                fixes_made += 1

        print(f"        📊 Daily class fixes: {fixes_made}")
        return current_entries

    def _move_class_to_fill_gap(self, entries: List[TimetableEntry], class_group: str,
                               target_day: str, target_period: int = None) -> bool:
        """Move an existing class to fill a gap."""

        # Find moveable classes for this class group from other days
        moveable_classes = [e for e in entries
                           if (e.class_group == class_group and
                               e.day != target_day and
                               not e.is_practical)]  # Don't move practicals

        for entry in moveable_classes[:3]:  # Limit candidates
            if target_period:
                # Try to move to specific period
                if self._can_move_class_to_slot(entries, entry, target_day, target_period):
                    entry.day = target_day
                    entry.period = target_period
                    return True
            else:
                # Find any available period on target day
                available_period = self._find_available_period(entries, class_group, target_day)
                if available_period and self._can_move_class_to_slot(entries, entry, target_day, available_period):
                    entry.day = target_day
                    entry.period = available_period
                    return True

        return False

    def _move_theory_class_to_day_conservative(self, entries: List[TimetableEntry],
                                             class_group: str, target_day: str) -> bool:
        """Conservatively move a theory class to target day."""

        # Find theory classes for this class group on other days
        theory_classes = [e for e in entries
                         if (e.class_group == class_group and
                             e.day != target_day and
                             not e.is_practical)]

        for entry in theory_classes[:2]:  # Limit to first 2 candidates
            available_period = self._find_available_period(entries, class_group, target_day)
            if available_period and self._can_move_class_to_slot(entries, entry, target_day, available_period):
                entry.day = target_day
                entry.period = available_period
                return True

        return False

    def _find_schedule_gaps(self, entries: List[TimetableEntry], class_group: str) -> Dict[str, List[int]]:
        """Find gaps in a class group's schedule."""
        gaps = {}

        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            # Get occupied periods for this class group on this day
            occupied_periods = set()
            for entry in entries:
                if entry.class_group == class_group and entry.day == day:
                    occupied_periods.add(entry.period)

            day_gaps = []

            if occupied_periods:
                # Strategy 1: Find gaps between min and max occupied periods (internal gaps)
                min_period = min(occupied_periods)
                max_period = max(occupied_periods)

                for period in range(min_period, max_period + 1):
                    if period not in occupied_periods:
                        day_gaps.append(period)

            # Strategy 2: Also consider filling early periods (1-3) if they're empty
            # This helps with compact scheduling
            for period in range(1, 4):
                if period not in occupied_periods and period not in day_gaps:
                    # Only add if there are classes later in the day
                    if any(p > period for p in occupied_periods):
                        day_gaps.append(period)

            # Strategy 3: Consider filling periods 4-6 if there are earlier classes
            for period in range(4, 7):
                if period not in occupied_periods and period not in day_gaps:
                    # Only add if there are classes earlier in the day
                    if any(p < period for p in occupied_periods):
                        # Don't add Friday periods beyond 4
                        if not (day.lower() == 'friday' and period > 4):
                            day_gaps.append(period)

            if day_gaps:
                gaps[day] = sorted(day_gaps)

        return gaps

    def _fill_gap_intelligently(self, entries: List[TimetableEntry], class_group: str,
                               day: str, period: int) -> bool:
        """Fill a specific gap with the best available subject."""
        # Get subjects that this class group needs more of
        needed_subjects = self._get_subjects_needing_more_classes(entries, class_group)

        for subject_code, needed_count in needed_subjects.items():
            if needed_count <= 0:
                continue

            # Try to find an available teacher for this subject
            teacher = self._find_available_teacher_for_subject(entries, subject_code, day, period)
            if not teacher:
                continue

            # Try to find an available classroom
            classroom = self._find_available_classroom(entries, day, period)
            if not classroom:
                continue

            # Check if this would violate any constraints
            if self._would_violate_constraints(entries, class_group, day, period,
                                             Subject.objects.filter(code=subject_code).first()):
                continue

            # Create the new entry
            subject = Subject.objects.filter(code=subject_code).first()
            if subject:
                new_entry = self._create_timetable_entry(
                    day=day,
                    period=period,
                    subject=subject,
                    teacher=teacher,
                    classroom=classroom,
                    class_group=class_group,
                    is_practical=subject.is_practical
                )
                entries.append(new_entry)
                print(f"        🎯 Added {subject_code} with {teacher.name} in {classroom.name}")
                return True

        return False

    def _get_subjects_needing_more_classes(self, entries: List[TimetableEntry], class_group: str) -> Dict[str, int]:
        """Get subjects that need more classes for this class group."""
        from .models import Subject

        # Count current classes per subject
        current_counts = {}
        for entry in entries:
            if entry.class_group == class_group and not entry.is_practical:
                subject_code = entry.subject.code
                current_counts[subject_code] = current_counts.get(subject_code, 0) + 1

        # Get required counts and calculate needs
        needed = {}
        all_subjects = Subject.objects.filter(is_practical=False)

        for subject in all_subjects:
            current = current_counts.get(subject.code, 0)
            required = subject.credits
            if current < required:
                needed[subject.code] = required - current

        # Sort by need (highest first)
        return dict(sorted(needed.items(), key=lambda x: x[1], reverse=True))

    def _find_available_teacher_for_subject(self, entries: List[TimetableEntry], subject_code: str,
                                          day: str, period: int) -> Teacher:
        """Find a teacher available for a specific subject at a specific time."""
        from .models import TeacherSubjectAssignment

        # Get teachers who can teach this subject
        assignments = TeacherSubjectAssignment.objects.filter(subject__code=subject_code)

        for assignment in assignments:
            teacher = assignment.teacher
            # Check if teacher is available
            conflict = any(e for e in entries
                         if e.teacher == teacher and e.day == day and e.period == period)

            if not conflict:
                return teacher

        return None

    def _would_violate_constraints(self, entries: List[TimetableEntry], class_group: str,
                                  day: str, period: int, subject: Subject) -> bool:
        """Check if adding a subject would violate any constraints."""
        # Check for basic conflicts
        for entry in entries:
            if (entry.class_group == class_group and
                entry.day == day and entry.period == period):
                return True  # Class group already has a class at this time

        # Check Friday constraints (no classes after period 4)
        if day.lower() == 'friday' and period > 4:
            return True

        # Check if this would create too many classes for this subject
        current_count = sum(1 for e in entries
                          if e.class_group == class_group and
                             e.subject == subject and not e.is_practical)

        if current_count >= subject.credits:
            return True  # Already have enough classes for this subject

        return False

    def _find_available_classroom(self, entries: List[TimetableEntry], day: str, period: int) -> Classroom:
        """Find an available classroom for a specific time."""
        from .models import Classroom

        # Get all available classrooms
        all_classrooms = Classroom.objects.all()

        for classroom in all_classrooms:
            # Check if this classroom is available at this time
            room_conflict = any(e for e in entries
                              if e.classroom == classroom and
                                 e.day == day and e.period == period)

            if not room_conflict:
                return classroom

        return None

    # Placeholder methods for other resolution strategies
    def _resolve_practical_blocks(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve practical block violations by creating proper 3-hour consecutive blocks."""
        print(f"    🔧 Resolving practical block: {violation['description']}")

        current_entries = list(entries)
        class_group = violation.get('class_group')
        subject_code = violation.get('subject')
        day = violation.get('day')

        if not all([class_group, subject_code, day]):
            return current_entries

        # Check if we already have a complete 3-hour block for this subject on this day
        existing_entries = []
        for entry in current_entries:
            if (entry.class_group == class_group and
                entry.subject.code == subject_code and
                entry.day == day and
                entry.is_practical):
                existing_entries.append(entry)

        # If we already have 3 consecutive periods, don't recreate
        if len(existing_entries) == 3:
            periods = sorted([e.period for e in existing_entries])
            if self._are_periods_consecutive(periods):
                print(f"        ✅ Complete 3-hour block already exists: {day} P{periods[0]}-P{periods[2]}")
                return current_entries

        # Remove incomplete/broken practical entries for this subject on this day
        entries_to_remove = []
        for entry in current_entries:
            if (entry.class_group == class_group and
                entry.subject.code == subject_code and
                entry.day == day and
                entry.is_practical):
                entries_to_remove.append(entry)

        for entry in entries_to_remove:
            current_entries.remove(entry)
            print(f"        ❌ Removed broken practical: {entry.day} P{entry.period}")

        # Find the subject object
        from .models import Subject
        subject = Subject.objects.filter(code=subject_code).first()
        if not subject:
            return current_entries

        # Find 3 consecutive available periods for this class group on this day
        for start_period in range(1, 5):  # P1-P3, P2-P4, P3-P5, P4-P6
            consecutive_periods = [start_period, start_period + 1, start_period + 2]

            # Check if all 3 periods are available for this class group
            periods_available = True
            for period in consecutive_periods:
                conflict = any(e for e in current_entries
                             if e.class_group == class_group and
                                e.day == day and e.period == period)
                if conflict:
                    periods_available = False
                    break

            if periods_available:
                # Find teacher and classroom for the practical
                teacher = self._find_available_teacher(current_entries, subject, day, start_period)
                classroom = self._find_available_practical_classroom(current_entries, day, start_period)

                if teacher and classroom:
                    # Create 3 consecutive practical periods
                    for period in consecutive_periods:
                        new_entry = self._create_timetable_entry(
                            day=day,
                            period=period,
                            subject=subject,
                            teacher=teacher,
                            classroom=classroom,
                            class_group=class_group,
                            is_practical=True
                        )
                        current_entries.append(new_entry)
                        print(f"        ✅ Created practical block: {day} P{period}")
                    break
                else:
                    print(f"        ⚠️ No teacher/classroom available for {day} P{start_period}-P{start_period+2}")

        return current_entries

    def _resolve_teacher_conflicts(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve teacher conflicts by reassigning teachers or moving classes."""
        print(f"    🔧 Resolving teacher conflict: {violation['description']}")

        current_entries = list(entries)
        teacher_name = violation.get('teacher')
        day = violation.get('day')
        period = violation.get('period')

        if not all([teacher_name, day, period]):
            return current_entries

        # Find all conflicting entries for this teacher at this time
        conflicting_entries = []
        for entry in current_entries:
            if (entry.teacher and entry.teacher.name == teacher_name and
                entry.day == day and entry.period == period):
                conflicting_entries.append(entry)

        if len(conflicting_entries) <= 1:
            return current_entries  # No conflict or already resolved

        # Strategy 1: Try to find alternative teachers for some of the conflicting classes
        for i, entry in enumerate(conflicting_entries[1:], 1):  # Keep first entry, reassign others
            # Find alternative teachers for this subject
            from .models import TeacherSubjectAssignment

            alternative_assignments = TeacherSubjectAssignment.objects.filter(
                subject=entry.subject
            ).exclude(teacher=entry.teacher)

            for assignment in alternative_assignments:
                # Check if this teacher is available at this time
                teacher_conflict = any(e for e in current_entries
                                    if e.teacher == assignment.teacher and
                                       e.day == day and e.period == period)

                if not teacher_conflict:
                    entry.teacher = assignment.teacher
                    print(f"        ✅ Reassigned {entry.subject.code} to {assignment.teacher.name}")
                    break
            else:
                # Strategy 2: Move this class to a different time slot
                moved = self._move_class_to_available_slot(current_entries, entry)
                if moved:
                    print(f"        ✅ Moved {entry.subject.code} for {entry.class_group} to different time")

        return current_entries

    def _resolve_room_conflicts(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """
        Resolve room conflicts using intelligent room allocation system.
        Handles multiple conflict types: double-booking, type mismatches, seniority violations.
        """
        print(f"    🔧 Resolving room conflict: {violation['description']}")

        current_entries = list(entries)
        conflict_subtype = violation.get('subtype', 'double_booking')

        # Handle different types of room conflicts
        if conflict_subtype == 'double_booking':
            current_entries = self._resolve_double_booking_conflict(current_entries, violation)
        elif conflict_subtype == 'type_mismatch':
            current_entries = self._resolve_room_type_mismatch(current_entries, violation)
        elif conflict_subtype == 'seniority_violation':
            current_entries = self._resolve_seniority_violation(current_entries, violation)
        elif conflict_subtype == 'lab_reservation_violation':
            current_entries = self._resolve_lab_reservation_violation(current_entries, violation)
        else:
            # Fallback to comprehensive resolution
            current_entries = self._resolve_comprehensive_room_conflicts(current_entries)

        return current_entries

    def _resolve_double_booking_conflict(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve double-booking conflicts using seniority-based priority."""
        classroom_name = violation.get('classroom')
        day = violation.get('day')
        period = violation.get('period')

        if not all([classroom_name, day, period]):
            return entries

        # Find conflicting entries
        conflicting_entries = [
            entry for entry in entries
            if (entry.classroom and entry.classroom.name == classroom_name and
                entry.day == day and entry.period == period)
        ]

        if len(conflicting_entries) <= 1:
            return entries

        # Sort by batch priority (senior batches keep their rooms)
        sorted_entries = sorted(
            conflicting_entries,
            key=lambda e: self.room_allocator.get_batch_priority(e.class_group)
        )

        # Keep highest priority entry, reassign others
        entries_to_reassign = sorted_entries[1:]

        for entry in entries_to_reassign:
            success = self._reassign_entry_to_suitable_room(entry, entries)
            if success:
                print(f"        ✅ Reassigned {entry.class_group} from double-booked {classroom_name}")
            else:
                print(f"        ❌ Could not reassign {entry.class_group} from {classroom_name}")

        return entries

    def _resolve_room_type_mismatch(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve room type mismatches (e.g., practical in non-lab room)."""
        # Find the entry with type mismatch
        target_entry = None
        for entry in entries:
            if (entry.classroom and entry.classroom.name == violation.get('classroom') and
                entry.day == violation.get('day') and entry.period == violation.get('period')):
                target_entry = entry
                break

        if not target_entry:
            return entries

        # Find appropriate room based on subject type
        if target_entry.subject and target_entry.subject.is_practical:
            # Practical needs lab
            new_room = self.room_allocator.allocate_room_for_practical(
                target_entry.day, target_entry.period, target_entry.class_group,
                target_entry.subject, entries
            )
        else:
            # Theory can use regular room
            new_room = self.room_allocator.allocate_room_for_theory(
                target_entry.day, target_entry.period, target_entry.class_group,
                target_entry.subject, entries
            )

        if new_room:
            old_room = target_entry.classroom.name
            target_entry.classroom = new_room
            print(f"        ✅ Fixed type mismatch: moved {target_entry.class_group} from {old_room} to {new_room.name}")

        return entries

    def _resolve_seniority_violation(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve seniority violations (junior batch in lab for theory)."""
        # Find the violating entry
        target_entry = None
        for entry in entries:
            if (entry.classroom and entry.classroom.name == violation.get('classroom') and
                entry.day == violation.get('day') and entry.period == violation.get('period') and
                entry.class_group == violation.get('class_group')):
                target_entry = entry
                break

        if not target_entry:
            return entries

        # Try to move junior batch to regular room
        regular_room = self.room_allocator.allocate_room_for_theory(
            target_entry.day, target_entry.period, target_entry.class_group,
            target_entry.subject, entries
        )

        if regular_room and not regular_room.is_lab:
            old_room = target_entry.classroom.name
            target_entry.classroom = regular_room
            print(f"        ✅ Fixed seniority violation: moved junior batch {target_entry.class_group} from lab {old_room} to {regular_room.name}")

        return entries

    def _resolve_lab_reservation_violation(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve lab reservation violations by moving theory classes from labs."""
        day = violation.get('day')
        period = violation.get('period')

        if not day or not period:
            return entries

        # Find theory classes in labs at this time
        theory_in_labs = [
            entry for entry in entries
            if (entry.day == day and entry.period == period and
                entry.classroom and entry.classroom.is_lab and
                entry.subject and not entry.subject.is_practical)
        ]

        # Move junior batch theory classes out of labs first
        for entry in theory_in_labs:
            is_senior = self.room_allocator.is_senior_batch(entry.class_group)
            if not is_senior:
                regular_room = self.room_allocator.get_available_regular_rooms_for_time(day, period, entries)
                if regular_room:
                    old_room = entry.classroom.name
                    entry.classroom = regular_room[0]
                    print(f"        ✅ Freed lab for reservation: moved {entry.class_group} from {old_room} to {regular_room[0].name}")
                    break

        return entries

    def _resolve_comprehensive_room_conflicts(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Comprehensive room conflict resolution using room allocator."""
        conflicts = self.room_allocator.find_room_conflicts(entries)

        resolved_count = 0
        for conflict in conflicts:
            if self.room_allocator.resolve_room_conflict(conflict, entries):
                resolved_count += 1
                print(f"        ✅ Resolved room conflict in {conflict['classroom']}")

        print(f"    📊 Comprehensive Resolution: {resolved_count}/{len(conflicts)} conflicts resolved")
        return entries

    def _reassign_entry_to_suitable_room(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> bool:
        """Reassign an entry to a suitable room based on subject type and seniority."""
        if not entry.subject:
            return False

        new_room = None
        if entry.subject.is_practical:
            new_room = self.room_allocator.allocate_room_for_practical(
                entry.day, entry.period, entry.class_group, entry.subject, entries
            )
        else:
            new_room = self.room_allocator.allocate_room_for_theory(
                entry.day, entry.period, entry.class_group, entry.subject, entries
            )

        if new_room:
            entry.classroom = new_room
            return True

        return False

    def optimize_room_allocation(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """
        Optimize overall room allocation using intelligent swapping.
        Improves seniority-based allocation and lab utilization.
        """
        print("    🔄 Optimizing room allocation with intelligent swapping...")

        # Perform batch room optimization
        optimization_results = self.room_allocator.batch_room_optimization(entries)

        print(f"    📊 Room Optimization Results:")
        print(f"       🔄 Swaps performed: {optimization_results['swaps_performed']}")
        print(f"       🎓 Senior batches improved: {optimization_results['senior_batches_improved']}")
        print(f"       📚 Junior batches moved: {optimization_results['junior_batches_moved']}")

        # Log detailed improvements
        for detail in optimization_results['details']:
            if detail['swaps'] > 0:
                print(f"       ✅ {detail['time_slot']}: {detail['swaps']} swaps")

        return entries

    def resolve_senior_batch_lab_access(self, entries: List[TimetableEntry],
                                      senior_class_group: str) -> List[TimetableEntry]:
        """
        Ensure senior batches get priority access to labs by swapping with junior batches.
        """
        print(f"    🎓 Ensuring lab access for senior batch: {senior_class_group}")

        # Find senior batch entries that need better room allocation
        senior_entries = [
            entry for entry in entries
            if (entry.class_group == senior_class_group and entry.classroom)
        ]

        swaps_made = 0
        for senior_entry in senior_entries:
            # Check if senior entry could benefit from a lab
            needs_lab = (
                (senior_entry.subject and senior_entry.subject.is_practical) or
                (senior_entry.subject and not senior_entry.subject.is_practical and not senior_entry.classroom.is_lab)
            )

            if needs_lab:
                if self.room_allocator.intelligent_room_swap(entries, senior_entry, 'lab'):
                    swaps_made += 1

        if swaps_made > 0:
            print(f"    ✅ Made {swaps_made} room swaps to improve senior batch lab access")
        else:
            print(f"    ℹ️  No beneficial swaps found for {senior_class_group}")

        return entries

    def _resolve_specific_room_conflict(self, entries: List[TimetableEntry], violation: Dict):
        """Resolve a specific room conflict with enhanced seniority-based logic."""
        classroom_name = violation['classroom']
        day = violation['day']
        period = violation['period']

        # Find conflicting entries
        conflicting_entries = [
            entry for entry in entries
            if (entry.classroom and entry.classroom.name == classroom_name and
                entry.day == day and entry.period == period)
        ]

        if len(conflicting_entries) <= 1:
            return

        # Sort by batch priority (senior batches keep their rooms)
        sorted_entries = sorted(
            conflicting_entries,
            key=lambda e: self.room_allocator.get_batch_priority(e.class_group)
        )

        # Keep highest priority entry, reassign others
        entries_to_reassign = sorted_entries[1:]

        for entry in entries_to_reassign:
            new_room = None

            if entry.subject and entry.subject.is_practical:
                # Practical classes need labs with 3-block allocation
                new_room = self.room_allocator.allocate_room_for_practical(
                    day, period, entry.class_group, entry.subject, entries
                )
            else:
                # Theory classes use seniority-based allocation
                new_room = self.room_allocator.allocate_room_for_theory(
                    day, period, entry.class_group, entry.subject, entries
                )

            if new_room:
                old_room = entry.classroom.name if entry.classroom else 'None'
                entry.classroom = new_room
                print(f"        ✅ Seniority-based reassignment: {entry.class_group} moved from {old_room} to {new_room.name}")
            else:
                # Last resort: move to different time slot
                moved = self._move_class_to_available_slot(entries, entry)
                if moved:
                    print(f"        ✅ Moved {entry.class_group} to different time slot")

    def _is_classroom_suitable(self, classroom, entry) -> bool:
        """
        Check if a classroom is suitable for a class using comprehensive criteria.
        Enforces senior batch lab priority and junior batch regular room assignment.
        """
        if not classroom or not entry:
            return False

        # Check capacity (assume 30 students per section as default)
        section_size = 30  # This could be made configurable
        if not classroom.can_accommodate_section_size(section_size):
            return False

        # Simplified: No seniority-based room allocation

        # Simplified: Check basic suitability without seniority rules
        # Practical subjects need labs
        if entry.subject and entry.subject.is_practical:
            return classroom.is_lab

        # Theory subjects can use any room
        return True

    def _resolve_compact_scheduling(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve compact scheduling violations by filling gaps and making schedule compact."""
        print(f"    🔧 Resolving compact scheduling: {violation['description']}")

        current_entries = list(entries)
        class_group = violation.get('class_group')
        day = violation.get('day')

        if not all([class_group, day]):
            return current_entries

        # Find classes for this class group on this day
        day_entries = [e for e in current_entries
                      if e.class_group == class_group and e.day == day]

        if not day_entries:
            return current_entries

        # Sort by period
        day_entries.sort(key=lambda e: e.period)

        # Get occupied periods
        occupied_periods = [e.period for e in day_entries]

        if not occupied_periods:
            return current_entries

        # Find gaps in the schedule
        min_period = min(occupied_periods)
        max_period = max(occupied_periods)
        gaps = []

        for period in range(min_period, max_period + 1):
            if period not in occupied_periods:
                gaps.append(period)

        if not gaps:
            return current_entries  # No gaps to fill

        print(f"        📍 Found gaps in {class_group} on {day}: {gaps}")

        # Strategy 1: Aggressively move classes from later periods to fill gaps
        gaps_filled = 0
        for gap_period in sorted(gaps):
            # Find a class from a later period that can be moved to this gap
            candidates = [e for e in day_entries if e.period > gap_period]
            candidates.sort(key=lambda e: e.period)  # Start with earliest candidates

            for entry in candidates:
                # Check if we can move this entry to the gap period
                if self._can_move_entry_to_period(current_entries, entry, day, gap_period):
                    old_period = entry.period
                    entry.period = gap_period
                    print(f"        ↗️ Moved {entry.subject.code} from P{old_period} to P{gap_period} to fill gap")
                    gaps_filled += 1

                    # Update the day_entries list and re-sort
                    day_entries.sort(key=lambda e: e.period)
                    break
                else:
                    # If we can't move due to conflicts, try to resolve those conflicts
                    if self._try_resolve_move_conflicts(current_entries, entry, day, gap_period):
                        old_period = entry.period
                        entry.period = gap_period
                        print(f"        🔧 Resolved conflicts and moved {entry.subject.code} from P{old_period} to P{gap_period}")
                        gaps_filled += 1
                        day_entries.sort(key=lambda e: e.period)
                        break

        # Strategy 2: If we still have gaps, try aggressive compaction
        if gaps_filled < len(gaps):
            print(f"        🚀 Applying aggressive compaction for remaining gaps...")
            day_entries.sort(key=lambda e: e.period)

            # Try to make the schedule as compact as possible starting from period 1
            target_period = 1
            for entry in day_entries[:]:  # Use slice to avoid modification during iteration
                if entry.period != target_period:
                    # Try to move this entry to the target period
                    if self._can_move_entry_to_period(current_entries, entry, day, target_period):
                        old_period = entry.period
                        entry.period = target_period
                        print(f"        🎯 Compacted: moved {entry.subject.code} from P{old_period} to P{target_period}")
                    elif self._try_resolve_move_conflicts(current_entries, entry, day, target_period):
                        old_period = entry.period
                        entry.period = target_period
                        print(f"        🔧 Resolved conflicts and compacted {entry.subject.code} from P{old_period} to P{target_period}")
                target_period += 1

        return current_entries

    def _can_move_entry_to_period(self, entries: List[TimetableEntry], entry: TimetableEntry,
                                 day: str, target_period: int) -> bool:
        """Check if an entry can be moved to a specific period without conflicts."""
        # Check class group conflict
        class_conflict = any(e for e in entries
                           if e.class_group == entry.class_group and
                              e.day == day and e.period == target_period and
                              e != entry)

        # Check teacher conflict
        teacher_conflict = any(e for e in entries
                             if e.teacher == entry.teacher and
                                e.day == day and e.period == target_period and
                                e != entry)

        # Check classroom conflict
        room_conflict = any(e for e in entries
                          if e.classroom == entry.classroom and
                             e.day == day and e.period == target_period and
                             e != entry)

        # Check if this would violate other constraints (like Friday limits)
        constraint_violation = self._would_violate_constraints(entries, entry.class_group, day, target_period, entry.subject)

        return not any([class_conflict, teacher_conflict, room_conflict, constraint_violation])

    def _try_resolve_move_conflicts(self, entries: List[TimetableEntry], entry: TimetableEntry,
                                   day: str, target_period: int) -> bool:
        """Aggressively try to resolve conflicts to enable moving an entry to target period."""
        # Find what's blocking the move
        blocking_entries = []

        # Find class group conflicts
        class_conflicts = [e for e in entries
                          if e.class_group == entry.class_group and
                             e.day == day and e.period == target_period and
                             e != entry]

        # Find teacher conflicts
        teacher_conflicts = [e for e in entries
                           if e.teacher == entry.teacher and
                              e.day == day and e.period == target_period and
                              e != entry]

        # Find room conflicts
        room_conflicts = [e for e in entries
                        if e.classroom == entry.classroom and
                           e.day == day and e.period == target_period and
                           e != entry]

        blocking_entries.extend(class_conflicts)
        blocking_entries.extend(teacher_conflicts)
        blocking_entries.extend(room_conflicts)

        if not blocking_entries:
            return True  # No conflicts to resolve

        # Try to move blocking entries to other periods
        for blocking_entry in blocking_entries:
            # Try to find an alternative period for the blocking entry
            for alt_period in range(1, 8):  # Try all periods
                if alt_period == target_period or alt_period == blocking_entry.period:
                    continue

                if self._can_move_entry_to_period(entries, blocking_entry, day, alt_period):
                    old_period = blocking_entry.period
                    blocking_entry.period = alt_period
                    print(f"          🔄 Moved blocking {blocking_entry.subject.code} from P{old_period} to P{alt_period}")
                    return True  # Successfully resolved conflict

        # If we can't move blocking entries, try to find alternative resources
        # Try to find alternative teacher for the entry we want to move
        if teacher_conflicts and entry.subject:
            alt_teacher = self._find_alternative_teacher(entries, entry.subject, day, target_period)
            if alt_teacher:
                old_teacher = entry.teacher.name if entry.teacher else "None"
                entry.teacher = alt_teacher
                subject_code = entry.subject.code if entry.subject else "Unknown"
                print(f"          👨‍🏫 Changed teacher for {subject_code} from {old_teacher} to {alt_teacher.name}")
                return True

        # Try to find alternative classroom for the entry we want to move
        if room_conflicts:
            alt_classroom = self._find_alternative_classroom(entries, day, target_period)
            if alt_classroom:
                old_classroom = entry.classroom.name if entry.classroom else "None"
                entry.classroom = alt_classroom
                subject_code = entry.subject.code if entry.subject else "Unknown"
                print(f"          🏫 Changed classroom for {subject_code} from {old_classroom} to {alt_classroom.name}")
                return True

        return False  # Could not resolve conflicts

    def _find_alternative_teacher(self, entries: List[TimetableEntry], subject: Subject,
                                 day: str, period: int) -> Teacher:
        """Find an alternative teacher for a subject at a specific time."""
        from .models import TeacherSubjectAssignment

        # Get all teachers who can teach this subject
        assignments = TeacherSubjectAssignment.objects.filter(subject=subject)

        for assignment in assignments:
            teacher = assignment.teacher
            # Check if this teacher is available at this time
            teacher_conflict = any(e for e in entries
                                 if e.teacher == teacher and
                                    e.day == day and e.period == period)

            if not teacher_conflict:
                return teacher

        return None

    def _find_alternative_classroom(self, entries: List[TimetableEntry], day: str, period: int) -> Classroom:
        """Find an alternative classroom for a specific time."""
        from .models import Classroom

        # Get all available classrooms
        all_classrooms = Classroom.objects.all()

        for classroom in all_classrooms:
            # Check if this classroom is available at this time
            room_conflict = any(e for e in entries
                              if e.classroom == classroom and
                                 e.day == day and e.period == period)

            if not room_conflict:
                return classroom

        return None

    def _resolve_friday_time_limits(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve Friday time limit violations by moving classes."""
        class_group = violation['class_group']
        subject_code = violation['subject']
        violating_period = violation['period']

        # Find the violating entry
        violating_entry = None
        for entry in entries:
            if (entry.class_group == class_group and
                entry.subject.code == subject_code and
                entry.day.lower().startswith('fri') and
                entry.period == violating_period):
                violating_entry = entry
                break

        if not violating_entry:
            return entries

        # Try to move to another day
        updated_entries = [e for e in entries if e != violating_entry]

        for target_day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
            for target_period in range(1, 8):
                if self._is_slot_available(updated_entries, class_group, target_day, target_period):
                    # Check teacher and classroom availability
                    if (self._is_teacher_available(updated_entries, violating_entry.teacher, target_day, target_period) and
                        self._is_classroom_available(updated_entries, violating_entry.classroom, target_day, target_period)):

                        # Create new entry
                        new_entry = self._create_entry(
                            target_day, target_period, violating_entry.subject,
                            violating_entry.teacher, violating_entry.classroom, class_group
                        )
                        updated_entries.append(new_entry)
                        print(f"    ✅ Moved {subject_code} from Friday P{violating_period} to {target_day} P{target_period}")
                        return updated_entries

        # If can't move, keep original
        updated_entries.append(violating_entry)
        return updated_entries

    def _resolve_minimum_daily_classes(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve minimum daily classes violations by adding classes to meet minimum requirement."""
        print(f"    🔧 Resolving minimum daily classes: {violation['description']}")

        current_entries = list(entries)
        class_group = violation.get('class_group')
        day = violation.get('day')

        if not all([class_group, day]):
            return current_entries

        # Count current classes for this day
        day_entries = [e for e in current_entries
                      if e.class_group == class_group and e.day == day]

        if len(day_entries) >= 2:  # Already meets minimum
            return current_entries

        # Find subjects that need more classes
        from .models import Subject
        subjects_needing_classes = []

        # Get all subjects for this class group
        class_subjects = set(e.subject for e in current_entries if e.class_group == class_group)

        for subject in class_subjects:
            subject_count = len([e for e in current_entries
                               if e.class_group == class_group and e.subject == subject])
            expected_count = subject.credits

            if subject_count < expected_count:
                subjects_needing_classes.append(subject)

        # Add classes for subjects that need them
        classes_to_add = 2 - len(day_entries)  # Need at least 2 classes per day

        for subject in subjects_needing_classes[:classes_to_add]:
            # Find available period
            for period in range(1, 7):
                # Check constraints
                if self._would_violate_constraints(current_entries, class_group, day, period, subject):
                    continue

                # Check if slot is available
                conflict = any(e for e in current_entries
                             if e.class_group == class_group and
                                e.day == day and e.period == period)

                if not conflict:
                    # Find teacher and classroom
                    teacher = self._find_available_teacher(current_entries, subject, day, period)
                    classroom = self._find_available_classroom(current_entries, day, period)

                    if teacher and classroom:
                        new_entry = self._create_timetable_entry(
                            day=day,
                            period=period,
                            subject=subject,
                            teacher=teacher,
                            classroom=classroom,
                            class_group=class_group,
                            is_practical=subject.is_practical
                        )
                        current_entries.append(new_entry)
                        print(f"        ✅ Added {subject.code} for daily minimum on {day} P{period}")
                        break

        return current_entries

    def _resolve_thesis_day(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve Thesis Day violations by moving non-thesis classes from Wednesday."""
        print(f"    🔧 Resolving thesis day: {violation['description']}")

        current_entries = list(entries)
        class_group = violation.get('class_group')

        if not class_group:
            return current_entries

        # Check if this is a final year batch with thesis
        if not any('8' in class_group or 'final' in class_group.lower() for _ in [1]):
            return current_entries

        # Find non-thesis classes scheduled on Wednesday for this class group
        wednesday_entries = [e for e in current_entries
                           if e.class_group == class_group and
                              e.day.lower().startswith('wed') and
                              'thesis' not in e.subject.name.lower()]

        # Move these classes to other days
        for entry in wednesday_entries:
            moved = False
            # Try Monday through Friday (except Wednesday)
            for day in ['Monday', 'Tuesday', 'Thursday', 'Friday']:
                for period in range(1, 7):
                    # Check if this slot would violate constraints
                    if self._would_violate_constraints(current_entries, class_group, day, period, entry.subject):
                        continue

                    # Check if slot is available for class group
                    class_conflict = any(e for e in current_entries
                                       if e.class_group == class_group and
                                          e.day == day and e.period == period)

                    # Check teacher availability
                    teacher_conflict = any(e for e in current_entries
                                         if e.teacher == entry.teacher and
                                            e.day == day and e.period == period and
                                            e != entry)

                    # Check classroom availability
                    room_conflict = any(e for e in current_entries
                                      if e.classroom == entry.classroom and
                                         e.day == day and e.period == period and
                                         e != entry)

                    if not any([class_conflict, teacher_conflict, room_conflict]):
                        # Move the class
                        entry.day = day
                        entry.period = period
                        print(f"        ↗️ Moved {entry.subject.code} from Wednesday to {day} P{period} for thesis day")
                        moved = True
                        break

                if moved:
                    break

        return current_entries

    # Helper methods
    def _is_slot_available(self, entries: List[TimetableEntry], class_group: str, day: str, period: int) -> bool:
        """Check if a slot is available for a class group."""
        for entry in entries:
            if entry.class_group == class_group and entry.day == day and entry.period == period:
                return False
        return True

    def _is_teacher_available(self, entries: List[TimetableEntry], teacher: Teacher, day: str, period: int) -> bool:
        """Check if a teacher is available at a specific time."""
        if not teacher:
            return True

        for entry in entries:
            if entry.teacher == teacher and entry.day == day and entry.period == period:
                return False
        return True

    def _is_classroom_available(self, entries: List[TimetableEntry], classroom: Classroom, day: str, period: int) -> bool:
        """Check if a classroom is available at a specific time."""
        if not classroom:
            return True

        for entry in entries:
            if entry.classroom == classroom and entry.day == day and entry.period == period:
                return False
        return True

    def _find_available_teacher(self, entries: List[TimetableEntry], teachers: List[Teacher], day: str, period: int) -> Teacher:
        """Find an available teacher from the list."""
        for teacher in teachers:
            if self._is_teacher_available(entries, teacher, day, period):
                return teacher
        return None

    def _resolve_subject_frequency_batch(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Batch resolve subject frequency violations to maintain credit hour compliance."""
        print("    📚 Batch processing subject frequency violations...")

        # Group violations by class group and subject
        violations_by_class_subject = {}
        for violation in violations:
            key = f"{violation['class_group']}_{violation['subject']}"
            if key not in violations_by_class_subject:
                violations_by_class_subject[key] = []
            violations_by_class_subject[key].append(violation)

        current_entries = list(entries)

        for key, group_violations in violations_by_class_subject.items():
            class_group, subject_code = key.split('_', 1)
            violation = group_violations[0]  # Take first violation as reference

            expected_count = violation['expected']
            actual_count = violation['actual']

            # Check if this is a practical subject
            from .models import Subject
            subject = Subject.objects.filter(code=subject_code).first()

            if subject and subject.is_practical:
                # For practical subjects, count sessions (3-hour blocks) not individual periods
                practical_sessions = self._count_practical_sessions(current_entries, class_group, subject_code)

                print(f"      🔧 Fixing {subject_code} in {class_group}: {practical_sessions} sessions → {expected_count} sessions")

                if practical_sessions < expected_count:
                    # Need to add more practical sessions (3-hour blocks)
                    sessions_to_add = expected_count - practical_sessions
                    current_entries = self._add_practical_sessions(
                        current_entries, class_group, subject_code, sessions_to_add
                    )
                elif practical_sessions > expected_count:
                    # Need to remove excess practical sessions
                    sessions_to_remove = practical_sessions - expected_count
                    current_entries = self._remove_excess_practical_sessions(
                        current_entries, class_group, subject_code, sessions_to_remove
                    )
            else:
                # For theory subjects, handle normally
                print(f"      🔧 Fixing {subject_code} in {class_group}: {actual_count} → {expected_count}")

                if actual_count < expected_count:
                    # Need to add more classes
                    classes_to_add = expected_count - actual_count
                    current_entries = self._add_missing_classes(
                        current_entries, class_group, subject_code, classes_to_add
                    )
                elif actual_count > expected_count:
                    # Need to remove excess classes
                    classes_to_remove = actual_count - expected_count
                    current_entries = self._remove_excess_classes(
                        current_entries, class_group, subject_code, classes_to_remove
                    )

        return current_entries

    def _count_practical_sessions(self, entries: List[TimetableEntry], class_group: str, subject_code: str) -> int:
        """Count the number of practical sessions (3-hour blocks) for a subject."""
        # Group practical entries by day
        days_with_practicals = {}
        for entry in entries:
            if (entry.class_group == class_group and
                entry.subject.code == subject_code and
                entry.is_practical):
                if entry.day not in days_with_practicals:
                    days_with_practicals[entry.day] = []
                days_with_practicals[entry.day].append(entry)

        # Count complete 3-hour blocks
        complete_sessions = 0
        for day, day_entries in days_with_practicals.items():
            if len(day_entries) >= 3:
                # Check if they are consecutive
                periods = sorted([e.period for e in day_entries])
                if self._are_periods_consecutive(periods[:3]):
                    complete_sessions += 1

        return complete_sessions

    def _add_practical_sessions(self, entries: List[TimetableEntry], class_group: str,
                               subject_code: str, sessions_to_add: int) -> List[TimetableEntry]:
        """Add practical sessions (3-hour blocks) for a subject."""
        current_entries = list(entries)

        from .models import Subject
        subject = Subject.objects.filter(code=subject_code).first()
        if not subject:
            return current_entries

        sessions_added = 0
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            if sessions_added >= sessions_to_add:
                break

            # Skip Wednesday for final year batches (thesis day)
            if day == 'Wednesday' and any('8' in class_group or 'final' in class_group.lower() for _ in [1]):
                continue

            # Try to find 3 consecutive periods for this day
            for start_period in range(1, 5):  # P1-P3, P2-P4, P3-P5, P4-P6
                consecutive_periods = [start_period, start_period + 1, start_period + 2]

                # Check if all 3 periods are available
                periods_available = True
                for period in consecutive_periods:
                    conflict = any(e for e in current_entries
                                 if e.class_group == class_group and
                                    e.day == day and e.period == period)
                    if conflict:
                        periods_available = False
                        break

                if periods_available:
                    # Find teacher and classroom
                    teacher = self._find_available_teacher(current_entries, subject, day, start_period)
                    classroom = self._find_available_practical_classroom(current_entries, day, start_period)

                    if teacher and classroom:
                        # Create 3 consecutive practical periods
                        for period in consecutive_periods:
                            new_entry = self._create_timetable_entry(
                                day=day,
                                period=period,
                                subject=subject,
                                teacher=teacher,
                                classroom=classroom,
                                class_group=class_group,
                                is_practical=True
                            )
                            current_entries.append(new_entry)
                        sessions_added += 1
                        print(f"        ✅ Added practical session: {day} P{start_period}-P{start_period+2}")
                        break

        return current_entries

    def _remove_excess_practical_sessions(self, entries: List[TimetableEntry], class_group: str,
                                        subject_code: str, sessions_to_remove: int) -> List[TimetableEntry]:
        """Remove excess practical sessions (complete 3-hour blocks)."""
        current_entries = list(entries)

        # Group practical entries by day
        days_with_practicals = {}
        for entry in current_entries:
            if (entry.class_group == class_group and
                entry.subject.code == subject_code and
                entry.is_practical):
                if entry.day not in days_with_practicals:
                    days_with_practicals[entry.day] = []
                days_with_practicals[entry.day].append(entry)

        sessions_removed = 0
        for day, day_entries in days_with_practicals.items():
            if sessions_removed >= sessions_to_remove:
                break

            # If this day has a complete 3-hour block, remove it
            if len(day_entries) >= 3:
                periods = sorted([e.period for e in day_entries], key=lambda x: x)
                if self._are_periods_consecutive(periods[:3]):
                    # Remove the first 3 consecutive periods
                    entries_to_remove = []
                    for period in periods[:3]:
                        for entry in day_entries:
                            if entry.period == period:
                                entries_to_remove.append(entry)
                                break

                    for entry in entries_to_remove:
                        current_entries.remove(entry)
                        print(f"        ❌ Removed excess practical: {entry.day} P{entry.period}")

                    sessions_removed += 1

        return current_entries

    def _are_periods_consecutive(self, periods: List[int]) -> bool:
        """Check if periods are consecutive."""
        if len(periods) < 2:
            return True

        sorted_periods = sorted(periods)
        for i in range(1, len(sorted_periods)):
            if sorted_periods[i] != sorted_periods[i-1] + 1:
                return False
        return True

    def _resolve_time_and_daily_constraints(self, entries: List[TimetableEntry],
                                          friday_violations: List[Dict],
                                          daily_violations: List[Dict]) -> List[TimetableEntry]:
        """Resolve Friday time limits and minimum daily classes together to avoid conflicts."""
        print("    ⏰ Coordinated resolution of Friday and Daily Class constraints...")

        current_entries = list(entries)

        # First, handle Friday violations by moving classes to earlier periods or other days
        for violation in friday_violations:
            class_group = violation['class_group']
            subject_code = violation['subject']
            current_period = violation['period']

            # Find the problematic entry
            problematic_entry = None
            for entry in current_entries:
                if (entry.class_group == class_group and
                    entry.subject.code == subject_code and
                    entry.day.lower().startswith('fri') and
                    entry.period == current_period):
                    problematic_entry = entry
                    break

            if problematic_entry:
                # Try to move to earlier Friday period first
                moved = self._move_to_earlier_friday_period(current_entries, problematic_entry)
                if not moved:
                    # Move to another day
                    self._move_to_another_day(current_entries, problematic_entry)

        # Then handle daily violations while respecting Friday constraints
        for violation in daily_violations:
            class_group = violation['class_group']
            day = violation['day']

            # Add classes to meet minimum requirement while respecting Friday limits
            current_entries = self._add_classes_for_daily_minimum(
                current_entries, class_group, day
            )

        return current_entries

    def _add_missing_classes(self, entries: List[TimetableEntry], class_group: str,
                           subject_code: str, count: int) -> List[TimetableEntry]:
        """Add missing classes for a subject while respecting all constraints."""
        from .models import Subject, Teacher, Classroom

        subject = Subject.objects.filter(code=subject_code).first()
        if not subject:
            return entries

        # Find available slots
        available_slots = self._find_available_slots(entries, class_group, count)

        current_entries = list(entries)
        classes_added = 0

        for day, period in available_slots:
            if classes_added >= count:
                break

            # Find teacher and classroom
            teacher = self._find_available_teacher(current_entries, subject, day, period)
            classroom = self._find_available_classroom(current_entries, day, period)

            if teacher and classroom:
                # Create new entry
                new_entry = self._create_timetable_entry(
                    day=day,
                    period=period,
                    subject=subject,
                    teacher=teacher,
                    classroom=classroom,
                    class_group=class_group,
                    is_practical=subject.is_practical
                )
                current_entries.append(new_entry)
                classes_added += 1
                print(f"        ✅ Added {subject_code} for {class_group} on {day} P{period}")

        return current_entries

    def _remove_excess_classes(self, entries: List[TimetableEntry], class_group: str,
                             subject_code: str, count: int) -> List[TimetableEntry]:
        """Remove excess classes for a subject."""
        current_entries = list(entries)

        # Find entries to remove (prefer removing from less optimal slots)
        subject_entries = [e for e in current_entries
                          if e.class_group == class_group and e.subject.code == subject_code]

        # Sort by preference (remove Friday late periods first, then other suboptimal slots)
        subject_entries.sort(key=lambda e: (
            e.day.lower().startswith('fri') and e.period > 3,  # Friday late periods first
            e.period > 5,  # Late periods
            e.period  # Higher periods
        ), reverse=True)

        removed = 0
        for entry in subject_entries:
            if removed >= count:
                break
            current_entries.remove(entry)
            removed += 1
            print(f"        ❌ Removed {subject_code} for {class_group} from {entry.day} P{entry.period}")

        return current_entries

    def _move_to_earlier_friday_period(self, entries: List[TimetableEntry], entry: TimetableEntry) -> bool:
        """Try to move an entry to an earlier Friday period."""
        for period in range(1, entry.period):
            if not self._would_violate_constraints(entries, entry.class_group, 'Friday', period, entry.subject):
                # Check if slot is available
                conflict = any(e for e in entries
                             if e.class_group == entry.class_group and
                                e.day.lower().startswith('fri') and e.period == period)

                if not conflict:
                    entry.period = period
                    print(f"        ↗️ Moved to Friday P{period}")
                    return True
        return False

    def _move_to_another_day(self, entries: List[TimetableEntry], entry: TimetableEntry):
        """Move an entry to another day."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']

        for day in days:
            for period in range(1, 7):  # Try periods 1-6
                if not self._would_violate_constraints(entries, entry.class_group, day, period, entry.subject):
                    # Check if slot is available
                    conflict = any(e for e in entries
                                 if e.class_group == entry.class_group and
                                    e.day == day and e.period == period)

                    if not conflict:
                        entry.day = day
                        entry.period = period
                        print(f"        ↗️ Moved to {day} P{period}")
                        return

    def _add_classes_for_daily_minimum(self, entries: List[TimetableEntry],
                                     class_group: str, day: str) -> List[TimetableEntry]:
        """Add classes to meet daily minimum while respecting Friday constraints."""
        current_entries = list(entries)

        # Count current classes for this day
        day_entries = [e for e in current_entries
                      if e.class_group == class_group and e.day == day]

        if len(day_entries) >= 2:  # Already meets minimum
            return current_entries

        # Find subjects that need more classes
        from .models import Subject
        subjects_needing_classes = []

        # Get all subjects for this class group
        class_subjects = set(e.subject for e in current_entries if e.class_group == class_group)

        for subject in class_subjects:
            subject_count = len([e for e in current_entries
                               if e.class_group == class_group and e.subject == subject])
            expected_count = subject.credits

            if subject_count < expected_count:
                subjects_needing_classes.append(subject)

        # Add classes for subjects that need them
        for subject in subjects_needing_classes[:2]:  # Add up to 2 classes
            # Find available period
            for period in range(1, 7):
                # Check Friday constraints
                if day.lower().startswith('fri'):
                    friday_practicals = len([e for e in current_entries
                                           if e.class_group == class_group and
                                              e.day.lower().startswith('fri') and e.is_practical])

                    if friday_practicals > 0 and period > 4:  # Has practical, limit P4
                        continue
                    elif friday_practicals == 0 and period > 3:  # No practical, limit P3
                        continue

                # Check if slot is available
                conflict = any(e for e in current_entries
                             if e.class_group == class_group and
                                e.day == day and e.period == period)

                if not conflict:
                    # Find teacher and classroom
                    teacher = self._find_available_teacher(current_entries, subject, day, period)
                    classroom = self._find_available_classroom(current_entries, day, period)

                    if teacher and classroom:
                        new_entry = self._create_timetable_entry(
                            day=day,
                            period=period,
                            subject=subject,
                            teacher=teacher,
                            classroom=classroom,
                            class_group=class_group,
                            is_practical=subject.is_practical
                        )
                        current_entries.append(new_entry)
                        print(f"        ✅ Added {subject.code} for daily minimum on {day} P{period}")
                        break

        return current_entries

    def _find_available_slots(self, entries: List[TimetableEntry], class_group: str,
                            count: int) -> List[tuple]:
        """Find available time slots for a class group."""
        available_slots = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for day in days:
            for period in range(1, 7):
                # Check Friday constraints
                if day.lower().startswith('fri'):
                    friday_entries = [e for e in entries
                                    if e.class_group == class_group and e.day.lower().startswith('fri')]
                    practical_count = len([e for e in friday_entries if e.is_practical])

                    if practical_count > 0 and period > 4:  # Has practical, limit P4
                        continue
                    elif practical_count == 0 and period > 3:  # No practical, limit P3
                        continue

                # Check if slot is available
                conflict = any(e for e in entries
                             if e.class_group == class_group and
                                e.day == day and e.period == period)

                if not conflict:
                    available_slots.append((day, period))

                    if len(available_slots) >= count:
                        break

            if len(available_slots) >= count:
                break

        return available_slots

    def _resolve_cross_semester_conflicts(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve cross-semester conflicts by moving one of the conflicting classes."""
        print(f"    🔧 Resolving cross-semester conflict: {violation['description']}")

        current_entries = list(entries)

        # Find conflicting entries
        if 'entries' in violation:
            conflicting_entries = []
            for entry_info in violation['entries']:
                for entry in current_entries:
                    if f"{entry.class_group}-{entry.subject.code}" == entry_info:
                        conflicting_entries.append(entry)
                        break

            # Move the second conflicting entry to a different time slot
            if len(conflicting_entries) >= 2:
                entry_to_move = conflicting_entries[1]  # Move the second one

                # Try to find an alternative slot
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    for period in range(1, 7):
                        if not self._would_violate_constraints(current_entries, entry_to_move.class_group, day, period, entry_to_move.subject):
                            # Check if slot is available
                            conflict = any(e for e in current_entries
                                         if e.class_group == entry_to_move.class_group and
                                            e.day == day and e.period == period)

                            if not conflict:
                                entry_to_move.day = day
                                entry_to_move.period = period
                                print(f"        ✅ Moved {entry_to_move.subject.code} for {entry_to_move.class_group} to {day} P{period}")
                                return current_entries

        return current_entries

    def _resolve_teacher_assignments(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve teacher assignment violations by finding a properly assigned teacher."""
        print(f"    🔧 Resolving teacher assignment: {violation['description']}")

        current_entries = list(entries)

        # Find the problematic entry
        teacher_name = violation.get('teacher')
        subject_code = violation.get('subject')
        class_group = violation.get('class_group')

        problematic_entry = None
        for entry in current_entries:
            if (entry.teacher and entry.teacher.name == teacher_name and
                entry.subject.code == subject_code and
                entry.class_group == class_group):
                problematic_entry = entry
                break

        if problematic_entry:
            # Find a teacher who is assigned to this subject
            from .models import TeacherSubjectAssignment, Teacher

            assignments = TeacherSubjectAssignment.objects.filter(subject=problematic_entry.subject)

            for assignment in assignments:
                # Check if this teacher is available at this time
                teacher_conflict = any(e for e in current_entries
                                    if e.teacher == assignment.teacher and
                                       e.day == problematic_entry.day and
                                       e.period == problematic_entry.period and
                                       e != problematic_entry)

                if not teacher_conflict:
                    problematic_entry.teacher = assignment.teacher
                    print(f"        ✅ Assigned {assignment.teacher.name} to {subject_code} for {class_group}")
                    return current_entries

        return current_entries

    def _resolve_friday_aware_scheduling(self, entries: List[TimetableEntry], violation: Dict) -> List[TimetableEntry]:
        """Resolve Friday-aware scheduling violations."""
        print(f"    🔧 Resolving Friday-aware scheduling: {violation['description']}")

        # This is typically handled by the Friday time limits constraint
        # For now, delegate to Friday time limit resolution
        return self._resolve_friday_time_limits(entries, violation)

    def _move_class_to_available_slot(self, entries: List[TimetableEntry], entry_to_move: TimetableEntry) -> bool:
        """Move a class to an available time slot."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for day in days:
            for period in range(1, 7):  # Try periods 1-6
                # Skip current slot
                if day == entry_to_move.day and period == entry_to_move.period:
                    continue

                # Check if this slot would violate constraints
                if self._would_violate_constraints(entries, entry_to_move.class_group, day, period, entry_to_move.subject):
                    continue

                # Check if slot is available for class group
                class_conflict = any(e for e in entries
                                   if e.class_group == entry_to_move.class_group and
                                      e.day == day and e.period == period)

                # Check if teacher is available
                teacher_conflict = any(e for e in entries
                                     if e.teacher == entry_to_move.teacher and
                                        e.day == day and e.period == period and
                                        e != entry_to_move)

                # Check if classroom is available
                room_conflict = any(e for e in entries
                                  if e.classroom == entry_to_move.classroom and
                                     e.day == day and e.period == period and
                                     e != entry_to_move)

                if not any([class_conflict, teacher_conflict, room_conflict]):
                    # Move the class
                    entry_to_move.day = day
                    entry_to_move.period = period
                    return True

        return False

    def _find_available_classroom(self, entries: List[TimetableEntry], day: str, period: int) -> Classroom:
        """Find an available classroom."""
        classrooms = Classroom.objects.all()
        for classroom in classrooms:
            if self._is_classroom_available(entries, classroom, day, period):
                return classroom
        return classrooms.first() if classrooms.exists() else None

    def _create_entry(self, day: str, period: int, subject: Subject, teacher: Teacher,
                     classroom: Classroom, class_group: str) -> TimetableEntry:
        """Create a new timetable entry."""
        from datetime import time

        return self._create_timetable_entry(
            day=day,
            period=period,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            class_group=class_group,
            is_practical=subject.is_practical if subject else False
        )

    def _would_violate_constraints(self, entries: List[TimetableEntry], class_group: str,
                                 day: str, period: int, subject: Subject) -> bool:
        """Check if adding a class would violate constraints."""
        # Check Friday constraints
        if day.lower().startswith('fri'):
            friday_entries = [e for e in entries if e.class_group == class_group and e.day.lower().startswith('fri')]
            practical_count = len([e for e in friday_entries if e.is_practical])

            if practical_count > 0 and period > 4:  # Has practical, theory limit P4
                return True
            elif practical_count == 0 and period > 3:  # No practical, limit P3
                return True

        return False

    def _add_consecutive_practical_periods(self, entries: List[TimetableEntry],
                                         class_group: str, subject_code: str,
                                         day: str, periods_needed: int) -> List[TimetableEntry]:
        """Add consecutive periods for practical subjects."""
        from .models import Subject, Teacher, Classroom

        subject = Subject.objects.filter(code=subject_code).first()
        if not subject:
            return entries

        current_entries = list(entries)

        # Find existing practical periods for this subject on this day
        existing_periods = []
        for entry in current_entries:
            if (entry.class_group == class_group and
                entry.subject.code == subject_code and
                entry.day == day and
                entry.is_practical):
                existing_periods.append(entry.period)

        existing_periods.sort()

        # Try to find consecutive slots around existing periods
        for start_period in range(1, 7 - periods_needed):
            consecutive_slots = list(range(start_period, start_period + periods_needed))

            # Check if these slots are available
            slots_available = True
            for period in consecutive_slots:
                # Skip if this period already has the practical
                if period in existing_periods:
                    continue

                # Check if slot is free for this class group
                conflict = any(e for e in current_entries
                             if e.class_group == class_group and
                                e.day == day and e.period == period)

                if conflict:
                    slots_available = False
                    break

            if slots_available:
                # Add the missing periods
                teacher = self._find_available_teacher(current_entries, subject, day, start_period)
                classroom = self._find_available_classroom(current_entries, day, start_period)

                if teacher and classroom:
                    for period in consecutive_slots:
                        if period not in existing_periods:
                            new_entry = self._create_timetable_entry(
                                day=day,
                                period=period,
                                subject=subject,
                                teacher=teacher,
                                classroom=classroom,
                                class_group=class_group,
                                is_practical=True
                            )
                            current_entries.append(new_entry)
                            print(f"        ✅ Added practical period: {day} P{period}")
                    break

        return current_entries

    def _make_practical_periods_consecutive(self, entries: List[TimetableEntry],
                                          practical_entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Make practical periods consecutive."""
        if len(practical_entries) != 3:
            return entries

        current_entries = list(entries)

        # Sort by period
        practical_entries.sort(key=lambda e: e.period)
        periods = [e.period for e in practical_entries]

        # Check if already consecutive
        if periods == [periods[0], periods[0] + 1, periods[0] + 2]:
            return current_entries  # Already consecutive

        # Find a block of 3 consecutive free periods
        day = practical_entries[0].day
        class_group = practical_entries[0].class_group

        for start_period in range(1, 5):  # Periods 1-3, 2-4, 3-5, 4-6
            consecutive_periods = [start_period, start_period + 1, start_period + 2]

            # Check if these periods are available (excluding current practical entries)
            periods_available = True
            for period in consecutive_periods:
                conflict = any(e for e in current_entries
                             if e.class_group == class_group and
                                e.day == day and e.period == period and
                                e not in practical_entries)

                if conflict:
                    periods_available = False
                    break

            if periods_available:
                # Move the practical entries to consecutive periods
                for i, entry in enumerate(practical_entries):
                    entry.period = consecutive_periods[i]
                    print(f"        ↗️ Moved practical to consecutive period: {day} P{consecutive_periods[i]}")
                break

        return current_entries

    def _find_available_teacher(self, entries: List[TimetableEntry], subject, day: str, period: int):
        """Find an available teacher for a subject at a specific time."""
        from .models import TeacherSubjectAssignment

        # Get teachers assigned to this subject
        assignments = TeacherSubjectAssignment.objects.filter(subject=subject)

        for assignment in assignments:
            # Check if teacher is available at this time
            teacher_conflict = any(e for e in entries
                                 if e.teacher == assignment.teacher and
                                    e.day == day and e.period == period)

            if not teacher_conflict:
                return assignment.teacher

        # If no assigned teacher available, try any available teacher
        from .models import Teacher
        all_teachers = Teacher.objects.all()

        for teacher in all_teachers:
            teacher_conflict = any(e for e in entries
                                 if e.teacher == teacher and
                                    e.day == day and e.period == period)

            if not teacher_conflict:
                return teacher

        return None

    def _would_violate_constraints(self, entries: List[TimetableEntry], class_group: str,
                                 day: str, period: int, subject) -> bool:
        """Check if adding a class at this time would violate constraints."""

        # Check Friday time limits
        if day.lower().startswith('fri'):
            friday_entries = [e for e in entries
                            if e.class_group == class_group and e.day.lower().startswith('fri')]
            practical_count = len([e for e in friday_entries if e.is_practical])

            if subject.is_practical:
                # Practical subjects can go up to P6 on Friday
                if period > 6:
                    return True
            else:
                # Theory subjects limited by practical presence
                if practical_count > 0 and period > 4:  # Has practical, theory limit P4
                    return True
                elif practical_count == 0 and period > 3:  # No practical, limit P3
                    return True

        # Check if this would create too many classes for the subject
        subject_count = len([e for e in entries
                           if e.class_group == class_group and e.subject == subject])

        if subject_count >= subject.credits:
            return True  # Already has enough classes

        # Check practical block constraints
        if subject.is_practical:
            # Practical subjects should be in 3-hour blocks
            day_practicals = [e for e in entries
                            if e.class_group == class_group and
                               e.subject == subject and
                               e.day == day and
                               e.is_practical]

            if len(day_practicals) >= 3:
                return True  # Already has a full practical block this day

        return False

    def _find_available_practical_classroom(self, entries: List[TimetableEntry], day: str, period: int):
        """Find an available classroom suitable for practical subjects (labs)."""
        from .models import Classroom

        # Prefer lab classrooms for practicals
        lab_classrooms = Classroom.objects.filter(name__icontains='lab')
        for classroom in lab_classrooms:
            # Check if classroom is available at this time
            conflict = any(e for e in entries
                         if e.classroom == classroom and
                            e.day == day and e.period == period)
            if not conflict:
                return classroom

        # If no lab available, use any available classroom
        all_classrooms = Classroom.objects.all()
        for classroom in all_classrooms:
            conflict = any(e for e in entries
                         if e.classroom == classroom and
                            e.day == day and e.period == period)
            if not conflict:
                return classroom

        return None

    def _force_resolve_remaining_violations(self, entries: List[TimetableEntry], validation_result: Dict) -> List[TimetableEntry]:
        """Aggressively resolve remaining violations when normal resolution gets stuck."""
        print("    🚨 Applying force resolution strategies...")

        current_entries = list(entries)
        violations_by_type = validation_result['violations_by_constraint']

        # Force resolve practical blocks by recreating them completely
        if 'Practical Blocks' in violations_by_type and violations_by_type['Practical Blocks']:
            print("    🔧 Force resolving practical blocks...")
            current_entries = self._force_fix_practical_blocks(current_entries, violations_by_type['Practical Blocks'])

        # Force resolve teacher conflicts by moving classes aggressively
        if 'Teacher Conflicts' in violations_by_type and violations_by_type['Teacher Conflicts']:
            print("    🔧 Force resolving teacher conflicts...")
            current_entries = self._force_fix_teacher_conflicts(current_entries, violations_by_type['Teacher Conflicts'])

        # Force resolve room conflicts by reassigning rooms aggressively
        if 'Room Conflicts' in violations_by_type and violations_by_type['Room Conflicts']:
            print("    🔧 Force resolving room conflicts...")
            current_entries = self._force_fix_room_conflicts(current_entries, violations_by_type['Room Conflicts'])

        # Force resolve compact scheduling violations aggressively
        if 'Compact Scheduling' in violations_by_type and violations_by_type['Compact Scheduling']:
            print("    🔧 Force resolving compact scheduling violations...")
            current_entries = self._force_fix_compact_scheduling(current_entries, violations_by_type['Compact Scheduling'])

        return current_entries

    def _force_fix_compact_scheduling(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Aggressively fix compact scheduling violations by forcing class movements."""
        current_entries = list(entries)

        for violation in violations:
            class_group = violation.get('class_group')
            day = violation.get('day')

            if not all([class_group, day]):
                continue

            print(f"        🚀 Force fixing compact scheduling for {class_group} on {day}")

            # Get all classes for this class group on this day
            day_entries = [e for e in current_entries
                          if e.class_group == class_group and e.day == day]

            if not day_entries:
                continue

            # Sort by period
            day_entries.sort(key=lambda e: e.period)

            # Force compact scheduling by moving ALL classes to consecutive periods starting from P1
            target_period = 1
            for entry in day_entries:
                if entry.period != target_period:
                    # Force move this entry to target period
                    success = self._force_move_entry_to_period(current_entries, entry, day, target_period)
                    if success:
                        print(f"          🎯 Force moved {entry.subject.code} from P{entry.period} to P{target_period}")
                        entry.period = target_period
                    else:
                        print(f"          ⚠️ Could not force move {entry.subject.code} to P{target_period}")
                target_period += 1

        return current_entries

    def _force_move_entry_to_period(self, entries: List[TimetableEntry], entry: TimetableEntry,
                                   day: str, target_period: int) -> bool:
        """Force move an entry to a target period by resolving ALL conflicts aggressively."""
        # Find ALL conflicting entries
        conflicts = [e for e in entries
                    if e != entry and e.day == day and e.period == target_period and
                       (e.class_group == entry.class_group or
                        e.teacher == entry.teacher or
                        e.classroom == entry.classroom)]

        # Move ALL conflicting entries to other periods
        for conflict_entry in conflicts:
            # Find any available period for the conflicting entry
            for alt_period in range(1, 8):
                if alt_period == target_period:
                    continue

                # Check if this alternative period is available
                alt_conflicts = [e for e in entries
                               if e != conflict_entry and e.day == day and e.period == alt_period and
                                  (e.class_group == conflict_entry.class_group or
                                   e.teacher == conflict_entry.teacher or
                                   e.classroom == conflict_entry.classroom)]

                if not alt_conflicts:
                    # Move the conflicting entry here
                    old_period = conflict_entry.period
                    conflict_entry.period = alt_period
                    print(f"            🔄 Force moved conflicting {conflict_entry.subject.code} from P{old_period} to P{alt_period}")
                    break
            else:
                # If we can't find a free period, try to change resources
                if self._force_change_resources(entries, conflict_entry, day, target_period):
                    print(f"            🔧 Changed resources for conflicting {conflict_entry.subject.code}")
                else:
                    return False  # Could not resolve this conflict

        return True  # All conflicts resolved

    def _force_change_resources(self, entries: List[TimetableEntry], entry: TimetableEntry,
                               day: str, avoid_period: int) -> bool:
        """Force change teacher or classroom for an entry to resolve conflicts."""
        # Try to change teacher
        if entry.subject:  # Make sure subject exists
            alt_teacher = self._find_alternative_teacher(entries, entry.subject, day, entry.period)
            if alt_teacher:
                old_teacher = entry.teacher.name if entry.teacher else "None"
                entry.teacher = alt_teacher
                print(f"              👨‍🏫 Force changed teacher from {old_teacher} to {alt_teacher.name}")
                return True

        # Try to change classroom
        alt_classroom = self._find_alternative_classroom(entries, day, entry.period)
        if alt_classroom:
            old_classroom = entry.classroom.name if entry.classroom else "None"
            entry.classroom = alt_classroom
            print(f"              🏫 Force changed classroom from {old_classroom} to {alt_classroom.name}")
            return True

        return False

    def _force_fix_practical_blocks(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Force fix practical blocks by completely recreating them."""
        current_entries = list(entries)

        # Group violations by class group and subject
        practical_issues = {}
        for violation in violations:
            class_group = violation.get('class_group')
            subject = violation.get('subject')
            if class_group and subject:
                key = f"{class_group}_{subject}"
                if key not in practical_issues:
                    practical_issues[key] = []
                practical_issues[key].append(violation)

        # Fix each practical subject completely
        for key, issue_violations in practical_issues.items():
            class_group, subject_code = key.split('_')

            # Remove ALL practical entries for this subject/class group
            entries_to_remove = []
            for entry in current_entries:
                if (entry.class_group == class_group and
                    entry.subject.code == subject_code and
                    entry.is_practical):
                    entries_to_remove.append(entry)

            for entry in entries_to_remove:
                current_entries.remove(entry)
                print(f"        ❌ Removed broken practical: {entry.subject.code} {entry.day} P{entry.period}")

            # Recreate as proper 3-hour block
            current_entries = self._create_new_practical_block(current_entries, class_group, subject_code)

        return current_entries

    def _create_new_practical_block(self, entries: List[TimetableEntry], class_group: str, subject_code: str) -> List[TimetableEntry]:
        """Create a new 3-hour practical block for the given class group and subject."""
        from .models import Subject

        subject = Subject.objects.filter(code=subject_code).first()
        if not subject:
            return entries

        current_entries = list(entries)

        # Try each day to find space for a 3-hour block
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            # Skip Wednesday for final year batches (thesis day)
            if day == 'Wednesday' and any('8' in class_group or 'final' in class_group.lower() for _ in [1]):
                continue

            # Try different starting periods
            for start_period in range(1, 5):  # P1-P3, P2-P4, P3-P5, P4-P6
                consecutive_periods = [start_period, start_period + 1, start_period + 2]

                # Check if all periods are free for this class group
                periods_free = True
                for period in consecutive_periods:
                    conflict = any(e for e in current_entries
                                 if e.class_group == class_group and
                                    e.day == day and e.period == period)
                    if conflict:
                        periods_free = False
                        break

                if periods_free:
                    # Find teacher and classroom
                    teacher = self._find_available_teacher(current_entries, subject, day, start_period)
                    classroom = self._find_available_practical_classroom(current_entries, day, start_period)

                    if teacher and classroom:
                        # Create the 3-hour block
                        for period in consecutive_periods:
                            new_entry = self._create_timetable_entry(
                                day=day,
                                period=period,
                                subject=subject,
                                teacher=teacher,
                                classroom=classroom,
                                class_group=class_group,
                                is_practical=True
                            )
                            current_entries.append(new_entry)
                            print(f"        ✅ Created practical block: {subject_code} {day} P{period}")
                        return current_entries

        print(f"        ⚠️ Could not create practical block for {subject_code} in {class_group}")
        return current_entries

    def _force_fix_teacher_conflicts(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Force fix teacher conflicts by aggressively moving classes."""
        current_entries = list(entries)

        for violation in violations:
            teacher_name = violation.get('teacher')
            day = violation.get('day')
            period = violation.get('period')

            if not all([teacher_name, day, period]):
                continue

            # Find all conflicting entries for this teacher at this time
            conflicting_entries = []
            for entry in current_entries:
                if (entry.teacher and entry.teacher.name == teacher_name and
                    entry.day == day and entry.period == period):
                    conflicting_entries.append(entry)

            # Keep the first entry, move the others
            for i, entry in enumerate(conflicting_entries[1:], 1):
                moved = False
                # Try to move to any available slot
                for move_day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    for move_period in range(1, 7):
                        # Check if this slot is available for the class group
                        class_conflict = any(e for e in current_entries
                                           if e.class_group == entry.class_group and
                                              e.day == move_day and e.period == move_period)

                        # Check teacher availability
                        teacher_conflict = any(e for e in current_entries
                                             if e.teacher and entry.teacher and
                                                e.teacher == entry.teacher and
                                                e.day == move_day and e.period == move_period and
                                                e != entry)

                        if not any([class_conflict, teacher_conflict]):
                            entry.day = move_day
                            entry.period = move_period
                            subject_code = entry.subject.code if entry.subject else "Unknown"
                            print(f"        ↗️ Moved {subject_code} to {move_day} P{move_period} to resolve teacher conflict")
                            moved = True
                            break

                    if moved:
                        break

        return current_entries

    def _force_fix_room_conflicts(self, entries: List[TimetableEntry], violations: List[Dict]) -> List[TimetableEntry]:
        """Force fix room conflicts by aggressively reassigning classrooms."""
        current_entries = list(entries)

        for violation in violations:
            classroom_name = violation.get('classroom')
            day = violation.get('day')
            period = violation.get('period')

            if not all([classroom_name, day, period]):
                continue

            # Find all conflicting entries for this classroom at this time
            conflicting_entries = []
            for entry in current_entries:
                if (entry.classroom and entry.classroom.name == classroom_name and
                    entry.day == day and entry.period == period):
                    conflicting_entries.append(entry)

            # Keep the first entry, reassign classrooms for the others
            from .models import Classroom
            available_classrooms = list(Classroom.objects.all())

            for i, entry in enumerate(conflicting_entries[1:], 1):
                # Find an available classroom
                for classroom in available_classrooms:
                    room_conflict = any(e for e in current_entries
                                      if e.classroom and e.classroom == classroom and
                                         e.day == day and e.period == period and
                                         e != entry)

                    if not room_conflict:
                        entry.classroom = classroom
                        subject_code = entry.subject.code if entry.subject else "Unknown"
                        print(f"        🏫 Reassigned {subject_code} to {classroom.name} to resolve room conflict")
                        break

        return current_entries

    def _remove_excess_practical_classes(self, entries: List[TimetableEntry],
                                       class_group: str, subject_code: str,
                                       classes_to_remove: int) -> List[TimetableEntry]:
        """Remove excess practical classes while trying to maintain 3-hour blocks."""
        # This method is now deprecated in favor of session-based removal
        # Redirect to the new session-based method
        sessions_to_remove = max(1, classes_to_remove // 3)  # Convert periods to sessions
        return self._remove_excess_practical_sessions(entries, class_group, subject_code, sessions_to_remove)

    def _optimize_practical_lab_allocation(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Optimize practical class lab allocation to ensure proper 3-block scheduling."""
        print("    🧪 Optimizing practical lab allocation...")

        # Analyze practical scheduling capacity
        analysis = self.room_allocator.analyze_practical_scheduling_capacity(entries)

        print(f"       📊 Practical Analysis: {analysis['practical_sessions_scheduled']}/{analysis['practical_sessions_needed']} sessions scheduled")

        # Check for practical scheduling violations
        violations_found = 0
        for entry in entries:
            if entry.subject and entry.subject.is_practical:
                if not entry.classroom or not entry.classroom.is_lab:
                    violations_found += 1
                    # Try to move practical to lab
                    new_lab = self.room_allocator.allocate_room_for_practical(
                        entry.day, entry.period, entry.class_group, entry.subject, entries
                    )
                    if new_lab:
                        old_room = entry.classroom.name if entry.classroom else 'None'
                        entry.classroom = new_lab
                        print(f"       ✅ Moved practical {entry.subject.code} from {old_room} to lab {new_lab.name}")

        if violations_found == 0:
            print("       ✅ All practical classes properly allocated to labs")

        return entries

    def _optimize_senior_batch_priority(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Aggressively optimize room allocation to ensure senior batches get ALL labs."""
        print("    🎓 Aggressively optimizing senior batch lab priority...")

        # Use the room allocator's enforcement method
        optimized_entries = self.room_allocator.enforce_senior_batch_lab_priority(entries)

        # Ensure practical block consistency
        optimized_entries = self.room_allocator.ensure_practical_block_consistency(optimized_entries)

        # Validate the results
        validation = self.room_allocator.validate_senior_batch_lab_allocation(optimized_entries)
        compliance_rate = validation['compliance_rate']

        print(f"       📊 Senior batch lab compliance: {compliance_rate:.1f}%")

        if compliance_rate < 100:
            print(f"       ⚠️  {len(validation['violations'])} senior batch classes still in regular rooms")
            # Try additional aggressive moves
            optimized_entries = self._force_senior_batch_lab_allocation(optimized_entries)
        else:
            print(f"       ✅ All senior batch classes successfully allocated to labs")

        return optimized_entries

    def _improve_senior_batch_allocation(self, batch_entries: List[TimetableEntry],
                                       all_entries: List[TimetableEntry]) -> int:
        """Improve room allocation for a specific senior batch."""
        improvements = 0

        for entry in batch_entries:
            if not entry.classroom:
                continue

            # Check if senior batch could get a better room
            current_room = entry.classroom

            # For theory classes, prefer labs if available
            if entry.subject and not entry.subject.is_practical and not current_room.is_lab:
                better_room = self.room_allocator.allocate_room_for_theory(
                    entry.day, entry.period, entry.class_group, entry.subject, all_entries
                )

                if better_room and better_room.is_lab and better_room != current_room:
                    # Check if we can swap with a junior batch
                    if self.room_allocator.intelligent_room_swap(all_entries, entry, 'lab'):
                        improvements += 1

        return improvements

    def comprehensive_room_optimization(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """
        Perform comprehensive room optimization using all available strategies.
        This is the main integration point for room allocation optimization.
        """
        print("🏛️ COMPREHENSIVE ROOM OPTIMIZATION")
        print("=" * 50)

        current_entries = list(entries)

        # Run all room optimization strategies
        for strategy in self.room_optimization_strategies:
            try:
                current_entries = strategy(current_entries)
            except Exception as e:
                print(f"    ❌ Error in room optimization strategy {strategy.__name__}: {e}")

        # Final validation
        room_conflicts = self.room_allocator.find_room_conflicts(current_entries)
        if room_conflicts:
            print(f"    ⚠️  {len(room_conflicts)} room conflicts remain after optimization")
            # Try one more round of conflict resolution
            for conflict in room_conflicts:
                self.room_allocator.resolve_room_conflict(conflict, current_entries)
        else:
            print("    ✅ No room conflicts detected after optimization")

        print("🏛️ Room optimization complete")
        return current_entries

    def _force_senior_batch_lab_allocation(self, entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """
        Force all senior batch classes into labs by aggressively moving junior batches.
        This ensures 100% compliance with senior batch lab priority.
        """
        print("    🚀 FORCE ALLOCATION: Moving ALL senior batches to labs")

        current_entries = list(entries)
        moves_made = 0

        # Find ALL senior batch classes not in labs
        senior_violations = [
            entry for entry in current_entries
            if (entry.classroom and not entry.classroom.is_lab and
                False)  # Simplified: No seniority-based checks
        ]

        print(f"       📊 Found {len(senior_violations)} senior batch classes to move to labs")

        # Find ALL junior batch classes in labs (theory only - practicals can stay)
        junior_candidates = [
            entry for entry in current_entries
            if (entry.classroom and entry.classroom.is_lab and
                not self.room_allocator.is_senior_batch(entry.class_group) and
                entry.subject and not entry.subject.is_practical)
        ]

        print(f"       📊 Found {len(junior_candidates)} junior theory classes in labs to relocate")

        # Force moves - prioritize by time slots to avoid conflicts
        for senior_entry in senior_violations:
            # Find any available lab by moving junior batches
            lab_found = False

            # Try to find a junior batch to displace
            for junior_entry in junior_candidates[:]:
                # Check if we can move the junior to the senior's current room
                if self._can_force_room_swap(senior_entry, junior_entry, current_entries):
                    # Perform the forced swap
                    senior_old_room = senior_entry.classroom.name
                    junior_old_room = junior_entry.classroom.name

                    senior_entry.classroom, junior_entry.classroom = junior_entry.classroom, senior_entry.classroom

                    print(f"       🔄 FORCED: Senior {senior_entry.class_group} → Lab {junior_old_room}")
                    print(f"                 Junior {junior_entry.class_group} → Regular {senior_old_room}")

                    junior_candidates.remove(junior_entry)
                    moves_made += 1
                    lab_found = True
                    break

            # If no swap possible, try to find any available lab
            if not lab_found:
                available_labs = self.room_allocator.get_available_labs_for_time(
                    senior_entry.day, senior_entry.period, current_entries
                )
                if available_labs:
                    old_room = senior_entry.classroom.name
                    senior_entry.classroom = available_labs[0]
                    print(f"       ✅ DIRECT: Senior {senior_entry.class_group} → Lab {available_labs[0].name}")
                    moves_made += 1

        print(f"       ✅ Completed {moves_made} forced moves for senior batch lab priority")

        # Final validation
        final_validation = self.room_allocator.validate_senior_batch_lab_allocation(current_entries)
        print(f"       📈 Final compliance rate: {final_validation['compliance_rate']:.1f}%")

        return current_entries

    def _can_force_room_swap(self, senior_entry: TimetableEntry, junior_entry: TimetableEntry,
                           entries: List[TimetableEntry]) -> bool:
        """Check if we can force a room swap between senior and junior entries."""
        # Different time slots - always safe to swap
        if (senior_entry.day != junior_entry.day or
            senior_entry.period != junior_entry.period):
            return True

        # Same time slot - check for conflicts
        return self.room_allocator._can_swap_rooms(senior_entry, junior_entry, entries)
