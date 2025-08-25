@echo off
echo Running user cleanup script...
cd django-backend\backend
python manage.py delete_users_without_data --dry-run
pause 