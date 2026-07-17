from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# PART 1: THE MANAGER (The Engine)
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # This enforces your rule: Email is mandatory
        if not email:
            raise ValueError('The Email field must be set')
        
        # This standardizes the email (e.g., makes the domain lowercase)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        # This hashes the password securely before saving
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Superusers automatically get admin panel access
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# PART 2: THE MODEL (The Database Table)
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # We define email as unique so no two merchants can share one
    email = models.EmailField(unique=True)
    
    # Required Django fields for permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # We link the Model to the custom Manager we built above
    objects = CustomUserManager()

    # THE MAGIC LINE: This tells Django to use email for logging in
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class Wallet(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    balance=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    currency=models.CharField(max_length=10,default='INR')

    def __str__(self):
        return f"{self.user}-{self.balance}"
    
#Yaha par humne DJANGO signals ka use kara hai .. iska use tab krta hai jab koi naya user create hone ke baad 
#hume specifically koi code run krna hai basically automation ... Ab mai chahta hu ki jese hi koi naya user create ho 
#uska wallet automatically ban jaaye with 0 balance .. agar yeh nahi karenge toh naye users ka wallet hi initialize nahi hoga 
#isme created ek bool value hai true ya false agar user naya hai toh true hoga 
#instance mai naya user ka details hoti hai 
#sender humara custom user hai 
@receiver(post_save,sender=CustomUser)
def create_user_wallet(sender,instance,created,**kwargs):
    if created==True:
        Wallet.objects.create(user=instance)