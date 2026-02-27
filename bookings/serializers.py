from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    service_name = serializers.ReadOnlyField(source='service.name')
    can_cancel = serializers.ReadOnlyField()
    in_progress = serializers.ReadOnlyField(source='is_in_progress')

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_email', 'service', 'service_name',
            'start_time', 'end_time', 'people_count', 'total_price',
            'status', 'can_cancel', 'in_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_price', 'status', 'created_at', 'updated_at',
                            'user_email', 'service_name', 'can_cancel', 'in_progress']