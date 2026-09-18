import uuid
from django.db import models
from django.conf import settings


class Event(models.Model):

    class Category(models.TextChoices):
        DEMONSTRATION = 'demonstration', 'Demonstration'
        MARCH = 'march', 'March'
        RALLY = 'rally', 'Rally'
        TOWN_HALL = 'town_hall', 'Town Hall'
        COMMUNITY_MEETING = 'community_meeting', 'Community Meeting'
        CANVASSING = 'canvassing', 'Political Canvassing'
        NEIGHBORHOOD_ORGANIZING = 'neighborhood_organizing', 'Neighborhood Organizing'
        ENVIRONMENTAL_CLEANUP = 'environmental_cleanup', 'Environmental Cleanup'
        FUNDRAISER = 'fundraiser', 'Fundraiser'
        PUBLIC_FORUM = 'public_forum', 'Public Forum'
        VIGIL = 'vigil', 'Peaceful Vigil'
        OTHER = 'other', 'Other'

    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public - anyone can see and RSVP'
        UNLISTED = 'unlisted', 'Unlisted - only accessible via direct link'
        PRIVATE = 'private', 'Private - invite only'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=3000, blank=True)
    category = models.CharField(max_length=30, choices=Category.choices)

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )

    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    # Location - general (always visible publicly)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    general_area = models.CharField(
        max_length=255, blank=True,
        help_text="e.g. 'Downtown Park' or 'Near City Hall' - shown publicly before RSVP"
    )

    # Location - precise (gated behind RSVP)
    exact_address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Visibility / privacy settings
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC)
    address_visible_to_all = models.BooleanField(
        default=False,
        help_text="If False, exact_address only shown to confirmed RSVPs"
    )

    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    # Capacity / logistics
    max_attendees = models.PositiveIntegerField(null=True, blank=True)  # null = unlimited

    image = models.ImageField(upload_to='events/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    class Meta:
        ordering = ['start_time']
        
class RSVP(models.Model):

    class Status(models.TextChoices):
        GOING = 'going', 'Going'
        INTERESTED = 'interested', 'Interested'
        WAITLISTED = 'waitlisted', 'Waitlisted'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rsvps'
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.GOING)
    checked_in = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # One RSVP per user per event - prevents duplicate sign-ups
        unique_together = ('event', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"


class HeroBanner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    eyebrow = models.CharField(
        max_length=100, blank=True,
        help_text="Small label above the headline, e.g. 'GET INTO IT'"
    )
    headline = models.CharField(
        max_length=200, blank=True,
        help_text="Leave blank to show the photo on its own, with no text overlay (e.g. if the photo already has messaging baked in)"
    )
    button_text = models.CharField(max_length=50, blank=True)
    button_url = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')

    is_active = models.BooleanField(
        default=True,
        help_text="Only one active banner is shown at a time, on the events page"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline or f"Banner ({self.created_at:%Y-%m-%d})"

    class Meta:
        ordering = ['-created_at']
