from django.core.management.base import BaseCommand
from timetable.models import Department, UserDepartment, Subject, Teacher, Classroom, Batch, ScheduleConfig, TimetableEntry
from users.models import User

class Command(BaseCommand):
    help = 'Fix existing data by assigning departments and owners to existing records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-all',
            action='store_true',
            help='Fix all existing data by assigning departments and owners',
        )
        parser.add_argument(
            '--check-status',
            action='store_true',
            help='Check the current status of data and department assignments',
        )

    def handle(self, *args, **options):
        if options['check_status']:
            self.check_data_status()
        
        if options['fix_all']:
            self.fix_all_data()

    def check_data_status(self):
        """Check the current status of data and department assignments"""
        self.stdout.write(self.style.SUCCESS("=== DATA STATUS CHECK ==="))
        
        # Check departments
        dept_count = Department.objects.count()
        self.stdout.write(f"Departments: {dept_count}")
        
        # Check user departments
        user_dept_count = UserDepartment.objects.count()
        self.stdout.write(f"User-Department assignments: {user_dept_count}")
        
        # Check data without departments
        subjects_no_dept = Subject.objects.filter(department__isnull=True).count()
        teachers_no_dept = Teacher.objects.filter(department__isnull=True).count()
        classrooms_no_dept = Classroom.objects.filter(department__isnull=True).count()
        batches_no_dept = Batch.objects.filter(department__isnull=True).count()
        configs_no_dept = ScheduleConfig.objects.filter(department__isnull=True).count()
        
        self.stdout.write(f"Subjects without department: {subjects_no_dept}")
        self.stdout.write(f"Teachers without department: {teachers_no_dept}")
        self.stdout.write(f"Classrooms without department: {classrooms_no_dept}")
        self.stdout.write(f"Batches without department: {batches_no_dept}")
        self.stdout.write(f"Schedule configs without department: {configs_no_dept}")
        
        # Check users
        users_count = User.objects.count()
        self.stdout.write(f"Total users: {users_count}")
        
        # Check if default department exists
        try:
            default_dept = Department.objects.get(code='SWE')
            self.stdout.write(f"Default department exists: {default_dept.name}")
        except Department.DoesNotExist:
            self.stdout.write(self.style.WARNING("Default department (SWE) does not exist!"))

    def fix_all_data(self):
        """Fix all existing data by assigning departments and owners"""
        self.stdout.write(self.style.SUCCESS("=== FIXING EXISTING DATA ==="))
        
        # Step 1: Ensure default department exists
        default_dept, created = Department.objects.get_or_create(
            code='SWE',
            defaults={
                'name': 'Software Engineering',
                'description': 'Software Engineering Department'
            }
        )
        
        if created:
            self.stdout.write(f"Created default department: {default_dept.name}")
        else:
            self.stdout.write(f"Using existing department: {default_dept.name}")
        
        # Step 2: Assign all users to default department
        users = User.objects.all()
        assigned_users = 0
        
        for user in users:
            user_dept, created = UserDepartment.objects.get_or_create(
                user=user,
                defaults={
                    'department': default_dept,
                    'role': 'ADMIN' if user.is_superuser else 'TEACHER'
                }
            )
            
            if created:
                assigned_users += 1
                self.stdout.write(f"Assigned {user.username} to {default_dept.name}")
        
        self.stdout.write(f"Assigned {assigned_users} users to departments")
        
        # Step 3: Fix existing data by assigning department and owner
        # Get the first admin user as default owner
        try:
            default_owner = UserDepartment.objects.filter(role='ADMIN').first().user
        except:
            default_owner = User.objects.first()
        
        if not default_owner:
            self.stdout.write(self.style.ERROR("No users found! Cannot proceed."))
            return
        
        self.stdout.write(f"Using {default_owner.username} as default owner")
        
        # Fix subjects
        subjects_fixed = Subject.objects.filter(department__isnull=True).update(
            department=default_dept,
            owner=default_owner
        )
        self.stdout.write(f"Fixed {subjects_fixed} subjects")
        
        # Fix teachers
        teachers_fixed = Teacher.objects.filter(department__isnull=True).update(
            department=default_dept,
            owner=default_owner
        )
        self.stdout.write(f"Fixed {teachers_fixed} teachers")
        
        # Fix classrooms
        classrooms_fixed = Classroom.objects.filter(department__isnull=True).update(
            department=default_dept,
            owner=default_owner
        )
        self.stdout.write(f"Fixed {classrooms_fixed} classrooms")
        
        # Fix batches
        batches_fixed = Batch.objects.filter(department__isnull=True).update(
            department=default_dept,
            owner=default_owner
        )
        self.stdout.write(f"Fixed {batches_fixed} batches")
        
        # Fix schedule configs
        configs_fixed = ScheduleConfig.objects.filter(department__isnull=True).update(
            department=default_dept,
            owner=default_owner
        )
        self.stdout.write(f"Fixed {configs_fixed} schedule configs")
        
        # Fix timetable entries
        entries_fixed = TimetableEntry.objects.filter(department__isnull=True).update(
            department=default_dept,
            owner=default_owner
        )
        self.stdout.write(f"Fixed {entries_fixed} timetable entries")
        
        self.stdout.write(self.style.SUCCESS("=== DATA FIXING COMPLETED ==="))
        
        # Show final status
        self.check_data_status()


