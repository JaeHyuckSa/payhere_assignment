# rest_framework_simplejwt
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# django
from django.urls import path

# users
from . import views

urlpatterns = [
    # Signup
    path("signup/", views.SingupView.as_view(), name="auth-signup"),
    
    # Login
    path("signin/", views.CustomTokenObtainPairView.as_view(), name="auth-signin"),
    path("signin/refresh/", TokenRefreshView.as_view(), name="auth-signin-refresh"),
    
    # Token verify
    path("verify/", TokenVerifyView.as_view(), name="auth-verify"),
]
