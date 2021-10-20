import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apptrix.settings')
app = Celery('apptrix')
import django
django.setup()
from main.models import User

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def send_email(self, user1_id, user2_id):
    user1 = User.objects.get(id=user1_id)
    user2 = User.objects.get(id=user2_id)
    template = "«Вы понравились {first_name}! Почта участника: {email}»"
    user1.email_user(
        message=template.format(first_name=user2.first_name,
                                email=user2.email),
        from_email=user2.email,
        subject="Apptrix"
    )
    user2.email_user(
        message=template.format(first_name=user1.first_name,
                                email=user1.email),
        from_email=user1.email,
        subject="Apptrix"
    )
