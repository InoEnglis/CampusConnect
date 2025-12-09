import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Comment, Conversation, Message, MessageStatus, Conversation, Notification
from django.utils import timezone
from channels.db import database_sync_to_async
from django.contrib.auth.models import User  
from datetime import datetime
from django.urls import reverse


# comment realtime websocket

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f"comments_{self.post_id}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connection accepted for post {self.post_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected for post {self.post_id}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        comment_text = text_data_json['comment']
        username = text_data_json['author']
        parent_id = text_data_json.get('parent_id')  # Get parent ID if it's a reply

        try:
            author = await database_sync_to_async(User.objects.get)(username=username)
        except User.DoesNotExist:
            print(f"User '{username}' not found.")
            return

        # Save comment or reply
        comment = await self.save_comment(comment_text, author, parent_id)
        await self.send_comment_to_clients(comment)

    @database_sync_to_async
    def create_notification(self, comment):
        # Notify the post author of a new comment
        Notification.objects.create(
            user=comment.post.author,
            message=f"New comment on your post: '{comment.comment[:20]}...'",
            notification_type='comment',
            timestamp=timezone.now(),
            read=False,
            link=reverse('post-detail', kwargs={'pk': comment.post.pk})
        )

    @database_sync_to_async
    def save_comment(self, comment_text, author, parent_id=None):
        parent_comment = None
        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)

        return Comment.objects.create(
            post_id=self.post_id,
            author=author,
            comment=comment_text,
            parent=parent_comment,
            created_on=timezone.now()
        )

    async def send_comment_to_clients(self, comment):
        comment_data = {
            'comment_id': comment.id,
            'comment': comment.comment,
            'author': comment.author.username,
            'created_on': comment.created_on.strftime("%Y-%m-%d %H:%M:%S"),
            'parent_id': comment.parent.id if comment.parent else None,  # Include parent ID for replies
        }

        # Send notification for the comment
        await self.create_notification(comment)

        # Send the new comment to all clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_comment',
                'message': json.dumps(comment_data)
            }
        )

    async def new_comment(self, event):
        # Send the comment data to the WebSocket
        await self.send(text_data=event['message'])



# chatting realtime websocket
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, User, Conversation, MessageStatus

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if it's a private chat by user_id
        user_id = self.scope['url_route']['kwargs'].get('user_id', None)
        if user_id:
            user_id = int(user_id)  # Convert user_id to an integer
            self.room_name = f'private_{sorted([user_id, self.scope["user"].id])[0]}_{sorted([user_id, self.scope["user"].id])[1]}'
        else:
            self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default_room')  # Global room

        self.room_group_name = f'chat_{self.room_name}'

        # Attempt to get or validate the conversation
        try:
            self.conversation = await database_sync_to_async(Conversation.objects.get)(name=self.room_name)
            print(f"Conversation found: {self.conversation.name}")
        except Conversation.DoesNotExist:
            print(f"Conversation with name '{self.room_name}' does not exist.")
            await self.close()
            return

        # Join the WebSocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)

        message_content = data.get('message')
        sender_username = data.get('sender')
        reply_to_id = data.get('reply_to')
        temp_id = data.get('temp_id') 
        if not message_content:
            print("Empty message received.")
            return
        try:
            sender = await database_sync_to_async(User.objects.get)(username=sender_username)
            print(f"Sender found: {sender.username}")
        except User.DoesNotExist:
            print(f"User '{sender_username}' not found.")
            return

        # Create the message object, including reply if applicable
        if reply_to_id:
            try:
                parent_message = await database_sync_to_async(Message.objects.get)(id=reply_to_id)
                print(f"Reply to message: {parent_message.id}")
                message = await database_sync_to_async(Message.objects.create)( 
                    conversation=self.conversation, sender=sender, content=message_content, reply_to=parent_message
                )
                reply_to_content = parent_message.content  # Get the content of the original message
            except Message.DoesNotExist:
                print(f"Parent message with ID {reply_to_id} does not exist.")
                return
        else:
            message = await database_sync_to_async(Message.objects.create)( 
                conversation=self.conversation, sender=sender, content=message_content
            )
            reply_to_content = None  # No reply content if it's a new message

        await database_sync_to_async(self.create_unread_message_status)(message)

        # Send the message to the WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': sender.username,
                'content': message_content,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'reply_to': reply_to_id,
                'reply_to_content': reply_to_content,  # Include the original message's content
                'message_id': message.id,
                'temp_id': temp_id,  
            }
        )

    async def chat_message(self, event):
        sender = event['sender']
        content = event['content']
        timestamp = event['timestamp']
        reply_to = event.get('reply_to')
        reply_to_content = event.get('reply_to_content')  # Get the reply_to_content from the event
        message_id = event['message_id']

        print(f"Sending mMessage: {sender} - {content} (ID: {message_id})")

        # Send the message content to WebSocket
        await self.send(text_data=json.dumps({
            'sender': sender,
            'content': content,
            'timestamp': timestamp,
            'reply_to': reply_to,
            'reply_to_content': reply_to_content, 
            'message_id': message_id,
        }))

        # Mark the message as read for the current user
        await database_sync_to_async(self.mark_message_as_read)(message_id)

    # Method to create unread message status for all participants except the sender
    def create_unread_message_status(self, message):
        for participant in message.conversation.participants.all():
            if participant != message.sender:  # Don't mark sender's own messages as unread
                MessageStatus.objects.create(
                    message=message,
                    user=participant,
                    is_read=False
                )

    # Method to mark message as read for a specific user
    def mark_message_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            # Mark the message as read for the current user
            message_status = MessageStatus.objects.get(message=message, user=self.scope['user'])
            message_status.is_read = True
            message_status.save()
        except MessageStatus.DoesNotExist:
            pass

# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import UserStatus
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
import json

class UserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            await self.update_user_status(True)  # Set user as online when they connect

        self.group_name = f"user_status_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.update_user_status(False)  # Set user as offline when they disconnect

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def update_user_status(self, is_online):
        status, created = UserStatus.objects.get_or_create(user=self.user)
        status.is_online = is_online
        status.last_activity = timezone.now()  # Update the last activity timestamp
        status.save()

