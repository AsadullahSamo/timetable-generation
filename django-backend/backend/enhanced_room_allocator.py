"""
ENHANCED ROOM ALLOCATION SYSTEM
===============================
Implements the client's specific room allocation requirements:
- 2nd year batches: Academic building rooms for theory, labs for practicals
- 1st, 3rd, 4th year batches: Main building rooms for theory, labs for practicals
- All practicals must be in labs with 3 consecutive blocks in same lab
- No room conflicts
- Consistent room assignment per section per day
"""

from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
from django.db.models import Q
from .models import Classroom, TimetableEntry, Batch, Subject


class EnhancedRoomAllocator:
    """
    Enhanced room allocation system implementing client's specific requirements.
    """
    
    def __init__(self):
        self.labs = []
        self.academic_building_rooms = []
        self.main_building_rooms = []
        self.all_rooms = []
        
        # Section-specific room assignments (for consistent daily assignment)
        self.section_room_assignments = {}  # {section: {day: room}}
        
        # Practical lab assignments (for same-lab rule)
        self.practical_lab_assignments = {}  # {(section, subject_code): lab}
        
        # Room usage tracking
        self.room_usage = defaultdict(lambda: defaultdict(set))  # {room_id: {day: set(periods)}}
        
        self._initialize_room_data()
    
    def _initialize_room_data(self):
        """Initialize room classification based on building and type."""
        all_rooms = list(Classroom.objects.all())
        
        # Classify rooms by building and type
        self.labs = [room for room in all_rooms if room.is_lab]
        self.academic_building_rooms = [room for room in all_rooms 
                                      if not room.is_lab and 'Academic' in room.building]
        self.main_building_rooms = [room for room in all_rooms 
                                  if not room.is_lab and 'Academic' not in room.building]
        self.all_rooms = all_rooms
        
        print(f"🏫 Enhanced Room Allocator Initialized:")
        print(f"   📍 Labs: {len(self.labs)} ({[lab.name for lab in self.labs]})")
        print(f"   📍 Academic Building Rooms: {len(self.academic_building_rooms)} ({[room.name for room in self.academic_building_rooms]})")
        print(f"   📍 Main Building Rooms: {len(self.main_building_rooms)} ({[room.name for room in self.main_building_rooms]})")
    
    def get_year_from_section(self, section: str) -> int:
        """Extract year from section (e.g., '21SW-I' -> 2021)."""
        try:
            # Extract batch name first
            batch_name = section.split('-')[0] if '-' in section else section
            year_digits = ''.join(filter(str.isdigit, batch_name))[:2]
            if year_digits:
                year = int(year_digits)
                return 2000 + year
        except:
            pass
        return 2021  # Default fallback
    
    def is_second_year_section(self, section: str) -> bool:
        """Check if section belongs to 2nd year (for academic building allocation)."""
        year = self.get_year_from_section(section)
        from datetime import datetime
        current_year = datetime.now().year
        
        # 2nd year students are those who started 2 years ago
        # For 2025: 2nd year = 23XX batches (started in 2023)
        return year == (current_year - 2)
    
    def get_preferred_rooms_for_section(self, section: str) -> List[Classroom]:
        """Get preferred rooms for theory classes based on section year."""
        if self.is_second_year_section(section):
            # 2nd year: Academic building rooms first, then main building
            return self.academic_building_rooms + self.main_building_rooms
        else:
            # 1st, 3rd, 4th year: Main building rooms first, then academic building
            return self.main_building_rooms + self.academic_building_rooms
    
    def get_available_rooms_for_time(self, day: str, period: int, duration: int = 1,
                                   entries: List[TimetableEntry] = None) -> List[Classroom]:
        """Get all rooms available for the specified time slot."""
        if entries is None:
            entries = []
        
        available_rooms = []
        
        for room in self.all_rooms:
            is_available = True
            
            # Check all periods for the duration
            for i in range(duration):
                check_period = period + i
                
                # Check if room is occupied during this period
                occupied = any(
                    entry.classroom and entry.classroom.id == room.id and
                    entry.day == day and entry.period == check_period
                    for entry in entries
                )
                
                if occupied:
                    is_available = False
                    break
            
            if is_available:
                available_rooms.append(room)
        
        return available_rooms
    
    def get_available_labs_for_time(self, day: str, period: int, duration: int = 1,
                                   entries: List[TimetableEntry] = None) -> List[Classroom]:
        """Get labs available for the specified time slot."""
        all_available = self.get_available_rooms_for_time(day, period, duration, entries)
        return [room for room in all_available if room.is_lab]
    
    def allocate_room_for_practical(self, day: str, start_period: int, section: str,
                                   subject: Subject, entries: List[TimetableEntry]) -> Optional[Classroom]:
        """
        Allocate lab for practical session (3 consecutive blocks).
        Enforces same-lab rule for practical subjects.
        """
        # Check if we already have a lab assigned for this section-subject combination
        assignment_key = (section, subject.code)
        if assignment_key in self.practical_lab_assignments:
            assigned_lab = self.practical_lab_assignments[assignment_key]
            
            # Check if the assigned lab is available for all 3 periods
            if self._is_lab_available_for_duration(assigned_lab, day, start_period, 3, entries):
                return assigned_lab
        
        # Find available labs for the 3-block duration
        available_labs = self.get_available_labs_for_time(day, start_period, 3, entries)
        
        if not available_labs:
            # Try to free up a lab by moving conflicting classes
            available_labs = self._force_lab_availability(day, start_period, 3, entries)
        
        if available_labs:
            # Select the best lab (prefer labs with lower usage)
            selected_lab = self._select_best_lab(available_labs, section)
            
            # Record the assignment for same-lab rule
            self.practical_lab_assignments[assignment_key] = selected_lab
            
            return selected_lab
        
        return None
    
    def allocate_room_for_theory(self, day: str, period: int, section: str,
                                subject: Subject, entries: List[TimetableEntry]) -> Optional[Classroom]:
        """
        Allocate room for theory class with section-specific preferences.
        Maintains consistent room assignment per section per day.
        """
        # Check if section already has a room assigned for this day
        if section in self.section_room_assignments and day in self.section_room_assignments[section]:
            assigned_room = self.section_room_assignments[section][day]
            
            # Check if the assigned room is available
            if self._is_room_available(assigned_room, day, period, entries):
                return assigned_room
        
        # Get preferred rooms for this section
        preferred_rooms = self.get_preferred_rooms_for_section(section)
        
        # Find available rooms from preferred list
        available_rooms = [room for room in preferred_rooms 
                          if self._is_room_available(room, day, period, entries)]
        
        if not available_rooms:
            # Try all rooms if preferred rooms are not available
            available_rooms = [room for room in self.all_rooms 
                             if not room.is_lab and self._is_room_available(room, day, period, entries)]
        
        if not available_rooms:
            # Try labs as last resort
            available_rooms = [room for room in self.labs 
                             if self._is_room_available(room, day, period, entries)]
        
        if available_rooms:
            selected_room = self._select_best_room(available_rooms, section)
            
            # Record the assignment for consistent daily assignment
            if section not in self.section_room_assignments:
                self.section_room_assignments[section] = {}
            self.section_room_assignments[section][day] = selected_room
            
            return selected_room
        
        return None
    
    def _is_lab_available_for_duration(self, lab: Classroom, day: str, start_period: int,
                                      duration: int, entries: List[TimetableEntry]) -> bool:
        """Check if lab is available for the specified duration."""
        for i in range(duration):
            period = start_period + i
            if not self._is_room_available(lab, day, period, entries):
                return False
        return True
    
    def _is_room_available(self, room: Classroom, day: str, period: int,
                          entries: List[TimetableEntry]) -> bool:
        """Check if room is available for the specified time slot."""
        return not any(
            entry.classroom and entry.classroom.id == room.id and
            entry.day == day and entry.period == period
            for entry in entries
        )
    
    def _force_lab_availability(self, day: str, start_period: int, duration: int,
                               entries: List[TimetableEntry]) -> List[Classroom]:
        """Try to free up labs by moving conflicting classes."""
        available_labs = []
        
        for lab in self.labs:
            if self._can_clear_lab_for_duration(lab, day, start_period, duration, entries):
                available_labs.append(lab)
        
        return available_labs
    
    def _can_clear_lab_for_duration(self, lab: Classroom, day: str, start_period: int,
                                   duration: int, entries: List[TimetableEntry]) -> bool:
        """Check if we can clear a lab for the specified duration by moving conflicting classes."""
        conflicting_entries = []
        
        # Find all conflicting entries
        for i in range(duration):
            period = start_period + i
            for entry in entries:
                if (entry.classroom and entry.classroom.id == lab.id and
                    entry.day == day and entry.period == period):
                    conflicting_entries.append(entry)
        
        # Check if all conflicting entries can be moved
        for entry in conflicting_entries:
            if not self._can_move_entry_to_alternative_room(entry, entries):
                return False
        
        return True
    
    def _can_move_entry_to_alternative_room(self, entry: TimetableEntry,
                                          entries: List[TimetableEntry]) -> bool:
        """Check if an entry can be moved to an alternative room."""
        # Find available rooms for this time slot
        available_rooms = self.get_available_rooms_for_time(
            entry.day, entry.period, 1, entries
        )
        
        # Filter out the current room
        available_rooms = [room for room in available_rooms if room.id != entry.classroom.id]
        
        return len(available_rooms) > 0
    
    def _select_best_lab(self, available_labs: List[Classroom], section: str) -> Classroom:
        """Select the best lab based on usage and section priority."""
        if not available_labs:
            return None
        
        # Prefer labs with lower usage
        def lab_score(lab):
            usage_count = sum(len(periods) for periods in self.room_usage[lab.id].values())
            return usage_count
        
        return min(available_labs, key=lab_score)
    
    def _select_best_room(self, available_rooms: List[Classroom], section: str) -> Classroom:
        """Select the best room based on section preferences and usage."""
        if not available_rooms:
            return None
        
        # Prefer rooms with lower usage
        def room_score(room):
            usage_count = sum(len(periods) for periods in self.room_usage[room.id].values())
            return usage_count
        
        return min(available_rooms, key=room_score)
    
    def update_room_usage(self, room: Classroom, day: str, period: int):
        """Update room usage tracking."""
        self.room_usage[room.id][day].add(period)
    
    def clear_room_usage(self, room: Classroom, day: str, period: int):
        """Clear room usage tracking."""
        if room.id in self.room_usage and day in self.room_usage[room.id]:
            self.room_usage[room.id][day].discard(period)
    
    def validate_room_allocation(self, entries: List[TimetableEntry]) -> List[Dict]:
        """Validate room allocation against client requirements."""
        violations = []
        
        # Check for room conflicts
        room_schedule = defaultdict(lambda: defaultdict(set))
        
        for entry in entries:
            if entry.classroom:
                room_schedule[entry.classroom.id][entry.day].add(entry.period)
        
        # Check for double bookings
        for room_id, day_schedule in room_schedule.items():
            for day, periods in day_schedule.items():
                if len(periods) != len(set(periods)):
                    violations.append({
                        'type': 'Room Double Booking',
                        'room_id': room_id,
                        'day': day,
                        'description': f'Room {room_id} has double booking on {day}'
                    })
        
        # Check practical lab assignments
        for entry in entries:
            if entry.is_practical and entry.classroom:
                if not entry.classroom.is_lab:
                    violations.append({
                        'type': 'Practical Not in Lab',
                        'entry_id': entry.id,
                        'description': f'Practical class {entry.subject.code} assigned to non-lab room {entry.classroom.name}'
                    })
        
        # Check same-lab rule for practicals
        practical_groups = defaultdict(lambda: defaultdict(list))
        for entry in entries:
            if entry.is_practical:
                key = (entry.class_group, entry.subject.code, entry.day)
                practical_groups[key].append(entry)
        
        for key, group_entries in practical_groups.items():
            if len(group_entries) >= 3:
                labs_used = set(entry.classroom.id for entry in group_entries if entry.classroom)
                if len(labs_used) > 1:
                    violations.append({
                        'type': 'Practical Multiple Labs',
                        'subject': group_entries[0].subject.code,
                        'class_group': group_entries[0].class_group,
                        'day': group_entries[0].day,
                        'description': f'Practical {group_entries[0].subject.code} uses multiple labs on {group_entries[0].day}'
                    })
        
        return violations
    
    def get_allocation_report(self) -> Dict:
        """Generate a report of current room allocation status."""
        return {
            'total_rooms': len(self.all_rooms),
            'labs': len(self.labs),
            'academic_building_rooms': len(self.academic_building_rooms),
            'main_building_rooms': len(self.main_building_rooms),
            'section_assignments': len(self.section_room_assignments),
            'practical_assignments': len(self.practical_lab_assignments),
            'room_usage': dict(self.room_usage)
        } 