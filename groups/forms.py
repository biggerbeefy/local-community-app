from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'is_public', 'is_discoverable']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }