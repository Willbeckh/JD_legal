from django.urls import path
from .views import (
    AssignedProjectListView,
    AssignmentCreateView,
    FinalTranscriptListView,
    MarkTranscriptFinalView,
    ProjectCreateView,
    ClientProjectListView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectUpdateView,
    TranscriptUploadView,
    TranscriptListView,
    UserSummaryView,
)

urlpatterns = [
    path("", ClientProjectListView.as_view(), name="project-list"),
    path("create/", ProjectCreateView.as_view(), name="project-create"),
    path("<int:id>/", ProjectDetailView.as_view(), name="project-detail"),
    path("<int:id>/update/", ProjectUpdateView.as_view(), name="project-update"),
    path("<int:id>/delete/", ProjectDeleteView.as_view(), name="project-delete"),
    path(
        "transcripts/upload/", TranscriptUploadView.as_view(), name="transcript-upload"
    ),
    path(
        "transcripts/<int:project_id>/",
        TranscriptListView.as_view(),
        name="transcript-list",
    ),
    path(
        "transcripts/<int:transcript_id>/mark-final/",
        MarkTranscriptFinalView.as_view(),
        name="mark-final",
    ),
    path(
        "projects/<int:project_id>/final-transcripts/",
        FinalTranscriptListView.as_view(),
        name="final-transcripts",
    ),
    path(
        "assignments/create/", AssignmentCreateView.as_view(), name="assignment-create"
    ),
    path("assigned/", AssignedProjectListView.as_view(), name="assigned-projects"),
    path("summary/", UserSummaryView.as_view(), name="user-summary"),
]
