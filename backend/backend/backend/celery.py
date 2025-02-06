from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')
# Using SQLite as broker
app.conf.update(
    broker_url='sqla+sqlite:///' + os.path.join(settings.BASE_DIR, 'db.sqlite3'),
    result_backend='django-db',
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json'
)

app.autodiscover_tasks()