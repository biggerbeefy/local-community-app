from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('mine/', views.my_events, name='my_events'),
    path('create/', views.event_create, name='event_create'),
    path('<uuid:event_id>/', views.event_detail, name='event_detail'),
    path('<uuid:event_id>/rsvp/', views.rsvp_toggle, name='rsvp_toggle'),
    path('<uuid:event_id>/rsvp/<uuid:rsvp_id>/approve/', views.rsvp_approve, name='rsvp_approve'),
    path('<uuid:event_id>/save/', views.event_save_toggle, name='event_save_toggle'),
    path('<uuid:event_id>/edit/', views.event_edit, name='event_edit'),
    path('<uuid:event_id>/delete/', views.event_delete, name='event_delete'),
]
