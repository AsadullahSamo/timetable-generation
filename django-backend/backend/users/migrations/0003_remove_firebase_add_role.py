# Generated manually to remove Firebase and restore role field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_user_role_user_firebase_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='firebase_uid',
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('ADMIN', 'Admin'), ('TEACHER', 'Teacher'), ('STUDENT', 'Student')], 
                default='TEACHER', 
                max_length=10
            ),
        ),
    ]
