from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('start/', views.start_conversation, name='start_conversation'),
    path('<uuid:user_id>/', views.conversation_detail, name='conversation_detail'),
    path('<uuid:user_id>/send/', views.send_message, name='send_message'),
]
