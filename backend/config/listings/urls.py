from django.urls import path
from . import views
from .views import (
    # API views
    PropertyListView,
    PropertyDetailView,
    FavoriteListView,
    FavoriteDetailView,
    NotificationPreferenceView,
    PropertyCSVUploadView,

    # UI views
    property_list_ui,
    dashboard_view,
    add_favorite,
    remove_favorite,
)

urlpatterns = [
    # UI ROUTES
    path("properties/", property_list_ui, name="property-list-ui"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("favorites/add/<int:property_id>/", add_favorite, name="add-favorite"),
    path("favorites/remove/<int:favorite_id>/", remove_favorite, name="remove-favorite"),
    # API ROUTESs
    path("api/properties/", PropertyListView.as_view(), name="api-property-list"),
    path("api/properties/<int:pk>/", PropertyDetailView.as_view(), name="api-property-detail"),
    path("api/favorites/", FavoriteListView.as_view(), name="api-favorite-list"),
    path("api/favorites/<int:pk>/", FavoriteDetailView.as_view(), name="api-favorite-detail"),
    path("api/notifications/", NotificationPreferenceView.as_view(), name="api-notifications"),
    path("api/upload-csv/", PropertyCSVUploadView.as_view(), name="api-upload-csv"),
    path("properties/", views.property_list_ui, name="property-list"),
    path("properties/add/", views.add_property_view, name="add-property"),
]
