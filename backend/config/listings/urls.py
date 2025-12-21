from django.urls import path
from .views import PropertyListView, PropertyDetailView, FavoriteListView, FavoriteDetailView
from .views import PropertyCSVUploadView

urlpatterns = [
    path('properties/', PropertyListView.as_view(), name='property-list'),
    path('properties/<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/<int:pk>/', FavoriteDetailView.as_view(), name='favorite-detail'),
    path('properties/upload/', PropertyCSVUploadView.as_view(), name='property-upload'),
]
