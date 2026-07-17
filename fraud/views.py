from django.shortcuts import render
from .models import FraudCheck
from .serializers import FraudSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
# Create your views here.

from rest_framework import generics

class FraudDetail(generics.ListAPIView):
    
    serializer_class=FraudSerializer
    def get_queryset(self):
        if self.request.user.is_staff==True:
            return FraudCheck.objects.all()
        else:
            return FraudCheck.objects.filter(
                transaction__merchant=self.request.user
                )
    permission_classes=[IsAuthenticated]

    