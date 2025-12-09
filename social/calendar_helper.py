from allauth.socialaccount.models import SocialToken
from googleapiclient.discovery import build

def get_calendar_service(user):
    token = SocialToken.objects.get(account__user=user, account__provider='google')
    service = build(
        'calendar', 
        'v3', 
        credentials=token.get_token_obj()
    )
    return service
