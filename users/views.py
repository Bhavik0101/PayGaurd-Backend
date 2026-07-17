from django.shortcuts import render
from .models import CustomUser
from .serializers import RegisterSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
# Create your views here.

class Register(CreateAPIView):
    queryset=CustomUser.objects.all()
    serializer_class=RegisterSerializer
    permission_classes=[AllowAny]