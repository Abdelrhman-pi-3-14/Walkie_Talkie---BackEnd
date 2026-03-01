from django.urls import path
from .consumer import PrivateChatConsumer,GroupChatConsumer,BaseChatConsumer

websocket_urlpatterns = [
     path("ws/chat/<str:chat_type>/<int:room_id>/", PrivateChatConsumer.as_asgi()),
     path("ws/chat/<str:chat_type>/<int:room_id>/", GroupChatConsumer.as_asgi()),
]
