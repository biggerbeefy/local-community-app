from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'group', 'city', 'state', 'zip_code', 'general_area', 'exact_address', 'latitude', 'longitude', 'visibility', 'address_visible_to_all', 'start_time', 'end_time', 'max_attendees', 'image', 'is_draft',]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'is_draft': 'Save as draft (only visible to you)',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from groups.models import Group
            group_ids = user.group_memberships.filter(status='approved').values_list('group_id', flat=True)
            self.fields['group'].queryset = Group.objects.filter(id__in=group_ids)