from django.contrib import admin
from .models import CustomUser,Wallet
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Wallet)