from django.db import models
from users.models import User


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_link = models.URLField()
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "admin"}
    )
    transcriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"role": "transcriber"},
        related_name="transcribed_projects",
    )
    proofreader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"role": "proofreader"},
        related_name="proofread_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Transcript(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to="transcripts/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(
        max_length=20,
        choices=[("transcriber", "Transcriber"), ("proofreader", "Proofreader")],
    )  # 'transcriber' or 'proofreader'
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Ensures only one 'final' transcript per project-role pair."""
        if self.is_final:
            Transcript.objects.filter(
                project=self.project, role=self.role, is_final=True
            ).exclude(id=self.id).update(is_final=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.title} - {self.role}"


class Assignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)

    class Meta:
        unique_together = ("project", "user", "role")

    def __str__(self):
        return f"{self.user.email} -- {self.role} for {self.project.title}"
