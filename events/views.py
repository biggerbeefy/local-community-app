from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event, RSVP
from .forms import EventForm

def event_list(request):
    events = Event.objects.filter(visibility=Event.Visibility.PUBLIC).order_by('start_time')
    return render(request, 'events/event_list.html', {'events': events})

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
