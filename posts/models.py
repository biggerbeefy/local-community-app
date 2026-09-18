import uuid
from django.db import models
from django.conf import settings


class Post(models.Model):

    class PostType(models.TextChoices):
        TEXT = 'text', 'Text'
        LINK = 'link', 'Link'
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')

    post_type = models.CharField(max_length=10, choices=PostType.choices, default=PostType.TEXT)
    title = models.CharField(max_length=300, blank=True)
    body = models.TextField(max_length=5000, blank=True)
    link_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Post by {self.author.username}"

    class Meta:
        ordering = ['-created_at']