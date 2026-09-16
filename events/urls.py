from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('<uuid:event_id>/', views.event_detail, name='event_detail'),
    path('<uuid:event_id>/rsvp/', views.rsvp_toggle, name='rsvp_toggle'),
]
