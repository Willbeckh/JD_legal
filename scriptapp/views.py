from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, permissions
from users.models import User
from core.utils import get_next_user
from users.permissions import IsAdmin
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from .models import Project, Transcript, Assignment
from .serializers import (
    AssignmentSerializer,
    ProjectSerializer,
    ProjectUpdateSerializer,
    TranscriptSerializer,
)


class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        project = serializer.save(admin=self.request.user)

        # chck for provided transcriber-id/proofreader_id
        transcriber = None
        proofreader = None

        transcriber_id = validated_data.pop("transcriber_id", None)
        proofreader_id = validated_data.pop("proofreader_id", None)

        # manual assignment if provided, else, fallback to round-robin
        if transcriber_id:
            transcriber = User.objects.filter(
                id=transcriber_id, role="transcriber"
            ).first()
        else:
            transcriber = get_next_user("transcriber")

        # get proofreader
        if proofreader_id:
            proofreader = User.objects.filter(
                id=proofreader_id, role="proofreader"
            ).first()
        else:
            proofreader = get_next_user("proofreader")

        if transcriber:
            Assignment.objects.create(
                project=project, user=transcriber, role="transcriber"
            )
        if proofreader:
            Assignment.objects.create(
                project=project, user=proofreader, role="proofreader"
            )


class ClientProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Project.objects.filter(admin=user)
        return Project.objects.none()  # Prevent non-admin access


class TranscriptUploadView(generics.CreateAPIView):
    serializer_class = TranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        role = self.request.user.role
        if role not in ["transcriber", "proofreader"]:
            raise PermissionDenied("Invalid role for uploading transcript")
        serializer.save(uploaded_by=self.request.user, role=role)


class TranscriptListView(generics.ListAPIView):
    serializer_class = TranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return Transcript.objects.filter(project__id=project_id)


class AssignmentCreateView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class ProjectDetailView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class ProjectUpdateView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    lookup_field = "id"


class ProjectDeleteView(generics.DestroyAPIView):
    """Soft deletes a project

    Args:
        generics (int:id): id of a specific project

    Returns:
        JSON message: Entry has been removed.
    """

    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    lookup_field = "id"

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.save()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Project archived."}, status=status.HTTP_204_NO_CONTENT
        )


class AssignedProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "transcriber":
            return Project.objects.filter(transcriber=user, is_archived=False)
        elif user.role == "proofreader":
            return Project.objects.filter(proofreader=user, is_archived=False)
        elif user.role == "admin":
            return Project.objects.filter(is_archived=False)
        return Project.objects.none()


class MarkTranscriptFinalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transcript_id):
        transcript = get_object_or_404(Transcript, id=transcript_id)

        if request.user.role != "admin":
            return Response(
                {"detail": "Only admins can mark final transcripts."}, status=403
            )

        transcript.is_final = True
        transcript.save()
        return Response({"detail": "Transcript marked as final."}, status=200)


class FinalTranscriptListView(generics.ListAPIView):
    serializer_class = TranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return Transcript.objects.filter(project__id=project_id, is_final=True)
