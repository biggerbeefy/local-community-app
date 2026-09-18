from django.contrib import admin
from .models import Group, GroupMembership


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'is_discoverable', 'creator', 'created_at')
    list_filter = ('is_public', 'is_discoverable')
    search_fields = ('name', 'description')


class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'status', 'joined_at')
    list_filter = ('role', 'status')
    search_fields = ('user__username', 'group__name')


admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMembership, GroupMembershipAdmin)

# Register your models here.
