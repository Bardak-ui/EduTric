from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("register/", views.register, name="register"),
]
