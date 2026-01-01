# listings/urls.py
from django.urls import path
from .views import (
    PropertyListView, PropertyDetailView,
    FavoriteListView, FavoriteDetailView,
    NotificationPreferenceView,
    PropertyCSVUploadView,
    property_list_ui, dashboard_view, remove_favorite
)

urlpatterns = [
    path("api/properties/", PropertyListView.as_view(), name="property-list"),
    path("api/properties/<int:pk>/", PropertyDetailView.as_view(), name="property-detail"),
    path("api/favorites/", FavoriteListView.as_view(), name="favorite-list"),
    path("api/favorites/<int:pk>/", FavoriteDetailView.as_view(), name="favorite-detail"),
    path("api/preferences/", NotificationPreferenceView.as_view(), name="notification-preferences"),
    path("api/upload/", PropertyCSVUploadView.as_view(), name="property-upload"),

    path("properties/", property_list_ui, name="property-list-ui"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("remove-favorite/", remove_favorite, name="remove-favorite"),
]
