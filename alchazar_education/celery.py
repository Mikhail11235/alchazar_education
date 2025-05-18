import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alchazar_education.settings')


app = Celery('alchazar_education')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
