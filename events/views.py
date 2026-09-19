from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from notifications.models import Notification
from .models import Event, RSVP, HeroBanner, SavedEvent
from .forms import EventForm

def event_list(request):
    events = Event.objects.filter(visibility=Event.Visibility.PUBLIC, is_draft=False).order_by('start_time')

    category = request.GET.get('category')
    if category:
        events = events.filter(category=category)

    city = request.GET.get('city')
    if city:
        events = events.filter(city__icontains=city)

    search = request.GET.get('search')
    if search:
        events = events.filter(title__icontains=search)

    banner = HeroBanner.objects.filter(is_active=True).first()

    return render(request, 'events/event_list.html', {'events': events, 'categories': Event.Category.choices, 'selected_category': category, 'selected_city': city, 'search_query': search, 'banner': banner,})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.is_draft and event.organizer != request.user:
        return HttpResponseForbidden("This event is still a draft.")

    user_rsvp = None
    is_saved = False
    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(event=event, user=request.user).first()
        is_saved = SavedEvent.objects.filter(event=event, user=request.user).exists()

    can_see_address = event.address_visible_to_all or (user_rsvp is not None and user_rsvp.status == RSVP.Status.GOING)
    going_count = event.rsvps.filter(status=RSVP.Status.GOING).count()

    pending_rsvps = None
    if request.user == event.organizer and event.visibility == Event.Visibility.PRIVATE:
        pending_rsvps = event.rsvps.filter(status=RSVP.Status.PENDING)

    return render(request, 'events/event_detail.html', {
        'event': event,
        'user_rsvp': user_rsvp,
        'can_see_address': can_see_address,
        'going_count': going_count,
        'is_saved': is_saved,
        'pending_rsvps': pending_rsvps,
    })

@login_required
def rsvp_toggle(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    existing = RSVP.objects.filter(event=event, user=request.user).first()

    if existing:
        existing.delete()
    else:
        is_private = event.visibility == Event.Visibility.PRIVATE and event.organizer != request.user
        status = RSVP.Status.PENDING if is_private else RSVP.Status.GOING
        RSVP.objects.create(event=event, user=request.user, status=status)

    return redirect('event_detail', event_id=event.id)

@login_required
def rsvp_approve(request, event_id, rsvp_id):
    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user:
        return HttpResponseForbidden("Only the organizer can approve RSVPs.")

    rsvp = get_object_or_404(RSVP, id=rsvp_id, event=event)
    rsvp.status = RSVP.Status.GOING
    rsvp.save()

    Notification.objects.create(
        recipient=rsvp.user,
        notif_type=Notification.Type.EVENT_ACCEPTED,
        message=f'Your RSVP for "{event.title}" was accepted',
        link=f'/events/{event.id}/',
    )

    return redirect('event_detail', event_id=event.id)

@login_required
def event_save_toggle(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    existing = SavedEvent.objects.filter(event=event, user=request.user).first()

    if existing:
        existing.delete()
    else:
        SavedEvent.objects.create(event=event, user=request.user)

    return redirect('event_detail', event_id=event.id)

@login_required
def my_events(request):
    tab = request.GET.get('tab', 'upcoming')
    now = timezone.now()

    if tab == 'saved':
        events = Event.objects.filter(saved_by__user=request.user).order_by('start_time')
    elif tab == 'going':
        events = Event.objects.filter(rsvps__user=request.user, rsvps__status=RSVP.Status.GOING).order_by('start_time')
    elif tab == 'past':
        events = Event.objects.filter(organizer=request.user, is_draft=False, start_time__lt=now).order_by('-start_time')
    elif tab == 'drafts':
        events = Event.objects.filter(organizer=request.user, is_draft=True).order_by('-updated_at')
    else:
        tab = 'upcoming'
        events = Event.objects.filter(organizer=request.user, is_draft=False, start_time__gte=now).order_by('start_time')

    return render(request, 'events/my_events.html', {'events': events, 'active_tab': tab})
@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(user=request.user)

    return render(request, 'events/event_form.html', {'form': form})
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user:
        return HttpResponseForbidden("You don't have permission to edit this event.")

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event, user=request.user)

    return render(request, 'events/event_form.html', {'form': form, 'editing': True})

@login_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.organizer != request.user:
        return HttpResponseForbidden("You don't have permission to delete this event.")

    if request.method == 'POST':
        event.delete()
        return redirect('event_list')

    return render(request, 'events/event_confirm_delete.html', {'event': event})

