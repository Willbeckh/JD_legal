from django.db import models
from users.models import User

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_link = models.URLField()
    admin = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Transcript(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to='transcripts/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20)  # 'transcriber' or 'proofreader'
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - {self.role}"
