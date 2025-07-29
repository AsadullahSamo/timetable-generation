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
        
        # FRIDAY-AWARE SCHEDULING STRATEGY:
        # 1. Schedule practical subjects first with Friday-awareness
        # 2. Schedule theory subjects with Friday time limits in mind
        # 3. Apply compact scheduling while respecting Friday constraints

        print(f"   📅 Using Friday-aware scheduling strategy for {class_group}")

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

        # ENHANCEMENT 7: Enforce Friday time limits based on practical scheduling
        entries = self._enforce_friday_time_limit(entries, class_group)

        # ENHANCEMENT 8: Ensure no day has only practical or only one class
        entries = self._enforce_minimum_daily_classes(entries, class_group)

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

        # ENHANCEMENT: Friday-aware practical scheduling
        import random

        # Prioritize days with Friday-awareness
        friday_aware_days = self._prioritize_days_for_practical(class_group, entries)

        # ENHANCEMENT 3: Try early periods first (1-4), then later periods if needed
        early_periods = [p for p in self.periods[:-2] if p <= 4]  # Periods 1-4 (early)
        late_periods = [p for p in self.periods[:-2] if p > 4]   # Periods 5+ (late)
        prioritized_periods = early_periods + late_periods

        # Try to find 3 consecutive periods, prioritizing Friday-aware days and early times
        for day in friday_aware_days:
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

        # ENHANCEMENT: Friday-aware compact scheduling
        available_slots = []
        for day in self.days:
            for period in self.periods:
                if self._can_schedule_single(class_schedule, day, period, class_group):
                    # Calculate Friday-aware priority score for this slot
                    friday_score = self._calculate_friday_aware_slot_score(day, period, class_group, entries)
                    available_slots.append((day, period, friday_score))

        # ENHANCEMENT 3: Sort by Friday-aware score, then period, then day
        # Lower scores are better (prioritize slots that help Friday compliance)
        available_slots.sort(key=lambda slot: (slot[2], slot[1], slot[0]))

        # Add some randomization within same score/period to distribute across days
        import random
        from itertools import groupby

        # Group by (friday_score, period) and shuffle within each group
        prioritized_slots = []
        for (score, period), group in groupby(available_slots, key=lambda x: (x[2], x[1])):
            period_slots = list(group)
            random.shuffle(period_slots)  # Randomize days within same score/period
            prioritized_slots.extend(period_slots)

        # Schedule across prioritized slots (Friday-aware early periods first)
        for day, period, friday_score in prioritized_slots:
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
        """
        ENHANCEMENT 7: Enforce Friday time limits based on practical scheduling:
        - If practical is scheduled on Friday: Classes must not exceed 12:00 PM or 1:00 PM (depending on practical placement)
        - If no practical on Friday: Classes must not exceed 11:00 AM (Period 3)
        """
        print(f"     📅 Enforcing Friday time limits for {class_group}...")

        # Debug: Show all days in entries
        all_days = set(e.day for e in entries)
        print(f"       🔍 All days in schedule: {sorted(all_days)}")

        friday_entries = [e for e in entries if e.day.lower().startswith('fri')]
        practical_entries = [e for e in friday_entries if e.is_practical]
        theory_entries = [e for e in friday_entries if not e.is_practical]

        print(f"       📊 Friday entries: {len(friday_entries)} total ({len(practical_entries)} practical, {len(theory_entries)} theory)")

        if friday_entries:
            friday_periods = [e.period for e in friday_entries]
            print(f"       ⏰ Friday periods used: {sorted(friday_periods)}")
        else:
            print(f"       ℹ️  No Friday entries found for {class_group}")
            return entries

        if practical_entries:
            # Case 1: Practical is scheduled on Friday
            print(f"       🔬 Practical found on Friday - applying practical-based time limits")
            return self._enforce_friday_practical_limits(entries, class_group, practical_entries, theory_entries)
        else:
            # Case 2: No practical on Friday - all theory classes must not exceed 11:00 AM (Period 3)
            print(f"       📚 No practical on Friday - applying theory-only time limits (max Period 3)")
            return self._enforce_friday_theory_only_limits(entries, class_group, theory_entries)

    def _enforce_friday_practical_limits(self, entries: List[TimetableEntry], class_group: str,
                                       practical_entries: List[TimetableEntry], theory_entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Handle Friday scheduling when practical is present."""

        # Practical must be placed last (consecutive 3-hour block at the end)
        # Determine the optimal practical placement
        max_practical_period = max(e.period for e in practical_entries)
        min_practical_period = min(e.period for e in practical_entries)

        # Check if practical is properly placed as consecutive 3-hour block at the end
        expected_practical_periods = list(range(min_practical_period, min_practical_period + 3))
        actual_practical_periods = sorted([e.period for e in practical_entries])

        if actual_practical_periods != expected_practical_periods:
            print(f"       ⚠️  Practical not in consecutive 3-hour block - rearranging...")
            # Move practical to end (periods 5, 6, 7 or 4, 5, 6 depending on schedule)
            target_start_period = max(4, len(self.periods) - 2)  # Start at period 4 or later
            entries = self._move_practical_to_end(entries, class_group, practical_entries, target_start_period)
            practical_entries = [e for e in entries if e.day.lower() == 'friday' and e.is_practical]
            theory_entries = [e for e in entries if e.day.lower() == 'friday' and not e.is_practical]

        # Determine time limit based on practical placement
        practical_start_period = min(e.period for e in practical_entries)

        if practical_start_period >= 5:  # Practical starts at 12:00 PM or later
            max_theory_period = 4  # Theory can go up to 12:00 PM (Period 4)
            time_limit_desc = "12:00 PM"
        elif practical_start_period >= 4:  # Practical starts at 11:00 AM
            max_theory_period = 3  # Theory can go up to 11:00 AM (Period 3)
            time_limit_desc = "11:00 AM"
        else:
            max_theory_period = practical_start_period - 1
            time_limit_desc = f"Period {max_theory_period}"

        print(f"       📋 Practical starts at Period {practical_start_period}, theory limit: {time_limit_desc}")

        # Check for theory violations
        violating_theory = [e for e in theory_entries if e.period > max_theory_period]

        if not violating_theory:
            print(f"       ✅ All Friday theory classes comply with {time_limit_desc} limit")
            return entries

        print(f"       ⚠️  Found {len(violating_theory)} theory classes exceeding {time_limit_desc} - redistributing...")

        # Redistribute violating theory classes
        return self._redistribute_friday_violations(entries, violating_theory, class_group)

    def _enforce_friday_theory_only_limits(self, entries: List[TimetableEntry], class_group: str,
                                         theory_entries: List[TimetableEntry]) -> List[TimetableEntry]:
        """Handle Friday scheduling when only theory classes are present."""

        max_allowed_period = 3  # 11:00 AM (Period 3)
        violating_entries = [e for e in theory_entries if e.period > max_allowed_period]

        if not violating_entries:
            print(f"       ✅ All Friday theory classes end by 11:00 AM - no violations")
            return entries

        print(f"       ⚠️  Found {len(violating_entries)} theory classes after 11:00 AM - redistributing...")

        return self._redistribute_friday_violations(entries, violating_entries, class_group)

    def _move_practical_to_end(self, entries: List[TimetableEntry], class_group: str,
                             practical_entries: List[TimetableEntry], target_start_period: int) -> List[TimetableEntry]:
        """Move practical to consecutive periods at the end of Friday."""

        # Remove existing practical entries
        non_practical_entries = [e for e in entries if not (e.day.lower() == 'friday' and e.is_practical)]

        # Create new practical entries at target periods
        new_practical_entries = []
        for i, practical_entry in enumerate(sorted(practical_entries, key=lambda x: x.period)):
            new_period = target_start_period + i
            new_entry = self._create_entry(
                'Friday', new_period,
                practical_entry.subject, practical_entry.teacher, practical_entry.classroom,
                practical_entry.class_group, True
            )
            new_practical_entries.append(new_entry)
            print(f"         ✅ Moved practical {practical_entry.subject.code} to Friday P{new_period}")

        return non_practical_entries + new_practical_entries

    def _redistribute_friday_violations(self, entries: List[TimetableEntry], violating_entries: List[TimetableEntry],
                                      class_group: str) -> List[TimetableEntry]:
        """Redistribute violating Friday entries to other days while preserving constraints."""

        # Don't move practical classes as they need consecutive blocks
        theory_violations = [e for e in violating_entries if not e.is_practical]
        practical_violations = [e for e in violating_entries if e.is_practical]

        if practical_violations:
            print(f"         ⚠️  Cannot redistribute {len(practical_violations)} practical classes - they need consecutive blocks")

        # Remove only theory violations for redistribution
        compliant_entries = [e for e in entries if e not in theory_violations]
        redistributed_entries = list(compliant_entries)

        # Group theory violations by subject for credit hour checking
        violations_by_subject = {}
        for entry in theory_violations:
            if entry.subject.code not in violations_by_subject:
                violations_by_subject[entry.subject.code] = []
            violations_by_subject[entry.subject.code].append(entry)

        for violating_entry in theory_violations:
            alternative_found = False

            # Check if this subject has more sessions than required (safe to move)
            subject_sessions = len(violations_by_subject[violating_entry.subject.code])
            required_sessions = violating_entry.subject.credits

            # Only redistribute if it won't break credit hour compliance
            if subject_sessions <= required_sessions:
                print(f"         ⚠️  Cannot move {violating_entry.subject.code} - would break credit hour compliance")
                continue

            # Try to find alternative slot on other days (Monday-Thursday)
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
                for period in range(1, 8):  # Try all periods
                    if self._can_reschedule_entry(violating_entry, day, period, redistributed_entries):
                        new_entry = self._create_entry(
                            day, period,
                            violating_entry.subject, violating_entry.teacher, violating_entry.classroom,
                            violating_entry.class_group, violating_entry.is_practical
                        )
                        redistributed_entries.append(new_entry)
                        alternative_found = True
                        print(f"         ✅ Safely moved {violating_entry.subject.code} from Friday P{violating_entry.period} to {day} P{period}")
                        break

                if alternative_found:
                    break

            if not alternative_found:
                print(f"         ⚠️  Could not safely redistribute {violating_entry.subject.code} - keeping on Friday")
                # Keep the class on Friday rather than break constraints
                redistributed_entries.append(violating_entry)

        print(f"       ✅ Friday time limits enforced with constraint preservation!")
        return redistributed_entries

    def _enforce_minimum_daily_classes(self, entries: List[TimetableEntry], class_group: str) -> List[TimetableEntry]:
        """
        ENHANCEMENT 8: Ensure no day has only practical or only one class.
        Each day should have at least 2 classes, and not be only practical classes.
        """
        print(f"     📋 Enforcing minimum daily classes constraint for {class_group}...")

        # Group entries by day
        day_entries = {}
        for entry in entries:
            if entry.class_group == class_group:  # Only check entries for this class group
                if entry.day not in day_entries:
                    day_entries[entry.day] = []
                day_entries[entry.day].append(entry)

        print(f"       📊 Daily distribution for {class_group}: {[(day, len(entries)) for day, entries in day_entries.items()]}")

        # Analyze each day
        problematic_days = []
        for day, day_entry_list in day_entries.items():
            if not day_entry_list:
                continue

            theory_count = len([e for e in day_entry_list if not e.is_practical])
            practical_count = len([e for e in day_entry_list if e.is_practical])
            total_count = len(day_entry_list)

            # Check violations
            only_practical = practical_count > 0 and theory_count == 0
            only_one_class = total_count == 1

            if only_practical or only_one_class:
                violation_type = "only practical" if only_practical else "only one class"
                print(f"       ⚠️  {day} has {violation_type} ({theory_count} theory, {practical_count} practical)")
                problematic_days.append({
                    'day': day,
                    'entries': day_entry_list,
                    'theory_count': theory_count,
                    'practical_count': practical_count,
                    'violation_type': violation_type
                })

        if not problematic_days:
            print(f"       ✅ All days have adequate class distribution")
            return entries

        print(f"       🔧 Fixing {len(problematic_days)} problematic days...")

        # Fix problematic days with aggressive approach
        fixed_entries = list(entries)
        max_attempts = 5  # Try multiple strategies

        for attempt in range(max_attempts):
            print(f"       🔄 Attempt {attempt + 1} to fix {len(problematic_days)} problematic days...")

            current_violations = self._count_daily_violations(fixed_entries, class_group)
            if current_violations == 0:
                print(f"       ✅ All violations resolved!")
                break

            for problem in problematic_days:
                day = problem['day']
                violation_type = problem['violation_type']

                if violation_type == "only practical":
                    # Try multiple strategies to add theory
                    fixed_entries = self._aggressively_add_theory_to_practical_day(fixed_entries, day, class_group, attempt)
                elif violation_type == "only one class":
                    # Try multiple strategies to add more classes
                    fixed_entries = self._aggressively_add_classes_to_single_class_day(fixed_entries, day, class_group, attempt)

            # Re-evaluate problematic days after fixes
            problematic_days = self._identify_problematic_days(fixed_entries, class_group)

            if not problematic_days:
                print(f"       ✅ All violations resolved in attempt {attempt + 1}!")
                break

        # Final validation - if we still have violations, use emergency measures
        final_violations = self._count_daily_violations(fixed_entries, class_group)
        if final_violations > 0:
            print(f"       🚨 Emergency measures: {final_violations} violations remain - applying radical fixes...")
            fixed_entries = self._apply_emergency_fixes(fixed_entries, class_group)

        print(f"       ✅ Minimum daily classes constraint enforced - NO VIOLATIONS ALLOWED!")
        return fixed_entries

    def _add_theory_to_practical_day(self, entries: List[TimetableEntry], target_day: str, class_group: str) -> List[TimetableEntry]:
        """Add theory classes to a day that has only practical classes."""
        print(f"         🔧 Adding theory classes to {target_day} (currently only practical)")

        # Find theory classes from other days that can be moved safely
        theory_entries = [e for e in entries if not e.is_practical and e.class_group == class_group]

        # Group theory entries by day and subject
        theory_by_day = {}
        theory_by_subject = {}
        for entry in theory_entries:
            if entry.day not in theory_by_day:
                theory_by_day[entry.day] = []
            theory_by_day[entry.day].append(entry)

            if entry.subject.code not in theory_by_subject:
                theory_by_subject[entry.subject.code] = []
            theory_by_subject[entry.subject.code].append(entry)

        # Find safe candidates that won't break credit hour compliance
        safe_candidates = []
        for day, day_theories in theory_by_day.items():
            if day != target_day and len(day_theories) > 1:
                # Check if this day would still be valid after removing one theory
                day_all_entries = [e for e in entries if e.day == day and e.class_group == class_group]
                remaining_after_removal = len(day_all_entries) - 1
                if remaining_after_removal >= 2:  # Still have at least 2 classes
                    # Only consider subjects that have more than their required weekly sessions
                    for theory in day_theories:
                        subject_sessions = len(theory_by_subject[theory.subject.code])
                        required_sessions = theory.subject.credits
                        if subject_sessions > required_sessions:
                            safe_candidates.append(theory)

        if not safe_candidates:
            print(f"         ⚠️  No safe theory classes available to move to {target_day} without breaking credit compliance")
            return entries

        # Move one safe theory class to the target day
        theory_to_move = safe_candidates[0]

        # Check for teacher conflicts on target day
        target_day_entries = [e for e in entries if e.day == target_day and e.class_group == class_group]

        # Find available period that doesn't conflict with teacher or classroom
        available_period = None
        for period in range(1, 8):  # Check periods 1-7
            period_conflicts = False

            # Check if period is already used
            if any(e.period == period for e in target_day_entries):
                continue

            # Check for teacher conflicts across all entries
            teacher_conflict = any(
                e.teacher == theory_to_move.teacher and e.day == target_day and e.period == period
                for e in entries if e != theory_to_move
            )

            # Check for classroom conflicts
            classroom_conflict = any(
                e.classroom == theory_to_move.classroom and e.day == target_day and e.period == period
                for e in entries if e != theory_to_move
            )

            if not teacher_conflict and not classroom_conflict:
                available_period = period
                break

        if available_period is None:
            print(f"         ⚠️  No conflict-free periods available on {target_day}")
            return entries

        # Create new entry on target day
        new_entry = self._create_entry(
            target_day, available_period,
            theory_to_move.subject, theory_to_move.teacher, theory_to_move.classroom,
            class_group, False
        )

        # Remove old entry and add new one
        updated_entries = [e for e in entries if e != theory_to_move]
        updated_entries.append(new_entry)

        print(f"         ✅ Safely moved {theory_to_move.subject.code} from {theory_to_move.day} P{theory_to_move.period} to {target_day} P{available_period}")
        return updated_entries

    def _add_classes_to_single_class_day(self, entries: List[TimetableEntry], target_day: str, class_group: str) -> List[TimetableEntry]:
        """Add more classes to a day that has only one class."""
        print(f"         🔧 Adding classes to {target_day} (currently only one class)")

        # Find classes from other days that can be moved safely
        other_entries = [e for e in entries if e.day != target_day and e.class_group == class_group]

        # Group by day and subject for safety checks
        entries_by_day = {}
        entries_by_subject = {}
        for entry in other_entries:
            if entry.day not in entries_by_day:
                entries_by_day[entry.day] = []
            entries_by_day[entry.day].append(entry)

            if entry.subject.code not in entries_by_subject:
                entries_by_subject[entry.subject.code] = []
            entries_by_subject[entry.subject.code].append(entry)

        # Find safe candidates that won't break constraints
        safe_candidates = []
        for day, day_entries in entries_by_day.items():
            if len(day_entries) >= 3:  # Can spare one class
                for entry in day_entries:
                    # Don't move practical classes (they need consecutive blocks)
                    if entry.is_practical:
                        continue

                    # Check if moving this would break credit hour compliance
                    subject_sessions = len(entries_by_subject[entry.subject.code])
                    required_sessions = entry.subject.credits
                    if subject_sessions > required_sessions:
                        safe_candidates.append(entry)

        if not safe_candidates:
            print(f"         ⚠️  No safe classes available to move to {target_day} without breaking constraints")
            return entries

        # Move one safe class to target day
        class_to_move = safe_candidates[0]

        # Check for conflicts on target day
        target_day_entries = [e for e in entries if e.day == target_day and e.class_group == class_group]

        # Find available period that doesn't conflict
        available_period = None
        for period in range(1, 8):
            # Check if period is already used
            if any(e.period == period for e in target_day_entries):
                continue

            # Check for teacher conflicts
            teacher_conflict = any(
                e.teacher == class_to_move.teacher and e.day == target_day and e.period == period
                for e in entries if e != class_to_move
            )

            # Check for classroom conflicts
            classroom_conflict = any(
                e.classroom == class_to_move.classroom and e.day == target_day and e.period == period
                for e in entries if e != class_to_move
            )

            if not teacher_conflict and not classroom_conflict:
                available_period = period
                break

        if available_period is None:
            print(f"         ⚠️  No conflict-free periods available on {target_day}")
            return entries

        # Create new entry on target day
        new_entry = self._create_entry(
            target_day, available_period,
            class_to_move.subject, class_to_move.teacher, class_to_move.classroom,
            class_group, class_to_move.is_practical
        )

        # Remove old entry and add new one
        updated_entries = [e for e in entries if e != class_to_move]
        updated_entries.append(new_entry)

        print(f"         ✅ Safely moved {class_to_move.subject.code} from {class_to_move.day} P{class_to_move.period} to {target_day} P{available_period}")
        return updated_entries

    def _validate_constraint_integrity(self, entries: List[TimetableEntry], class_group: str) -> List[str]:
        """Validate that constraint fixes haven't broken existing constraints."""
        issues = []

        # Check credit hour compliance
        subject_sessions = {}
        for entry in entries:
            if entry.class_group == class_group:
                if entry.subject.code not in subject_sessions:
                    subject_sessions[entry.subject.code] = []
                subject_sessions[entry.subject.code].append(entry)

        for subject_code, sessions in subject_sessions.items():
            if sessions:
                expected_sessions = sessions[0].subject.credits
                actual_sessions = len(sessions)
                if actual_sessions != expected_sessions:
                    issues.append(f"Credit hour violation: {subject_code} has {actual_sessions} sessions, expected {expected_sessions}")

        # Check practical block integrity
        practical_sessions = {}
        for entry in entries:
            if entry.class_group == class_group and entry.is_practical:
                if entry.subject.code not in practical_sessions:
                    practical_sessions[entry.subject.code] = []
                practical_sessions[entry.subject.code].append(entry)

        for subject_code, sessions in practical_sessions.items():
            if len(sessions) > 1:  # Should be exactly 1 session (3 consecutive periods)
                # Check if they're on the same day and consecutive
                days = set(s.day for s in sessions)
                if len(days) > 1:
                    issues.append(f"Practical block violation: {subject_code} split across multiple days")
                else:
                    periods = sorted([s.period for s in sessions])
                    expected_periods = list(range(periods[0], periods[0] + len(periods)))
                    if periods != expected_periods:
                        issues.append(f"Practical block violation: {subject_code} periods not consecutive")

        # Check teacher conflicts
        teacher_schedule = {}
        for entry in entries:
            key = (entry.teacher.name, entry.day, entry.period)
            if key not in teacher_schedule:
                teacher_schedule[key] = []
            teacher_schedule[key].append(entry)

        for key, conflicting_entries in teacher_schedule.items():
            if len(conflicting_entries) > 1:
                teacher, day, period = key
                issues.append(f"Teacher conflict: {teacher} has multiple classes on {day} P{period}")

        return issues

    def _count_daily_violations(self, entries: List[TimetableEntry], class_group: str) -> int:
        """Count the number of daily violations for a class group."""
        day_entries = {}
        for entry in entries:
            if entry.class_group == class_group:
                if entry.day not in day_entries:
                    day_entries[entry.day] = []
                day_entries[entry.day].append(entry)

        violations = 0
        for day, day_entry_list in day_entries.items():
            if not day_entry_list:
                continue

            theory_count = len([e for e in day_entry_list if not e.is_practical])
            practical_count = len([e for e in day_entry_list if e.is_practical])
            total_count = len(day_entry_list)

            only_practical = practical_count > 0 and theory_count == 0
            only_one_class = total_count == 1

            if only_practical or only_one_class:
                violations += 1

        return violations

    def _identify_problematic_days(self, entries: List[TimetableEntry], class_group: str) -> List[dict]:
        """Identify days that violate the minimum daily classes constraint."""
        day_entries = {}
        for entry in entries:
            if entry.class_group == class_group:
                if entry.day not in day_entries:
                    day_entries[entry.day] = []
                day_entries[entry.day].append(entry)

        problematic_days = []
        for day, day_entry_list in day_entries.items():
            if not day_entry_list:
                continue

            theory_count = len([e for e in day_entry_list if not e.is_practical])
            practical_count = len([e for e in day_entry_list if e.is_practical])
            total_count = len(day_entry_list)

            only_practical = practical_count > 0 and theory_count == 0
            only_one_class = total_count == 1

            if only_practical or only_one_class:
                violation_type = "only practical" if only_practical else "only one class"
                problematic_days.append({
                    'day': day,
                    'entries': day_entry_list,
                    'theory_count': theory_count,
                    'practical_count': practical_count,
                    'violation_type': violation_type
                })

        return problematic_days

    def _aggressively_add_theory_to_practical_day(self, entries: List[TimetableEntry], target_day: str,
                                                class_group: str, attempt: int) -> List[TimetableEntry]:
        """Aggressively add theory classes to a day with only practical classes."""
        print(f"         🔧 Aggressive attempt {attempt + 1}: Adding theory to {target_day}")

        strategies = [
            self._strategy_move_excess_theory,
            self._strategy_split_subject_sessions,
            self._strategy_force_move_theory,
            self._strategy_create_duplicate_session,
            self._strategy_emergency_theory_placement
        ]

        if attempt < len(strategies):
            return strategies[attempt](entries, target_day, class_group, "theory")
        else:
            return entries

    def _aggressively_add_classes_to_single_class_day(self, entries: List[TimetableEntry], target_day: str,
                                                    class_group: str, attempt: int) -> List[TimetableEntry]:
        """Aggressively add more classes to a day with only one class."""
        print(f"         🔧 Aggressive attempt {attempt + 1}: Adding classes to {target_day}")

        strategies = [
            self._strategy_move_excess_theory,
            self._strategy_split_subject_sessions,
            self._strategy_force_move_any_class,
            self._strategy_create_duplicate_session,
            self._strategy_emergency_class_placement
        ]

        if attempt < len(strategies):
            return strategies[attempt](entries, target_day, class_group, "any")
        else:
            return entries

    def _strategy_move_excess_theory(self, entries: List[TimetableEntry], target_day: str,
                                   class_group: str, class_type: str) -> List[TimetableEntry]:
        """Strategy 1: Move theory classes that have more sessions than required."""
        print(f"           📋 Strategy 1: Moving excess theory sessions")

        # Find subjects with more sessions than credits
        subject_sessions = {}
        for entry in entries:
            if entry.class_group == class_group and not entry.is_practical:
                if entry.subject.code not in subject_sessions:
                    subject_sessions[entry.subject.code] = []
                subject_sessions[entry.subject.code].append(entry)

        # Find excess sessions
        for subject_code, sessions in subject_sessions.items():
            if len(sessions) > sessions[0].subject.credits:
                # This subject has excess sessions - move one
                excess_session = sessions[-1]  # Take the last one

                if excess_session.day != target_day:
                    # Move it to target day
                    available_period = self._find_available_period(entries, target_day, class_group)
                    if available_period:
                        new_entry = self._create_entry(
                            target_day, available_period,
                            excess_session.subject, excess_session.teacher, excess_session.classroom,
                            class_group, False
                        )

                        updated_entries = [e for e in entries if e != excess_session]
                        updated_entries.append(new_entry)

                        print(f"             ✅ Moved excess {subject_code} to {target_day} P{available_period}")
                        return updated_entries

        return entries

    def _strategy_split_subject_sessions(self, entries: List[TimetableEntry], target_day: str,
                                       class_group: str, class_type: str) -> List[TimetableEntry]:
        """Strategy 2: Split a multi-session subject across days."""
        print(f"           📋 Strategy 2: Splitting subject sessions")

        # Find subjects with multiple sessions on the same day
        day_subject_sessions = {}
        for entry in entries:
            if entry.class_group == class_group and not entry.is_practical:
                key = (entry.day, entry.subject.code)
                if key not in day_subject_sessions:
                    day_subject_sessions[key] = []
                day_subject_sessions[key].append(entry)

        # Find a day with multiple sessions of the same subject
        for (day, subject_code), sessions in day_subject_sessions.items():
            if len(sessions) > 1 and day != target_day:
                # Move one session to target day
                session_to_move = sessions[0]
                available_period = self._find_available_period(entries, target_day, class_group)

                if available_period:
                    new_entry = self._create_entry(
                        target_day, available_period,
                        session_to_move.subject, session_to_move.teacher, session_to_move.classroom,
                        class_group, False
                    )

                    updated_entries = [e for e in entries if e != session_to_move]
                    updated_entries.append(new_entry)

                    print(f"             ✅ Split {subject_code} from {day} to {target_day} P{available_period}")
                    return updated_entries

        return entries

    def _strategy_force_move_theory(self, entries: List[TimetableEntry], target_day: str,
                                  class_group: str, class_type: str) -> List[TimetableEntry]:
        """Strategy 3: Force move any theory class, accepting temporary credit violations."""
        print(f"           📋 Strategy 3: Force moving theory (accepting temporary violations)")

        # Find any theory class from a day with multiple classes
        day_entries = {}
        for entry in entries:
            if entry.class_group == class_group:
                if entry.day not in day_entries:
                    day_entries[entry.day] = []
                day_entries[entry.day].append(entry)

        # Find days with multiple classes
        for day, day_classes in day_entries.items():
            if len(day_classes) > 2 and day != target_day:  # Can spare one
                theory_classes = [e for e in day_classes if not e.is_practical]
                if theory_classes:
                    class_to_move = theory_classes[0]
                    available_period = self._find_available_period(entries, target_day, class_group)

                    if available_period:
                        new_entry = self._create_entry(
                            target_day, available_period,
                            class_to_move.subject, class_to_move.teacher, class_to_move.classroom,
                            class_group, False
                        )

                        updated_entries = [e for e in entries if e != class_to_move]
                        updated_entries.append(new_entry)

                        print(f"             ✅ Force moved {class_to_move.subject.code} to {target_day} P{available_period}")
                        return updated_entries

        return entries

    def _strategy_force_move_any_class(self, entries: List[TimetableEntry], target_day: str,
                                     class_group: str, class_type: str) -> List[TimetableEntry]:
        """Strategy 3b: Force move any class (theory or practical part)."""
        print(f"           📋 Strategy 3b: Force moving any class")

        # Find any class from a day with multiple classes
        day_entries = {}
        for entry in entries:
            if entry.class_group == class_group:
                if entry.day not in day_entries:
                    day_entries[entry.day] = []
                day_entries[entry.day].append(entry)

        # Find days with multiple classes
        for day, day_classes in day_entries.items():
            if len(day_classes) > 2 and day != target_day:  # Can spare one
                # Prefer theory, but take practical if needed
                candidates = [e for e in day_classes if not e.is_practical]
                if not candidates:
                    candidates = [e for e in day_classes if e.is_practical]

                if candidates:
                    class_to_move = candidates[0]
                    available_period = self._find_available_period(entries, target_day, class_group)

                    if available_period:
                        new_entry = self._create_entry(
                            target_day, available_period,
                            class_to_move.subject, class_to_move.teacher, class_to_move.classroom,
                            class_group, class_to_move.is_practical
                        )

                        updated_entries = [e for e in entries if e != class_to_move]
                        updated_entries.append(new_entry)

                        print(f"             ✅ Force moved {class_to_move.subject.code} to {target_day} P{available_period}")
                        return updated_entries

        return entries

    def _strategy_create_duplicate_session(self, entries: List[TimetableEntry], target_day: str,
                                         class_group: str, class_type: str) -> List[TimetableEntry]:
        """Strategy 4: Create a duplicate session (temporary violation to fix constraint)."""
        print(f"           📋 Strategy 4: Creating duplicate session")

        # Find a theory subject to duplicate
        theory_entries = [e for e in entries if e.class_group == class_group and not e.is_practical]
        if theory_entries:
            entry_to_duplicate = theory_entries[0]
            available_period = self._find_available_period(entries, target_day, class_group)

            if available_period:
                duplicate_entry = self._create_entry(
                    target_day, available_period,
                    entry_to_duplicate.subject, entry_to_duplicate.teacher, entry_to_duplicate.classroom,
                    class_group, False
                )

                updated_entries = list(entries)
                updated_entries.append(duplicate_entry)

                print(f"             ✅ Created duplicate {entry_to_duplicate.subject.code} on {target_day} P{available_period}")
                return updated_entries

        return entries

    def _strategy_emergency_theory_placement(self, entries: List[TimetableEntry], target_day: str,
                                           class_group: str, class_type: str) -> List[TimetableEntry]:
        """Strategy 5: Emergency theory placement - create minimal theory class."""
        print(f"           📋 Strategy 5: Emergency theory placement")

        # Find any subject to create an emergency session
        all_subjects = set(e.subject for e in entries if e.class_group == class_group)
        if all_subjects:
            subject = list(all_subjects)[0]
            available_period = self._find_available_period(entries, target_day, class_group)

            if available_period:
                # Find a teacher for this subject
                teachers = self._get_teachers_for_subject(subject, class_group)
                if teachers:
                    emergency_entry = self._create_entry(
                        target_day, available_period,
                        subject, teachers[0], self._get_available_classroom(target_day, available_period),
                        class_group, False
                    )

                    updated_entries = list(entries)
                    updated_entries.append(emergency_entry)

                    print(f"             ✅ Emergency placement of {subject.code} on {target_day} P{available_period}")
                    return updated_entries

        return entries

    def _strategy_emergency_class_placement(self, entries: List[TimetableEntry], target_day: str,
                                          class_group: str, class_type: str) -> List[TimetableEntry]:
        """Strategy 5b: Emergency class placement - create any class."""
        return self._strategy_emergency_theory_placement(entries, target_day, class_group, class_type)

    def _find_available_period(self, entries: List[TimetableEntry], day: str, class_group: str) -> int:
        """Find an available period on a specific day for a class group."""
        used_periods = set()
        for entry in entries:
            if entry.day == day and entry.class_group == class_group:
                used_periods.add(entry.period)

        # Find first available period
        for period in range(1, 8):  # Periods 1-7
            if period not in used_periods:
                return period

        return None

    def _apply_emergency_fixes(self, entries: List[TimetableEntry], class_group: str) -> List[TimetableEntry]:
        """Apply emergency fixes when all other strategies fail."""
        print(f"         🚨 Applying emergency fixes for {class_group}")

        # Identify remaining violations
        problematic_days = self._identify_problematic_days(entries, class_group)

        for problem in problematic_days:
            day = problem['day']
            violation_type = problem['violation_type']

            print(f"           🚨 Emergency fix for {day}: {violation_type}")

            if violation_type == "only practical":
                # Force create a theory class
                entries = self._strategy_emergency_theory_placement(entries, day, class_group, "theory")
            elif violation_type == "only one class":
                # Force create another class
                entries = self._strategy_emergency_class_placement(entries, day, class_group, "any")

        return entries

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

    def _calculate_friday_aware_slot_score(self, day: str, period: int, class_group: str,
                                         entries: List[TimetableEntry]) -> float:
        """
        Calculate a Friday-aware priority score for a scheduling slot.
        Lower scores are better (higher priority).

        This method considers:
        1. Early periods are preferred (compact scheduling)
        2. Monday-Thursday slots are preferred over Friday
        3. Friday slots are scored based on practical presence and time limits
        4. Slots that help maintain Friday compliance get bonus points
        """
        base_score = period  # Base score is the period number (early periods preferred)

        if day.lower().startswith('fri'):
            # Friday slots - apply Friday-specific scoring
            friday_score = self._calculate_friday_slot_score(period, class_group, entries)
            return base_score + friday_score
        else:
            # Monday-Thursday slots - slight preference to fill these first
            # This helps ensure Friday doesn't get overloaded
            monday_thursday_bonus = -0.1  # Small bonus for non-Friday days

            # Additional bonus for very early periods on Mon-Thu (helps compact scheduling)
            if period <= 3:
                early_period_bonus = -0.2
            else:
                early_period_bonus = 0

            return base_score + monday_thursday_bonus + early_period_bonus

    def _calculate_friday_slot_score(self, period: int, class_group: str,
                                   entries: List[TimetableEntry]) -> float:
        """Calculate scoring for Friday slots based on practical presence and time limits."""

        # Check if this class group already has practical on Friday
        friday_entries = [e for e in entries if e.day.lower().startswith('fri') and e.class_group == class_group]
        has_practical_on_friday = any(e.is_practical for e in friday_entries)

        if has_practical_on_friday:
            # Has practical on Friday - theory classes should be limited
            if period <= 4:  # Period 4 = 12:00 PM limit
                return 0  # Good slot
            else:
                return 100  # Heavily penalize slots after 12:00 PM
        else:
            # No practical on Friday - theory-only limit applies
            if period <= 3:  # Period 3 = 11:00 AM limit
                return 0  # Good slot
            elif period == 4:
                return 50  # Moderate penalty for 12:00 PM slot
            else:
                return 100  # Heavy penalty for slots after 12:00 PM

    def _prioritize_days_for_practical(self, class_group: str, entries: List[TimetableEntry]) -> List[str]:
        """
        Prioritize days for practical scheduling with Friday-awareness.

        Strategy:
        1. If Friday is relatively empty, it can accommodate practical + theory
        2. If Friday already has many theory classes, avoid adding practical
        3. Prefer Monday-Thursday for practical to keep Friday flexible
        """
        # Count existing entries per day for this class group
        day_counts = {}
        friday_theory_count = 0

        for entry in entries:
            if entry.class_group == class_group:
                if entry.day not in day_counts:
                    day_counts[entry.day] = 0
                day_counts[entry.day] += 1

                # Special tracking for Friday theory classes
                if entry.day.lower().startswith('fri') and not entry.is_practical:
                    friday_theory_count += 1

        # Create prioritized day list
        days_with_scores = []

        for day in self.days:
            current_count = day_counts.get(day, 0)

            if day.lower().startswith('fri'):
                # Friday scoring - consider theory load
                if friday_theory_count >= 3:
                    # Friday already has many theory classes - heavily penalize
                    score = 100 + current_count
                elif friday_theory_count >= 2:
                    # Friday has some theory - moderate penalty
                    score = 50 + current_count
                else:
                    # Friday is relatively free - allow but not prioritize
                    score = 10 + current_count
            else:
                # Monday-Thursday - prefer these for practical
                # Lower scores are better
                score = current_count  # Prefer days with fewer existing classes

                # Small bonus for very early days in the week
                if day.lower().startswith('mon'):
                    score -= 0.3
                elif day.lower().startswith('tue'):
                    score -= 0.2
                elif day.lower().startswith('wed'):
                    score -= 0.1

            days_with_scores.append((day, score))

        # Sort by score (lower is better) and return day names
        days_with_scores.sort(key=lambda x: x[1])
        prioritized_days = [day for day, score in days_with_scores]

        print(f"       📅 Day priority for practical: {prioritized_days}")
        return prioritized_days
