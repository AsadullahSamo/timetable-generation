import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from timetable.models import Subject, Teacher, Classroom, Batch, ScheduleConfig, TimetableEntry

print("=== USER ANALYSIS ===")

# List all users
users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"\nUser: {user.username} ({user.email}) - ID: {user.id}")
    
    # Check what data this user has
    subjects_count = Subject.objects.filter(owner=user).count()
    teachers_count = Teacher.objects.filter(owner=user).count()
    classrooms_count = Classroom.objects.filter(owner=user).count()
    batches_count = Batch.objects.filter(owner=user).count()
    configs_count = ScheduleConfig.objects.filter(owner=user).count()
    entries_count = TimetableEntry.objects.filter(owner=user).count()
    
    print(f"  Subjects: {subjects_count}")
    print(f"  Teachers: {teachers_count}")
    print(f"  Classrooms: {classrooms_count}")
    print(f"  Batches: {batches_count}")
    print(f"  Configs: {configs_count}")
    print(f"  Entries: {entries_count}")
    
    total_data = subjects_count + teachers_count + classrooms_count + batches_count + configs_count + entries_count
    print(f"  Total data items: {total_data}")
    
    if total_data > 0:
        print("  *** HAS DATA ***")
    else:
        print("  *** NO DATA ***") 