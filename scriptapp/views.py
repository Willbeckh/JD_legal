from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from rest_framework import generics, permissions
from core.utils import get_next_user
from .models import Project, Transcript, Assignment
from .serializers import AssignmentSerializer, ProjectSerializer, TranscriptSerializer
from users.permissions import IsAdmin
from users.models import User

class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAdmin]  

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        project = serializer.save(admin=self.request.user)  

        # chck for provided transcriber-id/proofreader_id
        transcriber = None
        proofreader = None
        
        transcriber_id = validated_data.pop('transcriber_id', None)
        proofreader_id = validated_data.pop('proofreader_id', None)

        # manual assignment if provided, else, fallback to round-robin
        if transcriber_id:
            transcriber = User.objects.filter(id=transcriber_id, role='transcriber').first()
        else:
            transcriber = get_next_user('transcriber')


        # get proofreader
        if proofreader_id:
            proofreader = User.objects.filter(id=proofreader_id, role='proofreader').first()
        else:
            proofreader = get_next_user('proofreader')

        if transcriber:
            Assignment.objects.create(project=project, user=transcriber, role='transcriber')
        if proofreader:
            Assignment.objects.create(project=project, user=proofreader, role='proofreader')

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

class AssignmentCreateView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]