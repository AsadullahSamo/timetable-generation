from rest_framework import serializers
from users.models import User
from .models import Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry, Config, ClassGroup
# from users.serializers import UserSerializer



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class NestedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    # Accept subjects as an array of IDs on input
    subjects = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), many=True, required=False
    )
    # Add a read-only field to display subject names
    subject_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id',
            'name',
            'email',
            'subjects',
            'subject_names',
            'max_lessons_per_day',
            'unavailable_periods'
        ]

    def get_subject_names(self, obj):
        return [subject.name for subject in obj.subjects.all()]
        

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

class ClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = '__all__'