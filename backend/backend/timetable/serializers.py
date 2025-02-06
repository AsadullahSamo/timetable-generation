from rest_framework import serializers
from .models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry, Config

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = '__all__'

class ScheduleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleConfig
        fields = '__all__'

class TimetableEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableEntry
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()
    teacher = serializers.StringRelatedField()
    classroom = serializers.StringRelatedField()

    class Meta:
        model = TimetableEntry
        fields = ['day', 'period', 'subject', 'teacher', 'classroom', 'start_time', 'end_time']

class ConfigSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(
        format='%H:%M', 
        input_formats=['%H:%M', '%H:%M:%S'] 
    )
     
    class Meta:
        model = Config
        fields = '__all__'