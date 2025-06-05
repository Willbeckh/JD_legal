from django.contrib import admin
from django.urls import include, path
from .views import welcome_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", welcome_view, name="root"),
    path("api/auth/", include("users.urls")),
    path("api/projects/", include("scriptapp.urls")),
]
