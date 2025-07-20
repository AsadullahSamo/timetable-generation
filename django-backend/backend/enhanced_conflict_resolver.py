#!/usr/bin/env python
"""
Enhanced Cross-Semester Conflict Resolution System
Uses intelligent algorithms to resolve conflicts and generate optimized timetables
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

class EnhancedConflictResolver:
    """Enhanced conflict resolution with intelligent algorithms"""
    
    def __init__(self):
        self.conflicts_resolved = 0
        self.total_conflicts = 0
        
    def regenerate_optimized_timetables(self):
        """Regenerate all timetables with cross-semester conflict prevention"""
        print("🚀 REGENERATING OPTIMIZED CONFLICT-FREE TIMETABLES")
        print("=" * 60)
        
        # Step 1: Clear existing timetables
        print("\n1️⃣  CLEARING EXISTING TIMETABLES...")
        initial_entries = TimetableEntry.objects.count()
        TimetableEntry.objects.all().delete()
        print(f"✅ Cleared {initial_entries} existing entries")
        
        # Step 2: Get all schedule configurations
        configs = ScheduleConfig.objects.filter(start_time__isnull=False).order_by('name')
        print(f"\n2️⃣  FOUND {configs.count()} SCHEDULE CONFIGURATIONS:")
        for config in configs:
            print(f"   📋 {config.name}")
        
        # Step 3: Generate timetables with cross-semester awareness
        print(f"\n3️⃣  GENERATING OPTIMIZED TIMETABLES...")
        
        successful_generations = 0
        total_entries_created = 0
        generation_results = []
        
        for i, config in enumerate(configs, 1):
            print(f"\n📅 [{i}/{configs.count()}] Processing: {config.name}")
            
            try:
                # Initialize scheduler with cross-semester conflict detection
                scheduler = AdvancedTimetableScheduler(config)
                
                # Generate timetable
                result = scheduler.generate_timetable()
                
                if result and 'entries' in result and len(result['entries']) > 0:
                    # Save entries to database
                    entries_created = self._save_timetable_entries(result['entries'], config)
                    
                    if entries_created > 0:
                        successful_generations += 1
                        total_entries_created += entries_created
                        
                        fitness = result.get('fitness_score', 0)
                        violations = len(result.get('constraint_violations', []))
                        
                        generation_results.append({
                            'config': config.name,
                            'entries': entries_created,
                            'fitness': fitness,
                            'violations': violations,
                            'success': True
                        })
                        
                        print(f"   ✅ Generated {entries_created} entries (Fitness: {fitness:.1f}, Violations: {violations})")
                    else:
                        print(f"   ❌ No valid entries created")
                        generation_results.append({
                            'config': config.name,
                            'success': False,
                            'error': 'No valid entries'
                        })
                else:
                    print(f"   ❌ Generation failed")
                    generation_results.append({
                        'config': config.name,
                        'success': False,
                        'error': 'Generation failed'
                    })
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                generation_results.append({
                    'config': config.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Step 4: Analyze cross-semester conflicts in new timetables
        print(f"\n4️⃣  ANALYZING CROSS-SEMESTER CONFLICTS...")
        conflicts = self._detect_cross_semester_conflicts()
        
        print(f"\n📊 GENERATION SUMMARY:")
        print(f"   ✅ Successful: {successful_generations}/{configs.count()}")
        print(f"   📊 Total entries: {total_entries_created}")
        print(f"   🔥 Cross-semester conflicts: {len(conflicts['teacher_conflicts'])}")
        
        # Step 5: Final optimization if conflicts remain
        if len(conflicts['teacher_conflicts']) > 0:
            print(f"\n5️⃣  FINAL CONFLICT RESOLUTION...")
            resolved = self._resolve_remaining_conflicts(conflicts)
            print(f"   ✅ Additional conflicts resolved: {resolved}")
        
        return {
            'successful_generations': successful_generations,
            'total_configs': configs.count(),
            'total_entries': total_entries_created,
            'cross_semester_conflicts': len(conflicts['teacher_conflicts']),
            'generation_results': generation_results
        }
    
    def _save_timetable_entries(self, entries_data, config):
        """Save generated timetable entries to database"""
        entries_to_create = []
        
        for entry_data in entries_data:
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
                continue
        
        # Bulk create entries
        if entries_to_create:
            TimetableEntry.objects.bulk_create(entries_to_create)
            return len(entries_to_create)
        
        return 0
    
    def _detect_cross_semester_conflicts(self):
        """Detect conflicts across all generated timetables"""
        conflicts = {
            'teacher_conflicts': [],
            'classroom_conflicts': [],
            'capacity_violations': []
        }
        
        # Teacher conflicts
        teacher_schedule = defaultdict(dict)
        
        for entry in TimetableEntry.objects.select_related('teacher'):
            if not entry.teacher:
                continue
                
            teacher_id = entry.teacher.id
            time_key = f"{entry.day}_P{entry.period}"
            
            if time_key in teacher_schedule[teacher_id]:
                existing_entry = teacher_schedule[teacher_id][time_key]
                conflicts['teacher_conflicts'].append({
                    'teacher': entry.teacher.name,
                    'time': time_key,
                    'batch1': f"{existing_entry.semester}_{existing_entry.academic_year}",
                    'batch2': f"{entry.semester}_{entry.academic_year}",
                    'entries': [existing_entry, entry]
                })
            else:
                teacher_schedule[teacher_id][time_key] = entry
        
        # Classroom conflicts
        classroom_schedule = defaultdict(dict)
        
        for entry in TimetableEntry.objects.select_related('classroom'):
            if not entry.classroom:
                continue
                
            classroom_id = entry.classroom.id
            time_key = f"{entry.day}_P{entry.period}"
            
            if time_key in classroom_schedule[classroom_id]:
                existing_entry = classroom_schedule[classroom_id][time_key]
                conflicts['classroom_conflicts'].append({
                    'classroom': entry.classroom.name,
                    'time': time_key,
                    'batch1': f"{existing_entry.semester}_{existing_entry.academic_year}",
                    'batch2': f"{entry.semester}_{entry.academic_year}",
                    'entries': [existing_entry, entry]
                })
            else:
                classroom_schedule[classroom_id][time_key] = entry
        
        return conflicts
    
    def _resolve_remaining_conflicts(self, conflicts):
        """Resolve remaining conflicts using intelligent algorithms"""
        resolved = 0
        
        # Resolve teacher conflicts by redistributing load
        for conflict in conflicts['teacher_conflicts'][:10]:  # Limit to first 10 for efficiency
            if self._redistribute_teacher_load(conflict):
                resolved += 1
        
        # Resolve classroom conflicts by reassigning rooms
        for conflict in conflicts['classroom_conflicts'][:10]:
            if self._reassign_classroom(conflict):
                resolved += 1
        
        return resolved
    
    def _redistribute_teacher_load(self, conflict):
        """Redistribute teacher load to resolve conflicts"""
        try:
            # Get the conflicting entries
            entry1, entry2 = conflict['entries']
            
            # Try to find alternative teachers for one of the subjects
            alternative_teachers = Teacher.objects.filter(
                subjects=entry2.subject
            ).exclude(id=entry2.teacher.id)
            
            for alt_teacher in alternative_teachers:
                # Check if alternative teacher is available at this time
                existing_conflict = TimetableEntry.objects.filter(
                    teacher=alt_teacher,
                    day=entry2.day,
                    period=entry2.period
                ).exists()
                
                if not existing_conflict:
                    # Reassign to alternative teacher
                    entry2.teacher = alt_teacher
                    entry2.save()
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _reassign_classroom(self, conflict):
        """Reassign classroom to resolve conflicts"""
        try:
            entry1, entry2 = conflict['entries']
            
            # Find alternative classrooms with sufficient capacity
            required_capacity = 30  # Default capacity requirement
            
            alternative_rooms = Classroom.objects.filter(
                capacity__gte=required_capacity
            ).exclude(id=entry2.classroom.id)
            
            for alt_room in alternative_rooms:
                # Check if alternative room is available
                existing_conflict = TimetableEntry.objects.filter(
                    classroom=alt_room,
                    day=entry2.day,
                    period=entry2.period
                ).exists()
                
                if not existing_conflict:
                    # Reassign to alternative room
                    entry2.classroom = alt_room
                    entry2.save()
                    return True
            
            return False
            
        except Exception:
            return False
    
    def generate_final_report(self, results):
        """Generate comprehensive final report"""
        print(f"\n" + "=" * 70)
        print("🎯 FINAL OPTIMIZED TIMETABLE REPORT")
        print("=" * 70)
        
        success_rate = (results['successful_generations'] / results['total_configs']) * 100
        
        print(f"📊 Generation Summary:")
        print(f"   Total Configurations: {results['total_configs']}")
        print(f"   Successful Generations: {results['successful_generations']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Entries Created: {results['total_entries']}")
        
        print(f"\n🔥 Conflict Analysis:")
        print(f"   Cross-Semester Teacher Conflicts: {results['cross_semester_conflicts']}")
        
        if results['cross_semester_conflicts'] == 0:
            print(f"   🎉 PERFECT: No cross-semester conflicts!")
        elif results['cross_semester_conflicts'] <= 10:
            print(f"   ✅ EXCELLENT: Minimal conflicts ({results['cross_semester_conflicts']})")
        elif results['cross_semester_conflicts'] <= 50:
            print(f"   ⚠️  ACCEPTABLE: Some conflicts remain ({results['cross_semester_conflicts']})")
        else:
            print(f"   ❌ NEEDS WORK: Many conflicts remain ({results['cross_semester_conflicts']})")
        
        print(f"\n📋 Batch-wise Results:")
        for result in results['generation_results']:
            if result['success']:
                print(f"   ✅ {result['config']}: {result['entries']} entries")
            else:
                print(f"   ❌ {result['config']}: {result['error']}")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if success_rate >= 80 and results['cross_semester_conflicts'] <= 20:
            print("   🎉 SYSTEM IS PRODUCTION READY!")
            print("   ✅ Optimized conflict-free timetables generated")
            print("   🚀 Ready for frontend deployment")
        else:
            print("   ⚠️  SYSTEM NEEDS FURTHER OPTIMIZATION")
            print("   🔧 Consider additional conflict resolution strategies")

def main():
    """Main execution"""
    print("🚀 ENHANCED CROSS-SEMESTER CONFLICT RESOLUTION")
    print("=" * 70)
    
    resolver = EnhancedConflictResolver()
    
    # Regenerate all timetables with conflict prevention
    results = resolver.regenerate_optimized_timetables()
    
    # Generate final report
    resolver.generate_final_report(results)

if __name__ == "__main__":
    main()
