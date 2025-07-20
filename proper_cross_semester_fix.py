#!/usr/bin/env python
"""
PROPER CROSS-SEMESTER CONFLICT RESOLUTION - NO MORE LIES
Fixes the algorithm to actually work with all teachers and prevent conflicts
"""

import os
import sys
import django
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, ScheduleConfig, Subject, Teacher, Classroom
from timetable.algorithms.advanced_scheduler import AdvancedTimetableScheduler

class ProperCrossSemesterFix:
    """Actually fix the cross-semester issues properly"""
    
    def __init__(self):
        self.global_teacher_schedule = defaultdict(dict)  # teacher_id -> {(day, period): entry}
        self.global_classroom_schedule = defaultdict(dict)  # classroom_id -> {(day, period): entry}
        self.teacher_workloads = defaultdict(int)  # teacher_id -> total_periods
        
    def fix_and_regenerate_all(self):
        """Fix algorithm and regenerate all timetables properly"""
        print("🔧 PROPER CROSS-SEMESTER FIX - NO MORE LIES")
        print("=" * 60)
        
        # Step 1: Clear everything and start fresh
        print("\n1️⃣  CLEARING ALL EXISTING TIMETABLES...")
        initial_count = TimetableEntry.objects.count()
        TimetableEntry.objects.all().delete()
        print(f"✅ Cleared {initial_count} entries")
        
        # Step 2: Get all configurations
        configs = list(ScheduleConfig.objects.filter(start_time__isnull=False).order_by('name'))
        print(f"\n2️⃣  FOUND {len(configs)} CONFIGURATIONS TO PROCESS")
        
        # Step 3: Generate timetables one by one with proper conflict prevention
        successful = 0
        total_entries = 0
        
        for i, config in enumerate(configs, 1):
            print(f"\n📅 [{i}/{len(configs)}] Processing: {config.name}")
            
            # Generate timetable with current global state
            entries = self._generate_conflict_free_timetable(config)
            
            if entries:
                # Save to database
                saved_count = self._save_entries_to_db(entries, config)
                if saved_count > 0:
                    successful += 1
                    total_entries += saved_count
                    print(f"   ✅ Generated {saved_count} entries")
                    
                    # Update global schedules
                    self._update_global_schedules(entries)
                else:
                    print(f"   ❌ Failed to save entries")
            else:
                print(f"   ❌ Failed to generate timetable")
        
        # Step 4: Final analysis
        print(f"\n3️⃣  FINAL ANALYSIS...")
        self._analyze_final_results(successful, len(configs), total_entries)
        
        return successful == len(configs)
    
    def _generate_conflict_free_timetable(self, config):
        """Generate timetable that respects global conflicts"""
        print(f"   🧬 Generating with cross-semester awareness...")
        
        # Get all subjects for this config
        subjects_needed = []
        for class_group in config.class_groups:
            for subject_code in class_group.get('subjects', []):
                subject = Subject.objects.filter(code=subject_code).first()
                if subject:
                    subjects_needed.append((subject, class_group['name']))
        
        if not subjects_needed:
            print(f"   ⚠️  No subjects found for this config")
            return []
        
        entries = []
        max_attempts = 1000
        
        for subject, class_group in subjects_needed:
            # Try to schedule this subject
            scheduled = False
            attempts = 0
            
            while not scheduled and attempts < max_attempts:
                # Find available slot
                day = self._get_random_day()
                period = self._get_random_period()
                
                # Find teacher with proper conflict checking
                teacher = self._find_truly_available_teacher(subject, day, period)
                if not teacher:
                    attempts += 1
                    continue
                
                # Find classroom
                classroom = self._find_truly_available_classroom(day, period)
                if not classroom:
                    attempts += 1
                    continue
                
                # Create entry
                entry = self._create_timetable_entry(
                    day, period, subject, teacher, classroom, class_group, config
                )
                
                entries.append(entry)
                scheduled = True
                
                # Update temporary schedules for this generation
                self._update_temp_schedules(entry)
                
                attempts += 1
            
            if not scheduled:
                print(f"   ⚠️  Could not schedule {subject.name}")
        
        return entries
    
    def _find_truly_available_teacher(self, subject, day, period):
        """Find teacher that is truly available (no lies this time)"""
        # Get all teachers who can teach this subject
        qualified_teachers = list(Teacher.objects.filter(subjects=subject))
        
        if not qualified_teachers:
            return None
        
        # Sort by current workload (load balancing)
        qualified_teachers.sort(key=lambda t: self.teacher_workloads[t.id])
        
        # Find first available teacher
        for teacher in qualified_teachers:
            # Check global schedule (cross-semester conflicts)
            if (day, period) in self.global_teacher_schedule[teacher.id]:
                continue  # Teacher busy in another batch
            
            # Check temporary schedule (current generation)
            temp_key = f"temp_{teacher.id}_{day}_{period}"
            if hasattr(self, 'temp_teacher_schedule') and temp_key in self.temp_teacher_schedule:
                continue  # Teacher busy in current generation
            
            # Teacher is available!
            return teacher
        
        return None
    
    def _find_truly_available_classroom(self, day, period):
        """Find classroom that is truly available"""
        classrooms = list(Classroom.objects.all())
        
        for classroom in classrooms:
            # Check global schedule
            if (day, period) in self.global_classroom_schedule[classroom.id]:
                continue
            
            # Check temporary schedule
            temp_key = f"temp_{classroom.id}_{day}_{period}"
            if hasattr(self, 'temp_classroom_schedule') and temp_key in self.temp_classroom_schedule:
                continue
            
            return classroom
        
        return None
    
    def _create_timetable_entry(self, day, period, subject, teacher, classroom, class_group, config):
        """Create a timetable entry"""
        # Calculate time slot
        start_hour = 8 + (period - 1)  # Assuming 8 AM start
        start_time = f"{start_hour:02d}:00:00"
        end_time = f"{start_hour + 1:02d}:00:00"
        
        return TimetableEntry(
            day=day,
            period=period,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            class_group=class_group,
            start_time=start_time,
            end_time=end_time,
            is_practical=False,
            schedule_config=config,
            semester=config.semester,
            academic_year=config.academic_year
        )
    
    def _update_temp_schedules(self, entry):
        """Update temporary schedules during generation"""
        if not hasattr(self, 'temp_teacher_schedule'):
            self.temp_teacher_schedule = set()
        if not hasattr(self, 'temp_classroom_schedule'):
            self.temp_classroom_schedule = set()
        
        teacher_key = f"temp_{entry.teacher.id}_{entry.day}_{entry.period}"
        classroom_key = f"temp_{entry.classroom.id}_{entry.day}_{entry.period}"
        
        self.temp_teacher_schedule.add(teacher_key)
        self.temp_classroom_schedule.add(classroom_key)
    
    def _update_global_schedules(self, entries):
        """Update global schedules after successful generation"""
        for entry in entries:
            # Update global teacher schedule
            self.global_teacher_schedule[entry.teacher.id][(entry.day, entry.period)] = entry
            
            # Update global classroom schedule
            self.global_classroom_schedule[entry.classroom.id][(entry.day, entry.period)] = entry
            
            # Update teacher workload
            self.teacher_workloads[entry.teacher.id] += 1
        
        # Clear temporary schedules
        if hasattr(self, 'temp_teacher_schedule'):
            self.temp_teacher_schedule.clear()
        if hasattr(self, 'temp_classroom_schedule'):
            self.temp_classroom_schedule.clear()
    
    def _save_entries_to_db(self, entries, config):
        """Save entries to database"""
        try:
            TimetableEntry.objects.bulk_create(entries)
            return len(entries)
        except Exception as e:
            print(f"   ❌ Save error: {e}")
            return 0
    
    def _get_random_day(self):
        """Get random day"""
        import random
        return random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    
    def _get_random_period(self):
        """Get random period"""
        import random
        return random.randint(1, 7)
    
    def _analyze_final_results(self, successful, total, total_entries):
        """Analyze final results"""
        print(f"\n📊 FINAL RESULTS:")
        print(f"   Successful generations: {successful}/{total}")
        print(f"   Total entries created: {total_entries}")
        
        # Check teacher distribution
        teacher_usage = defaultdict(int)
        unique_teachers = set()
        
        for entry in TimetableEntry.objects.select_related('teacher'):
            if entry.teacher:
                teacher_usage[entry.teacher.name] += 1
                unique_teachers.add(entry.teacher.name)
        
        print(f"   Unique teachers used: {len(unique_teachers)}")
        print(f"   Teacher distribution:")
        
        sorted_usage = sorted(teacher_usage.items(), key=lambda x: x[1], reverse=True)
        for teacher, count in sorted_usage[:10]:
            print(f"     {teacher}: {count} periods")
        
        # Check for conflicts
        conflicts = self._detect_final_conflicts()
        print(f"   Cross-semester conflicts: {conflicts}")
        
        # Final verdict
        if successful == total and conflicts == 0 and len(unique_teachers) > 10:
            print(f"\n🎉 SUCCESS: PROPERLY FIXED!")
            print(f"   ✅ All batches generated")
            print(f"   ✅ No cross-semester conflicts")
            print(f"   ✅ Good teacher distribution")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS:")
            if successful < total:
                print(f"   ❌ {total - successful} batches failed")
            if conflicts > 0:
                print(f"   ❌ {conflicts} conflicts remain")
            if len(unique_teachers) <= 10:
                print(f"   ❌ Poor teacher distribution ({len(unique_teachers)} teachers)")
    
    def _detect_final_conflicts(self):
        """Detect final conflicts"""
        conflicts = 0
        teacher_schedule = defaultdict(dict)
        
        for entry in TimetableEntry.objects.select_related('teacher'):
            if entry.teacher:
                teacher_id = entry.teacher.id
                time_key = (entry.day, entry.period)
                
                if time_key in teacher_schedule[teacher_id]:
                    conflicts += 1
                else:
                    teacher_schedule[teacher_id][time_key] = entry
        
        return conflicts

def main():
    """Main execution"""
    fixer = ProperCrossSemesterFix()
    success = fixer.fix_and_regenerate_all()
    
    if success:
        print("\n🎯 SYSTEM IS NOW PROPERLY FIXED!")
    else:
        print("\n❌ SYSTEM STILL HAS ISSUES")

if __name__ == "__main__":
    main()
