from django.core.management.base import BaseCommand
from django.db import models
from users.models import User
from timetable.models import Subject, Teacher, Classroom, Batch, ScheduleConfig, TimetableEntry, Department, UserDepartment

class Command(BaseCommand):
    help = 'Delete all users except the one that has data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all users
        all_users = User.objects.all()
        self.stdout.write(f"Total users found: {all_users.count()}")
        
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
            # (SharedAccess, 'shared access'),
        ]
        
        for model, model_name in models_to_check:
            if hasattr(model, 'owner'):
                # Models with owner field
                owners = model.objects.values_list('owner_id', flat=True).distinct()
                users_with_data.update(owners)
                self.stdout.write(f"Users with {model_name}: {list(owners)}")
            elif hasattr(model, 'user'):
                # Models with user field
                users = model.objects.values_list('user_id', flat=True).distinct()
                users_with_data.update(users)
                self.stdout.write(f"Users with {model_name}: {list(users)}")
        
        # Also check superusers
        superusers = User.objects.filter(is_superuser=True).values_list('id', flat=True)
        users_with_data.update(superusers)
        self.stdout.write(f"Superusers: {list(superusers)}")
        
        # Get users to keep (those with data)
        users_to_keep = User.objects.filter(id__in=users_with_data)
        self.stdout.write(f"\nUsers to keep ({users_to_keep.count()}):")
        for user in users_to_keep:
            self.stdout.write(f"  - {user.username} ({user.email}) - ID: {user.id}")
        
        # Get users to delete
        users_to_delete = User.objects.exclude(id__in=users_with_data)
        self.stdout.write(f"\nUsers to delete ({users_to_delete.count()}):")
        for user in users_to_delete:
            self.stdout.write(f"  - {user.username} ({user.email}) - ID: {user.id}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN - No users were actually deleted"))
            return
        
        # Confirm deletion
        if users_to_delete.count() > 0:
            confirm = input(f"\nAre you sure you want to delete {users_to_delete.count()} users? (yes/no): ")
            if confirm.lower() == 'yes':
                # Delete users
                deleted_count = users_to_delete.count()
                users_to_delete.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"\nSuccessfully deleted {deleted_count} users")
                )
            else:
                self.stdout.write(self.style.WARNING("Deletion cancelled"))
        else:
            self.stdout.write(self.style.SUCCESS("No users to delete")) 