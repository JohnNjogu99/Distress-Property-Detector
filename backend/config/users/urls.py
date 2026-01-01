from django.urls import path
from .views import UserRegisterView, register_view, login_view, logout_view

urlpatterns = [
    # API endpoint
    path("register/", UserRegisterView.as_view(), name="api-register"),

    # Frontend endpoints
    path("login/", login_view, name="login"),
    path("register-form/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
]
