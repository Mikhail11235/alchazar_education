import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run Flower Celery monitoring tool'

    def handle(self, *args, **kwargs):
        os.system('celery -A alchazar_education flower --broker=redis://localhost:6379/0')
