@echo off
echo WARNING: This will delete users without data!
echo.
cd django-backend\backend
python manage.py delete_users_without_data
pause 