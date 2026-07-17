from .models import CustomUser
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
       model=CustomUser
       fields=['email','password']
       #extra_kwargs is used in serializer
       # classes to provide additionaal configuration in a
       #  field without explicity defining it 
       extra_kwargs={
           'password':{'write_only':True}
       }
       #We are overriding the inbuilt create function of DRF ,
       # because we dont want to save password in plain text 
    def create(self, validated_data):
      #here we have used create_user because we want to hash the password 
      # .. in built create functions saves the password in plain text
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user