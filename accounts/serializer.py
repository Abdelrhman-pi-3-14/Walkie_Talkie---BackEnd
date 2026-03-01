from rest_framework import serializers
from .models import User
from .models import OTP
from django.contrib.auth.password_validation import validate_password

# Create your views here.
class RegisterSerializer(serializers.ModelSerializer) :

    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta() :
      model = User
      fields = ('first_name','last_name', 'email','phone_number', 'password', 'password2' , 'gender', 'image_url' , 'bio')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password: password doesnt match !!"})
        return super().validate(attrs)
      
    def create(self,validated_data):
        validated_data.pop("password2") 
        user = User(
        user = User(
        username=str(uuid.uuid4()),
         **validated_data
          )
        
        **validated_data
         )
        user.set_password('password')        
        user.save()
        return user


class PasswordLogInSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True , write_only = True)
    
    class Meta :
        model = User
        fields = ['phone_number', 'password']
    
    
    def validate(self, data):
        phone = data.get('phone_number')
        password = data.get('password')
        
        try:
            user = User.objects.get(phone_number = phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("this phone is not exist ")
        
        if not user.check_password(password):
            raise serializers.ValidationError("wrong passord ")
        
        data['user'] = user 
        return data 
    




class OtpLogInSerializer(serializers.ModelSerializer):
      phone_number = serializers.CharField()
      otp = serializers.CharField(required=False, write_only=True)
      
      
      class Meta:
        model = OTP
        fields = ['phone_number', 'otp']

      
      def validate(self, data):
          phone = data.get('phone_number')
          otp_code = data.get('otp')
         
          otp = OTP.objects.filter(phone_number = phone , otp = otp_code , is_used = False).first()
          if not otp :
              raise serializers.ValidationError(" incorrect or this otp been used before")
    
          otp.is_used = True
          otp.save()
          data['user'] = otp.user
          return data
              
    