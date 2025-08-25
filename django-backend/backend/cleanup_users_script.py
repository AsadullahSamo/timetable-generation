#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from timetable.models import Subject, Teacher, Classroom, Batch, ScheduleConfig, TimetableEntry, Department, UserDepartment, SharedAccess

def main():
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
        (Department, 'departments'),
        (UserDepartment, 'user departments'),
        (SharedAccess, 'shared access'),
    ]
    
    for model, model_name in models_to_check:
        if hasattr(model, 'owner'):
            # Models with owner field
            owners = model.objects.values_list('owner_id', flat=True).distinct()
            users_with_data.update(owners)
            print(f"Users with {model_name}: {list(owners)}")
        elif hasattr(model, 'user'):
            # Models with user field
            users = model.objects.values_list('user_id', flat=True).distinct()
            users_with_data.update(users)
            print(f"Users with {model_name}: {list(users)}")
    
    # Also check superusers
    superusers = User.objects.filter(is_superuser=True).values_list('id', flat=True)
    users_with_data.update(superusers)
    print(f"Superusers: {list(superusers)}")
    
    # Get users to keep (those with data)
    users_to_keep = User.objects.filter(id__in=users_with_data)
    print(f"\nUsers to keep ({users_to_keep.count()}):")
    for user in users_to_keep:
        print(f"  - {user.username} ({user.email}) - ID: {user.id}")
    
    # Get users to delete
    users_to_delete = User.objects.exclude(id__in=users_with_data)
    print(f"\nUsers to delete ({users_to_delete.count()}):")
    for user in users_to_delete:
        print(f"  - {user.username} ({user.email}) - ID: {user.id}")
    
    # Check if --dry-run flag is provided
    if '--dry-run' in sys.argv:
        print("\nDRY RUN - No users were actually deleted")
        return
    
    # Confirm deletion
    if users_to_delete.count() > 0:
        confirm = input(f"\nAre you sure you want to delete {users_to_delete.count()} users? (yes/no): ")
        if confirm.lower() == 'yes':
            # Delete users
            deleted_count = users_to_delete.count()
            users_to_delete.delete()
            print(f"\nSuccessfully deleted {deleted_count} users")
        else:
            print("Deletion cancelled")
    else:
        print("No users to delete")

if __name__ == '__main__':
    main() 