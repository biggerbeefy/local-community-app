import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):

    class Type(models.TextChoices):
        EVENT_REMINDER = 'event_reminder', 'Event reminder'
        POST_COMMENT = 'post_comment', 'New comment'
        POST_LIKES = 'post_likes', 'Likes milestone'
        GROUP_ACCEPTED = 'group_accepted', 'Group membership accepted'
        EVENT_ACCEPTED = 'event_accepted', 'Event RSVP accepted'

    ICONS = {
        Type.EVENT_REMINDER: '⏰',
        Type.POST_COMMENT: '💬',
        Type.POST_LIKES: '❤️',
        Type.GROUP_ACCEPTED: '✅',
        Type.EVENT_ACCEPTED: '🎟️',
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notif_type = models.CharField(max_length=20, choices=Type.choices)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=300, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username}: {self.message}"

    @property
    def icon(self):
        return self.ICONS.get(self.notif_type, '🔔')
