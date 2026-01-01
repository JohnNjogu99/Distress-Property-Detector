# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from rest_framework import generics, permissions, serializers
from listings.models import Favorite, NotificationPreference

# -------------------------
# Frontend Auth Views
# -------------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("property-list-ui")
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("property-list-ui")
    else:
        form = UserCreationForm()
    return render(request, "auth/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

# -------------------------
# Dashboard
# -------------------------
@login_required
def dashboard_view(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user).select_related("property")
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)

    if request.method == "POST":
        prefs.email_notifications = bool(request.POST.get("email_notifications"))
        prefs.sms_notifications = bool(request.POST.get("sms_notifications"))
        prefs.save()
        messages.success(request, "Notification preferences updated.")

    return render(request, "auth/dashboard.html", {
        "user": user,
        "favorites": favorites,
        "prefs": prefs,
    })

# -------------------------
# API Registration
# -------------------------
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
