from rest_framework import generics
from .models import Property, Favorite
from .serializers import PropertySerializer, FavoriteSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .forms import PropertyCSVUploadForm
from .utils import process_csv, process_csv_file


class PropertyCSVUploadView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can upload

    def post(self, request, format=None):
        form = PropertyCSVUploadForm(request.FILES)
        if form.is_valid():
            file = form.cleaned_data['csv_file']
            count = process_csv(file)
            return Response({'message': f'{count} properties uploaded successfully.'})
        return Response({'error': 'Invalid file.'}, status=400)
# List all properties
class PropertyListView(generics.ListCreateAPIView):
    queryset = Property.objects.all().order_by('-created_at')
    serializer_class = PropertySerializer

# Get/Update/Delete a specific property
class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
class FavoriteListView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class FavoriteDetailView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
    
        return Favorite.objects.filter(user=self.request.user)