import re
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

@register.filter
def link_hashtags(text):
    hashtag_pattern = r"#(\w+)"
    
    def replace(match):
        tag = match.group(1)
        url = reverse('hashtag-posts', args=[tag])
        return f'<a href="{url}" style="color: #57B9FF; font-weight:bold;">#{tag}</a>'
    return mark_safe(re.sub(hashtag_pattern, replace, text))
