
# task.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import EventReminder
from django.utils import timezone
import logging

# Configure logging
logger = logging.getLogger(__name__)
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import EventReminder

@shared_task
def send_event_reminder(event_reminder_id):
    try:
        event_reminder = EventReminder.objects.get(id=event_reminder_id)
        reminder_time = timezone.now()  # The time the reminder is sent

        # Prepare the event location based on location_type
        if event_reminder.event.location_type == 'inside':
            location = f"University of Antique\ \n"\
                       f"Department: {event_reminder.event.department},\n " \
                       f"Building: {event_reminder.event.building}, \n" \
                       f"Room: {event_reminder.event.room_number} \n"
        elif event_reminder.event.location_type == 'outside':
            location = f"University of Antique"\
                       f"Province: {event_reminder.event.province}, \n " \
                       f"Municipality: {event_reminder.event.municipality}, \n " \
                       f"Barangay: {event_reminder.event.barangay}, \n " \
                       f"Location: {event_reminder.event.specific_location}"
        else:
            location = "Location details not provided."

        # Prepare the email content
        subject = f"Reminder for {event_reminder.event.name}"
        message = (
            f"Event: {event_reminder.event.name}\n"
            f"Location: {location}\n"
            f"Description: {event_reminder.event.description}\n"
            f"Reminder Sent At: {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        send_mail(
            subject,
            message,
            'from@kasubaycampusconnect.com',
            [event_reminder.email],
            fail_silently=False
        )

        # Log the success
        logger.info(f"Reminder sent for event: {event_reminder.event.name} to {event_reminder.email} at {reminder_time}.")

        # Mark the reminder as sent
        event_reminder.email_sent = True
        event_reminder.save()

    except EventReminder.DoesNotExist:
        logger.error(f"EventReminder with ID {event_reminder_id} not found.")
    except Exception as e:
        logger.error(f"Error occurred while sending reminder for EventReminder ID {event_reminder_id}: {e}")






from celery import shared_task
from .models import UserStatus

@shared_task
def clean_inactive_user_status():
    UserStatus.clean_inactive_users(timeout_minutes=30)








# for testing

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_static_email():
    """
    A simple Celery task that sends a static email to a predefined recipient.
    """
    subject = "Test Email Subject"
    message = "This is a test message sent via Celery."
    recipient_list = ["myemailwarmachine@gmail.com"]  # Replace with a real email address for testing

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Use the default FROM email in settings.py
            recipient_list,
            fail_silently=False,
        )
        return f"Email sent to {recipient_list}"
    except Exception as e:
        return f"Error occurred: {e}"




@shared_task
def test_task():
    logger.info("Test task executed successfully")
    return "Done"

def simple_task():
    return "Hello, Celery"