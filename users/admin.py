from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Community Info', {'fields': ('bio', 'location_zip', 'is_verified_resident', 'profile_picture')}),
    )
    list_display = ('username', 'email', 'is_verified_resident', 'is_staff')

admin.site.register(CustomUser, CustomUserAdmin)
