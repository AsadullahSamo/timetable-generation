from django.core.management.base import BaseCommand
from timetable.models import Config, ClassGroup, Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry

class Command(BaseCommand):
    help = 'Cleans up all data from timetable tables'

    def handle(self, *args, **kwargs):
        # Delete in correct order to respect foreign key constraints
        self.stdout.write('Starting database cleanup...')
        
        # First delete all timetable entries
        count = TimetableEntry.objects.all().count()
        TimetableEntry.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} timetable entries'))
        
        # Delete schedule configs
        count = ScheduleConfig.objects.all().count()
        ScheduleConfig.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} schedule configs'))
        
        # Delete old configs
        count = Config.objects.all().count()
        Config.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} old configs'))
        
        # Delete class groups
        count = ClassGroup.objects.all().count()
        ClassGroup.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} class groups'))
        
        # Clear teacher-subject relationships first
        for teacher in Teacher.objects.all():
            teacher.subjects.clear()
        self.stdout.write(self.style.SUCCESS('Cleared teacher-subject relationships'))
        
        # Delete teachers
        count = Teacher.objects.all().count()
        Teacher.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} teachers'))
        
        # Delete subjects
        count = Subject.objects.all().count()
        Subject.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} subjects'))
        
        # Delete classrooms
        count = Classroom.objects.all().count()
        Classroom.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} classrooms'))
        
        self.stdout.write(self.style.SUCCESS('Database cleanup completed successfully')) 