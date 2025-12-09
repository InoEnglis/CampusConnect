from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_conversation_name(context, conversation):
    current_user = context['request'].user
    return conversation.get_conversation_name(current_user)
