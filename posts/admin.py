from django.contrib import admin
from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'group', 'post_type', 'created_at')
    list_filter = ('post_type', 'group')
    search_fields = ('title', 'body', 'author__username')


admin.site.register(Post, PostAdmin)