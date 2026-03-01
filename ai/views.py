from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from serializer import ChatSerializer
from transformers import pipeline
from diffusers import StableDiffusionPipeline
from django.conf import settings
from rest_framework.permissions import AllowAny
import base64
from io import BytesIO







hugging_face_key = "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"
headers = {"Authorization": f"Bearer {hugging_face_key}"}


class HuggingFaceViewApi(APIView):
        
    permission_classes = [AllowAny] 
    
    def post(self,request):
        serializer = ChatSerializer(data = request)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data['prompt']
        mode = serializer.validated_data['mode']
        
        if mode == 'text':
              model_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
              payload = {"inputs": prompt}
              response = request.post(model_url, headers = headers , json = payload)
              data = response.json()
              return Response({
                "type": "text",
                "output": data[0]["generated_text"] if "generated_text" in data[0] else str(data)
            })
              
        elif mode == 'image':
            model_url = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
            payload = {"inputs": prompt}
            response = request.post(model_url, headers = headers , json = payload)
            image_data = response.content
            image_base64 = base64.b64decode(image_data).decode("uft-8")
            return Response(
                {
                    'type' : 'image',
                    'output': image_base64
                }
            )
            
        else:
            return Response(
                {"error": "Invalid mode, choose 'text' or 'image'"},
                status=status.HTTP_400_BAD_REQUEST
            )