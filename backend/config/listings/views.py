# listings/views.py
from rest_framework import generics, serializers, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, Favorite, NotificationPreference
from .forms import PropertyCSVUploadForm
from .utils import process_csv, calculate_distress_score, get_market_average_price, notify_users

# -------------------------
# CSV Upload (Admin Only)
# -------------------------
class PropertyCSVUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, format=None):
        form = PropertyCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['csv_file']
            count = process_csv(file)
            return Response({'message': f'{count} properties uploaded successfully.'})
        return Response({'error': 'Invalid file.'}, status=400)

# -------------------------
# Property Endpoints
# -------------------------
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'location',
            'price', 'distress_score', 'source',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['distress_score', 'created_at', 'updated_at']

class PropertyListView(generics.ListCreateAPIView):
    queryset = Property.objects.all().order_by('-created_at')
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'distress_score', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        data = serializer.validated_data
        market_avg = get_market_average_price(data['location'])
        score = calculate_distress_score(
            price=data['price'],
            description=data.get('description', ''),
            market_average=market_avg,
        )
        property_obj = serializer.save(distress_score=score, source="api")
        notify_users(property_obj)

class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_update(self, serializer):
        data = serializer.validated_data
        market_avg = get_market_average_price(data['location'])
        score = calculate_distress_score(
            price=data['price'],
            description=data.get('description', ''),
            market_average=market_avg,
        )
        property_obj = serializer.save(distress_score=score)
        notify_users(property_obj)

# -------------------------
# Favorites Endpoints
# -------------------------
class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source='property',
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'property', 'property_id', 'added_at']
        read_only_fields = ['id', 'property', 'added_at']

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

# -------------------------
# Notification Preferences
# -------------------------
class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ['user']

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pref, created = NotificationPreference.objects.get_or_create(user=self.request.user)
        return pref
