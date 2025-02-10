from django.contrib import admin
from .models import Config, ClassGroup, Subject, Teacher

admin.site.register(Config)
admin.site.register(ClassGroup)
admin.site.register(Subject)
admin.site.register(Teacher)