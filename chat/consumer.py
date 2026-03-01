import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, PrivateChat, GroupChat

class BaseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_type = self.scope['url_route']['kwargs']['chat_type']
        
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        if not self.room_id:
           await close()
           return
          
        self.user =self.scope['user']
        
 
        if not self.user.is_authenticated:
            await self.close()
            return
        
        
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        
        if not await self.authorize_user():
            await self.close()
            return
        

        self.room_group_name = self.get_group_name()
        
    
          
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.get_group_name(),
            self.channel_name
        )    
        
    async def receive(self, text_data = None, bytes_data = None):
        
      try:  
        data = json.loads(text_data)
      except:
          return
       
       
      if data.get("type") == "message":
           await self.handle_message(data)
           
      elif data.get("type") == "typing":
            await self.handle_typing(data)

      elif data.get("type") == "read":
            await self.handle_read(data)   
       
       
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))
   
       
       
    
    async def handle_message(self, data):
        raise NotImplementedError()

    async def handle_typing(self, data):
        raise NotImplementedError()

    async def handle_read(self, data):
        raise NotImplementedError()

    @database_sync_to_async
    def authorize_user(self):
        raise NotImplementedError()

    def get_group_name(self):
        raise NotImplementedError() 
    
    
    
class PrivateChatConsumer(BaseChatConsumer):
    
    def get_group_name(self):
        return f"private_{int(self.room_id)}"
    
    @database_sync_to_async
    def authorize_user(self):
        try:
            chat = PrivateChat.objects.get(id=self.room_id)
            return self.user == chat.user1 or self.user == chat.user2
        except PrivateChat.DoesNotExist:
            return False
    
    async def handle_message(self, data):
        message_data = await self.save_message(data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "data": message_data
            }
        )

    @database_sync_to_async
    def save_message(self, data):
        chat = PrivateChat.objects.get(id=self.room_id)

        message = Message.objects.create(
            sender=self.user,
            private_chat=chat,
            message_type=data["message_type"],
            text=data.get("text", "")
        )

        return {
            "type": "message",
            "id": message.id,
            "text": message.text,
            "sender_id": self.user.id,
            "created_at": str(message.created_at)
        }

    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "data": {
                    "type": "typing",
                    "user_id": self.user.id,
                    "is_typing": data.get("is_typing", False)
                }
            }
        )

    async def handle_read(self, data):
        message_ids = data.get("message_ids", [])

        await self.mark_as_read(message_ids)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "data": {
                    "type": "read",
                    "message_ids": message_ids,
                    "user_id": self.user.id
                }
            }
        )

    @database_sync_to_async
    def mark_as_read(self, message_ids):
        Message.objects.filter(
            id__in=message_ids,
            private_chat_id=self.room_id
        ).update(is_read=True)    
        
        

class GroupChatConsumer(BaseChatConsumer):
      
    def get_group_name(self):
        return f"group_{int(self.room_id)}"
    
    @database_sync_to_async
    def authorize_user(self):
      try:
         group = GroupChat.objects.get(id=self.room_id)
         return group.participants.filter(id=self.user.id).exists()
      except:
          GroupChat.DoesNotExist
          return False
      
      
    async def handle_message(self, data):
        message_data = await self.save_message(data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "data": message_data
            }
        )  
      
      
    @database_sync_to_async
    def save_message(self,data):
        group = GroupChat.objects.get(id= self.room_id)
        message = Message.objects.create(
            sender = self.user,
            group_chat = group,
            message_type = data['message_type'],
            text=data['text']
        )
        
        return {
            "type": "message",
            "id": message.id,
            "text": message.text,
            "sender_id": self.user.id,
            "created_at": str(message.created_at)
        }
    
    async def handle_typing(self , data):
        await self.channel_layer.group_send(
          self.room_group_name,
       {
        "type": "chat_message",
        "data": {
            "type": "read",
            "message_ids": [message_id],
            "user_id": self.user.id
        }
    }
)

        
    async def handle_read(self, data):
        message_id = data['message_id']
        await self.mark_group_read(message_id)
        await self.channel_layer.group_send(
            await self.channel_layer.group_send(
            self.room_group_name,
           {
            "type": "chat_message",
            "data": {
            "type": "read",
            "message_ids": [message_id],
            "user_id": self.user.id
        }
    }
)
 
         )         
         
    @database_sync_to_async
    def mark_group_read(self,id):
        messages = Message.objects.filter(
            id = id,
            group_chat_id=self.room_id
        )
        for message in messages:
            message.read_by.add(self.user)
             