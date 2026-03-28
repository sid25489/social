import os
from celery import Celery
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialproject.settings')

app = Celery('socialproject')

# Handle Celery configuration with error logging
try:
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
    logger.info('Celery configured successfully')
except Exception as e:
    logger.warning(f'Celery configuration failed: {e}. Running in degraded mode.')
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
