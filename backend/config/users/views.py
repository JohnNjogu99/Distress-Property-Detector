from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from rest_framework import generics, permissions, serializers
from django.contrib.auth.models import User

# -------------------------
# Frontend Login View
# -------------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("property-list-ui")  # redirect to listings page
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})

# -------------------------
# Frontend Register View
# -------------------------
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect("property-list-ui")
    else:
        form = UserCreationForm()
    return render(request, "auth/register.html", {"form": form})

# -------------------------
# Frontend Logout View
# -------------------------
def logout_view(request):
    logout(request)
    return redirect("login")

# -------------------------
# API Registration Serializer
# -------------------------
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
        )

# -------------------------
# API Registration View
# -------------------------
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
