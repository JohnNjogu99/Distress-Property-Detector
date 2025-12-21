from rest_framework import serializers
from .models import Property, Favorite

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'location', 
            'price', 'distress_score', 'source', 
            'created_at', 'updated_at'
        ]
