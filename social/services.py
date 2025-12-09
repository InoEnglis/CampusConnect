# social/services.py
from .models import Notification
from django.contrib.auth.models import User

def create_notification(user: User, message: str):
    """
    Create a notification for a specific user with the given message.
    """
    Notification.objects.create(user=user, message=message)
