from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser ):
    
    
    first_name = models.CharField(max_length=100 , null = False , blank= False)

    last_name = models.CharField(max_length=100 , null = False , blank= False)
    
    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=20,unique=True,)

    gender = models.CharField(max_length=10,blank=True)

    image_url = models.TextField(null=True,blank=True)

    bio = models.TextField(null=True,blank=True )
    
    USERNAME_FIELD = 'phone_number'
    
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
     return f"user_name: {self.username}phone_number: {self.phone_number}"


class OTP(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    
    class Meta:
       db_table = 'otp'
           
    def __str__(self):
        return f"{self.user.phone_number} - {self.code}"
    
    
    
    