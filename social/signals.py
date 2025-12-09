from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Notification, UserStatus, User, UserProfile
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in

@receiver(post_save, sender=Comment)
def create_notification_for_comment(sender, instance, created, **kwargs):
    if created:
        if instance.parent is None:  # Only create a notification for direct comments
            notification = Notification.objects.create(
                user=instance.post.author,  # Notify the post author
                message=f'New comment on your post: "{instance.comment[:20]}..."',
                notification_type='comment',  # Correctly use the type from NOTIFICATION_TYPES
                timestamp=timezone.now()
            )
            notification.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        


@receiver(user_logged_in)
def set_user_status_online(sender, request, user, **kwargs):
    # Ensure the user's status is set to online when they log in
    UserStatus.objects.get_or_create(user=user, defaults={'is_online': True})
    # If the status exists, just ensure it's marked as online
    user_status = UserStatus.objects.get(user=user)
    user_status.is_online = True
    user_status.save()