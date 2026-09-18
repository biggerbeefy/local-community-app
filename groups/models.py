import uuid
from django.db import models
from django.conf import settings


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=150)
    description = models.TextField(max_length=2000, blank=True)

    is_public = models.BooleanField(default=True, help_text="If False, joining requires admin approval")
    is_discoverable = models.BooleanField(default=True, help_text="If False, group won't appear in search/browse")
    posts_visible_to_non_members = models.BooleanField(
        default=True,
        help_text="If True, anyone can view posts even without joining. Only applies to private groups (public groups' posts are always visible)."
    )
    member_list_public = models.BooleanField(
        default=False,
        help_text="If True, non-members can view the group's member list."
    )

    profile_picture = models.ImageField(upload_to="groups/", blank=True, null=True)
    banner_image = models.ImageField(upload_to="groups/banners/", blank=True, null=True)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class GroupMembership(models.Model):

    class Role(models.TextChoices):
        MEMBER = 'member', 'Member'
        MODERATOR = 'moderator', 'Moderator'
        ADMIN = 'admin', 'Admin'

    class Status(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        PENDING = 'pending', 'Pending Approval'
        BANNED = 'banned', 'Banned'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.APPROVED)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"

    class Meta:
        unique_together = ('group', 'user')
        ordering = ['-joined_at']

        