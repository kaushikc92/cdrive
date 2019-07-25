from rest_framework import serializers
from .models import CDriveFile, CDriveUser, CDriveApplication

class CDriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveFile
        fields = ('file_name', 'file_owner', 'file_size')

class CDriveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveUser
        fields = ('username', 'email', 'firstname', 'lastname')

class CDriveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveApplication
        fields = ('name', 'url')
