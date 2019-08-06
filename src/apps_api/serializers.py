from rest_framework import serializers
from .models import CDriveApplication

class CDriveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CDriveApplication
        fields = ('name', 'url')
