# This will be imported by Django's WSGI/ASGI
from .celery import app as celery_app

__all__ = ('celery_app',)