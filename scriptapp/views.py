from django.http import Http404
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework import status, generics, permissions
from users.models import User
from core.utils import get_next_user
from users.permissions import IsAdmin
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.db.models import Sum  # Import Sum for aggregation
from .models import (
    Project,
    Transcript,
    Assignment,
)  # Ensure Assignment and Project models are correctly imported
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

        transcriber_id = validated_data.pop("transcriber_id", None)
        proofreader_id = validated_data.pop("proofreader_id", None)

        # Assign transcriber
        transcriber = None
        if transcriber_id:
            transcriber = User.objects.filter(
                id=transcriber_id, role="transcriber"
            ).first()
            if not transcriber:
                raise ValidationError({"transcriber": ["Invalid transcriber ID"]})
        else:
            transcriber = get_next_user("transcriber")

        # Assign proofreader
        proofreader = None
        if proofreader_id:
            proofreader = User.objects.filter(
                id=proofreader_id, role="proofreader"
            ).first()
            if not proofreader:
                raise ValidationError({"proofreader": "Invalid proofreader ID"})
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
            # Admins see projects they created
            return Project.objects.filter(admin=user, is_archived=False)
        # Non-admins (clients) should potentially see projects they "own" if `Project` has a client field
        # or if `Assignment` defines client roles. Based on the current setup, it seems only admins create projects.
        # If a client can also be an admin, this would be fine. If 'client' is a separate role,
        # you'd need to define how clients are linked to projects.
        # For now, it raises PermissionDenied for non-admins as per your original code.
        raise PermissionDenied("You do not have permission to access this resource.")


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
        # Fix: use .exists() instead of .exist()
        if not Project.objects.filter(id=project_id).exists():
            raise NotFound("Project not found.")
        # Filter transcripts belonging to the specified project
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
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound("Project not found.")

        self.perform_destroy(instance)
        return Response(
            {"detail": "Project archived."}, status=status.HTTP_204_NO_CONTENT
        )


class AssignedProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Filter projects based on assignments
        # Use Assignment model to link users to projects by role
        if user.role == "transcriber":
            return Project.objects.filter(
                assignments__user=user,
                assignments__role="transcriber",
                is_archived=False,
            ).distinct()  # Use distinct to avoid duplicate projects if a project has multiple assignments for the same user (unlikely but good practice)
        elif user.role == "proofreader":
            return Project.objects.filter(
                assignments__user=user,
                assignments__role="proofreader",
                is_archived=False,
            ).distinct()
        elif user.role == "admin":
            # Admins can see all unarchived projects
            return Project.objects.filter(is_archived=False)
        raise PermissionDenied("You do not have permission to access this resource.")


class MarkTranscriptFinalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transcript_id):
        transcript = get_object_or_404(Transcript, id=transcript_id)

        if request.user.role != "admin":
            raise PermissionDenied("Only admins can mark final transcripts.")

        transcript.is_final = True
        transcript.save()
        return Response(
            {"detail": "Transcript marked as final."}, status=status.HTTP_200_OK
        )


class FinalTranscriptListView(generics.ListAPIView):
    serializer_class = TranscriptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        if not Project.objects.filter(id=project_id).exists():
            raise NotFound("Project not found.")
        return Transcript.objects.filter(project__id=project_id, is_final=True)


class UserSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        total_tasks = 0  # Define default
        total_revenue = 0.0  # Define default as float for easier calculation

        # Calculate total tasks (e.g., total assignments for the user)
        # Assuming an 'Assignment' means a 'task' for the user
        total_tasks = Assignment.objects.filter(user=user).count()

        # Calculate revenue based on FINALIZED Transcripts uploaded by the user
        if user.role == "transcriber":
            # Sum price of final transcripts uploaded by this transcriber
            revenue_sum_data = Transcript.objects.filter(
                uploaded_by=user, role="transcriber", is_final=True
            ).aggregate(total_price=Sum("price"))

            total_revenue = (
                revenue_sum_data["total_price"]
                if revenue_sum_data["total_price"] is not None
                else 0.0
            )

        elif user.role == "proofreader":
            # Sum price of final transcripts uploaded by this proofreader
            revenue_sum_data = Transcript.objects.filter(
                uploaded_by=user, role="proofreader", is_final=True
            ).aggregate(total_price=Sum("price"))

            total_revenue = (
                revenue_sum_data["total_price"]
                if revenue_sum_data["total_price"] is not None
                else 0.0
            )

        elif user.role == "admin":
            # Admin can see total revenue from all final transcripts
            revenue_sum_data = Transcript.objects.filter(is_final=True).aggregate(
                total_price=Sum("price")
            )

            total_revenue = (
                revenue_sum_data["total_price"]
                if revenue_sum_data["total_price"] is not None
                else 0.0
            )

        return Response(
            {
                "total_tasks": total_tasks,
                "total_revenue": float(
                    total_revenue
                ),  # Ensure it's a float for JSON serialization
                "activity_summary": "Your recent activity includes completing tasks and earning revenue.",
            },
            status=status.HTTP_200_OK,
        )
