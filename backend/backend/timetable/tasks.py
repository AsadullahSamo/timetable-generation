from celery import shared_task
from datetime import datetime, timedelta
from .models import TimetableEntry, ScheduleConfig, Teacher, Subject, Classroom
from .algorithms.scheduler import TimetableScheduler

@shared_task
def generate_timetable(config_id):
    config = ScheduleConfig.objects.get(id=config_id)
    scheduler = TimetableScheduler(config)
    result = scheduler.generate()
    
    # Clear existing entries
    TimetableEntry.objects.all().delete()
    
    # Save new entries
    entries = []
    for entry_data in result['entries']:
        # Smart subject name resolution
        subject_name = entry_data['subject']
        try:
            # Try exact match first
            subject = Subject.objects.get(name=subject_name)
        except Subject.DoesNotExist:
            # Try without (PR) suffix
            clean_name = subject_name.replace(' (PR)', '')
            try:
                subject = Subject.objects.get(name=clean_name)
            except Subject.DoesNotExist:
                # Skip this entry if subject not found
                continue

        entries.append(TimetableEntry(
            day=entry_data['day'],
            period=entry_data['period'],
            subject=subject,
            teacher=Teacher.objects.get(name=entry_data['teacher']),
            classroom=Classroom.objects.get(name=entry_data['classroom']),
            class_group=entry_data['class_group'],
            start_time=entry_data['start_time'],
            end_time=entry_data['end_time'],
            is_practical=subject.is_practical  # Use the subject's database property
        ))
    
    TimetableEntry.objects.bulk_create(entries)
    return result