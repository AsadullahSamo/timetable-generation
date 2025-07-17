from datetime import datetime, timedelta
from django.utils import timezone
from ..models import TimetableEntry, Subject, Teacher, Classroom
import random

class TimetableScheduler:
    def __init__(self, config):
        self.config = config
        self.timetable = []
        self.teacher_availability = {}
        self.classroom_availability = {}
        self.subject_frequency = {}
        self.constraints = config.constraints
        self.weekly_subject_count = {}  # Track weekly subject frequency
        
        # Initialize data structures from config
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
        
        # Initialize weekly subject count
        for class_group in self.class_groups:
            self.weekly_subject_count[class_group] = {
                subject.id: {'theory': 0, 'practical': 0} for subject in self.subjects
            }

    def _create_time_slots(self):
        """Generate time slots based on config"""
        self.time_slots = []
        current_time = datetime.combine(datetime.today(), self.config.start_time)
        
        for _ in range(len(self.periods)):
            end_time = current_time + timedelta(minutes=self.config.lesson_duration)
            self.time_slots.append({
                'start': current_time.time(),
                'end': end_time.time()
            })
            current_time = end_time

    def _schedule_lessons(self):
        """Core scheduling algorithm"""
        # First schedule practical subjects
        for class_group in self.class_groups:
            practical_subjects = self.subjects.filter(is_practical=True)
            for subject in practical_subjects:
                self._schedule_practical_block(subject, class_group)

        # Then schedule theory subjects
        for class_group in self.class_groups:
            theory_subjects = self.subjects.filter(is_practical=False)
            for subject in theory_subjects:
                self._schedule_theory_classes(subject, class_group)

    def _schedule_practical_block(self, subject, class_group):
        """Schedule a block of practical sessions"""
        practical_slots = 3  # Standard 3-hour practical

        # Try to find a block of consecutive periods
        for day in self.days:
            for start_slot in range(len(self.time_slots) - practical_slots + 1):
                if self._can_schedule_practical_block(day, start_slot, practical_slots, subject, class_group):
                    classroom = self._find_available_classroom(day, start_slot, practical_slots)
                    teacher = self._find_practical_teacher(subject, day, start_slot, practical_slots)
                    
                    if teacher and classroom:
                        # Schedule the practical block
                        for i in range(practical_slots):
                            self._create_entry(
                                day,
                                start_slot + i,
                                self.time_slots[start_slot + i],
                                class_group,
                                subject,
                                teacher,
                                classroom,
                                is_practical=True
                            )
                        return True
        return False

    def _can_schedule_practical_block(self, day, start_slot, num_slots, subject, class_group):
        """Check if we can schedule a practical block"""
        # Check if slots are available
        for i in range(num_slots):
            slot_idx = start_slot + i
            if slot_idx >= len(self.time_slots):
                return False
            if not self._is_slot_available(day, slot_idx, subject, class_group):
                return False
                
        # Check constraints
        if not self._meets_constraints(subject, day, class_group):
            return False
            
        return True

    def _find_practical_teacher(self, subject, day, start_slot, num_slots):
        """Find available teacher for practical session"""
        available_teachers = []
        for teacher in self.teachers.filter(subjects=subject):
            can_teach = True
            # Check availability for all slots
            for i in range(num_slots):
                if (start_slot + i) in self.teacher_availability[day][teacher.id]:
                    can_teach = False
                    break
            if can_teach and self._check_teacher_constraints(teacher, day, start_slot):
                available_teachers.append(teacher)
        
        return random.choice(available_teachers) if available_teachers else None

    def _find_available_classroom(self, day, start_slot, num_slots):
        """Find available classroom"""
        for classroom in self.classrooms:
            available = True
            for i in range(num_slots):
                if (start_slot + i) in self.classroom_availability[day][classroom.id]:
                    available = False
                    break
            if available:
                return classroom
        return None

    def _schedule_theory_classes(self, subject, class_group):
        """Schedule theory classes for a subject"""
        classes_per_week = 5 if subject.credits == 3 else 4
        classes_scheduled = 0
        
        while classes_scheduled < classes_per_week:
            scheduled = False
            for day in self.days:
                if classes_scheduled >= classes_per_week:
                    break
                    
                # Try each period
                for slot_idx, time_slot in enumerate(self.time_slots):
                    if self._can_schedule_theory(subject, class_group, day, slot_idx):
                        classroom = self._find_available_classroom(day, slot_idx, 1)
                        teacher = self._find_theory_teacher(subject, day, slot_idx)
                        
                        if teacher and classroom:
                            self._create_entry(
                                day,
                                slot_idx,
                                time_slot,
                                class_group,
                                subject,
                                teacher,
                                classroom,
                                is_practical=False
                            )
                            classes_scheduled += 1
                            scheduled = True
                            break
                
                if not scheduled:
                    break
            
            if not scheduled:
                break

    def _can_schedule_theory(self, subject, class_group, day, slot_idx):
        """Check if we can schedule a theory class"""
        # Check basic availability
        if not self._is_slot_available(day, slot_idx, subject, class_group):
            return False
            
        # Check constraints
        if not self._meets_constraints(subject, day, class_group):
            return False
            
        return True

    def _is_slot_available(self, day, slot_idx, subject, class_group):
        """Check if a slot is available"""
        # Check if class group is already scheduled
        for entry in self.timetable:
            if (entry.day == day and 
                entry.period == slot_idx + 1 and 
                entry.class_group == class_group):
                return False
        
        return True

    def _find_theory_teacher(self, subject, day, slot_idx):
        """Find available teacher for theory class"""
        available_teachers = []
        for teacher in self.teachers.filter(subjects=subject):
            if slot_idx not in self.teacher_availability[day][teacher.id]:
                if self._check_teacher_constraints(teacher, day, slot_idx):
                    available_teachers.append(teacher)
        
        return random.choice(available_teachers) if available_teachers else None

    def _check_teacher_constraints(self, teacher, day, slot_idx):
        """Check all teacher-related constraints"""
        # Check max lessons per day
        if self._get_teacher_daily_lessons(teacher, day) >= teacher.max_lessons_per_day:
            return False
            
        # Check consecutive classes
        if not self._check_teacher_consecutive_constraint(teacher, day, slot_idx):
            return False
            
        # Check unavailable periods
        if day in teacher.unavailable_periods:
            return False
            
        return True

    def _check_teacher_consecutive_constraint(self, teacher, day, slot_idx):
        """Check if teacher has consecutive classes"""
        prev_slot = slot_idx - 1
        if prev_slot >= 0 and prev_slot in self.teacher_availability[day][teacher.id]:
            # If teacher has consecutive classes, ensure there's a gap after
            next_slot = slot_idx + 1
            if next_slot < len(self.time_slots):
                return next_slot not in self.teacher_availability[day][teacher.id]
        return True

    def _get_teacher_daily_lessons(self, teacher, day):
        """Get number of lessons a teacher has on a specific day"""
        return len(self.teacher_availability[day][teacher.id])

    def _meets_constraints(self, subject, day, class_group):
        """Check all constraints from the Constraints page"""
        active_constraints = [c for c in self.constraints if c.get('active', False)]
        
        for constraint in active_constraints:
            if not self._check_constraint(constraint, subject, day, class_group):
                return False
                
        return True

    def _check_constraint(self, constraint, subject, day, class_group):
        """Check individual constraint"""
        constraint_type = constraint.get('category')
        
        if constraint_type == 'credit':
            return self._check_credit_constraint(constraint, subject, class_group)
        elif constraint_type == 'teacher':
            return self._check_teacher_constraint(constraint, subject, day)
        else:  # general constraints
            return self._check_general_constraint(constraint, subject, day, class_group)
            
        return True

    def _check_credit_constraint(self, constraint, subject, class_group):
        """Check credit hour related constraints"""
        weekly_count = self.weekly_subject_count[class_group][subject.id]
        total_count = weekly_count['theory'] + weekly_count['practical']
        
        if subject.credits == 3:
            return total_count < 5  # 4-5 classes per week for 3 credit subjects
        elif subject.credits == 2:
            return total_count < 4  # 3-4 classes per week for 2 credit subjects
            
        return True

    def _check_teacher_constraint(self, constraint, subject, day):
        """Check teacher related constraints"""
        # Already handled in _check_teacher_constraints
        return True

    def _check_general_constraint(self, constraint, subject, day, class_group):
        """Check general constraints"""
        # Check max classes per day for same subject
        day_count = sum(1 for entry in self.timetable 
                       if entry.day == day 
                       and entry.subject == subject 
                       and entry.class_group == class_group)
        if day_count >= 2:  # Max 2 classes per day
            return False
            
        return True

    def _create_entry(self, day, slot_idx, time_slot, class_group, subject, teacher, classroom, is_practical):
        """Create timetable entry and update tracking structures"""
        entry = TimetableEntry(
            day=day,
            period=slot_idx + 1,
            class_group=class_group,
            subject=subject,
            teacher=teacher,
            classroom=classroom,
            start_time=time_slot['start'],
            end_time=time_slot['end'],
            is_practical=is_practical
        )
        self.timetable.append(entry)
        
        # Update availability tracking
        if teacher:
            self.teacher_availability[day][teacher.id].add(slot_idx)
        if classroom:
            self.classroom_availability[day][classroom.id].add(slot_idx)
        
        # Update subject frequency
        entry_type = 'practical' if is_practical else 'theory'
        self.weekly_subject_count[class_group][subject.id][entry_type] += 1

    def _format_timetable(self):
        """Format output for API response"""
        return {
            'days': self.days,
            'timeSlots': [f"{ts['start'].strftime('%I:%M %p')} - {ts['end'].strftime('%I:%M %p')}" 
                         for ts in self.time_slots],
            'entries': [{
                'day': entry.day,
                'period': entry.period,
                'subject': f"{entry.subject.name}{' (PR)' if entry.is_practical else ''}",
                'teacher': entry.teacher.name if entry.teacher else '',
                'classroom': entry.classroom.name if entry.classroom else '',
                'class_group': entry.class_group,
                'start_time': entry.start_time.strftime("%H:%M:%S"),
                'end_time': entry.end_time.strftime("%H:%M:%S")
            } for entry in self.timetable]
        }