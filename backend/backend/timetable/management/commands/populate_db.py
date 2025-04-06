from django.core.management.base import BaseCommand
from timetable.models import Config, ClassGroup, Subject, Teacher, Classroom, ScheduleConfig, TimetableEntry
from django.utils import timezone
from datetime import time

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        # Create Classrooms (Labs and Regular Rooms)
        labs = [
            ('Lab. No. 01', 40, 'Block A'),  # For MC
            ('Lab. No. 02', 40, 'Block A'),  # For WE
            ('Lab. No. 03', 40, 'Block A'),  # For SERE
            ('Tutorial Room 01', 30, 'Block B'),
            ('Tutorial Room 02', 30, 'Block B'),
            ('Lecture Hall 01', 60, 'Block C'),
            ('Lecture Hall 02', 60, 'Block C'),
        ]
        
        classrooms = []
        for name, capacity, building in labs:
            classroom, created = Classroom.objects.get_or_create(
                name=name,
                defaults={
                    'capacity': capacity,
                    'building': building
                }
            )
            classrooms.append(classroom)
            if created:
                self.stdout.write(f'Created classroom: {name}')
            else:
                self.stdout.write(f'Using existing classroom: {name}')

        # Create Subjects with proper credit hours
        subjects_data = [
            # Major subjects with practicals (3+1)
            ('SW416', 'Multimedia Communication', 3, True),
            ('SW417', 'Web Engineering', 3, True),
            # Major subjects without practicals (3+0)
            ('SW415', 'Software Reengineering', 3, False),
            ('SW418', 'Formal Methods in Software Engineering', 3, False),
            # Thesis/Project
            ('SW498', 'Thesis/Project', 0, True),  # Special case: 0+3
            # Additional subjects for other batches
            ('SW410', 'Software Quality Assurance', 3, False),
            ('SW411', 'Cloud Computing', 3, True),
            ('SW412', 'Mobile App Development', 3, True),
            ('SW413', 'Information Security', 3, False),
            ('SW414', 'Artificial Intelligence', 3, True),
        ]
        
        subjects = []
        for code, name, credits, is_practical in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'credits': credits,
                    'is_practical': is_practical
                }
            )
            subjects.append(subject)
            if created:
                self.stdout.write(f'Created subject: {code} - {name}')
            else:
                self.stdout.write(f'Using existing subject: {code} - {name}')

        # Create Teachers with their subjects and constraints
        teachers_data = [
            # Format: (name, email, max_lessons, unavailable_periods, [subject_codes], is_practical_teacher)
            ('Dr. Sania Bhatti', 'sania.bhatti@faculty.edu', 4, {'Friday': [7, 8]}, ['SW416'], False),
            ('Ms. Aleena', 'aleena@faculty.edu', 4, {'Monday': [1, 2]}, ['SW416'], True),
            ('Mr. Aqib', 'aqib@faculty.edu', 4, {'Wednesday': [6, 7, 8]}, ['SW416'], True),
            ('Mr. Salahuddin Saddar', 'salahuddin@faculty.edu', 4, {'Thursday': [7, 8]}, ['SW415'], False),
            ('Ms. Sana Faiz', 'sana.faiz@faculty.edu', 4, {'Tuesday': [6, 7, 8]}, ['SW415'], False),
            ('Ms. Mariam Memon', 'mariam@faculty.edu', 4, {'Monday': [7, 8]}, ['SW418'], False),
            ('Mr. Arsalan Aftab', 'arsalan@faculty.edu', 4, {'Friday': [6, 7, 8]}, ['SW418'], False),
            ('Ms. Dua', 'dua@faculty.edu', 4, {'Thursday': [1, 2]}, ['SW417'], False),
            ('Ms. Afifah', 'afifah@faculty.edu', 4, {'Tuesday': [7, 8]}, ['SW417'], True),
            ('Mr. Tabish', 'tabish@faculty.edu', 4, {'Wednesday': [1, 2]}, ['SW417'], True),
        ]
        
        teachers = []
        for name, email, max_lessons, unavailable, subject_codes, is_practical in teachers_data:
            teacher, created = Teacher.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'max_lessons_per_day': max_lessons,
                    'unavailable_periods': unavailable
                }
            )
            # Assign subjects to teacher
            for subject_code in subject_codes:
                subject = Subject.objects.get(code=subject_code)
                teacher.subjects.add(subject)
            teachers.append(teacher)
            if created:
                self.stdout.write(f'Created teacher: {name}')
            else:
                self.stdout.write(f'Using existing teacher: {name}')

        # Create Schedule Config with realistic constraints
        schedule_config = ScheduleConfig.objects.create(
            name='Default Schedule',
            days=['MON', 'TUE', 'WED', 'THU', 'FRI'],
            periods=[f"Period {i+1}" for i in range(8)],
            start_time=time(8, 0),  # 8:00 AM
            lesson_duration=45,      # 45 minutes
            class_groups=[
                '215W-BATCH SECTION-I (1st Semester Final YEAR)',
                '215W-BATCH SECTION-II (1st Semester Final YEAR)',
                '215W-BATCH SECTION-III (1st Semester Final YEAR)',
                '215W-BATCH SECTION-IV (1st Semester Final YEAR)',
            ],
            constraints=[
                # Credit hour constraints
                {
                    'category': 'credit',
                    'type': 'max_classes_per_day',
                    'value': 2,
                    'active': True
                },
                # Teacher constraints
                {
                    'category': 'teacher',
                    'type': 'max_consecutive_classes',
                    'value': 2,
                    'active': True
                },
                {
                    'category': 'teacher',
                    'type': 'respect_unavailability',
                    'active': True
                },
                # Lab constraints
                {
                    'category': 'general',
                    'type': 'practical_block_size',
                    'value': 3,
                    'active': True
                },
                {
                    'category': 'general',
                    'type': 'lab_assignment',
                    'rules': {
                        'SW416': 'Lab. No. 01',  # MC in Lab 1
                        'SW417': 'Lab. No. 02',  # WE in Lab 2
                        'SW415': 'Lab. No. 03',  # SERE in Lab 3
                    },
                    'active': True
                },
                # Time slot preferences
                {
                    'category': 'general',
                    'type': 'preferred_slots',
                    'rules': {
                        'practical': [4, 5, 6, 7, 8],  # Prefer practicals in later slots
                        'theory': [1, 2, 3, 4]         # Prefer theory in earlier slots
                    },
                    'active': True
                }
            ]
        )
        self.stdout.write(f'Created schedule config: {schedule_config.name}')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with sample data')) 