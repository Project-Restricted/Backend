from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ModeratorRequestView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='custom-register'),
    path('login/', LoginView.as_view(), name='custom-login'),
    path('logout/', LogoutView.as_view(), name='custom-logout'),
    path('moderator-request/', ModeratorRequestView.as_view(), name='moderator-request'),
]
