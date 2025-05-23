# Generated by Django 5.1.6 on 2025-02-08 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0006_alter_scheduleconfig_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='user',
        ),
        migrations.AddField(
            model_name='teacher',
            name='email',
            field=models.EmailField(default=None, max_length=254, unique=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='name',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
