from django.db import models
from users.models import User
import json
from datetime import date

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()
    building = models.CharField(max_length=50)

    # Room classification properties
    @property
    def is_lab(self):
        """Check if this classroom is a lab."""
        return 'lab' in self.name.lower() or 'laboratory' in self.name.lower()

    @property
    def room_type(self):
        """Get the room type for allocation purposes."""
        if self.is_lab:
            return 'lab'
        return 'regular'

    @property
    def building_priority(self):
        """Get building priority for allocation (lower = higher priority)."""
        priority_map = {
            'Lab Block': 1,      # Highest priority for labs
            'Main Block': 2,     # Main building rooms
            'Main Building': 2,  # Alternative main building name
            'Academic Building': 3,  # Academic building rooms
            'Admin Block': 4     # Lowest priority
        }
        return priority_map.get(self.building, 5)

    def is_suitable_for_practical(self):
        """Check if this room is suitable for practical classes."""
        return self.is_lab

    def is_suitable_for_theory(self):
        """Check if this room is suitable for theory classes."""
        return True  # All rooms can host theory classes

    def can_accommodate_section_size(self, section_size):
        """Check if room capacity can accommodate the section size."""
        return self.capacity >= section_size

    class Meta:
        ordering = ['building', 'name']

class ScheduleConfig(models.Model):
    name = models.CharField(max_length=255)
    days = models.JSONField(default=list)
    periods = models.JSONField(default=list)
    start_time = models.TimeField()
    lesson_duration = models.PositiveIntegerField()
    constraints = models.JSONField(default=dict)
    class_groups = models.JSONField(default=list)
    semester = models.CharField(max_length=50, default="Fall 2024")
    academic_year = models.CharField(max_length=20, default="2024-2025")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Ensure periods is always stored as array of strings
        if isinstance(self.periods, str):
            try:
                self.periods = json.loads(self.periods)
            except json.JSONDecodeError:
                self.periods = []
        elif not isinstance(self.periods, list):
            self.periods = []
            
        # Ensure class_groups is always stored as array of strings
        if isinstance(self.class_groups, str):
            try:
                self.class_groups = json.loads(self.class_groups)
            except json.JSONDecodeError:
                self.class_groups = []
        elif not isinstance(self.class_groups, list):
            self.class_groups = []
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Config(models.Model):
    name = models.CharField(max_length=255)
    days = models.JSONField(default=list)
    periods = models.PositiveIntegerField()
    start_time = models.TimeField()
    lesson_duration = models.PositiveIntegerField()
    generated_periods = models.JSONField(default=dict)

    def __str__(self):
        return self.name
    
class ClassGroup(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    latest_start_time = models.TimeField()
    min_lessons = models.PositiveIntegerField()
    max_lessons = models.PositiveIntegerField()
    class_groups = models.JSONField()

    def __str__(self):
        return ".".join(self.class_groups) or "No class groups"
    
class Batch(models.Model):
    name = models.CharField(max_length=10, unique=True, help_text="e.g., 21SW, 22SW, 23SW, 24SW")
    description = models.CharField(max_length=100, help_text="e.g., 8th Semester - Final Year")
    semester_number = models.PositiveIntegerField(help_text="e.g., 8 for 8th semester")
    academic_year = models.CharField(max_length=20, default="2024-2025")
    total_sections = models.PositiveIntegerField(default=1, help_text="Number of sections in this batch (e.g., 3 for I, II, III)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-semester_number']  # Final year first

    def __str__(self):
        return f"{self.name} - {self.description} ({self.total_sections} sections)"

    def get_sections(self):
        """Return list of section names for this batch"""
        sections = []
        for i in range(1, self.total_sections + 1):
            if i == 1:
                sections.append("I")
            elif i == 2:
                sections.append("II")
            elif i == 3:
                sections.append("III")
            elif i == 4:
                sections.append("IV")
            elif i == 5:
                sections.append("V")
            else:
                sections.append(str(i))
        return sections

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)  # Remove unique=True to allow duplicates
    credits = models.PositiveIntegerField()
    is_practical = models.BooleanField(default=False)
    batch = models.CharField(max_length=10, blank=True, null=True, help_text="e.g., 21SW, 22SW, 23SW, 24SW")

    class Meta:
        # Allow up to 2 subjects with the same code (theory + practical)
        pass

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Check if this code is already used more than once
        if self.code:
            existing_count = Subject.objects.filter(code__iexact=self.code).exclude(pk=self.pk).count()
            if existing_count >= 2:
                raise ValidationError({
                    'code': f'Subject code "{self.code}" is already used twice. Maximum allowed is 2 (theory and practical versions).'
                })

    def save(self, *args, **kwargs):
        # Auto-detect practical subjects based on name or code
        if '(PR)' in self.name or 'PR' in self.code:
            self.is_practical = True
        
        # Run validation before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Teacher(models.Model):
    name = models.CharField(max_length=255, default="")
    email = models.EmailField(unique=True, default="")
    # Note: subjects relationship now handled through TeacherSubjectAssignment
    max_lessons_per_day = models.PositiveIntegerField(default=4)
    unavailable_periods = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

    def get_subjects(self):
        """Get all subjects this teacher is assigned to"""
        return Subject.objects.filter(teachersubjectassignment__teacher=self).distinct()

    def get_assignments(self):
        """Get all teacher-subject assignments"""
        return TeacherSubjectAssignment.objects.filter(teacher=self)

class TeacherSubjectAssignment(models.Model):
    """Intermediate model to handle teacher-subject assignments with section specificity"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    sections = models.JSONField(default=list, help_text="List of sections this teacher handles for this subject, e.g., ['I', 'II']")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Remove unique_together constraint to allow multiple assignments for same teacher-subject-batch
        # This allows teachers to be assigned to different sections of the same subject
        verbose_name = "Teacher Subject Assignment"
        verbose_name_plural = "Teacher Subject Assignments"

    def clean(self):
        """Validate that sections don't conflict with existing assignments"""
        from django.core.exceptions import ValidationError

        if not self.sections:
            return  # No sections specified means all sections

        # Check for conflicts with other assignments for the same subject and batch
        existing_assignments = TeacherSubjectAssignment.objects.filter(
            subject=self.subject,
            batch=self.batch
        ).exclude(pk=self.pk if self.pk else None)

        for assignment in existing_assignments:
            if not assignment.sections:  # Other assignment covers all sections
                raise ValidationError(
                    f"Teacher {assignment.teacher.name} is already assigned to all sections of {self.subject.name} in {self.batch.name}"
                )

            # Check for section overlap
            overlapping_sections = set(self.sections) & set(assignment.sections)
            if overlapping_sections:
                raise ValidationError(
                    f"Sections {', '.join(overlapping_sections)} are already assigned to {assignment.teacher.name} for {self.subject.name} in {self.batch.name}"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        sections_str = ", ".join(self.sections) if self.sections else "All"
        return f"{self.teacher.name} - {self.subject.name} ({self.batch.name} - Sections: {sections_str})"

    def get_sections_display(self):
        """Return formatted sections string"""
        if not self.sections:
            return "All Sections"
        return f"Section{'s' if len(self.sections) > 1 else ''}: {', '.join(self.sections)}"
    

class TimetableEntry(models.Model):
    day = models.CharField(max_length=20)
    period = models.IntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    class_group = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_practical = models.BooleanField(default=False)
    schedule_config = models.ForeignKey(ScheduleConfig, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.CharField(max_length=50, default="Fall 2024")
    academic_year = models.CharField(max_length=20, default="2024-2025")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['day', 'period']

    def __str__(self):
        return f"{self.day} Period {self.period}: {self.subject} {'(PR)' if self.is_practical else ''} - {self.teacher} - {self.classroom}"