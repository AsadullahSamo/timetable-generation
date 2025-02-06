# timetable/algorithms/scheduler.py
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import TimetableEntry, Subject, Teacher, Classroom

class TimetableScheduler:
    def __init__(self, config):
        self.config = config
        self.timetable = []
        self.teacher_availability = {}
        self.classroom_availability = {}
        self.subject_frequency = {}
        self.constraints = config.constraints
        
        # Initialize data structures
        self.days = config.days
        self.periods = config.periods
        self.teachers = Teacher.objects.all()
        self.classrooms = Classroom.objects.all()
        self.subjects = Subject.objects.all()
        self.class_groups = config.class_groups

    def generate(self):
        try:
            self._initialize_availability()
            self._create_time_slots()
            self._schedule_lessons()
            return self._format_timetable()
        except Exception as e:
            print(f"Scheduling error: {str(e)}")
            raise

    def _initialize_availability(self):
        """Initialize availability tracking structures"""
        for day in self.days:
            self.teacher_availability[day] = {
                teacher.id: set() for teacher in self.teachers
            }
            self.classroom_availability[day] = {
                classroom.id: set() for classroom in self.classrooms
            }
            self.subject_frequency[day] = {
                class_group: {} for class_group in self.class_groups
            }

    def _create_time_slots(self):
        """Generate time slots based on config"""
        self.time_slots = []
        current_time = datetime.combine(timezone.now().date(), self.config.start_time)
        
        for _ in range(len(self.periods)):
            end_time = current_time + timedelta(minutes=self.config.lesson_duration)
            self.time_slots.append({
                'start': current_time.time(),
                'end': end_time.time()
            })
            current_time = end_time

    def _schedule_lessons(self):
        """Core scheduling algorithm"""
        for day in self.days:
            for slot_idx, time_slot in enumerate(self.time_slots):
                for class_group in self.class_groups:
                    self._schedule_single_slot(day, slot_idx, time_slot, class_group)

    def _schedule_single_slot(self, day, slot_idx, time_slot, class_group):
        """Schedule a single time slot for a class group"""
        scheduled = False
        attempts = 0
        max_attempts = len(self.subjects) * 2  # Prevent infinite loops

        while not scheduled and attempts < max_attempts:
            attempts += 1
            for subject in self.subjects.order_by('-credits'):  # Prioritize high-credit subjects
                classroom = self._find_available_classroom(day, slot_idx, subject.credits)
                teacher = self._find_available_teacher(subject, day, slot_idx, classroom)
                
                if teacher and classroom and self._meets_constraints(subject, day, class_group):
                    self._create_entry(day, slot_idx, time_slot, class_group, subject, teacher, classroom)
                    scheduled = True
                    break

        if not scheduled:
            print(f"Warning: Could not schedule {class_group} on {day} at {time_slot['start']}")

    def _find_available_teacher(self, subject, day, slot_idx, classroom):
        """Find available teacher for subject"""
        for teacher in self.teachers.filter(subjects=subject):
            if (slot_idx not in self.teacher_availability[day][teacher.id] and
                not self._has_teacher_conflict(teacher, day, slot_idx, classroom)):
                return teacher
        return None

    def _find_available_classroom(self, day, slot_idx, required_capacity):
        """Find suitable classroom"""
        for classroom in self.classrooms.order_by('-capacity'):
            if (slot_idx not in self.classroom_availability[day][classroom.id] and
                classroom.capacity >= required_capacity):
                return classroom
        return None

    def _meets_constraints(self, subject, day, class_group):
        """Check constraints"""
        # Implement your constraint checking logic here
        constraints_met = True
        
        # Example constraint: Max 2 lessons per day for same subject
        current_count = self.subject_frequency[day][class_group].get(subject.id, 0)
        if current_count >= self.constraints.get('max_subject_per_day', 3):
            constraints_met = False
            
        # Add other constraints based on config
        return constraints_met

    def _has_teacher_conflict(self, teacher, day, slot_idx, classroom):
        """Check teacher's existing commitments"""
        # Check if teacher has consecutive classes in different buildings
        prev_slot = slot_idx - 1
        next_slot = slot_idx + 1
        
        if prev_slot >= 0 and prev_slot in self.teacher_availability[day][teacher.id]:
            prev_classroom = self._get_teacher_classroom(teacher, day, prev_slot)
            if prev_classroom and prev_classroom.building != classroom.building:
                if 'no_consecutive_building_changes' in self.constraints:
                    return True
                    
        return False

    def _create_entry(self, day, slot_idx, time_slot, class_group, subject, teacher, classroom):
        """Create timetable entry and update tracking structures"""
        entry = TimetableEntry(
            day=day,
            period=slot_idx + 1,
            class_group=class_group,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            start_time=time_slot['start'],
            end_time=time_slot['end']
        )
        self.timetable.append(entry)
        
        # Update availability tracking
        self.teacher_availability[day][teacher.id].add(slot_idx)
        self.classroom_availability[day][classroom.id].add(slot_idx)
        self.subject_frequency[day][class_group][subject.id] = \
            self.subject_frequency[day][class_group].get(subject.id, 0) + 1

    def _format_timetable(self):
        """Format output for API response"""
        return {
            'days': self.days,
            'timeSlots': [ts['start'].strftime("%I:%M %p") for ts in self.time_slots],
            'entries': [{
                'day': entry.day,
                'period': entry.period,
                'subject': entry.subject.name,
                'teacher': entry.teacher.user.get_full_name(),
                'classroom': entry.classroom.name,
                'start_time': entry.start_time.strftime("%H:%M:%S"),
                'end_time': entry.end_time.strftime("%H:%M:%S")
            } for entry in self.timetable]
        }