from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'is_public', 'is_discoverable', 'posts_visible_to_non_members', 'member_list_public', 'profile_picture', 'banner_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }