from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from rest_framework import generics, permissions

from .models import Project, Transcript
from .serializers import ProjectSerializer, TranscriptSerializer
from users.permissions import IsAdmin, IsTranscriber, IsProofreader


class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAdmin]  

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)  


class ClientProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Project.objects.filter(admin=user)
        return Project.objects.none()  # Prevent non-admin access


class TranscriptUploadView(generics.CreateAPIView):
    serializer_class = TranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        role = self.request.user.role
        if role not in ['transcriber', 'proofreader']:
            raise PermissionDenied("Invalid role for uploading transcript")
        serializer.save(uploaded_by=self.request.user, role=role)


class TranscriptListView(generics.ListAPIView):
    serializer_class = TranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Transcript.objects.filter(project__id=project_id)
