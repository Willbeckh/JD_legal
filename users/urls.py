from django.urls import path
from .views import RegisterView, LoginView, MeView, UserListView, UserUpdateView, UserDeleteView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('me/', MeView.as_view()),
    path('', UserListView.as_view(), name='user-list'),
    path('<int:id>/', UserUpdateView.as_view(), name='user-update'),
    path('<int:id>/delete/', UserDeleteView.as_view(), name='user-delete'),
]
