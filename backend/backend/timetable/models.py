from django.db import models
from users.models import User

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.PositiveIntegerField()

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    max_lessons_per_day = models.PositiveIntegerField(default=4)
    unavailable_periods = models.JSONField(default=dict)

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()
    building = models.CharField(max_length=50)

class ScheduleConfig(models.Model):
    name = models.CharField(max_length=100)
    days = models.JSONField(default=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
    periods = models.JSONField()
    start_time = models.TimeField()
    lesson_duration = models.PositiveIntegerField()
    constraints = models.JSONField(default=dict)

class TimetableEntry(models.Model):
    day = models.CharField(max_length=10)
    period = models.PositiveIntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    class_group = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()


class Config(models.Model):
    name = models.CharField(max_length=255)
    days = models.JSONField(default=list)
    periods = models.PositiveIntegerField()
    start_time = models.TimeField()
    lesson_duration = models.PositiveIntegerField()
    generated_periods = models.JSONField(default=dict)

    def __str__(self):
        return self.name