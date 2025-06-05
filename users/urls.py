from django.urls import path
from .views import (
    LogoutView,
    RegisterView,
    MeView,
    UserListView,
    UserUpdateView,
    UserDeleteView,
    CustomTokenObtainPairView,  # ← custom JWT login
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # JWT Auth
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # User registration and profile
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),  # returns authenticated user profile
    path("logout/", LogoutView.as_view(), name="logout"),
    # Admin/User management
    path("users/", UserListView.as_view(), name="user-list"),
    path("user/<int:id>/", UserUpdateView.as_view(), name="user-update"),
    path("user/<int:id>/delete/", UserDeleteView.as_view(), name="user-delete"),
]
