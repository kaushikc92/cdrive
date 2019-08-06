from rest_framework import serializers
from .models import CDriveFile

class CDriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveFile
        fields = ('name', 'owner', 'size')

class CDriveFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveFolder
        fields = ('name', 'owner')
