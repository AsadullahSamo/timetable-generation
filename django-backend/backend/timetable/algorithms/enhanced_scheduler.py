"""
ENHANCED TIMETABLE SCHEDULER
============================
Integrates enhanced room allocation and constraint resolution to address client requirements:
- Proper room allocation based on batch years
- 3-block consecutive practical sessions in same lab
- Zero constraint violations
- Consistent room assignment per section per day
- NEW: Same theory subject distribution
- NEW: Breaks between classes
- NEW: Teacher breaks after 2 consecutive classes
"""

import random
from datetime import time, datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.db import models, transaction
from ..models import Subject, Teacher, Classroom, TimetableEntry, ScheduleConfig, TeacherSubjectAssignment, Batch
from ..enhanced_room_allocator import EnhancedRoomAllocator
from ..enhanced_constraint_resolver import EnhancedConstraintResolver
from ..enhanced_constraint_validator import EnhancedConstraintValidator
from collections import defaultdict


class EnhancedScheduler:
    """
    Enhanced timetable scheduler with integrated room allocation and constraint resolution.
    """
    
    def __init__(self, config: ScheduleConfig):
        self.config = config
        self.days = config.days
        self.periods = [int(p) for p in config.periods]
        self.start_time = config.start_time
        self.class_duration = config.class_duration
        
        # Initialize enhanced components
        self.room_allocator = EnhancedRoomAllocator()
        self.constraint_resolver = EnhancedConstraintResolver()
        self.constraint_validator = EnhancedConstraintValidator()  # Use enhanced validator
        
        # Get class groups from Batch model
        self.class_groups = [batch.name for batch in Batch.objects.all()]
        
        # Load all available data
        self.all_subjects = list(Subject.objects.all())
        self.all_teachers = list(Teacher.objects.all())
        self.all_classrooms = list(Classroom.objects.all())
        
        # Create default classroom if none exist
        if not self.all_classrooms:
            classroom = Classroom.objects.create(
                name="Default Classroom",
                building="Main Building"
            )
            self.all_classrooms = [classroom]
        
        # Tracking structures
        self.global_teacher_schedule = {}
        self.global_classroom_schedule = {}
        
        print(f"📊 Enhanced Scheduler: {len(self.all_subjects)} subjects, {len(self.all_teachers)} teachers, {len(self.all_classrooms)} classrooms")
        print(f"🏛️ Enhanced Room Allocation: {len(self.room_allocator.labs)} labs, {len(self.room_allocator.academic_building_rooms)} academic rooms, {len(self.room_allocator.main_building_rooms)} main rooms")
        print(f"🔧 Enhanced Constraint Validation: All 19 constraints including teacher unavailability")
    
    def generate_timetable(self) -> Dict:
        """Generate complete timetable with enhanced room allocation and constraint resolution."""
        start_time = datetime.now()
        
        print(f"🚀 ENHANCED TIMETABLE GENERATION: {self.config.name}")
        print(f"📅 Class groups: {self.class_groups}")
        
        try:
            # STEP 1: Clean up previous timetables for this config
            self._cleanup_previous_timetables()
            
            # STEP 2: Load existing cross-semester schedules
            self._load_existing_schedules()
            
            # STEP 3: Expand class groups to include sections
            expanded_class_groups = self._expand_class_groups_with_sections()
            print(f"📋 Expanded to sections: {expanded_class_groups}")
            
            # STEP 4: Generate timetables for all class groups (including sections)
            all_entries = []
            
            for class_group in expanded_class_groups:
                print(f"\n📋 Generating for {class_group}...")
                
                # Get subjects for this specific class group
                subjects = self._get_subjects_for_class_group(class_group)
                print(f"   📚 Found {len(subjects)} subjects for {class_group}")
                
                # Generate entries for this class group
                entries = self._generate_for_class_group(class_group, subjects)
                all_entries.extend(entries)
                
                print(f"   ✅ Generated {len(entries)} entries for {class_group}")
            
            # STEP 5: Apply enhanced constraint resolution with NEW constraints
            print(f"\n🔧 Applying enhanced constraint resolution (including 3 new constraints)...")
            resolution_result = self.constraint_resolver.resolve_all_violations(all_entries)
            
            if resolution_result['overall_success']:
                print(f"🎉 All constraints resolved successfully (including 3 new ones)!")
            else:
                print(f"⚠️ Some constraints remain unresolved: {resolution_result['final_violations']} violations")
            
            # STEP 6: Final validation with enhanced validator
            print(f"\n🔍 Final validation with enhanced constraint validator...")
            final_validation = self.constraint_validator.validate_all_constraints(resolution_result['entries'])
            print(f"📊 Final validation: {final_validation['total_violations']} violations")
            
            # STEP 7: Save to database
            saved_count = self._save_entries_to_database(resolution_result['entries'])
            
            # STEP 8: Generate final report
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            report = {
                'success': True,
                'entries_generated': len(resolution_result['entries']),
                'entries_saved': saved_count,
                'generation_time': generation_time,
                'initial_violations': resolution_result['initial_violations'],
                'final_violations': resolution_result['final_violations'],
                'iterations_completed': resolution_result['iterations_completed'],
                'final_validation_violations': final_validation['total_violations'],
                'room_allocation_report': self.room_allocator.get_allocation_report()
            }
            
            print(f"\n📊 ENHANCED GENERATION COMPLETE:")
            print(f"   ✅ Entries generated: {report['entries_generated']}")
            print(f"   ✅ Entries saved: {report['entries_saved']}")
            print(f"   ⏱️ Generation time: {generation_time:.2f} seconds")
            print(f"   🔧 Initial violations: {report['initial_violations']}")
            print(f"   🔧 Final violations: {report['final_violations']}")
            print(f"   🔧 Final validation violations: {report['final_validation_violations']}")
            print(f"   🔄 Iterations completed: {report['iterations_completed']}")
            print(f"   🆕 3 NEW CONSTRAINTS: Same theory subject, Breaks between classes, Teacher breaks")
            
            return report
            
        except Exception as e:
            print(f"❌ Error during enhanced timetable generation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'entries_generated': 0,
                'entries_saved': 0
            }
    
    def _cleanup_previous_timetables(self):
        """Clean up previous timetables for this config."""
        try:
            TimetableEntry.objects.filter(schedule_config=self.config).delete()
            print(f"🧹 Cleaned up previous timetables for config: {self.config.name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up previous timetables: {str(e)}")
    
    def _load_existing_schedules(self):
        """Load existing cross-semester schedules for conflict detection."""
        try:
            existing_entries = TimetableEntry.objects.filter(schedule_config__isnull=False).exclude(schedule_config=self.config)
            for entry in existing_entries:
                self._mark_global_schedule(entry.teacher, entry.classroom, entry.day, entry.period)
            print(f"📋 Loaded {len(existing_entries)} existing cross-semester entries")
        except Exception as e:
            print(f"⚠️ Warning: Could not load existing schedules: {str(e)}")
    
    def _expand_class_groups_with_sections(self) -> List[str]:
        """Expand class groups to include individual sections."""
        expanded_groups = []
        
        for class_group in self.class_groups:
            # Get batch details
            batch = Batch.objects.filter(name=class_group).first()
            if batch and batch.total_sections > 1:
                # Add individual sections
                for section in batch.get_sections():
                    expanded_groups.append(f"{class_group}-{section}")
            else:
                # Single section or no batch info
                expanded_groups.append(class_group)
        
        return expanded_groups
    
    def _get_subjects_for_class_group(self, class_group: str) -> List[Subject]:
        """Get subjects for a specific class group."""
        # Extract batch name from class group
        batch_name = class_group.split('-')[0] if '-' in class_group else class_group
        
        # Get subjects for this batch
        subjects = Subject.objects.filter(batch=batch_name)
        
        # Filter by teacher assignments if available
        available_subjects = []
        for subject in subjects:
            if self._has_teacher_for_subject(subject, class_group):
                available_subjects.append(subject)
        
        return available_subjects
    
    def _has_teacher_for_subject(self, subject: Subject, class_group: str) -> bool:
        """Check if there's a teacher available for this subject and class group."""
        batch_name = class_group.split('-')[0] if '-' in class_group else class_group
        section = class_group.split('-')[1] if '-' in class_group else None
        
        # Check teacher assignments
        assignments = TeacherSubjectAssignment.objects.filter(subject=subject)
        
        for assignment in assignments:
            if assignment.batch.name == batch_name:
                if section is None:
                    return True
                
                # Map section letters to Roman numerals
                section_mapping = {'A': 'I', 'B': 'II', 'C': 'III'}
                mapped_section = section_mapping.get(section, section)
                
                if mapped_section in assignment.sections:
                    return True
        
        return False
    
    def _generate_for_class_group(self, class_group: str, subjects: List[Subject]) -> List[TimetableEntry]:
        """Generate timetable entries for a specific class group."""
        entries = []
        class_schedule = defaultdict(lambda: defaultdict(bool))
        
        # STEP 1: Schedule practical subjects first (3-block consecutive)
        practical_subjects = [subject for subject in subjects if subject.is_practical]
        for subject in practical_subjects:
            self._schedule_practical_subject(entries, class_schedule, subject, class_group)
        
        # STEP 2: Schedule theory subjects
        theory_subjects = [subject for subject in subjects if not subject.is_practical]
        for subject in theory_subjects:
            self._schedule_theory_subject(entries, class_schedule, subject, class_group)
        
        return entries
    
    def _schedule_practical_subject(self, entries: List[TimetableEntry], class_schedule: dict, 
                                  subject: Subject, class_group: str):
        """Schedule a practical subject with 3 consecutive blocks in same lab."""
        print(f"    🧪 Scheduling practical: {subject.code}")
        
        # Find available 3-block slots
        available_slots = self._find_available_3_block_slots(class_schedule, class_group)
        
        for day, start_period in available_slots:
            # Try to allocate lab for 3 consecutive periods
            lab = self.room_allocator.allocate_room_for_practical(
                day, start_period, class_group, subject, entries
            )
            
            if lab:
                # Find available teacher for all 3 periods
                teacher = self._find_available_teacher_for_duration(subject, day, start_period, 3, entries)
                
                if teacher:
                    # Create 3 consecutive entries
                    for i in range(3):
                        period = start_period + i
                        
                        # Mark as occupied
                        class_schedule[day][period] = True
                        self._mark_global_schedule(teacher, lab, day, period)
                        
                        # Create entry
                        entry = self._create_entry(day, period, subject, teacher, lab, class_group, True)
                        entries.append(entry)
                    
                    print(f"      ✅ Scheduled {subject.code} in {lab.name} on {day} P{start_period}-{start_period+2}")
                    return
        
        print(f"      ❌ Could not schedule practical {subject.code}")
    
    def _schedule_theory_subject(self, entries: List[TimetableEntry], class_schedule: dict, 
                               subject: Subject, class_group: str):
        """Schedule a theory subject."""
        print(f"    📚 Scheduling theory: {subject.code}")
        
        target_classes = subject.credits
        current_scheduled = 0
        
        # Try normal scheduling first
        current_scheduled = self._attempt_normal_theory_scheduling(
            entries, class_schedule, subject, class_group, target_classes, current_scheduled
        )
        
        # If still missing classes, try aggressive scheduling
        if current_scheduled < target_classes:
            current_scheduled = self._aggressive_theory_scheduling(
                entries, class_schedule, subject, class_group, target_classes, current_scheduled
            )
        
        print(f"      ✅ Scheduled {current_scheduled}/{target_classes} classes for {subject.code}")
    
    def _find_available_3_block_slots(self, class_schedule: dict, class_group: str) -> List[Tuple[str, int]]:
        """Find available 3-block consecutive slots."""
        available_slots = []
        
        for day in self.days:
            for start_period in range(1, len(self.periods) - 1):  # Need 3 consecutive periods
                # Check if all 3 periods are available
                if all(not class_schedule[day][start_period + i] for i in range(3)):
                    available_slots.append((day, start_period))
        
        # Sort by preference (earlier in week, earlier periods)
        available_slots.sort(key=lambda x: (self.days.index(x[0]), x[1]))
        return available_slots
    
    def _attempt_normal_theory_scheduling(self, entries: List[TimetableEntry], class_schedule: dict,
                                        subject: Subject, class_group: str, target: int, current_scheduled: int) -> int:
        """Attempt normal theory scheduling."""
        for day in self.days:
            for period in self.periods:
                if current_scheduled >= target:
                    break
                
                if not class_schedule[day][period]:
                    # Try to schedule here
                    can_schedule, teacher = self._can_schedule_theory_at_slot(entries, day, period, class_group, subject)
                    
                    if can_schedule:
                        room = self.room_allocator.allocate_room_for_theory(day, period, class_group, subject, entries)
                        
                        if room:
                            # Mark as occupied
                            class_schedule[day][period] = True
                            self._mark_global_schedule(teacher, room, day, period)
                            
                            # Create entry
                            entry = self._create_entry(day, period, subject, teacher, room, class_group, False)
                            entries.append(entry)
                            current_scheduled += 1
        
        return current_scheduled
    
    def _aggressive_theory_scheduling(self, entries: List[TimetableEntry], class_schedule: dict,
                                   subject: Subject, class_group: str, target: int, current_scheduled: int) -> int:
        """Aggressive theory scheduling when normal scheduling fails."""
        # Try to move other classes to make room
        for day in self.days:
            for period in self.periods:
                if current_scheduled >= target:
                    break
                
                if not class_schedule[day][period]:
                    # Try to force schedule here
                    if self._force_schedule_theory_at_slot(entries, day, period, class_group, subject):
                        can_schedule, teacher = self._can_schedule_theory_at_slot(entries, day, period, class_group, subject)
                        
                        if can_schedule:
                            room = self.room_allocator.allocate_room_for_theory(day, period, class_group, subject, entries)
                            
                            if room:
                                # Mark as occupied
                                class_schedule[day][period] = True
                                self._mark_global_schedule(teacher, room, day, period)
                                
                                # Create entry
                                entry = self._create_entry(day, period, subject, teacher, room, class_group, False)
                                entries.append(entry)
                                current_scheduled += 1
        
        return current_scheduled
    
    def _can_schedule_theory_at_slot(self, entries: List[TimetableEntry], day: str, period: int,
                                   class_group: str, subject: Subject) -> Tuple[bool, Optional[Teacher]]:
        """
        Check if theory can be scheduled at a specific slot.
        Returns (can_schedule, available_teacher) tuple.
        """
        # Check if slot is available for class group
        if any(entry.class_group == class_group and entry.day == day and entry.period == period 
               for entry in entries):
            return False, None
        
        # Check teacher availability and find available teacher
        teachers = self._get_teachers_for_subject(subject, class_group)
        available_teacher = None
        
        for teacher in teachers:
            if self._is_teacher_available(teacher, day, period, entries):
                available_teacher = teacher
                break
        
        if not available_teacher:
            return False, None
        
        # Check room availability
        available_rooms = self.room_allocator.get_available_rooms_for_time(day, period, 1, entries)
        if not available_rooms:
            return False, None
        
        return True, available_teacher
    
    def _force_schedule_theory_at_slot(self, entries: List[TimetableEntry], day: str, period: int,
                                     class_group: str, subject: Subject) -> bool:
        """Force schedule theory at a specific slot by moving conflicting classes."""
        # Find conflicting entries
        conflicting_entries = [entry for entry in entries 
                             if entry.class_group == class_group and entry.day == day and entry.period == period]
        
        # Try to move conflicting entries
        for entry in conflicting_entries:
            if self._can_move_entry_to_alternative_slot(entry, entries):
                # Move the entry
                new_slot = self._find_alternative_slot_for_entry(entry, entries)
                if new_slot:
                    entry.day, entry.period = new_slot
                    return True
        
        return False
    
    def _can_move_entry_to_alternative_slot(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> bool:
        """Check if an entry can be moved to an alternative slot."""
        for day in self.days:
            for period in self.periods:
                if day == entry.day and period == entry.period:
                    continue
                
                if self._is_slot_available_for_entry(entry, day, period, entries):
                    return True
        
        return False
    
    def _find_alternative_slot_for_entry(self, entry: TimetableEntry, entries: List[TimetableEntry]) -> Tuple[str, int]:
        """Find an alternative slot for an entry."""
        for day in self.days:
            for period in self.periods:
                if day == entry.day and period == entry.period:
                    continue
                
                if self._is_slot_available_for_entry(entry, day, period, entries):
                    return (day, period)
        
        return None
    
    def _is_slot_available_for_entry(self, entry: TimetableEntry, day: str, period: int,
                                   entries: List[TimetableEntry]) -> bool:
        """Check if a slot is available for a specific entry."""
        # Check class group availability
        if any(e.class_group == entry.class_group and e.day == day and e.period == period 
               for e in entries):
            return False
        
        # Check teacher availability
        if entry.teacher and not self._is_teacher_available(entry.teacher, day, period, entries):
            return False
        
        # Check room availability
        if entry.classroom:
            room_available = not any(
                e.classroom and e.classroom.id == entry.classroom.id and
                e.day == day and e.period == period
                for e in entries
            )
            if not room_available:
                return False
        
        return True
    
    def _find_available_teacher_for_duration(self, subject: Subject, day: str, start_period: int,
                                           duration: int, entries: List[TimetableEntry]) -> Teacher:
        """Find a teacher available for the entire duration."""
        teachers = self._get_teachers_for_subject(subject, "")
        
        for teacher in teachers:
            available = True
            for i in range(duration):
                period = start_period + i
                if not self._is_teacher_available(teacher, day, period, entries):
                    available = False
                    break
            
            if available:
                return teacher
        
        return None
    
    def _find_available_teacher_for_subject(self, subject: Subject, day: str, period: int,
                                          entries: List[TimetableEntry]) -> Teacher:
        """Find an available teacher for a subject at a specific time."""
        teachers = self._get_teachers_for_subject(subject, "")
        
        for teacher in teachers:
            if self._is_teacher_available(teacher, day, period, entries):
                return teacher
        
        return None
    
    def _get_teachers_for_subject(self, subject: Subject, class_group: str) -> List[Teacher]:
        """Get teachers assigned to a subject."""
        assignments = TeacherSubjectAssignment.objects.filter(subject=subject)
        teachers = []
        
        for assignment in assignments:
            if class_group:
                # Check if teacher is assigned to this specific class group
                batch_name = class_group.split('-')[0] if '-' in class_group else class_group
                if assignment.batch.name == batch_name:
                    section = class_group.split('-')[1] if '-' in class_group else None
                    if section is None:
                        teachers.append(assignment.teacher)
                    else:
                        # Map section letters to Roman numerals
                        section_mapping = {'A': 'I', 'B': 'II', 'C': 'III'}
                        mapped_section = section_mapping.get(section, section)
                        
                        if mapped_section in assignment.sections:
                            teachers.append(assignment.teacher)
            else:
                teachers.append(assignment.teacher)
        
        return teachers
    
    def _is_teacher_available(self, teacher: Teacher, day: str, period: int,
                             entries: List[TimetableEntry]) -> bool:
        """
        Check if a teacher is available at the specified day and period.
        Respects teacher unavailability constraints and existing schedule conflicts.
        """
        # First check for existing schedule conflicts
        if any(
            entry.teacher and entry.teacher.id == teacher.id and
            entry.day == day and entry.period == period
            for entry in entries
        ):
            return False
        
        # Then check teacher unavailability constraints
        if not teacher or not hasattr(teacher, 'unavailable_periods'):
            return True
        
        # Check if teacher has unavailability data
        if not isinstance(teacher.unavailable_periods, dict) or not teacher.unavailable_periods:
            return True
        
        # Check if this day is in teacher's unavailable periods
        if day in teacher.unavailable_periods:
            unavailable_periods = teacher.unavailable_periods[day]
            
            # If unavailable_periods is a list, check specific periods
            if isinstance(unavailable_periods, list):
                if period in unavailable_periods:
                    print(f"    🚫 Teacher {teacher.name} unavailable at {day} P{period}")
                    return False
            # If unavailable_periods is not a list, assume entire day is unavailable
            elif unavailable_periods:
                print(f"    🚫 Teacher {teacher.name} unavailable on entire day {day}")
                return False
        
        return True
    
    def _create_entry(self, day: str, period: int, subject: Subject, teacher: Teacher,
                     classroom: Classroom, class_group: str, is_practical: bool) -> TimetableEntry:
        """Create a new timetable entry."""
        # Calculate start and end times
        start_time = self.start_time
        class_duration = timedelta(minutes=self.class_duration)
        
        # Calculate actual start time for this period
        total_minutes = (period - 1) * (self.class_duration + 15)  # 15 min break
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
            schedule_config=self.config,
            semester=getattr(self.config, 'semester', 'Fall 2024'),
            academic_year=getattr(self.config, 'academic_year', '2024-2025')
        )
    
    def _mark_global_schedule(self, teacher: Teacher, classroom: Classroom, day: str, period: int):
        """Mark global schedule for conflict detection."""
        if teacher:
            if teacher.id not in self.global_teacher_schedule:
                self.global_teacher_schedule[teacher.id] = {}
            if day not in self.global_teacher_schedule[teacher.id]:
                self.global_teacher_schedule[teacher.id][day] = set()
            self.global_teacher_schedule[teacher.id][day].add(period)
        
        if classroom:
            if classroom.id not in self.global_classroom_schedule:
                self.global_classroom_schedule[classroom.id] = {}
            if day not in self.global_classroom_schedule[classroom.id]:
                self.global_classroom_schedule[classroom.id][day] = set()
            self.global_classroom_schedule[classroom.id][day].add(period)
    
    def _save_entries_to_database(self, entries: List[TimetableEntry]) -> int:
        """Save entries to database."""
        try:
            with transaction.atomic():
                saved_entries = []
                for entry in entries:
                    entry.save()
                    saved_entries.append(entry)
                
                print(f"💾 Saved {len(saved_entries)} entries to database")
                return len(saved_entries)
        except Exception as e:
            print(f"❌ Error saving entries to database: {str(e)}")
            return 0 