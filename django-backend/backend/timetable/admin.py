from django.contrib import admin
from .models import Config, ClassGroup, Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry

admin.site.register(Config)
admin.site.register(ClassGroup)
admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(Classroom)
admin.site.register(ScheduleConfig)
admin.site.register(TimetableEntry)