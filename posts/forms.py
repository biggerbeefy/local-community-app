from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_type', 'title', 'body', 'link_url', 'image']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
        }

from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment...'}),
        }