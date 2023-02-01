# django
from django.urls import path

# users
from . import views

urlpatterns = [
    # Signup
    path("signup/", views.SingupView.as_view(), name="auth-signup"),
]
