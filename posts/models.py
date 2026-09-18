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

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"

    class Meta:
        ordering = ['created_at']


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')