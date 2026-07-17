from .models import Transaction
from rest_framework import serializers

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transaction
        fields=['id','merchant','status','created_at','amount']
        #Yaha par merchant ko read only isliye kara h kyuki koi dusra merchant
        #  kisi aur merchant ki id daalkar payment kr skta hai ... read only se 
        # sirf id dikh skti hai par channge nahi ho skti
        read_only_fields = ['merchant','status']