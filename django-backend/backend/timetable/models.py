from django.db import models
from users.models import User
import json
from datetime import date

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()
    building = models.CharField(max_length=50)

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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-semester_number']  # Final year first

    def __str__(self):
        return f"{self.name} - {self.description}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.PositiveIntegerField()
    is_practical = models.BooleanField(default=False)
    batch = models.CharField(max_length=10, blank=True, null=True, help_text="e.g., 21SW, 22SW, 23SW, 24SW")

    def save(self, *args, **kwargs):
        # Auto-detect practical subjects based on name or code
        if '(PR)' in self.name or '(Pr)' in self.name or 'Pr' in self.code or 'PR' in self.code:
            self.is_practical = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Teacher(models.Model):
    name = models.CharField(max_length=255, default="")
    email = models.EmailField(unique=True, default="")
    subjects = models.ManyToManyField('Subject', blank=True)
    max_lessons_per_day = models.PositiveIntegerField(default=4)
    unavailable_periods = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
    

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