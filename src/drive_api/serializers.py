from rest_framework import serializers
from .models import CDriveFile, CDriveUser

class CDriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveFile
        fields = ('file_name', 'file_owner', 'file_size')

class CDriveUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveUser
        exclude = ('shared_files',)
