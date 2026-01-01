# users/urls.py
from django.urls import path
from .views import login_view, register_view, logout_view, dashboard_view, UserRegisterView

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("api/register/", UserRegisterView.as_view(), name="api-register"),
]
