from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event, RSVP
from .forms import EventForm

def event_list(request):
    events = Event.objects.filter(visibility=Event.Visibility.PUBLIC).order_by('start_time')

    category = request.GET.get('category')
    if category:
        events = events.filter(category=category)

    city = request.GET.get('city')
    if city:
        events = events.filter(city__icontains=city)

    search = request.GET.get('search')
    if search:
        events = events.filter(title__icontains=search)

    return render(request, 'events/event_list.html', {'events': events, 'categories': Event.Category.choices, 'selected_category': category, 'selected_city': city, 'search_query': search,})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    user_rsvp = None
    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(event=event, user=request.user, status=RSVP.Status.GOING).first()

    can_see_address = event.address_visible_to_all or user_rsvp is not None

    return render(request, 'events/event_detail.html', {
        'event': event,
        'user_rsvp': user_rsvp,
        'can_see_address': can_see_address,
    })

@login_required
def rsvp_toggle(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    existing = RSVP.objects.filter(event=event, user=request.user).first()

    if existing:
        existing.delete()
    else:
        RSVP.objects.create(event=event, user=request.user, status=RSVP.Status.GOING)

    return redirect('event_detail', event_id=event.id)
@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()

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
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

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

