from rest_framework import serializers
from .models import CDriveUser

class CDriveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveUser
        fields = ('username', 'email', 'firstname', 'lastname')

