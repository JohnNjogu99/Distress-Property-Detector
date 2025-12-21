from rest_framework import serializers
from .models import Notification
from listings.serializers import PropertySerializer

class NotificationSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'property', 'notification_type', 'message', 'sent', 'created_at']
