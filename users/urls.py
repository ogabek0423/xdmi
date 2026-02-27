from .views import register, logout_view, profile, edit_profile
from django.urls import path, include

urlpatterns = [
    path("register/", register, name="register"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile, name="profile"),
    path("edit_profile/", edit_profile, name="edit_profile"),
]