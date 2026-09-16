from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event_list')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form})

from django.contrib.auth.decorators import login_required
from events.models import Event, RSVP

@login_required
def profile(request):
    organized_events = Event.objects.filter(organizer=request.user).order_by('start_time')
    rsvps = RSVP.objects.filter(user=request.user, status=RSVP.Status.GOING).select_related('event').order_by('event__start_time')

    return render(request, 'users/profile.html', {
        'organized_events': organized_events,
        'rsvps': rsvps,
    })

# Create your views here.
