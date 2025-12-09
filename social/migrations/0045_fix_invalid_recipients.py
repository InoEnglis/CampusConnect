from django.db import migrations

def fix_invalid_senders(apps, schema_editor):
    Message = apps.get_model('social', 'Message')
    User = apps.get_model('auth', 'User')

    # Option: Delete invalid messages based on sender_id
    invalid_messages = Message.objects.filter(sender_id__isnull=False).exclude(sender__in=User.objects.all())
    invalid_messages.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('social', '0041_remove_message_is_read_remove_message_recipient_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_invalid_senders),
    ]
