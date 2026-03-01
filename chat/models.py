import os
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


def attachment_upload_path(instance, filename):

    chat_id = instance.message.private_chat_id or instance.message.group_chat_id
    return f'chat_attachments/{chat_id}/{filename}'


class PrivateChat(models.Model):
    user1 = models.ForeignKey(
          'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='private_chats_as_user1'
    )
    user2 = models.ForeignKey(
          'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='private_chats_as_user2'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'private_chat'
        unique_together = [['user1', 'user2']] 

    def __str__(self):
        return f"Private chat: {self.user1.first_name} & {self.user2.first_name}"


class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(
          'accounts.User', 
        related_name='group_chats'
    )
    created_by = models.ForeignKey(
          'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_groups'
    )
    group_image_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_chat'

    def __str__(self):
        return self.name


class Message(models.Model):
    MESSAGE_TYPE_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    )

    sender = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='messages',
        db_index=True
    )
    private_chat = models.ForeignKey(
        PrivateChat, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='messages',
        db_index=True
    )
    group_chat = models.ForeignKey(
        GroupChat, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='messages',
        db_index=True
    )
    message_type = models.CharField(
        max_length=10, 
        choices=MESSAGE_TYPE_CHOICES,
        db_index=True
    )
    text = models.TextField(blank=True)  
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True
    )
    read_by = models.ManyToManyField(
    settings.AUTH_USER_MODEL,
    related_name="read_messages",
    blank=True
    )


    class Meta:
        db_table = 'chat_message'  
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(private_chat__isnull=False) & models.Q(group_chat__isnull=True)) |
                    (models.Q(private_chat__isnull=True) & models.Q(group_chat__isnull=False))
                ),
                name='exactly_one_chat'
            )
        ]
        indexes = [
            models.Index(fields=['private_chat', 'created_at']),
            models.Index(fields=['group_chat', 'created_at']),
        ]

    def clean(self):
        if (self.private_chat and self.group_chat) or (not self.private_chat and not self.group_chat):
            raise ValidationError(
                "Message must belong to either private chat or group chat, not both or neither."
            )
        if self.message_type == 'text' and not self.text:
            raise ValidationError("Text message must contain text.")
        if self.message_type != 'text' and self.text:
            raise ValidationError("Non‑text messages should not contain text.")

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        if self.message_type == 'text':
            return self.text[:20]
        return f"{self.message_type} from {self.sender.first_name}"


class MessageAttachment(models.Model):
    FILE_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    )

    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        db_index=True
    )
    file = models.FileField(
        upload_to=attachment_upload_path
    )
    file_type = models.CharField(
        max_length=20, 
        choices=FILE_TYPE_CHOICES
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_attachment'
        ordering = ['uploaded_at']

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return f"{self.file_type} attachment for message {self.message_id}"