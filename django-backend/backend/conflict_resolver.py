#!/usr/bin/env python
"""
Conflict Resolution System for MUET Timetables
Resolves cross-batch conflicts and provides optimized timetables
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

class ConflictResolver:
    """Resolves conflicts and optimizes timetables"""
    
    def __init__(self):
        self.conflicts = []
        self.resolutions = []
        
    def detect_all_conflicts(self):
        """Detect all types of conflicts"""
        print("🔍 DETECTING ALL CONFLICTS...")
        
        # Teacher conflicts
        teacher_conflicts = self._detect_teacher_conflicts()
        
        # Classroom conflicts  
        classroom_conflicts = self._detect_classroom_conflicts()
        
        # Capacity violations
        capacity_violations = self._detect_capacity_violations()
        
        total_conflicts = len(teacher_conflicts) + len(classroom_conflicts) + len(capacity_violations)
        
        print(f"📊 CONFLICTS FOUND:")
        print(f"  👨‍🏫 Teacher conflicts: {len(teacher_conflicts)}")
        print(f"  🏫 Classroom conflicts: {len(classroom_conflicts)}")
        print(f"  📏 Capacity violations: {len(capacity_violations)}")
        print(f"  🔥 TOTAL: {total_conflicts}")
        
        return {
            'teacher_conflicts': teacher_conflicts,
            'classroom_conflicts': classroom_conflicts,
            'capacity_violations': capacity_violations,
            'total': total_conflicts
        }
    
    def _detect_teacher_conflicts(self):
        """Detect teacher double-booking across batches"""
        conflicts = []
        teacher_schedule = defaultdict(dict)
        
        for entry in TimetableEntry.objects.select_related('teacher'):
            if not entry.teacher:
                continue
                
            teacher_id = entry.teacher.id
            time_key = f"{entry.day}_P{entry.period}"
            
            if time_key in teacher_schedule[teacher_id]:
                existing = teacher_schedule[teacher_id][time_key]
                conflicts.append({
                    'type': 'teacher_conflict',
                    'teacher': entry.teacher.name,
                    'time': time_key,
                    'batch1': f"{existing.semester}_{existing.academic_year}",
                    'batch2': f"{entry.semester}_{entry.academic_year}",
                    'subject1': existing.subject.name,
                    'subject2': entry.subject.name,
                    'entries': [existing, entry]
                })
            else:
                teacher_schedule[teacher_id][time_key] = entry
        
        return conflicts
    
    def _detect_classroom_conflicts(self):
        """Detect classroom double-booking"""
        conflicts = []
        room_schedule = defaultdict(dict)
        
        for entry in TimetableEntry.objects.select_related('classroom'):
            if not entry.classroom:
                continue
                
            room_id = entry.classroom.id
            time_key = f"{entry.day}_P{entry.period}"
            
            if time_key in room_schedule[room_id]:
                existing = room_schedule[room_id][time_key]
                conflicts.append({
                    'type': 'classroom_conflict',
                    'classroom': entry.classroom.name,
                    'time': time_key,
                    'batch1': f"{existing.semester}_{existing.academic_year}",
                    'batch2': f"{entry.semester}_{entry.academic_year}",
                    'entries': [existing, entry]
                })
            else:
                room_schedule[room_id][time_key] = entry
        
        return conflicts
    
    def _detect_capacity_violations(self):
        """Detect classroom capacity violations"""
        violations = []
        
        # Get class sizes from schedule configs
        class_sizes = {}
        for config in ScheduleConfig.objects.all():
            for class_group in config.class_groups:
                if isinstance(class_group, dict) and 'students' in class_group:
                    class_sizes[class_group['name']] = class_group['students']
        
        for entry in TimetableEntry.objects.select_related('classroom'):
            if entry.classroom and entry.class_group in class_sizes:
                class_size = class_sizes[entry.class_group]
                if entry.classroom.capacity < class_size:
                    violations.append({
                        'type': 'capacity_violation',
                        'classroom': entry.classroom.name,
                        'capacity': entry.classroom.capacity,
                        'class_size': class_size,
                        'class_group': entry.class_group,
                        'entry': entry
                    })
        
        return violations
    
    def resolve_conflicts(self, conflicts):
        """Resolve detected conflicts"""
        print(f"\n🔧 RESOLVING {conflicts['total']} CONFLICTS...")
        
        resolved = 0
        
        # Resolve teacher conflicts
        for conflict in conflicts['teacher_conflicts']:
            if self._resolve_teacher_conflict(conflict):
                resolved += 1
        
        # Resolve classroom conflicts
        for conflict in conflicts['classroom_conflicts']:
            if self._resolve_classroom_conflict(conflict):
                resolved += 1
        
        # Resolve capacity violations
        for violation in conflicts['capacity_violations']:
            if self._resolve_capacity_violation(violation):
                resolved += 1
        
        print(f"✅ RESOLVED: {resolved}/{conflicts['total']} conflicts")
        return resolved
    
    def _resolve_teacher_conflict(self, conflict):
        """Resolve teacher double-booking"""
        try:
            # Strategy: Move one entry to different time slot
            entry_to_move = conflict['entries'][1]  # Move the second entry
            
            # Find alternative time slot
            alternative_slot = self._find_alternative_slot(entry_to_move)
            
            if alternative_slot:
                entry_to_move.day = alternative_slot['day']
                entry_to_move.period = alternative_slot['period']
                entry_to_move.save()
                
                print(f"  ✅ Moved {conflict['teacher']} from {conflict['time']} to {alternative_slot['day']}_P{alternative_slot['period']}")
                return True
            else:
                print(f"  ❌ No alternative slot found for {conflict['teacher']}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error resolving teacher conflict: {e}")
            return False
    
    def _resolve_classroom_conflict(self, conflict):
        """Resolve classroom double-booking"""
        try:
            # Strategy: Assign different classroom
            entry_to_reassign = conflict['entries'][1]
            
            # Find alternative classroom
            alternative_room = self._find_alternative_classroom(entry_to_reassign)
            
            if alternative_room:
                entry_to_reassign.classroom = alternative_room
                entry_to_reassign.save()
                
                print(f"  ✅ Moved class from {conflict['classroom']} to {alternative_room.name}")
                return True
            else:
                print(f"  ❌ No alternative classroom found")
                return False
                
        except Exception as e:
            print(f"  ❌ Error resolving classroom conflict: {e}")
            return False
    
    def _resolve_capacity_violation(self, violation):
        """Resolve capacity violations"""
        try:
            # Strategy: Find larger classroom
            larger_room = Classroom.objects.filter(
                capacity__gte=violation['class_size']
            ).exclude(
                id=violation['entry'].classroom.id
            ).first()
            
            if larger_room:
                # Check if larger room is available
                time_key = f"{violation['entry'].day}_P{violation['entry'].period}"
                existing = TimetableEntry.objects.filter(
                    classroom=larger_room,
                    day=violation['entry'].day,
                    period=violation['entry'].period
                ).first()
                
                if not existing:
                    violation['entry'].classroom = larger_room
                    violation['entry'].save()
                    
                    print(f"  ✅ Moved to larger room: {larger_room.name} (cap: {larger_room.capacity})")
                    return True
            
            print(f"  ❌ No suitable larger classroom available")
            return False
            
        except Exception as e:
            print(f"  ❌ Error resolving capacity violation: {e}")
            return False
    
    def _find_alternative_slot(self, entry):
        """Find alternative time slot for entry"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        periods = range(1, 8)
        
        for day in days:
            for period in periods:
                # Check if teacher is available
                teacher_conflict = TimetableEntry.objects.filter(
                    teacher=entry.teacher,
                    day=day,
                    period=period
                ).exists()
                
                # Check if classroom is available
                room_conflict = TimetableEntry.objects.filter(
                    classroom=entry.classroom,
                    day=day,
                    period=period
                ).exists()
                
                if not teacher_conflict and not room_conflict:
                    return {'day': day, 'period': period}
        
        return None
    
    def _find_alternative_classroom(self, entry):
        """Find alternative classroom for entry"""
        # Get class size
        class_sizes = {}
        for config in ScheduleConfig.objects.all():
            for class_group in config.class_groups:
                if isinstance(class_group, dict) and 'students' in class_group:
                    class_sizes[class_group['name']] = class_group['students']
        
        required_capacity = class_sizes.get(entry.class_group, 30)
        
        # Find available classrooms with sufficient capacity
        available_rooms = Classroom.objects.filter(
            capacity__gte=required_capacity
        ).exclude(id=entry.classroom.id)
        
        for room in available_rooms:
            # Check if room is available at this time
            conflict = TimetableEntry.objects.filter(
                classroom=room,
                day=entry.day,
                period=entry.period
            ).exists()
            
            if not conflict:
                return room
        
        return None

def main():
    """Main execution"""
    print("🚀 MUET CONFLICT RESOLUTION SYSTEM")
    print("=" * 60)
    
    resolver = ConflictResolver()
    
    # Detect conflicts
    conflicts = resolver.detect_all_conflicts()
    
    if conflicts['total'] == 0:
        print("✅ NO CONFLICTS FOUND - TIMETABLES ARE OPTIMIZED!")
        return
    
    # Resolve conflicts
    resolved_count = resolver.resolve_conflicts(conflicts)
    
    # Final verification
    print(f"\n🔍 FINAL VERIFICATION...")
    final_conflicts = resolver.detect_all_conflicts()
    
    print(f"\n📊 RESOLUTION SUMMARY:")
    print(f"  Initial conflicts: {conflicts['total']}")
    print(f"  Resolved: {resolved_count}")
    print(f"  Remaining: {final_conflicts['total']}")
    
    if final_conflicts['total'] == 0:
        print("🎉 ALL CONFLICTS RESOLVED - TIMETABLES OPTIMIZED!")
    else:
        print(f"⚠️  {final_conflicts['total']} conflicts remain - may need manual intervention")

if __name__ == "__main__":
    main()
