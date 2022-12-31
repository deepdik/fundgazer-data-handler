import os

from celery import Celery

from main import settings


def make_celery():
    """
    """
    celery = Celery(
        'dataHandler',
    )
    celery.conf.broker_url = settings.CELERY_BROKER_URL
    celery.conf.result_backend = settings.CELERY_RESULT_BACKEND
    celery.conf.include = ['api.utils.celery_tasks.data_handler']
    celery.conf.task_create_missing_queues = True
    celery.conf.task_acks_late = True
    celery.conf.worker_prefetch_multiplier = 1
    return celery
