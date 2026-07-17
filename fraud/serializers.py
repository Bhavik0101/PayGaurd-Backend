from rest_framework import serializers
from .models import FraudCheck

class FraudSerializer(serializers.ModelSerializer):
    class Meta:
        model=FraudCheck
        fields="__all__"