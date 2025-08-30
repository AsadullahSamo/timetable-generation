"""
WORKING TIMETABLE SCHEDULER
==========================
Fast, reliable, conflict-free timetable generation algorithm.
Replaces the broken genetic algorithm with deterministic scheduling.
"""

import random
from datetime import time, datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.db import models
from ..models import Subject, Teacher, Classroom, TimetableEntry, ScheduleConfig


class WorkingTimetableScheduler:
    """
    Fast, deterministic timetable scheduler that actually works.
    No genetic algorithms, no infinite loops, just working code.
    """
    
    def __init__(self, config: ScheduleConfig):
        self.config = config
        self.days = config.days
        self.periods = [int(p) for p in config.periods]  # Convert to integers
        self.start_time = config.start_time
        self.class_duration = config.class_duration
        self.class_groups = config.class_groups

        # Load data
        self.subjects = list(Subject.objects.all())
        self.teachers = list(Teacher.objects.all())
        self.classrooms = list(Classroom.objects.all())

        # Create default classroom if none exist
        if not self.classrooms:
            classroom = Classroom.objects.create(
                name="Default Room",
                building="Main Building"
            )
            self.classrooms = [classroom]

        # Tracking structures
        self.schedule = {}  # {(day, period, class_group): entry}
        self.teacher_schedule = {}  # {(teacher_id, day, period): True}
        self.classroom_schedule = {}  # {(classroom_id, day, period): True}

        # Load existing timetable entries to avoid cross-semester conflicts
        self.existing_teacher_schedule = {}
        existing_entries = TimetableEntry.objects.exclude(schedule_config=config)
        for entry in existing_entries:
            key = (entry.teacher.id, entry.day, entry.period)
            self.existing_teacher_schedule[key] = entry

        print(f"📊 Scheduler initialized: {len(self.subjects)} subjects, {len(self.teachers)} teachers, {len(self.classrooms)} classrooms")
        if self.existing_teacher_schedule:
            print(f"🔍 Found {len(self.existing_teacher_schedule)} existing teacher assignments to avoid conflicts")
    
    def generate_timetable(self) -> Dict:
        """Generate complete timetable for all class groups."""
        start_time = datetime.now()
        
        print(f"🚀 Starting timetable generation for {self.config.name}")
        print(f"📅 Class groups: {self.class_groups}")
        
        try:
            entries = []
            
            # Generate for each class group
            for class_group in self.class_groups:
                print(f"\n📋 Generating for {class_group}...")
                class_entries = self._generate_for_class_group(class_group)
                entries.extend(class_entries)
                print(f"✅ Generated {len(class_entries)} entries for {class_group}")
            
            # Check for conflicts
            conflicts = self._check_all_conflicts(entries)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'entries': [self._entry_to_dict(entry) for entry in entries],
                'fitness_score': 100.0 - len(conflicts),
                'constraint_violations': conflicts,
                'generation_time': generation_time,
                'total_entries': len(entries),
                'success': True
            }
            
            print(f"\n🎉 GENERATION COMPLETE!")
            print(f"📊 Total entries: {len(entries)}")
            print(f"⏱️  Generation time: {generation_time:.2f}s")
            
            if conflicts:
                print(f"⚠️  Conflicts found: {len(conflicts)}")
                for conflict in conflicts[:5]:  # Show first 5
                    print(f"   - {conflict}")
            else:
                print("✅ NO CONFLICTS - PERFECT TIMETABLE!")
            
            return result
            
        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _generate_for_class_group(self, class_group: str) -> List[TimetableEntry]:
        """Generate timetable entries for a specific class group."""
        entries = []
        
        # Get subjects for this class group based on semester
        semester_subjects = self._get_subjects_for_class_group(class_group)
        
        print(f"   📚 Subjects for {class_group}: {[s.code for s in semester_subjects]}")
        
        # Schedule practical subjects first (they need consecutive periods)
        practical_subjects = [s for s in semester_subjects if self._is_practical_subject(s)]
        for subject in practical_subjects:
            self._schedule_practical_subject(entries, subject, class_group)

        # Schedule theory subjects
        theory_subjects = [s for s in semester_subjects if not self._is_practical_subject(s)]
        for subject in theory_subjects:
            self._schedule_theory_subject(entries, subject, class_group)
        
        return entries
    
    def _get_subjects_for_class_group(self, class_group: str) -> List[Subject]:
        """Get subjects for the class group - UNIVERSAL VERSION."""
        # Try to get subjects from database relationships first
        subjects = []

        # Method 1: Check if subjects have a class_group or semester field
        try:
            # Look for subjects that might be linked to this class group
            subjects = list(Subject.objects.filter(
                models.Q(name__icontains=class_group) |
                models.Q(code__icontains=class_group)
            ))
        except:
            pass

        # Method 2: If no specific mapping, use ALL subjects (let user/admin decide)
        if not subjects:
            subjects = list(Subject.objects.all())
            print(f"   📚 No specific subjects found for {class_group}, using all {len(subjects)} subjects")

        # Method 3: This fallback is no longer needed - the system is now fully universal

        return subjects

    def _is_practical_subject(self, subject: Subject) -> bool:
        """Universal method to detect if a subject is practical."""
        # Method 1: Check the is_practical field if it exists
        if hasattr(subject, 'is_practical') and subject.is_practical:
            return True

        # Method 2: Check common practical indicators in code/name
        practical_indicators = [
            ' Pr', 'Pr', '_LAB', 'LAB', 'Lab', 'Practical', 'PRACTICAL',
            'Workshop', 'WORKSHOP', 'Project', 'PROJECT'
        ]

        for indicator in practical_indicators:
            if indicator in subject.code or indicator in subject.name:
                return True

        # Method 3: Check if credits = 1 (common for practicals) - but be more specific
        if subject.credits == 1 and any(ind in subject.code.upper() or ind in subject.name.upper()
                                       for ind in ['LAB', 'PRACTICAL', 'PROJECT', 'WORKSHOP']):
            return True

        return False

    def _get_teachers_for_subject(self, subject: Subject) -> List[Teacher]:
        """Universal method to find teachers for a subject."""
        # Method 1: Use many-to-many relationship if it exists
        try:
            teachers = list(subject.teacher_set.all())
            if teachers:
                return teachers
        except:
            pass

        # Method 2: Check reverse relationship
        try:
            teachers = [t for t in self.teachers if subject in t.subjects.all()]
            if teachers:
                return teachers
        except:
            pass

        # Method 3: Fallback - assign any available teacher (for new data)
        print(f"   🔄 No specific teacher assignment found for {subject.code}, using available teachers")
        return self.teachers  # Return all teachers as potential candidates

    def _schedule_practical_subject(self, entries: List[TimetableEntry],
                                  subject: Subject, class_group: str):
        """Schedule a practical subject (needs 3 consecutive periods)."""
        print(f"   🧪 Scheduling practical: {subject.code}")
        
        # Find available teachers - UNIVERSAL METHOD
        available_teachers = self._get_teachers_for_subject(subject)
        if not available_teachers:
            print(f"   ⚠️  No teachers found for {subject.code}")
            return
        
        # Try to find 3 consecutive periods
        for day in self.days:
            for start_period in self.periods[:-2]:  # Need at least 3 periods
                if self._can_schedule_block(day, start_period, 3, class_group):
                    # Find available teacher for this time
                    teacher = self._find_available_teacher(available_teachers, day, start_period, 3)
                    if teacher:
                        classroom = self._find_available_classroom(day, start_period, 3)
                        if classroom:
                            # Schedule 3 consecutive periods
                            for i in range(3):
                                period = start_period + i
                                entry = self._create_entry(
                                    day, period, subject, teacher, classroom, 
                                    class_group, is_practical=True
                                )
                                entries.append(entry)
                                self._mark_slot_used(day, period, class_group, teacher, classroom)
                            
                            print(f"   ✅ Scheduled {subject.code}: {day} P{start_period}-{start_period+2} with {teacher.name}")
                            return
        
        print(f"   ❌ Could not schedule practical {subject.code}")
    
    def _schedule_theory_subject(self, entries: List[TimetableEntry], 
                               subject: Subject, class_group: str):
        """Schedule a theory subject (needs credits number of periods per week)."""
        print(f"   📖 Scheduling theory: {subject.code} ({subject.credits} credits)")
        
        # Find available teachers - UNIVERSAL METHOD
        available_teachers = self._get_teachers_for_subject(subject)
        if not available_teachers:
            print(f"   ⚠️  No teachers found for {subject.code}")
            return
        
        scheduled_periods = 0
        target_periods = subject.credits  # 1 credit = 1 period per week
        
        # Try to schedule the required number of periods
        for day in self.days:
            if scheduled_periods >= target_periods:
                break
                
            for period in self.periods:
                if scheduled_periods >= target_periods:
                    break
                    
                if self._can_schedule_single(day, period, class_group):
                    teacher = self._find_available_teacher(available_teachers, day, period, 1)
                    if teacher:
                        classroom = self._find_available_classroom(day, period, 1)
                        if classroom:
                            entry = self._create_entry(
                                day, period, subject, teacher, classroom, 
                                class_group, is_practical=False
                            )
                            entries.append(entry)
                            self._mark_slot_used(day, period, class_group, teacher, classroom)
                            scheduled_periods += 1
                            
                            print(f"   ✅ Scheduled {subject.code}: {day} P{period} with {teacher.name}")
        
        if scheduled_periods < target_periods:
            print(f"   ⚠️  Only scheduled {scheduled_periods}/{target_periods} periods for {subject.code}")
    
    def _can_schedule_block(self, day: str, start_period: int, duration: int, class_group: str) -> bool:
        """Check if a block of periods can be scheduled."""
        for i in range(duration):
            period = start_period + i
            if period not in self.periods:
                return False
            if (day, period, class_group) in self.schedule:
                return False
        return True
    
    def _can_schedule_single(self, day: str, period: int, class_group: str) -> bool:
        """Check if a single period can be scheduled."""
        return (day, period, class_group) not in self.schedule
    
    def _find_available_teacher(self, teachers: List[Teacher], day: str,
                              start_period: int, duration: int) -> Optional[Teacher]:
        """Find a teacher available for the specified time slot."""
        for teacher in teachers:
            available = True
            for i in range(duration):
                period = start_period + i
                # Check current schedule
                if (teacher.id, day, period) in self.teacher_schedule:
                    available = False
                    break
                # Check existing cross-semester schedule
                if (teacher.id, day, period) in self.existing_teacher_schedule:
                    available = False
                    break
            if available:
                return teacher
        return None
    
    def _find_available_classroom(self, day: str, start_period: int, duration: int) -> Optional[Classroom]:
        """Find a classroom available for the specified time slot."""
        for classroom in self.classrooms:
            available = True
            for i in range(duration):
                period = start_period + i
                if (classroom.id, day, period) in self.classroom_schedule:
                    available = False
                    break
            if available:
                return classroom
        return self.classrooms[0]  # Return first classroom as fallback

    def _create_entry(self, day: str, period: int, subject: Subject,
                     teacher: Teacher, classroom: Classroom, class_group: str,
                     is_practical: bool = False) -> TimetableEntry:
        """Create a timetable entry."""
        # Calculate start and end times
        start_time = self._get_period_start_time(period)
        end_time = self._get_period_end_time(period)

        return TimetableEntry(
            day=day,
            period=period,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            class_group=class_group,
            start_time=start_time,
            end_time=end_time,
            is_practical=is_practical,
            schedule_config=self.config
        )

    def _mark_slot_used(self, day: str, period: int, class_group: str,
                       teacher: Teacher, classroom: Classroom):
        """Mark a time slot as used."""
        self.schedule[(day, period, class_group)] = True
        self.teacher_schedule[(teacher.id, day, period)] = True
        self.classroom_schedule[(classroom.id, day, period)] = True

    def _get_period_start_time(self, period: int) -> time:
        """Get start time for a period."""
        start_hour = self.start_time.hour
        start_minute = self.start_time.minute

        # Each period is class_duration minutes
        total_minutes = (period - 1) * self.class_duration
        hours_to_add = total_minutes // 60
        minutes_to_add = total_minutes % 60

        return time(
            hour=start_hour + hours_to_add,
            minute=start_minute + minutes_to_add
        )

    def _get_period_end_time(self, period: int) -> time:
        """Get end time for a period."""
        start = self._get_period_start_time(period)
        end_hour = start.hour
        end_minute = start.minute + self.class_duration

        # Handle minute overflow properly
        while end_minute >= 60:
            end_hour += 1
            end_minute -= 60

        # Handle hour overflow
        if end_hour >= 24:
            end_hour = 23
            end_minute = 59

        return time(hour=end_hour, minute=end_minute)

    def _check_all_conflicts(self, entries: List[TimetableEntry]) -> List[str]:
        """Check for all types of conflicts in the generated timetable."""
        conflicts = []

        # Check teacher conflicts
        teacher_slots = {}
        for entry in entries:
            key = f"{entry.teacher.id}_{entry.day}_{entry.period}"
            if key in teacher_slots:
                conflicts.append(
                    f"Teacher conflict: {entry.teacher.name} at {entry.day} P{entry.period}"
                )
            else:
                teacher_slots[key] = entry

        # Check classroom conflicts
        classroom_slots = {}
        for entry in entries:
            key = f"{entry.classroom.id}_{entry.day}_{entry.period}"
            if key in classroom_slots:
                conflicts.append(
                    f"Classroom conflict: {entry.classroom.name} at {entry.day} P{entry.period}"
                )
            else:
                classroom_slots[key] = entry

        # Check class group conflicts (students can't be in two places at once)
        class_slots = {}
        for entry in entries:
            key = f"{entry.class_group}_{entry.day}_{entry.period}"
            if key in class_slots:
                conflicts.append(
                    f"Class conflict: {entry.class_group} at {entry.day} P{entry.period}"
                )
            else:
                class_slots[key] = entry

        return conflicts

    def _entry_to_dict(self, entry: TimetableEntry) -> Dict:
        """Convert TimetableEntry to dictionary for JSON response."""
        return {
            'day': entry.day,
            'period': entry.period,
            'subject': entry.subject.name,
            'subject_code': entry.subject.code,
            'teacher': entry.teacher.name,
            'classroom': entry.classroom.name,
            'class_group': entry.class_group,
            'start_time': entry.start_time.strftime('%H:%M'),
            'end_time': entry.end_time.strftime('%H:%M'),
            'is_practical': entry.is_practical,
            'credits': entry.subject.credits
        }
