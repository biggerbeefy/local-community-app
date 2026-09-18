from django.contrib import admin
from .models import Event, RSVP, HeroBanner

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'organizer', 'city', 'start_time', 'visibility')
    list_filter = ('category', 'visibility', 'city')
    search_fields = ('title', 'description', 'city', 'zip_code')

class RSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'checked_in', 'created_at')
    list_filter = ('status', 'checked_in')
    search_fields = ('user__username', 'event__title')

class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'created_at')
    list_filter = ('is_active',)

admin.site.register(Event, EventAdmin)
admin.site.register(RSVP, RSVPAdmin)
admin.site.register(HeroBanner, HeroBannerAdmin)
