from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from timetable.models import Department, UserDepartment
from users.models import User

class Command(BaseCommand):
    help = 'Set up initial departments and assign users to them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-defaults',
            action='store_true',
            help='Create default departments (SWE, CS, EE)',
        )
        parser.add_argument(
            '--assign-users',
            action='store_true',
            help='Assign existing users to departments',
        )

    def handle(self, *args, **options):
        if options['create_defaults']:
            self.create_default_departments()
        
        if options['assign_users']:
            self.assign_users_to_departments()

    def create_default_departments(self):
        """Create default departments"""
        departments_data = [
            {
                'name': 'Software Engineering',
                'code': 'SWE',
                'description': 'Software Engineering Department'
            },
            {
                'name': 'Computer Science',
                'code': 'CS',
                'description': 'Computer Science Department'
            },
            {
                'name': 'Electrical Engineering',
                'code': 'EE',
                'description': 'Electrical Engineering Department'
            },
            {
                'name': 'Mechanical Engineering',
                'code': 'ME',
                'description': 'Mechanical Engineering Department'
            }
        ]

        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created department: {dept.name} ({dept.code})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Department already exists: {dept.name} ({dept.code})')
                )

    def assign_users_to_departments(self):
        """Assign existing users to departments"""
        # Get or create default department
        default_dept, created = Department.objects.get_or_create(
            code='SWE',
            defaults={
                'name': 'Software Engineering',
                'description': 'Software Engineering Department'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created default department: {default_dept.name}')
            )

        # Assign all existing users to the default department
        users = User.objects.all()
        assigned_count = 0

        for user in users:
            # Skip if user already has a department
            if hasattr(user, 'userdepartment') and user.userdepartment.is_active:
                continue

            # Create user-department relationship
            user_dept, created = UserDepartment.objects.get_or_create(
                user=user,
                defaults={
                    'department': default_dept,
                    'role': 'TEACHER' if not user.is_superuser else 'ADMIN'
                }
            )

            if created:
                assigned_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Assigned {user.username} to {default_dept.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully assigned {assigned_count} users to departments')
        )


