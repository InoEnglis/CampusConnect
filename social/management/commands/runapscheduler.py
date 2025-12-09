import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management.base import BaseCommand
from social.models import Event

logger = logging.getLogger(__name__)

def send_event_reminder(event_id):
    event = Event.objects.filter(id=event_id).first()
    if event:
        logger.info(f"Reminder: {event.title} is starting soon!")

class Command(BaseCommand):
    help = "Starts the APScheduler."

    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.start()

        # Schedule reminders for upcoming events
        for event in Event.objects.all():
            if event.reminder_time:
                scheduler.add_job(
                    send_event_reminder,
                    trigger=DateTrigger(run_date=event.reminder_time),
                    args=[event.id],
                    id=f"event_{event.id}",
                    replace_existing=True,
                )

        self.stdout.write("Scheduler is running. Press Ctrl+C to exit.")
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
