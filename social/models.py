from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils.timezone import now
from django.utils import timezone
class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name}"

# Group model
class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    profile_image = models.ImageField(upload_to='uploads/group_images', blank=True, null=True, default='uploads/profile_pictures/default_profile.png')
    created_at = models.DateTimeField(auto_now_add=True)

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_groups')
    admins = models.ManyToManyField(User, related_name='admin_groups', blank=True)
    members = models.ManyToManyField(User, related_name='group_members', blank=True)

    is_private = models.BooleanField(default=False)
    join_mode = models.CharField(max_length=10, choices=[('auto', 'Auto-Approve'), ('manual', 'Manual Approval')], default='manual')

    hashtags = models.ManyToManyField('Hashtag', blank=True)
    banned_users = models.ManyToManyField(User, related_name='banned_groups', blank=True)
    post_approval_required = models.BooleanField(default=False)

    banner_color = models.CharField(max_length=7, default='#FFFFFF')
    
    def __str__(self):
        return self.name

    def add_admin(self, user):
        if self.admins.count() < 5:
            self.admins.add(user)
        else:
            raise ValueError("You can only have up to 5 admins in a group.")

    def is_admin(self, user):
        return user == self.creator or user in self.admins.all()
    
    def is_moderator(self, user):
        membership = self.membership_set.filter(user=user).first()
        return membership and membership.role == 'moderator'

    def is_banned(self, user):
        return user in self.banned_users.all()

    def is_muted(self, user):
        return MutedUser.objects.filter(group=self, user=user).exists()

    def ban_user(self, user):
        self.banned_users.add(user)
        self.members.remove(user)  
        self.save()

    def mute_user(self, user):
        MutedUser.objects.create(group=self, user=user)
        self.save()

    def kick_user(self, user):
        self.members.remove(user)
        self.save()

    def promote_to_moderator(self, user):
        membership = self.membership_set.filter(user=user).first()
        if membership:
            membership.role = 'moderator'
            membership.save()

    def demote_to_member(self, user):
        membership = self.membership_set.filter(user=user).first()
        if membership:
            membership.role = 'member'
            membership.save()


class GroupJoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='join_requests_set')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True, help_text="Optional message from the user")

    class Meta:
        unique_together = ('user', 'group')  

    def __str__(self):
        return f"{self.user.username} -> {self.group.name} ({self.status})"


class GroupRule(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='rules')
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.group.name})"
    

class FlaggedContent(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content_type = models.CharField(max_length=20)  # e.g., 'post', 'comment'
    content_id = models.PositiveIntegerField()
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    reported_at = models.DateTimeField(auto_now_add=True)

class MutedUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    muted_at = models.DateTimeField(auto_now_add=True)

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=[
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('editor', 'Editor')
    ], default='member')
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.urls import reverse


class Post(models.Model):
    body = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    video = models.FileField(upload_to='uploads/post_videos', blank=True, null=True)  #
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', related_name='posts', on_delete=models.CASCADE, null=True, blank=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='posts')
    
    def like_count(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.id)])

    def __str__(self):
        return self.body[:20]


class PostImage(models.Model):
    """Model for multiple images associated with a post."""
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/post_images')


class PostFile(models.Model):
    """Model for files associated with a post."""
    post = models.ForeignKey(Post, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/post_files')


@receiver(post_save, sender=Post)
def broadcast_new_post(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "posts",
            {
                "type": "post_message",
                "message": {
                    "author": instance.author.username,
                    "body": instance.body,
                    "created_on": instance.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                    "group": instance.group.name if instance.group else None
                }
            }
        )


# Comment model
class Comment(models.Model):
    comment = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return self.comment[:20]
    
class UserUnderInvestigation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investigation')
    started_at = models.DateTimeField(default=now)
    reason = models.TextField(blank=True)
    investigator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigations_started')

    def __str__(self):
        return f"{self.user.username} under investigation"

from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Academic choices
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Academic choices
COURSE_CHOICES = [
    ('BSIT', 'BSIT'),
    ('BSCS', 'BSCS'),
    ('BSIS', 'BSIS'),
    ('BLIS', 'BLIS'),
    # Add more as needed
]

YEAR_LEVEL_CHOICES = [
    ('1st Year', '1st Year'),
    ('2nd Year', '2nd Year'),
    ('3rd Year', '3rd Year'),
    ('4th Year', '4th Year'),
]

SECTION_CHOICES = [
    ('Section A', 'Section A'),
    ('Section B', 'Section B'),
    ('Section C', 'Section C'),
    ('Section D', 'Section D'),
    ('Section E', 'Section E'),
    ('Section F', 'Section F'),
    ('Section G', 'Section G'),
    ('Section H', 'Section H'),

    # Add more as needed
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    picture = models.ImageField(upload_to='uploads/profile_pictures', default='uploads/profile_pictures/default_profile.png', blank=True)
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    following = models.ManyToManyField(User, blank=True, related_name='following')
    is_email_verified = models.BooleanField(default=False)

    # New fields for setup
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)

    # Academic/Professional fields
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, blank=True, null=True)
    year_level = models.CharField(max_length=20, choices=YEAR_LEVEL_CHOICES, blank=True, null=True)
    course = models.CharField(max_length=50, choices=COURSE_CHOICES, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    # Separated Address fields
    province = models.CharField(max_length=100, blank=True, null=True)
    municipality = models.CharField(max_length=100, blank=True, null=True)
    barangay = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)

    current_work = models.CharField(max_length=100, blank=True, null=True)
    setup_complete = models.BooleanField(default=False)

    # New fields for banning and soft deleting
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    banned_until = models.DateTimeField(null=True, blank=True)

    def is_currently_banned(self):
        if self.is_banned and self.banned_until:
            if timezone.now() > self.banned_until:
                self.unban()
                return False
            return True
        return self.is_banned

    def delete(self, *args, **kwargs):
        """Soft delete the profile by setting deleted_at."""
        if not self.deleted_at:
            self.deleted_at = timezone.now()  
            self.save()
        else:
            super().delete(*args, **kwargs)

    def restore(self):
        """Restore the profile from soft delete by clearing the deleted_at field."""
        self.deleted_at = None
        self.save()
        
    def ban(self, duration_days=None):
        """Ban the user, optionally for a specified number of days."""
        self.is_banned = True
        if duration_days:
            self.banned_until = timezone.now() + timedelta(days=duration_days)
        self.save()

        # Create or update the BannedUser record
        BannedUser.objects.update_or_create(
            user=self.user, 
            defaults={
                'banned_at': timezone.now(),
                'ban_duration_days': duration_days or 0  # If no duration, it's permanent
            }
        )

    def unban(self):
        """Unban the user by setting is_banned to False and reactivating the user."""
        self.is_banned = False
        self.user.is_active = True  
        self.user.save()
        self.save()
        BannedUser.objects.filter(user=self.user).delete()

    @property
    def is_deleted(self):
        """Check if the user is in the trash (soft deleted)."""
        return bool(self.deleted_at)

    @property
    def is_temporarily_banned(self):
        """Check if the user is banned."""
        return self.is_banned

    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


    
    
class BannedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ban_record')
    banned_at = models.DateTimeField(auto_now_add=True)
    ban_duration_days = models.IntegerField(default=0)  # Field for storing ban duration in days

    def __str__(self):
        return self.user.username

    def is_banned_for(self, days):
        """Check if the user is currently banned for the specified number of days."""
        return (timezone.now() - self.banned_at).days <= days

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class Conversation(models.Model):
    CONVERSATION_TYPES = (
        ('global', 'Global'),
        ('private', 'Private'),
    )
    name = models.CharField(max_length=255, unique=True, default="default_room")
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=CONVERSATION_TYPES, default='global') 
    
    def __str__(self):
        return self.name
    
    def get_conversation_name(self, current_user):
        if self.type == 'global':
            return "Global Chat"
        
        other_participants = self.participants.exclude(id=current_user.id)
        if self.type == 'private' and other_participants.exists():
            participant_names = [participant.username for participant in other_participants]
            return '_'.join(participant_names)  # Show names of participants in private chat.
        return "Private Chat"  # Default return in case the participants list is empty.
    
    def latest_message(self):
        """Returns the latest message for this conversation."""
        return self.conversation_messages.order_by('-timestamp').first()

    def latest_message_is_unread(self, user):
        """Checks if the latest message in this conversation is unread for the specific user."""
        latest_message = self.latest_message()
        if latest_message:
            return MessageStatus.objects.filter(
                message=latest_message,
                user=user,
                is_read=False
            ).exists()
        return False
    
    def latest_message_content(self):
        """Returns the latest message content for this conversation."""
        latest_message = self.latest_message()
        return latest_message.content if latest_message else "No messages yet."
    
    def unread_messages_count(self, user):
        """Returns the count of unread messages for a specific user in this conversation."""
        return MessageStatus.objects.filter(
            message__conversation=self,
            user=user,
            is_read=False
        ).count()


class Message(models.Model):
    conversation = models.ForeignKey(
        "Conversation",
        on_delete=models.CASCADE,
        related_name="conversation_messages"
    )
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_messages"
    )
    content = models.TextField(blank=True, null=False, default="")  # Default set to empty string
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="message_replies"
    )
    image = models.ImageField(
        upload_to="messages/images/",
        blank=True,
        null=True
    )
    file = models.FileField(
        upload_to="messages/files/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.sender.username}: {self.content[:30] if self.content else "Attachment"}'
    
    @property
    def reply_to_content(self):
        if self.reply_to:
            return self.reply_to.content
        return None



class MessageStatus(models.Model):
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="message_statuses" 
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="status_messages" 
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Message '{self.message.id}' read by {self.user.username}: {self.is_read}"

    

    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment', 'Comment'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('reply', 'Reply'), 
        ('event', 'Event'),
       
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True) # The user who triggered the notification (the one sharing the post)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)  # The post being shared (optional for share type)
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='comment')  # Set default to 'comment'
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False) 
    read_at = models.DateTimeField(null=True, blank=True) 
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
    
class SharedPost(models.Model):
    original_post = models.ForeignKey(Post, related_name='shared_posts', on_delete=models.CASCADE)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_on = models.DateTimeField(default=timezone.now)
    shared_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.shared_by.username} shared {self.original_post}"
    
    def get_absolute_url(self):
        return f"/post/{self.original_post.id}/"
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Ensure one user can like a post only once

    def __str__(self):
        return f'{self.user.username} likes post {self.post.id}'
    

# report model
class Report(models.Model):
    REASON_CHOICES = (
        ('spam', 'Spam'),
        ('abuse', 'Abuse'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    additional_comments = models.TextField(blank=True, null=True)
    reported_on = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    is_evidence = models.BooleanField(default=False) 

    def __str__(self):
        return f'Report by {self.reporter} on {self.post}'
    

# Events
class Event(models.Model):
    LOCATION_CHOICES = [
        ('inside', 'Inside the University'),
        ('outside', 'Outside the University'),
    ]

    name = models.CharField(max_length=255, default='')
    description = models.TextField()
    date = models.DateTimeField()
    location_type = models.CharField(max_length=7, choices=LOCATION_CHOICES, default='inside')  # Location type: inside or outside
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    images = models.ManyToManyField('EventImage', blank=True)
    video = models.URLField(blank=True, null=True) 
    video_file = models.FileField(upload_to='event_videos/', blank=True, null=True) 
    files = models.ManyToManyField('EventFile', blank=True)

    # Inside the university fields
    department = models.CharField(max_length=255, blank=True, null=True)
    building = models.CharField(max_length=255, blank=True, null=True)
    room_number = models.CharField(max_length=255, blank=True, null=True)

    # Outside the university fields
    province = models.CharField(max_length=255, blank=True, null=True)
    municipality = models.CharField(max_length=255, blank=True, null=True)
    barangay = models.CharField(max_length=255, blank=True, null=True)
    specific_location = models.CharField(max_length=255, blank=True, null=True)
    registration_link = models.URLField(blank=True, null=True)


    def __str__(self):
        return self.name


class EventImage(models.Model):
    image = models.ImageField(upload_to='event_images/')
    
    def __str__(self):
        return f"Image for {self.id}"


class EventFile(models.Model):
    file = models.FileField(upload_to='event_files/')
    
    def __str__(self):
        return f"File for {self.id}"
    

class Rule(models.Model):
    
    number = models.PositiveIntegerField()  
    description = models.TextField()

    def __str__(self):
        return f"Rule {self.number}"
    
class EventReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)  # Make the email field nullable
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'Reminder for {self.event.name} to {self.email}'

class Feedback(models.Model):
    FEATURE_CHOICES = [
        ('Account Setup', 'Account Setup'),
        ('Post Creation', 'Post Creation'),
        ('Notifications', 'Notifications'),
        ('Profile Settings', 'Profile Settings'),
        ('Messages', 'Messages'),
        ('Search', 'Search'),
        ('Design', 'Design'),
        ('Event Creation', 'Event Creation'),
        ('Follower/Following', 'Follower/Following'),
        ('Groups', 'Groups'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    feature = models.CharField(max_length=50, choices=FEATURE_CHOICES, null=True, blank=True)
    feedback_text = models.TextField()
    screenshot = models.ImageField(upload_to='feedback_screenshots/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user or 'Anonymous'} on {self.created_at}"
    
    
class Evidence(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence for post {self.post.id} (Report ID: {self.report.id})"
    
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6, blank=False, null=False, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_verification_code(self):
        """Generate a 6-digit random verification code."""
        self.verification_code = ''.join(random.choices(string.digits, k=6))
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.verification_code}"
    
    


from django.db import models
from django.contrib.auth.models import User

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"

    @classmethod
    def clean_inactive_users(cls, timeout_minutes=30):
        """Mark users as offline if they haven't been active for a certain time."""
        from django.utils import timezone
        timeout = timezone.now() - timezone.timedelta(minutes=timeout_minutes)
        inactive_users = cls.objects.filter(last_activity__lt=timeout, is_online=True)
        for user_status in inactive_users:
            user_status.is_online = False
            user_status.save()
