from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'city', 'state', 'zip_code', 'general_area', 'exact_address', 'latitude', 'longitude', 'visibility', 'address_visible_to_all', 'start_time', 'end_time', 'max_attendees']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }