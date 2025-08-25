#!/usr/bin/env python
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
    print("=== USER ANALYSIS ===")
    
    # List all users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    users_with_data = []
    users_without_data = []
    
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
        
        if total_data > 0 or user.is_superuser:
            print("  *** HAS DATA OR IS SUPERUSER ***")
            users_with_data.append(user)
        else:
            print("  *** NO DATA ***")
            users_without_data.append(user)
    
    print(f"\n=== SUMMARY ===")
    print(f"Users with data or superusers: {len(users_with_data)}")
    print(f"Users without data: {len(users_without_data)}")
    
    if users_without_data:
        print(f"\nUsers to delete:")
        for user in users_without_data:
            print(f"  - {user.username} ({user.email}) - ID: {user.id}")
        
        # Check if --delete flag is provided
        if '--delete' in sys.argv:
            confirm = input(f"\nAre you sure you want to delete {len(users_without_data)} users? (yes/no): ")
            if confirm.lower() == 'yes':
                for user in users_without_data:
                    print(f"Deleting user: {user.username}")
                    user.delete()
                print(f"Successfully deleted {len(users_without_data)} users")
            else:
                print("Deletion cancelled")
        else:
            print("\nTo delete these users, run: python check_and_delete_users.py --delete")
    else:
        print("No users to delete")

if __name__ == '__main__':
    main() 