from rest_framework import serializers
from .models import Project, Transcript, Assignment


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['admin', 'created_at']


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = ['id', 'project', 'file', 'uploaded_by',
                  'role', 'uploaded_at', 'is_final']
        read_only_fields = [
            'uploaded_by', 'role', 'uploaded_at', ]


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'file_link', 'transcriber', 'proofreader']
        extra_kwargs = {
            'transcriber': {'required': False},
            'proofreader': {'required': False},
        }
