from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def get_chat_messages(request, room_name):
    try:
        conversation = get_object_or_404(Conversation, name=room_name)
        conversation_name = conversation.get_conversation_name(request.user)

        if conversation.type == 'private':
            receiver = conversation.participants.exclude(id=request.user.id).first()
            receiver_name = receiver.profile.name if receiver and receiver.profile.name else receiver.username
            receiver_profile_pic = receiver.profile.picture.url if receiver and receiver.profile.picture else None
        else:
            receiver_name = "Global Chat"
            receiver_profile_pic = None

        messages = Message.objects.filter(conversation=conversation).select_related('sender', 'reply_to').order_by('timestamp')

        messages_data = []
        for message in messages:
            message_data = {
                "id": message.id,
                "sender": message.sender.username,
                "sender_profile_pic": message.sender.profile.picture.url if message.sender.profile.picture else None,
                "content": message.content,
                "timestamp": message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "reply_to_id": message.reply_to.id if message.reply_to else None,
                "reply_to_content": message.reply_to.content if message.reply_to else None,
            }

            if message.reply_to:
                message_data["reply_to_preview"] = {
                    "sender": message.reply_to.sender.username,
                    "content": (message.reply_to.content[:50] + "...") if message.reply_to.content else "Attachment",
                }

            messages_data.append(message_data)

        return JsonResponse({
            "receiver_name": receiver_name,
            "receiver_profile_pic": receiver_profile_pic,
            "conversation_name": conversation_name,
            "messages": messages_data,
        })

    except Exception as e:
        logger.error(f"Error fetching chat messages for room {room_name}: {e}")
        return JsonResponse({"error": "Failed to fetch messages."}, status=500)


from django.shortcuts import redirect
from .models import Message, Conversation

def send_file_message(request, conversation_id):
    if request.method == 'POST' and request.FILES.get('file'):
        conversation = Conversation.objects.get(id=conversation_id)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            file=request.FILES['file'],
            content=""
        )

        return redirect('conversation_detail', conversation_id=conversation_id)

    return redirect('conversation_detail', conversation_id=conversation_id)
