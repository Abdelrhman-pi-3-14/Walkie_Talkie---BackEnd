from django.db import models
from accounts.models import User



class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = "sessions"

    def __str__(self):
        return f"Chat {self.id} - {self.user}"


class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ("user", "User"),
        ("ai", "AI"),
    )



    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta : 
        db_table = "messages"
    
    def __str__(self):
        return f" message : {self.content}"
    
    
class GeneratedImage(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     prompt = models.TextField()
     image_url = models.URLField() 
     created_at = models.DateTimeField(auto_now_add=True)
     
     class Meta:
         db_table = "imges"
         
     def __str__(self):
        return f" image : {self.image_url}"

