from django.urls import path
from django.shortcuts import render, get_object_or_404
from .views import BannedUserView, HashtagPostListView, PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, SearchView, set_event_reminder
from .views import group_detail, group_list, create_group, join_group, GetLatestPostsView, notifications_api, extract_and_assign_hashtags
from .views import PostListView, notifications_page, user_list_view, CustomLoginView, create_event, event_list, account_setup
from . import views
from . import chatView 

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>', CommentDeleteView.as_view(), name='comment-delete'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/follower/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/follower/remove', RemoveFollower.as_view(), name='remove-follower'),
    path('search/', SearchView.as_view(), name='search'),
    path('groups/create/', create_group, name='create_group'),
    path('groups/', group_list, name='group_list'), 
    path('groups/join/<int:group_id>/', join_group, name='join_group'),
    path('groups/<int:group_id>/', group_detail, name='group_detail'),
    path('post/new/', GetLatestPostsView.as_view(), name='get_latest_posts'),
    # new stuff
    path('api/notifications/', notifications_api, name='notifications-api'),
    path('notifications/', notifications_page, name='notification-page'),
    path('conversations/', views.conversation_list, name='conversation_list'), 
    path('navbar/', views.navbar_view, name='navbar_view'),
    path('unread-message-count/', views.get_unread_message_count, name='unread_message_count'),
    path('users/', user_list_view, name='user_list'),
    path('conversation-search/', views.conversation_search, name='conversation_search'),
    path('unread-notification-count/', views.unread_notifications_count, name='unread_notification_count'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('share/<int:post_id>/', views.share_post, name='share_post'),
    path('users/<str:username>/followers/', views.follower_list, name='follower-list'),

    path('post/<int:post_id>/report/', views.report_post, name='report-post'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path("create-event/", create_event, name="create_event"),
    path("events/", event_list, name="event_list"),
    path('profile/<int:user_id>/followers/', views.follower_list, name='follower_list'),
    path('profile/<int:user_id>/followed/', views.followed_list, name='followed_list'),
    path('messages/<str:room_name>/', chatView.get_chat_messages, name='get_chat_messages'),
    path("chat/<int:user_id>/", views.start_conversation, name="start-conversation"),

    path('account-setup/', account_setup, name='account-setup'),
    

    path('social/hashtag/<str:hashtag_name>/', HashtagPostListView.as_view(), name='hashtag-posts'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('groups/<int:group_id>/admin/requests/', views.admin_approval, name='admin_approval'),
    
    path('groups/<int:group_id>/create_rule/', views.create_group_rule, name='create_group_rule'),
    
    path('groups/<int:group_id>/settings/', views.group_settings, name='group_settings'),
    
    path('groups/<int:group_id>/manage/', views.manage_users, name='manage_users'),
    
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('about/', views.about_view, name='about'),
    path('set_event_reminder/<int:event_id>/', views.set_event_reminder, name='set_event_reminder'),
    
    path('unread-message-count/', views.get_unread_message_count, name='unread_message_count'),
    path('mark-message-as-read/<int:message_id>/', views.mark_message_as_read, name='mark_message_as_read'),
    path('banned/', BannedUserView.as_view(), name='banned_user'),
  

]
    


