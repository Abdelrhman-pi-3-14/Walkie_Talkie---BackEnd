from rest_framework import serializers

class ChatSerializer(serializers.Serializer):
    prompt = serializers.CharField()
    mode = serializers.ChoiceField(choices=['text', 'image'])
