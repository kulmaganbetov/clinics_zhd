from django.urls import path
from .views import ChatView, ChatAPIView, ClearChatView

app_name = 'chatbot'

urlpatterns = [
    path('', ChatView.as_view(), name='chat'),
    path('api/send/', ChatAPIView.as_view(), name='api_send'),
    path('api/clear/', ClearChatView.as_view(), name='api_clear'),
]
