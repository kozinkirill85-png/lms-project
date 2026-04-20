from celery.schedules import crontab

beat_schedule = {
    'deactivate-inactive-users-every-day': {
        'task': 'lms.tasks.deactivate_inactive_users',
        'schedule': crontab(hour=3, minute=0),  # Каждый день в 3:00
        'options': {'queue': 'celery'}
    },
}