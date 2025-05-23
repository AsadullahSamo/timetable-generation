# Generated by Django 5.1.7 on 2025-04-05 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0010_scheduleconfig_class_groups'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timetableentry',
            options={'ordering': ['day', 'period']},
        ),
        migrations.AddField(
            model_name='timetableentry',
            name='is_practical',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='timetableentry',
            name='day',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='timetableentry',
            name='period',
            field=models.IntegerField(),
        ),
    ]
