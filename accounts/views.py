from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from rest_framework import generics
from .serializer import RegisterSerializer , PasswordLogInSerializer, OtpLogInSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP
import random
from twilio.rest import Client
from rest_framework.permissions import AllowAny




def sendOTPviaSMS(phone_number,otp_code):
    account_sid = "AC0c76ac1e47793fca2d4f9b8096363308"
    auth_token = "c4359ea9e03e12efc5426498bf2614cc"    
    twilio_number = "+201016082339"      
    
    client = Client(account_sid=account_sid , auth_token = auth_token)
    
    message = client.messages.create(
        body=f"Your OTP code is: {otp_code}",
        from_=twilio_number,
        to=phone_number
    )



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, phone_number=user.phone_number, otp=otp_code)
        print(f"OTP for {user.phone_number}: {otp_code}")
        sendOTPviaSMS(phone_number=user.phone_number , otp_code= otp_code)
    
    
    
class PasswordLogIn(APIView):
    permission_classes = [AllowAny]
    
    def post(self , request):
        serializer = PasswordLogInSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
     
        user = serializer.validated_data['user']
   
        sendOTPviaSMS(phone_number=user.phone_number , otp_code= serializer.otp )
        return Response({
            "message": "Password correct. Please enter OTP.",
            "phone_number": user.phone_number
        }, status=status.HTTP_200_OK)


class OTPLogIn(APIView):
    permission_classes = [AllowAny]
    
    
    def post(self , request):
        serializer = OtpLogInSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
     
        user = serializer.validated_data['user']
        
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return Response({
            "message": "Login successful",
            "user_id": user.id,
            "phone_number": user.phone_number,
            "access": access_token,
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
   
    