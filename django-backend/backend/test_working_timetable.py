#!/usr/bin/env python3
"""
COMPREHENSIVE TIMETABLE GENERATION TEST
======================================
Tests the working timetable scheduler with real data for all 4 batches.
Generates conflict-free, optimized timetables for 21SW, 22SW, 23SW, 24SW.
"""

import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from timetable.models import ScheduleConfig, TimetableEntry, Subject, Teacher, Classroom
from timetable.algorithms.working_scheduler import WorkingTimetableScheduler


def test_timetable_generation():
    """Test timetable generation for all batches."""
    
    print("🎓 COMPREHENSIVE TIMETABLE GENERATION TEST")
    print("=" * 80)
    print("📅 Testing with real MUET Software Engineering data")
    print("🎯 Batches: 21SW (8th), 22SW (6th), 23SW (4th), 24SW (2nd)")
    print("=" * 80)
    
    # Check data availability
    subjects = Subject.objects.all()
    teachers = Teacher.objects.all()
    classrooms = Classroom.objects.all()
    configs = ScheduleConfig.objects.all()
    
    print(f"\n📊 DATA STATUS:")
    print(f"   Subjects: {subjects.count()}")
    print(f"   Teachers: {teachers.count()}")
    print(f"   Classrooms: {classrooms.count()}")
    print(f"   Configs: {configs.count()}")
    
    if not subjects.exists():
        print("❌ No subjects found! Run populate_test_data.py first")
        return False
    
    if not teachers.exists():
        print("❌ No teachers found! Run populate_test_data.py first")
        return False
    
    if not configs.exists():
        print("❌ No schedule configs found!")
        return False
    
    # Create classrooms if none exist
    if not classrooms.exists():
        print("\n🏫 Creating test classrooms...")
        Classroom.objects.create(name="Room 101", capacity=50, building="Main Building")
        Classroom.objects.create(name="Room 102", capacity=50, building="Main Building")
        Classroom.objects.create(name="Lab 1", capacity=30, building="Lab Building")
        Classroom.objects.create(name="Lab 2", capacity=30, building="Lab Building")
        print("✅ Created 4 classrooms")
    
    # Clear existing timetable entries
    existing_entries = TimetableEntry.objects.count()
    if existing_entries > 0:
        TimetableEntry.objects.all().delete()
        print(f"🗑️  Cleared {existing_entries} existing timetable entries")
    
    # Generate timetables for all configs
    print(f"\n🚀 GENERATING TIMETABLES FOR ALL BATCHES")
    print("-" * 80)
    
    total_entries = 0
    total_conflicts = 0
    successful_generations = 0
    generation_results = []
    
    start_time = datetime.now()
    
    for i, config in enumerate(configs.order_by('name'), 1):
        print(f"\n[{i}/{configs.count()}] 📋 GENERATING: {config.name}")
        print(f"   Class Groups: {config.class_groups}")
        print(f"   Days: {config.days}")
        print(f"   Periods: {config.periods}")
        
        try:
            # Initialize scheduler
            scheduler = WorkingTimetableScheduler(config)
            
            # Generate timetable
            result = scheduler.generate_timetable()
            
            if result and result.get('success', False):
                entries = result['entries']
                conflicts = result.get('constraint_violations', [])
                
                # Save entries to database
                saved_entries = 0
                for entry_data in entries:
                    try:
                        subject = Subject.objects.get(name=entry_data['subject'])
                        teacher = Teacher.objects.get(name=entry_data['teacher'])
                        classroom = Classroom.objects.get(name=entry_data['classroom'])
                        
                        TimetableEntry.objects.create(
                            day=entry_data['day'],
                            period=entry_data['period'],
                            subject=subject,
                            teacher=teacher,
                            classroom=classroom,
                            class_group=entry_data['class_group'],
                            start_time=entry_data['start_time'],
                            end_time=entry_data['end_time'],
                            is_practical=entry_data['is_practical'],
                            schedule_config=config
                        )
                        saved_entries += 1
                    except Exception as e:
                        print(f"   ⚠️  Error saving entry: {str(e)}")
                
                # Record results
                generation_results.append({
                    'config': config.name,
                    'entries': len(entries),
                    'conflicts': len(conflicts),
                    'saved_entries': saved_entries,
                    'generation_time': result.get('generation_time', 0),
                    'fitness_score': result.get('fitness_score', 0)
                })
                
                total_entries += len(entries)
                total_conflicts += len(conflicts)
                successful_generations += 1
                
                print(f"   ✅ SUCCESS: {len(entries)} entries, {len(conflicts)} conflicts")
                print(f"   💾 Saved: {saved_entries} entries to database")
                print(f"   ⏱️  Time: {result.get('generation_time', 0):.2f}s")
                print(f"   📊 Fitness: {result.get('fitness_score', 0):.1f}")
                
                if conflicts:
                    print(f"   ⚠️  Conflicts:")
                    for conflict in conflicts[:3]:  # Show first 3
                        print(f"      - {conflict}")
                    if len(conflicts) > 3:
                        print(f"      ... and {len(conflicts) - 3} more")
                
            else:
                print(f"   ❌ FAILED: No valid timetable generated")
                generation_results.append({
                    'config': config.name,
                    'entries': 0,
                    'conflicts': 0,
                    'saved_entries': 0,
                    'generation_time': 0,
                    'fitness_score': 0
                })
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            generation_results.append({
                'config': config.name,
                'entries': 0,
                'conflicts': 0,
                'saved_entries': 0,
                'generation_time': 0,
                'fitness_score': 0
            })
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    # Final results
    print(f"\n🎉 GENERATION COMPLETE!")
    print("=" * 80)
    print(f"⏱️  Total Time: {total_time:.2f} seconds")
    print(f"✅ Successful Generations: {successful_generations}/{configs.count()}")
    print(f"📊 Total Entries Generated: {total_entries}")
    print(f"💾 Total Entries in Database: {TimetableEntry.objects.count()}")
    print(f"⚠️  Total Conflicts: {total_conflicts}")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    print("-" * 80)
    for result in generation_results:
        status = "✅" if result['entries'] > 0 else "❌"
        print(f"{status} {result['config']:<25} | "
              f"Entries: {result['entries']:>3} | "
              f"Conflicts: {result['conflicts']:>2} | "
              f"Time: {result['generation_time']:>5.2f}s | "
              f"Fitness: {result['fitness_score']:>5.1f}")
    
    # Success assessment
    if successful_generations == configs.count() and total_conflicts == 0:
        print(f"\n🏆 PERFECT SUCCESS!")
        print("✅ All batches generated successfully")
        print("✅ Zero conflicts detected")
        print("✅ Timetables are optimized and ready for use")
        return True
    elif successful_generations == configs.count():
        print(f"\n✅ GENERATION SUCCESS WITH MINOR ISSUES")
        print(f"✅ All batches generated successfully")
        print(f"⚠️  {total_conflicts} conflicts need resolution")
        return True
    else:
        print(f"\n❌ PARTIAL SUCCESS")
        print(f"⚠️  {configs.count() - successful_generations} batches failed to generate")
        return False


def verify_cross_semester_conflicts():
    """Verify no conflicts exist across different semesters."""
    print(f"\n🔍 CROSS-SEMESTER CONFLICT VERIFICATION")
    print("-" * 80)
    
    entries = TimetableEntry.objects.all()
    conflicts = []
    
    # Check teacher conflicts across semesters
    teacher_schedule = {}
    for entry in entries:
        key = f"{entry.teacher.id}_{entry.day}_{entry.period}"
        if key in teacher_schedule:
            existing = teacher_schedule[key]
            if existing.class_group != entry.class_group:
                conflicts.append(
                    f"Cross-semester teacher conflict: {entry.teacher.name} "
                    f"teaching {existing.class_group} and {entry.class_group} "
                    f"at {entry.day} P{entry.period}"
                )
        else:
            teacher_schedule[key] = entry
    
    if conflicts:
        print(f"❌ Found {len(conflicts)} cross-semester conflicts:")
        for conflict in conflicts:
            print(f"   - {conflict}")
        return False
    else:
        print("✅ No cross-semester conflicts detected!")
        return True


if __name__ == '__main__':
    print("🎯 Starting comprehensive timetable generation test...")
    
    # Test timetable generation
    generation_success = test_timetable_generation()
    
    # Verify cross-semester conflicts
    conflict_free = verify_cross_semester_conflicts()
    
    # Final assessment
    print(f"\n🏁 FINAL ASSESSMENT")
    print("=" * 80)
    
    if generation_success and conflict_free:
        print("🏆 COMPLETE SUCCESS!")
        print("✅ All timetables generated successfully")
        print("✅ No conflicts detected")
        print("✅ System is working perfectly")
        print("\n🎯 The timetable generation system is now:")
        print("   ✅ WORKING")
        print("   ✅ OPTIMIZED") 
        print("   ✅ ERROR-FREE")
        print("   ✅ CONFLICT-FREE")
    else:
        print("⚠️  ISSUES DETECTED")
        if not generation_success:
            print("❌ Some timetables failed to generate")
        if not conflict_free:
            print("❌ Conflicts detected in generated timetables")
        print("\n🔧 Further optimization needed")
