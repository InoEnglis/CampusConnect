from social.models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, read=False).count()
        return {'unread_notifications_count': notifications}
    return {'unread_notifications_count': 0}
