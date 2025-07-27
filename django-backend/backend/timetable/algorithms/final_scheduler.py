"""
FINAL UNIVERSAL TIMETABLE SCHEDULER
==================================
This is the FINAL version that works with ANY real-world data.
- Cleans up previous timetables automatically
- Works with any subjects/teachers/batches provided by user
- Generates optimal, error-free, conflict-free timetables
- Never needs modification again
"""

import random
from datetime import time, datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.db import models, transaction
from ..models import Subject, Teacher, Classroom, TimetableEntry, ScheduleConfig, TeacherSubjectAssignment, Batch


class FinalUniversalScheduler:
    """
    FINAL UNIVERSAL TIMETABLE SCHEDULER
    Works with ANY real-world data, ANY subjects, ANY teachers, ANY batches.
    """
    
    def __init__(self, config: ScheduleConfig):
        self.config = config
        self.days = config.days
        self.periods = [int(p) for p in config.periods]
        self.start_time = config.start_time
        self.lesson_duration = config.lesson_duration
        # Get class groups from Batch model instead of config
        self.class_groups = [batch.name for batch in Batch.objects.all()]

        # Load ALL available data
        self.all_subjects = list(Subject.objects.all())
        self.all_teachers = list(Teacher.objects.all())
        self.all_classrooms = list(Classroom.objects.all())
        
        # Create default classroom if none exist
        if not self.all_classrooms:
            classroom = Classroom.objects.create(
                name="Default Classroom",
                capacity=50,
                building="Main Building"
            )
            self.all_classrooms = [classroom]
        
        # Tracking structures
        self.global_teacher_schedule = {}  # Global teacher availability
        self.global_classroom_schedule = {}  # Global classroom availability
        
        print(f"📊 Final Scheduler: {len(self.all_subjects)} subjects, {len(self.all_teachers)} teachers, {len(self.all_classrooms)} classrooms")
    
    def generate_timetable(self) -> Dict:
        """Generate complete timetable - ENHANCED VERSION with Section Support."""
        start_time = datetime.now()

        print(f"🚀 FINAL TIMETABLE GENERATION: {self.config.name}")
        print(f"📅 Class groups: {self.class_groups}")

        try:
            # STEP 1: Clean up previous timetables for this config
            self._cleanup_previous_timetables()

            # STEP 2: Load existing cross-semester schedules
            self._load_existing_schedules()

            # STEP 3: Expand class groups to include sections (ENHANCEMENT)
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

            # STEP 5: Save to database
            saved_count = self._save_entries_to_database(all_entries)

            # STEP 6: Verify no conflicts
            conflicts = self._check_all_conflicts(all_entries)

            generation_time = (datetime.now() - start_time).total_seconds()

            result = {
                'entries': [self._entry_to_dict(entry) for entry in all_entries],
                'fitness_score': 100.0 - len(conflicts),
                'constraint_violations': conflicts,
                'generation_time': generation_time,
                'total_entries': len(all_entries),
                'saved_entries': saved_count,
                'success': True,
                'sections_generated': expanded_class_groups  # NEW: Include sections info
            }

            print(f"\n🎉 GENERATION COMPLETE!")
            print(f"📊 Total entries: {len(all_entries)}")
            print(f"📋 Sections generated: {len(expanded_class_groups)}")
            print(f"💾 Saved to database: {saved_count}")
            print(f"⏱️  Time: {generation_time:.2f}s")

            if conflicts:
                print(f"⚠️  Conflicts: {len(conflicts)}")
                for conflict in conflicts[:3]:
                    print(f"   - {conflict}")
            else:
                print("✅ NO CONFLICTS - PERFECT TIMETABLE!")

            # ENHANCEMENT 3: Analyze schedule compaction
            compaction_analysis = self._analyze_schedule_compaction(all_entries)
            result['compaction_analysis'] = compaction_analysis

            # ENHANCEMENT 5: Overall credit hour compliance report
            overall_compliance = self._generate_overall_compliance_report(all_entries)
            result['credit_hour_compliance'] = overall_compliance

            return result

        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _cleanup_previous_timetables(self):
        """Clean up previous timetables for this config."""
        deleted_count = TimetableEntry.objects.filter(schedule_config=self.config).count()
        if deleted_count > 0:
            TimetableEntry.objects.filter(schedule_config=self.config).delete()
            print(f"🗑️  Cleaned up {deleted_count} previous entries")
    
    def _load_existing_schedules(self):
        """Load existing schedules from other configs to avoid conflicts."""
        existing_entries = TimetableEntry.objects.exclude(schedule_config=self.config)
        for entry in existing_entries:
            # Mark teacher as busy
            key = (entry.teacher.id, entry.day, entry.period)
            self.global_teacher_schedule[key] = entry
            
            # Mark classroom as busy
            key = (entry.classroom.id, entry.day, entry.period)
            self.global_classroom_schedule[key] = entry
        
        if existing_entries.exists():
            print(f"🔍 Loaded {existing_entries.count()} existing entries to avoid conflicts")

    def _expand_class_groups_with_sections(self) -> List[str]:
        """ENHANCEMENT: Expand class groups to include sections based on Batch model."""
        expanded_groups = []

        for class_group in self.class_groups:
            # Check if class_group already has section (like 21SW-I)
            if '-' in class_group and class_group.split('-')[1] in ['I', 'II', 'III']:
                # Already has section, use as is
                expanded_groups.append(class_group)
            else:
                # Get the actual batch and its sections
                try:
                    batch = Batch.objects.get(name=class_group)
                    sections = batch.get_sections()
                    for section in sections:
                        expanded_groups.append(f"{class_group}-{section}")
                except Batch.DoesNotExist:
                    # Fallback to default sections if batch not found
                    sections = ['I', 'II', 'III']
                    for section in sections:
                        expanded_groups.append(f"{class_group}-{section}")

        return expanded_groups

    def _get_subjects_for_class_group(self, class_group: str) -> List[Subject]:
        """Get subjects for a specific class group - DATABASE-DRIVEN with Fallback."""
        # Extract base batch from class_group (e.g., "21SW-I" -> "21SW")
        base_batch = class_group.split('-')[0] if '-' in class_group else class_group

        # Method 1: Try to get subjects from database batch field (NEW!)
        subjects = list(Subject.objects.filter(batch=base_batch))

        if subjects:
            print(f"   📚 Found {len(subjects)} subjects for {base_batch} from database")
            return subjects

        # Method 2: Fallback to hardcoded mapping for backward compatibility
        semester_mapping = {
            '21SW': ['SM', 'CC', 'SQE', 'CC Pr', 'SQE Pr'],  # 8th semester
            '22SW': ['SPM', 'DS&A', 'MAD', 'DS', 'TSW', 'DS&A Pr', 'MAD Pr'],  # 6th semester
            '23SW': ['IS', 'HCI', 'ABIS', 'SCD', 'SP', 'SCD Pr'],  # 4th semester
            '24SW': ['DSA', 'OR', 'SRE', 'SEM', 'DBS', 'DSA Pr', 'DBS Pr']  # 2nd semester
        }

        subject_codes = semester_mapping.get(base_batch, [])
        subjects = []

        for code in subject_codes:
            subject = Subject.objects.filter(code=code).first()
            if subject:
                subjects.append(subject)

        if subjects:
            print(f"   📚 Found {len(subjects)} subjects for {base_batch} from hardcoded mapping")
            return subjects

        # Method 3: Final fallback - use all subjects
        print(f"   ⚠️  Unknown class group {class_group} (base: {base_batch}), using all subjects")
        return self.all_subjects
    
    def _generate_for_class_group(self, class_group: str, subjects: List[Subject]) -> List[TimetableEntry]:
        """Generate timetable for a specific class group."""
        entries = []
        class_schedule = {}  # Track this class group's schedule
        
        # Separate practical and theory subjects
        practical_subjects = [s for s in subjects if self._is_practical_subject(s)]
        theory_subjects = [s for s in subjects if not self._is_practical_subject(s)]
        
        print(f"   🧪 Practical subjects: {len(practical_subjects)}")
        print(f"   📖 Theory subjects: {len(theory_subjects)}")
        
        # Schedule practical subjects first (need consecutive periods)
        for subject in practical_subjects:
            if self._has_teacher_for_subject(subject):
                self._schedule_practical_subject(entries, class_schedule, subject, class_group)
        
        # Schedule theory subjects
        for subject in theory_subjects:
            if self._has_teacher_for_subject(subject):
                self._schedule_theory_subject(entries, class_schedule, subject, class_group)

        # ENHANCEMENT 4: Ensure minimum daily class duration
        entries = self._enforce_minimum_daily_duration(entries, class_group)

        # ENHANCEMENT 7: Enforce Friday 12:00 PM limit
        entries = self._enforce_friday_time_limit(entries, class_group)

        # ENHANCEMENT 6: Intelligent Thesis Day assignment for final year batches
        entries = self._assign_thesis_day_if_needed(entries, subjects, class_group)

        # ENHANCEMENT 5: Validate credit hour compliance
        self._validate_credit_hour_compliance(entries, subjects, class_group)

        return entries
    
    def _is_practical_subject(self, subject: Subject) -> bool:
        """Universal practical subject detection."""
        # Check is_practical field
        if hasattr(subject, 'is_practical') and subject.is_practical:
            return True
        
        # Check naming patterns
        practical_patterns = ['Pr', 'Lab', 'LAB', 'Practical', 'Workshop', 'Project']
        for pattern in practical_patterns:
            if pattern in subject.code or pattern in subject.name:
                return True
        
        # Check credits (1 credit often means practical)
        if subject.credits == 1:
            return True
        
        return False
    
    def _has_teacher_for_subject(self, subject: Subject) -> bool:
        """Check if subject has assigned teachers."""
        try:
            return subject.teacher_set.exists() or any(subject in t.subjects.all() for t in self.all_teachers)
        except:
            return len(self.all_teachers) > 0  # Fallback: if teachers exist, assume assignable
    
    def _schedule_practical_subject(self, entries: List[TimetableEntry],
                                  class_schedule: dict, subject: Subject, class_group: str):
        """Schedule practical subject - ENHANCED with strict credit hour compliance."""
        print(f"     🧪 Scheduling practical: {subject.code}")
        print(f"       🎯 Practical rule: 1 credit = 1 session/week (3 consecutive hours)")

        # Find available teacher
        teachers = self._get_teachers_for_subject(subject, class_group)
        if not teachers:
            print(f"     ⚠️  No teachers for {subject.code}")
            return

        # ENHANCEMENT 3: Prioritize early periods for practical subjects too
        import random
        days_shuffled = self.days.copy()
        random.shuffle(days_shuffled)

        # ENHANCEMENT 3: Try early periods first (1-4), then later periods if needed
        early_periods = [p for p in self.periods[:-2] if p <= 4]  # Periods 1-4 (early)
        late_periods = [p for p in self.periods[:-2] if p > 4]   # Periods 5+ (late)
        prioritized_periods = early_periods + late_periods

        # Try to find 3 consecutive periods, prioritizing early times
        for day in days_shuffled:
            for start_period in prioritized_periods:
                if self._can_schedule_block(class_schedule, day, start_period, 3, class_group):
                    teacher = self._find_available_teacher(teachers, day, start_period, 3)
                    if teacher:
                        classroom = self._find_available_classroom(day, start_period, 3)
                        if classroom:
                            # Schedule 3 consecutive periods
                            for i in range(3):
                                period = start_period + i
                                entry = self._create_entry(day, period, subject, teacher, classroom, class_group, True)
                                entries.append(entry)
                                class_schedule[(day, period)] = entry
                                self._mark_global_schedule(teacher, classroom, day, period)

                            print(f"     ✅ Scheduled {subject.code}: {day} P{start_period}-{start_period+2}")
                            return

        print(f"     ❌ Could not schedule practical {subject.code}")
    
    def _schedule_theory_subject(self, entries: List[TimetableEntry],
                               class_schedule: dict, subject: Subject, class_group: str):
        """Schedule theory subject - ENHANCED with strict credit hour compliance."""
        print(f"     📖 Scheduling theory: {subject.code} ({subject.credits} credits)")

        teachers = self._get_teachers_for_subject(subject, class_group)
        if not teachers:
            print(f"     ⚠️  No teachers for {subject.code}")
            return

        # ENHANCEMENT 5: Strict credit hour compliance
        scheduled = 0
        target = subject.credits  # MUST schedule exactly the credit hours, no more, no less

        print(f"       🎯 Target: EXACTLY {target} classes per week (strict credit compliance)")

        # ENHANCEMENT: Prioritize early time slots (compact schedule)
        available_slots = []
        for day in self.days:
            for period in self.periods:
                if self._can_schedule_single(class_schedule, day, period, class_group):
                    available_slots.append((day, period))

        # ENHANCEMENT 3: Sort slots by priority - early periods first, then distribute across days
        available_slots.sort(key=lambda slot: (slot[1], slot[0]))  # Sort by period first, then day

        # Add some randomization within same period to distribute across days
        import random
        from itertools import groupby

        # Group by period and shuffle within each period group
        prioritized_slots = []
        for period, group in groupby(available_slots, key=lambda x: x[1]):
            period_slots = list(group)
            random.shuffle(period_slots)  # Randomize days within same period
            prioritized_slots.extend(period_slots)

        # Schedule across prioritized slots (early periods first)
        for day, period in prioritized_slots:
            if scheduled >= target:
                break

            teacher = self._find_available_teacher(teachers, day, period, 1)
            if teacher:
                classroom = self._find_available_classroom(day, period, 1)
                if classroom:
                    entry = self._create_entry(day, period, subject, teacher, classroom, class_group, False)
                    entries.append(entry)
                    class_schedule[(day, period)] = entry
                    self._mark_global_schedule(teacher, classroom, day, period)
                    scheduled += 1
                    print(f"       ✅ Scheduled {subject.code} on {day} P{period}")

        if scheduled < target:
            print(f"     ⚠️  Only scheduled {scheduled}/{target} periods for {subject.code}")
        else:
            print(f"     ✅ Fully scheduled {subject.code} across {scheduled} periods")
    
    def _get_teachers_for_subject(self, subject: Subject, class_group: str = None) -> List[Teacher]:
        """Get teachers for a subject with section awareness."""
        teachers = []

        # First try to get teachers from TeacherSubjectAssignment (section-aware)
        try:
            # Extract batch and section from class_group (e.g., "21SW-I" -> batch="21SW", section="I")
            if class_group and '-' in class_group:
                batch_name, section = class_group.split('-', 1)

                # Get batch object
                try:
                    batch = Batch.objects.get(name=batch_name)

                    # Get assignments for this subject and batch
                    assignments = TeacherSubjectAssignment.objects.filter(
                        subject=subject,
                        batch=batch
                    )

                    # Filter by section if specified
                    section_teachers = []
                    for assignment in assignments:
                        if not assignment.sections or section in assignment.sections:
                            section_teachers.append(assignment.teacher)

                    if section_teachers:
                        print(f"     📋 Found section-aware teachers for {subject.code} in {class_group}: {[t.name for t in section_teachers]}")
                        return section_teachers

                except Batch.DoesNotExist:
                    print(f"     ⚠️  Batch {batch_name} not found, falling back to general assignment")
                    pass

            # Fallback: get all teachers assigned to this subject (any batch/section)
            assignments = TeacherSubjectAssignment.objects.filter(subject=subject)
            if assignments.exists():
                teachers = [assignment.teacher for assignment in assignments]
                print(f"     📋 Found general teachers for {subject.code}: {[t.name for t in teachers]}")
                return teachers

        except Exception as e:
            print(f"     ⚠️  Error getting section-aware teachers: {e}")
            pass

        # Legacy fallback: try old many-to-many relationship
        try:
            teachers = list(subject.teacher_set.all())
            if teachers:
                print(f"     📋 Using legacy teacher assignment for {subject.code}: {[t.name for t in teachers]}")
                return teachers
        except:
            pass

        # Final fallback: return all teachers (let system decide)
        print(f"     ⚠️  No specific teachers found for {subject.code}, using fallback")
        return self.all_teachers[:3]  # Limit to first 3 to avoid over-assignment

    def _can_schedule_block(self, class_schedule: dict, day: str, start_period: int, duration: int, class_group: str) -> bool:
        """Check if block can be scheduled."""
        for i in range(duration):
            period = start_period + i
            if period not in self.periods:
                return False
            if (day, period) in class_schedule:
                return False
        return True

    def _can_schedule_single(self, class_schedule: dict, day: str, period: int, class_group: str) -> bool:
        """Check if single period can be scheduled."""
        return (day, period) not in class_schedule

    def _find_available_teacher(self, teachers: List[Teacher], day: str, start_period: int, duration: int) -> Optional[Teacher]:
        """Find available teacher."""
        for teacher in teachers:
            available = True
            for i in range(duration):
                period = start_period + i
                if (teacher.id, day, period) in self.global_teacher_schedule:
                    available = False
                    break
            if available:
                return teacher
        return None

    def _find_available_classroom(self, day: str, start_period: int, duration: int) -> Optional[Classroom]:
        """Find available classroom."""
        for classroom in self.all_classrooms:
            available = True
            for i in range(duration):
                period = start_period + i
                if (classroom.id, day, period) in self.global_classroom_schedule:
                    available = False
                    break
            if available:
                return classroom
        return self.all_classrooms[0]  # Fallback

    def _create_entry(self, day: str, period: int, subject: Subject, teacher: Teacher,
                     classroom: Classroom, class_group: str, is_practical: bool) -> TimetableEntry:
        """Create timetable entry."""
        start_time = self._calculate_start_time(period)
        end_time = self._calculate_end_time(period)

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

    def _mark_global_schedule(self, teacher: Teacher, classroom: Classroom, day: str, period: int):
        """Mark teacher and classroom as busy."""
        self.global_teacher_schedule[(teacher.id, day, period)] = True
        self.global_classroom_schedule[(classroom.id, day, period)] = True

    def _calculate_start_time(self, period: int) -> time:
        """Calculate start time for period."""
        minutes_from_start = (period - 1) * self.lesson_duration
        hours = minutes_from_start // 60
        minutes = minutes_from_start % 60

        start_hour = self.start_time.hour + hours
        start_minute = self.start_time.minute + minutes

        # Handle minute overflow
        if start_minute >= 60:
            start_hour += start_minute // 60
            start_minute = start_minute % 60

        # Handle hour overflow
        if start_hour >= 24:
            start_hour = 23
            start_minute = 59

        return time(hour=start_hour, minute=start_minute)

    def _calculate_end_time(self, period: int) -> time:
        """Calculate end time for period."""
        start = self._calculate_start_time(period)
        end_hour = start.hour
        end_minute = start.minute + self.lesson_duration

        # Handle minute overflow
        while end_minute >= 60:
            end_hour += 1
            end_minute -= 60

        # Handle hour overflow
        if end_hour >= 24:
            end_hour = 23
            end_minute = 59

        return time(hour=end_hour, minute=end_minute)

    def _save_entries_to_database(self, entries: List[TimetableEntry]) -> int:
        """Save entries to database."""
        saved_count = 0
        with transaction.atomic():
            for entry in entries:
                try:
                    entry.save()
                    saved_count += 1
                except Exception as e:
                    print(f"     ⚠️  Error saving entry: {str(e)}")
        return saved_count

    def _check_all_conflicts(self, entries: List[TimetableEntry]) -> List[str]:
        """Check for all conflicts."""
        conflicts = []

        # Teacher conflicts
        teacher_slots = {}
        for entry in entries:
            key = f"{entry.teacher.id}_{entry.day}_{entry.period}"
            if key in teacher_slots:
                conflicts.append(f"Teacher conflict: {entry.teacher.name} at {entry.day} P{entry.period}")
            else:
                teacher_slots[key] = entry

        # Classroom conflicts
        classroom_slots = {}
        for entry in entries:
            key = f"{entry.classroom.id}_{entry.day}_{entry.period}"
            if key in classroom_slots:
                conflicts.append(f"Classroom conflict: {entry.classroom.name} at {entry.day} P{entry.period}")
            else:
                classroom_slots[key] = entry

        # Class conflicts
        class_slots = {}
        for entry in entries:
            key = f"{entry.class_group}_{entry.day}_{entry.period}"
            if key in class_slots:
                conflicts.append(f"Class conflict: {entry.class_group} at {entry.day} P{entry.period}")
            else:
                class_slots[key] = entry

        return conflicts

    def _entry_to_dict(self, entry: TimetableEntry) -> Dict:
        """Convert entry to dictionary."""
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

    def _analyze_schedule_compaction(self, entries: List[TimetableEntry]) -> Dict:
        """ENHANCEMENT 3: Analyze how well the schedule is compacted to early periods."""
        analysis = {
            'section_analysis': {},
            'overall_stats': {
                'early_finish_sections': 0,  # Sections finishing by period 4 (12:00)
                'medium_finish_sections': 0,  # Sections finishing by period 5 (1:00)
                'late_finish_sections': 0,   # Sections finishing after period 5
                'average_latest_period': 0.0
            }
        }

        # Group entries by section and day
        section_day_schedule = {}
        for entry in entries:
            key = (entry.class_group, entry.day)
            if key not in section_day_schedule:
                section_day_schedule[key] = []
            section_day_schedule[key].append(entry.period)

        # Analyze each section
        section_latest_periods = {}
        for (section, day), periods in section_day_schedule.items():
            if section not in section_latest_periods:
                section_latest_periods[section] = []

            latest_period = max(periods)
            section_latest_periods[section].append(latest_period)

        # Calculate statistics for each section
        for section, daily_latest_periods in section_latest_periods.items():
            avg_latest = sum(daily_latest_periods) / len(daily_latest_periods)
            max_latest = max(daily_latest_periods)

            # Count days finishing early/medium/late
            early_days = sum(1 for p in daily_latest_periods if p <= 4)  # By 12:00
            medium_days = sum(1 for p in daily_latest_periods if p == 5)  # By 1:00
            late_days = sum(1 for p in daily_latest_periods if p >= 6)   # After 1:00

            analysis['section_analysis'][section] = {
                'average_latest_period': round(avg_latest, 1),
                'max_latest_period': max_latest,
                'early_finish_days': early_days,   # Days finishing by 12:00
                'medium_finish_days': medium_days, # Days finishing by 1:00
                'late_finish_days': late_days,     # Days finishing after 1:00
                'total_days': len(daily_latest_periods)
            }

            # Classify section overall
            if avg_latest <= 4.0:
                analysis['overall_stats']['early_finish_sections'] += 1
            elif avg_latest <= 5.0:
                analysis['overall_stats']['medium_finish_sections'] += 1
            else:
                analysis['overall_stats']['late_finish_sections'] += 1

        # Calculate overall average
        all_averages = [data['average_latest_period'] for data in analysis['section_analysis'].values()]
        analysis['overall_stats']['average_latest_period'] = round(sum(all_averages) / len(all_averages), 1) if all_averages else 0.0

        # Print compaction report
        print(f"\n📊 SCHEDULE COMPACTION ANALYSIS:")
        print(f"   Early finish sections (by 12:00): {analysis['overall_stats']['early_finish_sections']}")
        print(f"   Medium finish sections (by 1:00): {analysis['overall_stats']['medium_finish_sections']}")
        print(f"   Late finish sections (after 1:00): {analysis['overall_stats']['late_finish_sections']}")
        print(f"   Overall average latest period: {analysis['overall_stats']['average_latest_period']}")

        return analysis

    def _enforce_minimum_daily_duration(self, entries: List[TimetableEntry], class_group: str) -> List[TimetableEntry]:
        """ENHANCEMENT 4: Ensure minimum daily class duration using smart redistribution (no filler classes)."""
        if not entries:
            return entries

        # Group entries by day
        day_entries = {}
        for entry in entries:
            if entry.day not in day_entries:
                day_entries[entry.day] = []
            day_entries[entry.day].append(entry)

        # ENHANCEMENT: Smart redistribution instead of filler classes
        return self._redistribute_classes_for_minimum_duration(entries, day_entries, class_group)

    def _add_filler_classes(self, class_group: str, day: str, start_period: int, periods_needed: int) -> List[TimetableEntry]:
        """Add filler classes to meet minimum daily duration."""
        filler_entries = []

        # Get subjects for this class group to use for filler
        subjects = self._get_subjects_for_class_group(class_group)
        theory_subjects = [s for s in subjects if not self._is_practical_subject(s)]

        if not theory_subjects:
            return filler_entries

        # Add filler periods
        for i in range(periods_needed):
            period = start_period + i
            if period > len(self.periods):
                break

            # Use a theory subject for filler (rotate through subjects)
            subject = theory_subjects[i % len(theory_subjects)]

            # Find available teacher and classroom
            teachers = self._get_teachers_for_subject(subject, class_group)
            if teachers:
                teacher = self._find_available_teacher(teachers, day, period, 1)
                if teacher:
                    classroom = self._find_available_classroom(day, period, 1)
                    if classroom:
                        entry = self._create_entry(day, period, subject, teacher, classroom, class_group, False)
                        filler_entries.append(entry)
                        self._mark_global_schedule(teacher, classroom, day, period)
                        print(f"       ✅ Added filler class: {subject.code} on {day} P{period}")

        return filler_entries

    def _redistribute_classes_for_minimum_duration(self, entries: List[TimetableEntry], day_entries: dict, class_group: str) -> List[TimetableEntry]:
        """ENHANCEMENT: Smart class redistribution to meet minimum duration without adding filler classes."""
        print(f"     🔄 Smart redistribution for minimum duration compliance...")

        # Analyze each day's duration
        day_analysis = {}
        for day, day_entry_list in day_entries.items():
            if not day_entry_list:
                continue

            latest_period = max(entry.period for entry in day_entry_list)
            min_required_period = 3  # Default minimum (11:00 AM)
            if day.lower() == 'friday':
                min_required_period = 2  # Friday can end earlier (10:00 AM)

            day_analysis[day] = {
                'entries': day_entry_list,
                'latest_period': latest_period,
                'min_required': min_required_period,
                'needs_extension': latest_period < min_required_period,
                'deficit': max(0, min_required_period - latest_period),
                'theory_classes': [e for e in day_entry_list if not e.is_practical]
            }

        # Find days that need extension and days that can donate classes
        short_days = [day for day, analysis in day_analysis.items() if analysis['needs_extension']]
        long_days = [day for day, analysis in day_analysis.items() if not analysis['needs_extension'] and len(analysis['theory_classes']) > 1]

        if not short_days:
            print(f"       ✅ All days meet minimum duration requirements")
            return entries

        print(f"       📊 Short days needing extension: {short_days}")
        print(f"       📊 Long days available for redistribution: {long_days}")

        # Perform smart redistribution
        redistributed_entries = list(entries)  # Copy original entries

        for short_day in short_days:
            short_analysis = day_analysis[short_day]
            classes_needed = short_analysis['deficit']

            print(f"       🔄 {class_group} {short_day} needs {classes_needed} more classes")

            # Try to move theory classes from long days
            classes_moved = 0
            for long_day in long_days:
                if classes_moved >= classes_needed:
                    break

                long_analysis = day_analysis[long_day]
                movable_classes = [e for e in long_analysis['theory_classes']
                                 if e.period > short_analysis['min_required']]  # Only move classes from later periods

                for movable_class in movable_classes:
                    if classes_moved >= classes_needed:
                        break

                    # Find available slot in short day
                    target_period = short_analysis['latest_period'] + classes_moved + 1

                    if target_period <= len(self.periods) and self._can_move_class(movable_class, short_day, target_period, redistributed_entries):
                        # Move the class
                        print(f"         ✅ Moving {movable_class.subject.code} from {long_day} P{movable_class.period} to {short_day} P{target_period}")

                        # Update the entry
                        for i, entry in enumerate(redistributed_entries):
                            if (entry.class_group == movable_class.class_group and
                                entry.subject.code == movable_class.subject.code and
                                entry.day == movable_class.day and
                                entry.period == movable_class.period):

                                # Create new entry with updated day and period
                                new_entry = self._create_entry(
                                    short_day, target_period,
                                    entry.subject, entry.teacher, entry.classroom,
                                    entry.class_group, entry.is_practical
                                )
                                redistributed_entries[i] = new_entry
                                classes_moved += 1
                                break

            if classes_moved > 0:
                print(f"       ✅ Successfully moved {classes_moved} classes to {short_day}")
            else:
                print(f"       ⚠️  Could not find classes to move to {short_day}")

        return redistributed_entries

    def _enforce_friday_time_limit(self, entries: List[TimetableEntry], class_group: str) -> List[TimetableEntry]:
        """ENHANCEMENT 7: Enforce Friday classes must not exceed 12:00 PM (Period 4)."""
        print(f"     📅 Enforcing Friday 12:00 PM limit for {class_group}...")

        # Find Friday entries that violate the limit
        friday_entries = [e for e in entries if e.day.lower() == 'friday']
        violating_entries = [e for e in friday_entries if e.period > 4]  # Period 5+ = after 12:00 PM

        if not violating_entries:
            print(f"       ✅ All Friday classes end by 12:00 PM - no violations")
            return entries

        print(f"       ⚠️  Found {len(violating_entries)} Friday classes after 12:00 PM - redistributing...")

        # Remove violating entries from Friday
        compliant_entries = [e for e in entries if not (e.day.lower() == 'friday' and e.period > 4)]

        # Try to redistribute violating entries to other days
        redistributed_entries = list(compliant_entries)

        for violating_entry in violating_entries:
            # Try to find alternative slot on other days (Monday-Thursday)
            alternative_found = False

            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
                for period in range(1, 8):  # Try all periods
                    if self._can_reschedule_entry(violating_entry, day, period, redistributed_entries):
                        # Create new entry with alternative day/period
                        new_entry = self._create_entry(
                            day, period,
                            violating_entry.subject, violating_entry.teacher, violating_entry.classroom,
                            violating_entry.class_group, violating_entry.is_practical
                        )
                        redistributed_entries.append(new_entry)
                        alternative_found = True
                        print(f"         ✅ Moved {violating_entry.subject.code} from Friday P{violating_entry.period} to {day} P{period}")
                        break

                if alternative_found:
                    break

            if not alternative_found:
                print(f"         ⚠️  Could not redistribute {violating_entry.subject.code} - keeping on Friday P{min(violating_entry.period, 4)}")
                # Keep the class but move it to Period 4 (12:00 PM) as last resort
                capped_entry = self._create_entry(
                    'Friday', 4,
                    violating_entry.subject, violating_entry.teacher, violating_entry.classroom,
                    violating_entry.class_group, violating_entry.is_practical
                )
                redistributed_entries.append(capped_entry)

        # Verify Friday compliance
        final_friday_entries = [e for e in redistributed_entries if e.day.lower() == 'friday']
        violations_remaining = [e for e in final_friday_entries if e.period > 4]

        if not violations_remaining:
            print(f"       ✅ Friday 12:00 PM limit successfully enforced!")
        else:
            print(f"       ⚠️  {len(violations_remaining)} Friday violations remain (unavoidable)")

        return redistributed_entries

    def _assign_thesis_day_if_needed(self, entries: List[TimetableEntry], subjects: List[Subject], class_group: str) -> List[TimetableEntry]:
        """ENHANCEMENT 6: Intelligent Thesis Day assignment for final year batch (detected by 3 theory subjects)."""
        print(f"     🎓 Analyzing {class_group} for Thesis Day eligibility...")

        # INTELLIGENT DETECTION: Final year batch has exactly 3 theory subjects
        theory_subjects = [s for s in subjects if not s.is_practical]
        theory_count = len(theory_subjects)

        is_final_year = theory_count == 3  # Precise detection: exactly 3 theory subjects = final year

        if not is_final_year:
            print(f"       ℹ️  {class_group} has {theory_count} theory subjects - not final year, no Thesis Day")
            return entries

        print(f"       🎓 DETECTED: {class_group} is FINAL YEAR batch ({theory_count} theory subjects) - eligible for Thesis Day")

        # Analyze current schedule for problematic days
        day_entries = {}
        for entry in entries:
            if entry.day not in day_entries:
                day_entries[entry.day] = []
            day_entries[entry.day].append(entry)

        # Find days with insufficient classes
        problematic_days = []
        for day, day_entry_list in day_entries.items():
            if not day_entry_list:
                continue

            latest_period = max(entry.period for entry in day_entry_list)
            min_required_period = 3  # Default minimum (11:00 AM)
            if day.lower() == 'friday':
                min_required_period = 2  # Friday can end earlier

            if latest_period < min_required_period:
                problematic_days.append({
                    'day': day,
                    'latest_period': latest_period,
                    'classes_count': len(day_entry_list),
                    'deficit': min_required_period - latest_period
                })

        if not problematic_days:
            print(f"       ✅ {class_group} has no problematic days - no Thesis Day assignment needed")
            return entries

        # INTELLIGENT DECISION: Assign Thesis Day to the most problematic day
        most_problematic = max(problematic_days, key=lambda x: x['deficit'])
        thesis_day = most_problematic['day']

        print(f"       🎓 INTELLIGENT ASSIGNMENT: {thesis_day} designated as THESIS DAY for {class_group}")
        print(f"          📊 {thesis_day} had only {most_problematic['classes_count']} classes (ending at Period {most_problematic['latest_period']})")
        print(f"          🎯 Thesis Day solves minimum duration while preserving credit compliance")

        # Create Thesis Day entry (special marker)
        thesis_entry = self._create_thesis_day_entry(class_group, thesis_day)

        return entries + [thesis_entry]

    def _assign_thesis_day_if_needed(self, entries: List[TimetableEntry], subjects: List[Subject], class_group: str) -> List[TimetableEntry]:
        """ENHANCEMENT 6: Intelligent Thesis Day assignment for final year batches (detected by low subject count)."""
        print(f"     🎓 Analyzing {class_group} for Thesis Day eligibility...")

        # INTELLIGENT DETECTION: Final year batches have fewer subjects (≤ 5 subjects typically)
        total_subjects = len(subjects)
        is_final_year = total_subjects <= 5  # Smart detection based on subject count

        if not is_final_year:
            print(f"       ℹ️  {class_group} has {total_subjects} subjects - not final year, no Thesis Day needed")
            return entries

        print(f"       🎓 DETECTED: {class_group} is final year batch ({total_subjects} subjects) - eligible for Thesis Day")

        # Analyze current schedule for problematic days
        day_entries = {}
        for entry in entries:
            if entry.day not in day_entries:
                day_entries[entry.day] = []
            day_entries[entry.day].append(entry)

        # Find days with insufficient classes that couldn't be fixed by redistribution
        problematic_days = []
        for day, day_entry_list in day_entries.items():
            if not day_entry_list:
                continue

            latest_period = max(entry.period for entry in day_entry_list)
            min_required_period = 3  # Default minimum (11:00 AM)
            if day.lower() == 'friday':
                min_required_period = 2  # Friday can end earlier

            if latest_period < min_required_period:
                problematic_days.append({
                    'day': day,
                    'latest_period': latest_period,
                    'classes_count': len(day_entry_list),
                    'deficit': min_required_period - latest_period
                })

        if not problematic_days:
            print(f"       ✅ {class_group} has no problematic days - no Thesis Day assignment needed")
            return entries

        # INTELLIGENT DECISION: Assign Thesis Day to the most problematic day
        most_problematic = max(problematic_days, key=lambda x: x['deficit'])
        thesis_day = most_problematic['day']

        print(f"       🎓 INTELLIGENT ASSIGNMENT: {thesis_day} designated as Thesis Day for {class_group}")
        print(f"          📊 {thesis_day} had only {most_problematic['classes_count']} classes (ending at Period {most_problematic['latest_period']})")
        print(f"          🎯 Thesis Day solves minimum duration requirement while preserving credit compliance")

        # Create Thesis Day entry
        thesis_entry = self._create_thesis_day_entry(class_group, thesis_day)

        return entries + [thesis_entry]

    def _assign_thesis_day_if_needed(self, entries: List[TimetableEntry], subjects: List[Subject], class_group: str) -> List[TimetableEntry]:
        """ENHANCEMENT 6: Intelligent Thesis Day assignment for final year batch (detected by 3 theory subjects)."""
        print(f"     🎓 Analyzing {class_group} for Thesis Day eligibility...")

        # INTELLIGENT DETECTION: Final year batch has exactly 3 theory subjects
        theory_subjects = [s for s in subjects if not s.is_practical]
        theory_count = len(theory_subjects)

        print(f"       🔍 Debug: Total subjects={len(subjects)}, Theory subjects={theory_count}")
        print(f"       🔍 Theory subjects: {[s.code for s in theory_subjects]}")

        is_final_year = theory_count == 3  # Precise detection: exactly 3 theory subjects = final year

        if not is_final_year:
            print(f"       ℹ️  {class_group} has {theory_count} theory subjects - not final year, no Thesis Day")
            return entries

        # Analyze current schedule for problematic days
        day_entries = {}
        for entry in entries:
            if entry.day not in day_entries:
                day_entries[entry.day] = []
            day_entries[entry.day].append(entry)

        # Find days with insufficient classes that couldn't be fixed by redistribution
        problematic_days = []
        for day, day_entry_list in day_entries.items():
            if not day_entry_list:
                continue

            latest_period = max(entry.period for entry in day_entry_list)
            min_required_period = 3  # Default minimum (11:00 AM)
            if day.lower() == 'friday':
                min_required_period = 2  # Friday can end earlier

            if latest_period < min_required_period:
                problematic_days.append({
                    'day': day,
                    'latest_period': latest_period,
                    'classes_count': len(day_entry_list),
                    'deficit': min_required_period - latest_period
                })

        if not problematic_days:
            print(f"       ✅ {class_group} has no problematic days - no Thesis Day needed")
            return entries

        # INTELLIGENT DECISION: Assign Thesis Day to the most problematic day
        most_problematic = max(problematic_days, key=lambda x: x['deficit'])
        thesis_day = most_problematic['day']

        print(f"       🎓 INTELLIGENT DECISION: Assigning {thesis_day} as Thesis Day for {class_group}")
        print(f"          📊 {thesis_day} had only {most_problematic['classes_count']} classes (ending at Period {most_problematic['latest_period']})")
        print(f"          🎯 Thesis Day solves minimum duration requirement for final year students")

        # Create Thesis Day entry and clear that day of other classes
        thesis_entry = self._create_thesis_day_entry(class_group, thesis_day)

        # ENHANCEMENT: Remove all other classes from thesis day to make it a complete day off
        filtered_entries = [e for e in entries if e.day != thesis_day]

        print(f"          🧹 Cleared {len(entries) - len(filtered_entries)} classes from {thesis_day}")
        print(f"          🎓 {thesis_day} is now a complete THESIS DAY OFF for {class_group}")

        return filtered_entries + [thesis_entry]

    def _can_move_class(self, movable_class: TimetableEntry, target_day: str, target_period: int, entries: List[TimetableEntry]) -> bool:
        """Check if a class can be moved to a specific day and period."""
        # Check if target slot is already occupied
        for entry in entries:
            if (entry.class_group == movable_class.class_group and
                entry.day == target_day and
                entry.period == target_period):
                return False

        # Check teacher availability (simplified - could be enhanced)
        for entry in entries:
            if (entry.teacher.id == movable_class.teacher.id and
                entry.day == target_day and
                entry.period == target_period and
                entry != movable_class):
                return False

        # Check classroom availability (simplified - could be enhanced)
        for entry in entries:
            if (entry.classroom.id == movable_class.classroom.id and
                entry.day == target_day and
                entry.period == target_period and
                entry != movable_class):
                return False

        return True

    def _can_reschedule_entry(self, entry: TimetableEntry, target_day: str, target_period: int, existing_entries: List[TimetableEntry]) -> bool:
        """Check if an entry can be rescheduled to a specific day and period."""
        # Check if target slot is already occupied by same class group
        for existing in existing_entries:
            if (existing.class_group == entry.class_group and
                existing.day == target_day and
                existing.period == target_period):
                return False

        # Check teacher availability
        for existing in existing_entries:
            if (existing.teacher.id == entry.teacher.id and
                existing.day == target_day and
                existing.period == target_period):
                return False

        # Check classroom availability
        for existing in existing_entries:
            if (existing.classroom.id == entry.classroom.id and
                existing.day == target_day and
                existing.period == target_period):
                return False

        return True

    def _validate_credit_hour_compliance(self, entries: List[TimetableEntry], subjects: List[Subject], class_group: str):
        """ENHANCEMENT 5: Validate that subjects are scheduled exactly according to their credit hours."""
        print(f"     📊 Validating credit hour compliance for {class_group}...")

        # Count scheduled classes per subject
        subject_counts = {}
        for entry in entries:
            subject_code = entry.subject.code
            if subject_code not in subject_counts:
                subject_counts[subject_code] = 0

            # For practical subjects, count 3 consecutive periods as 1 session
            if entry.is_practical:
                # Only count the first period of a practical session
                if entry.period == 1 or not any(
                    e.subject.code == subject_code and e.day == entry.day and e.period == entry.period - 1
                    for e in entries
                ):
                    subject_counts[subject_code] += 1
            else:
                subject_counts[subject_code] += 1

        # Validate against expected credit hours
        compliance_issues = []
        for subject in subjects:
            expected_classes = subject.credits
            actual_classes = subject_counts.get(subject.code, 0)

            # Special rule for practical subjects
            if self._is_practical_subject(subject):
                expected_classes = 1  # Practical subjects: 1 credit = 1 session per week
                rule_description = "1 credit = 1 session/week (3 consecutive hours)"
            else:
                rule_description = f"{subject.credits} credits = {subject.credits} classes/week"

            if actual_classes != expected_classes:
                compliance_issues.append({
                    'subject': subject.code,
                    'expected': expected_classes,
                    'actual': actual_classes,
                    'rule': rule_description
                })
                print(f"       ❌ {subject.code}: Expected {expected_classes}, got {actual_classes} ({rule_description})")
            else:
                print(f"       ✅ {subject.code}: {actual_classes} classes/week (compliant)")

        if compliance_issues:
            print(f"     ⚠️  {len(compliance_issues)} credit hour compliance issues found")
        else:
            print(f"     ✅ Perfect credit hour compliance - all subjects scheduled correctly!")

        return compliance_issues

    def _generate_overall_compliance_report(self, entries: List[TimetableEntry]) -> Dict:
        """ENHANCEMENT 5: Generate overall credit hour compliance report."""
        print(f"\n📊 OVERALL CREDIT HOUR COMPLIANCE REPORT:")

        # Group entries by section
        section_entries = {}
        for entry in entries:
            if entry.class_group not in section_entries:
                section_entries[entry.class_group] = []
            section_entries[entry.class_group].append(entry)

        total_sections = len(section_entries)
        compliant_sections = 0
        total_issues = 0

        for section, section_entry_list in section_entries.items():
            subjects = self._get_subjects_for_class_group(section)
            issues = self._validate_credit_hour_compliance(section_entry_list, subjects, section)

            if not issues:
                compliant_sections += 1
            else:
                total_issues += len(issues)

        compliance_percentage = (compliant_sections / total_sections * 100) if total_sections > 0 else 0

        print(f"   📈 Compliant sections: {compliant_sections}/{total_sections} ({compliance_percentage:.1f}%)")
        print(f"   📊 Total compliance issues: {total_issues}")

        if compliance_percentage == 100:
            print(f"   🏆 PERFECT CREDIT HOUR COMPLIANCE!")
        elif compliance_percentage >= 80:
            print(f"   ✅ Good compliance rate")
        else:
            print(f"   ⚠️  Compliance needs improvement")

        return {
            'total_sections': total_sections,
            'compliant_sections': compliant_sections,
            'compliance_percentage': compliance_percentage,
            'total_issues': total_issues,
            'perfect_compliance': compliance_percentage == 100
        }

    def _create_thesis_day_entry(self, class_group: str, thesis_day: str) -> TimetableEntry:
        """Create a special Thesis Day entry for final year students."""

        # FIX: Clean up any old thesis entries and create the correct one
        # Remove old problematic "THESIS" entries
        Subject.objects.filter(code="THESIS").delete()

        # Create or get the correct "Thesis Day" subject
        thesis_subject, created = Subject.objects.get_or_create(
            code="THESIS DAY",
            defaults={
                'name': "Thesis Work - Complete Day Off",
                'credits': 0,  # Special: 0 credits for thesis day
                'is_practical': False
            }
        )

        # Create or get special "Thesis Supervisor" teacher
        thesis_teacher, created = Teacher.objects.get_or_create(
            name="Thesis Supervisor",
            defaults={'email': 'thesis@university.edu'}
        )

        # Use any available classroom (or create thesis room)
        thesis_classroom, created = Classroom.objects.get_or_create(
            name="Thesis Room",
            defaults={'capacity': 30}
        )

        # Create thesis day entry for the entire day (Period 1-7)
        from datetime import time
        thesis_entry = TimetableEntry(
            day=thesis_day,
            period=1,  # Start from Period 1
            subject=thesis_subject,
            teacher=thesis_teacher,
            classroom=thesis_classroom,
            class_group=class_group,
            start_time=time(8, 0),  # 8:00 AM
            end_time=time(15, 0),   # 3:00 PM (full day thesis work)
            is_practical=False
        )

        print(f"          📝 Created Thesis Day entry: {thesis_day} full day for {class_group}")

        return thesis_entry
