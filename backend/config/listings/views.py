# listings/views.py

# =========================
# Django imports
# =========================
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

# =========================
# DRF imports
# =========================
from rest_framework import generics, serializers, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    AllowAny,
)
from django_filters.rest_framework import DjangoFilterBackend

# =========================
# Local imports
# =========================
from .models import Property, Favorite, NotificationPreference
from .forms import PropertyForm, PropertyCSVUploadForm
from .utils import (
    process_csv,
    calculate_distress_score,
    get_market_average_price,
    notify_users,
)

# ======================================================
# UI: Add Property (Manual Entry)
# ======================================================
@login_required
def add_property_view(request):
    if request.method == "POST":
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_obj = form.save(commit=False)

            market_avg = get_market_average_price(property_obj.location)
            property_obj.distress_score = calculate_distress_score(
                price=property_obj.price,
                description=property_obj.description,
                market_average=market_avg,
            )

            property_obj.source = "manual"
            property_obj.save()

            notify_users(property_obj)
            messages.success(request, "Property added successfully.")
            return redirect("property-list")
    else:
        form = PropertyForm()

    return render(request, "properties/add_property.html", {"form": form})


# ======================================================
# UI: Favorites
# ======================================================
@login_required
def add_favorite(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    Favorite.objects.get_or_create(user=request.user, property=property_obj)
    messages.success(request, f"Saved '{property_obj.title}' to favorites!")
    return redirect("property-list")


@require_POST
@login_required
def remove_favorite(request, favorite_id):
    fav = get_object_or_404(Favorite, pk=favorite_id, user=request.user)
    fav.delete()
    messages.success(request, "Favorite removed successfully.")
    return redirect("dashboard")


# ======================================================
# UI: Property List
# ======================================================
@login_required
def property_list_ui(request):
    properties = Property.objects.all().order_by("-created_at")
    return render(
        request,
        "properties/property_list.html",
        {"properties": properties},
    )


# ======================================================
# UI: Dashboard
# ======================================================
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
        return redirect("dashboard")

    return render(
        request,
        "auth/dashboard.html",
        {
            "user": user,
            "favorites": favorites,
            "prefs": prefs,
        },
    )


# ======================================================
# Admin: CSV Upload (API)
# ======================================================
class PropertyCSVUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        form = PropertyCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["csv_file"]
            count = process_csv(file)
            return Response(
                {"message": f"{count} properties uploaded successfully."}
            )
        return Response({"error": "Invalid file."}, status=400)


# ======================================================
# API: Property
# ======================================================
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "description",
            "location",
            "price",
            "distress_score",
            "source",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["distress_score", "created_at", "updated_at"]


class PropertyListView(generics.ListCreateAPIView):
    queryset = Property.objects.all().order_by("-created_at")
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["location"]
    search_fields = ["title", "description"]
    ordering_fields = ["price", "distress_score", "created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        data = serializer.validated_data
        market_avg = get_market_average_price(data["location"])
        score = calculate_distress_score(
            price=data["price"],
            description=data.get("description", ""),
            market_average=market_avg,
        )

        property_obj = serializer.save(
            distress_score=score,
            source="api",
        )
        notify_users(property_obj)


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_update(self, serializer):
        data = serializer.validated_data
        market_avg = get_market_average_price(data["location"])
        score = calculate_distress_score(
            price=data["price"],
            description=data.get("description", ""),
            market_average=market_avg,
        )
        property_obj = serializer.save(distress_score=score)
        notify_users(property_obj)


# ======================================================
# API: Favorites
# ======================================================
class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source="property",
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ["id", "property", "property_id", "added_at"]
        read_only_fields = ["id", "property", "added_at"]


class FavoriteListView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteDetailView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


# ======================================================
# API: Notification Preferences
# ======================================================
class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ["user"]


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pref, _ = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return pref
