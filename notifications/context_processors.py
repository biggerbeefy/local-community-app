from datetime import timedelta
from django.utils import timezone
from .models import Notification


def _generate_event_reminders(user):
    from events.models import RSVP

    now = timezone.now()
    soon = now + timedelta(hours=24)

    upcoming_rsvps = RSVP.objects.filter(
        user=user,
        status=RSVP.Status.GOING,
        event__start_time__gte=now,
        event__start_time__lte=soon,
    ).select_related('event')

    for rsvp in upcoming_rsvps:
        link = f'/events/{rsvp.event.id}/'
        already_notified = Notification.objects.filter(
            recipient=user,
            notif_type=Notification.Type.EVENT_REMINDER,
            link=link,
        ).exists()
        if not already_notified:
            Notification.objects.create(
                recipient=user,
                notif_type=Notification.Type.EVENT_REMINDER,
                message=f'"{rsvp.event.title}" starts {rsvp.event.start_time.strftime("%b %d, %I:%M %p")}',
                link=link,
            )


def notifications_panel(request):
    if not request.user.is_authenticated:
        return {}

    _generate_event_reminders(request.user)

    notifications = Notification.objects.filter(recipient=request.user)[:8]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return {
        'notif_list': notifications,
        'notif_unread_count': unread_count,
    }
