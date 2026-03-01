from django.contrib import admin
from ai.models import ChatMessage, ChatSession , GeneratedImage
# Register your models here.
admin.site.register(ChatMessage)  
admin.site.register(ChatSession) 
admin.site.register(GeneratedImage)
