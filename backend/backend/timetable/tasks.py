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
        entries.append(TimetableEntry(
            day=entry_data['day'],
            period=entry_data['period'],
            subject=Subject.objects.get(name=entry_data['subject']),
            teacher=Teacher.objects.get(user__username=entry_data['teacher']),
            classroom=Classroom.objects.get(name=entry_data['classroom']),
            start_time=entry_data['start_time'],
            end_time=entry_data['end_time']
        ))
    
    TimetableEntry.objects.bulk_create(entries)
    return result