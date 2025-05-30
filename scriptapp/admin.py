from django.contrib import admin
from .models import Project, Transcript

# Register your models here.
admin.site.register([Project, Transcript])