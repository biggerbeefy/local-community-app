from django.urls import path
from . import views

urlpatterns = [
    path('group/<uuid:group_id>/', views.post_list, name='post_list'),
    path('group/<uuid:group_id>/create/', views.post_create, name='post_create'),
    path('<uuid:post_id>/', views.post_detail, name='post_detail'),
]