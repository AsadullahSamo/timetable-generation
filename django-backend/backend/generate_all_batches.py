#!/usr/bin/env python
"""
Generate timetables for ALL MUET batches
"""

import os
import sys
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import TimetableEntry, ScheduleConfig, Subject, Teacher, Classroom
from timetable.algorithms.advanced_scheduler import AdvancedTimetableScheduler

def generate_all_muet_timetables():
    """Generate timetables for all MUET batches"""
    
    print("🚀 GENERATING TIMETABLES FOR ALL MUET BATCHES")
    print("=" * 60)
    
    # Get all schedule configurations
    configs = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('name')
    
    if not configs.exists():
        print("❌ No schedule configurations found!")
        return
    
    print(f"📋 Found {configs.count()} schedule configurations:")
    for config in configs:
        print(f"  - {config.name}")
    
    print("\n🔄 Starting timetable generation...")
    
    total_entries = 0
    successful_generations = 0
    failed_generations = 0
    
    for i, config in enumerate(configs, 1):
        print(f"\n📅 [{i}/{configs.count()}] Generating: {config.name}")
        
        try:
            # Initialize scheduler
            scheduler = AdvancedTimetableScheduler(config)
            
            # Generate timetable
            start_time = time.time()
            result = scheduler.generate_timetable()
            generation_time = time.time() - start_time
            
            if result and 'entries' in result:
                entries_count = len(result['entries'])
                
                # Save entries to database
                entries_to_create = []
                
                for entry_data in result['entries']:
                    try:
                        # Get subject
                        subject_name = entry_data['subject'].replace(' (PR)', '')
                        subject = Subject.objects.filter(name=subject_name).first()
                        if not subject:
                            continue
                        
                        # Get teacher
                        teacher = Teacher.objects.filter(name=entry_data['teacher']).first()
                        if not teacher:
                            continue
                        
                        # Get classroom
                        classroom = Classroom.objects.filter(name=entry_data['classroom']).first()
                        if not classroom:
                            continue
                        
                        # Create entry
                        entry = TimetableEntry(
                            day=entry_data['day'],
                            period=entry_data['period'],
                            subject=subject,
                            teacher=teacher,
                            classroom=classroom,
                            class_group=entry_data['class_group'],
                            start_time=entry_data['start_time'],
                            end_time=entry_data['end_time'],
                            is_practical='(PR)' in entry_data['subject'],
                            schedule_config=config,
                            semester=config.semester,
                            academic_year=config.academic_year
                        )
                        entries_to_create.append(entry)
                        
                    except Exception as e:
                        print(f"    ⚠️  Skipped entry: {e}")
                        continue
                
                # Bulk create entries
                if entries_to_create:
                    TimetableEntry.objects.bulk_create(entries_to_create)
                    created_count = len(entries_to_create)
                    total_entries += created_count
                    successful_generations += 1
                    
                    print(f"    ✅ Generated {created_count} entries in {generation_time:.2f}s")
                    print(f"    📊 Fitness: {result.get('fitness_score', 0):.1f}")
                    
                    violations = result.get('constraint_violations', [])
                    if violations:
                        print(f"    ⚠️  {len(violations)} constraint violations")
                else:
                    print(f"    ❌ No valid entries created")
                    failed_generations += 1
            else:
                print(f"    ❌ Generation failed")
                failed_generations += 1
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            failed_generations += 1
    
    print("\n" + "=" * 60)
    print("🎯 GENERATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {successful_generations}")
    print(f"❌ Failed: {failed_generations}")
    print(f"📊 Total entries created: {total_entries}")
    
    # Verify cross-batch data
    print(f"\n🔍 CROSS-BATCH VERIFICATION")
    print("-" * 40)
    
    # Check entries by batch
    from collections import defaultdict
    entries_by_batch = defaultdict(int)
    teachers_by_batch = defaultdict(set)
    
    for entry in TimetableEntry.objects.all():
        batch_key = f"{entry.semester}_{entry.academic_year}"
        entries_by_batch[batch_key] += 1
        if entry.teacher:
            teachers_by_batch[batch_key].add(entry.teacher.name)
    
    for batch, count in entries_by_batch.items():
        teacher_count = len(teachers_by_batch[batch])
        print(f"📅 {batch}: {count} entries, {teacher_count} teachers")
    
    # Check for cross-batch teachers
    all_teacher_batches = defaultdict(set)
    for entry in TimetableEntry.objects.all():
        if entry.teacher:
            batch_key = f"{entry.semester}_{entry.academic_year}"
            all_teacher_batches[entry.teacher.name].add(batch_key)
    
    multi_batch_teachers = {name: batches for name, batches in all_teacher_batches.items() if len(batches) > 1}
    
    print(f"\n👨‍🏫 Teachers in multiple batches: {len(multi_batch_teachers)}")
    for teacher, batches in list(multi_batch_teachers.items())[:5]:
        print(f"  - {teacher}: {len(batches)} batches")
    
    print(f"\n🎉 ALL MUET TIMETABLES GENERATED!")

if __name__ == "__main__":
    generate_all_muet_timetables()
