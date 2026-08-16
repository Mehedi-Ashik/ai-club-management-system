from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category',
            'event_date', 'venue', 'capacity', 'fee',
            'is_public', 'status',
        ]