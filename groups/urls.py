from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('<uuid:group_id>/', views.group_detail, name='group_detail'),
    path('<uuid:group_id>/edit/', views.group_edit, name='group_edit'),
    path('<uuid:group_id>/join/', views.group_join, name='group_join'),
    path('<uuid:group_id>/leave/', views.group_leave, name='group_leave'),
    path('<uuid:group_id>/approve/<uuid:membership_id>/', views.approve_member, name='approve_member'),
    path('<uuid:group_id>/promote/<uuid:membership_id>/', views.promote_admin, name='promote_admin'),
    path('<uuid:group_id>/ban/<uuid:membership_id>/', views.ban_member, name='ban_member'),
    path('<uuid:group_id>/unban/<uuid:membership_id>/', views.unban_member, name='unban_member'),
]