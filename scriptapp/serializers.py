from rest_framework import serializers
from .models import Project, Transcript

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['admin', 'created_at']

class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'uploaded_at', 'role']
