from django.urls import re_path
from . import consumers
from social.consumers import UserStatusConsumer

websocket_urlpatterns = [
    # This is for the comment consumer, related to post-specific comments
    re_path(r'ws/social/(?P<post_id>\d+)/$', consumers.CommentConsumer.as_asgi()),
    
    # This is for the general chat rooms (not private chat)
    re_path(r'ws/social/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    
    # This is for private messaging between users (distinct from general chat and comments)
    re_path(r'ws/social/private/(?P<user_id>\d+)/$', consumers.ChatConsumer.as_asgi()),  
    
    
    re_path(r"^ws/user_status/$", UserStatusConsumer.as_asgi()),
]
