import os
import sys
import django

# Add the Django backend to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'django-backend', 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from timetable.models import Subject, Teacher, Classroom, Batch, ScheduleConfig, TimetableEntry

def main():
    print("=== DELETING USERS WITHOUT DATA ===")
    
    # Get all users
    all_users = User.objects.all()
    print(f"Total users found: {all_users.count()}")
    
    # Find users with data
    users_with_data = set()
    
    # Check each model for users with data
    models_to_check = [
        (Subject, 'subjects'),
        (Teacher, 'teachers'),
        (Classroom, 'classrooms'),
        (Batch, 'batches'),
        (ScheduleConfig, 'schedule configs'),
        (TimetableEntry, 'timetable entries'),
    ]
    
    for model, model_name in models_to_check:
        if hasattr(model, 'owner'):
            owners = model.objects.values_list('owner_id', flat=True).distinct()
            users_with_data.update(owners)
            print(f"Users with {model_name}: {list(owners)}")
    
    # Also keep superusers
    superusers = User.objects.filter(is_superuser=True).values_list('id', flat=True)
    users_with_data.update(superusers)
    print(f"Superusers: {list(superusers)}")
    
    # Get users to delete (those without data and not superusers)
    users_to_delete = User.objects.exclude(id__in=users_with_data)
    
    print(f"\nUsers to delete ({users_to_delete.count()}):")
    for user in users_to_delete:
        print(f"  - {user.username} ({user.email}) - ID: {user.id}")
    
    # Delete users
    if users_to_delete.count() > 0:
        deleted_count = users_to_delete.count()
        users_to_delete.delete()
        print(f"\nSuccessfully deleted {deleted_count} users")
    else:
        print("No users to delete")

if __name__ == '__main__':
    main() 