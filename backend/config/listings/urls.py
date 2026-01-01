# listings/urls.py
from django.urls import path, include
from .views import (
    PropertyListView, PropertyDetailView,
    PropertyCSVUploadView,
    FavoriteListView, FavoriteDetailView,
    NotificationPreferenceView
)
from .views_frontend import property_list_view

urlpatterns = [
    # Frontend UI
    path('', property_list_view, name='property-list-ui'),

    # API Endpoints
    path('api/properties/', PropertyListView.as_view(), name='property-list'),
    path('api/properties/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('api/properties/upload/', PropertyCSVUploadView.as_view(), name='property-upload'),

    path('api/favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('api/favorites/<int:pk>/', FavoriteDetailView.as_view(), name='favorite-detail'),

    path('api/notifications/', NotificationPreferenceView.as_view(), name='notifications'),

    # User auth
    path('api/auth/', include('users.urls')),
]
