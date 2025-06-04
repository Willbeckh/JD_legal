from django.urls import path
from .views import (
    AssignmentCreateView,
    ProjectCreateView,
    ClientProjectListView,
    TranscriptUploadView,
    TranscriptListView,
)

urlpatterns = [
    path('projects/', ClientProjectListView.as_view(), name='project-list'),
    path('projects/create/', ProjectCreateView.as_view(), name='project-create'),
    path('transcripts/upload/', TranscriptUploadView.as_view(), name='transcript-upload'),
    path('transcripts/<int:project_id>/', TranscriptListView.as_view(), name='transcript-list'),
    path('assignments/create/', AssignmentCreateView.as_view(), name="assignment-create")
]
