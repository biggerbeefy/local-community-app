from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_type', 'title', 'body', 'link_url', 'image']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
        }