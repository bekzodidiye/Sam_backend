from rest_framework import serializers
from apps.models import CheckIn

class CheckInSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.get_full_name', read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)
    checkOutTime = serializers.DateTimeField(source='check_out_time', required=False)
    workingHours = serializers.JSONField(source='working_hours_snapshot', required=False)
    photo = serializers.SerializerMethodField(read_only=True)
    location_lat = serializers.FloatField()
    location_lng = serializers.FloatField()

    def get_photo(self, obj):
        if obj.photo:
            url = obj.photo.url
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(url)
            if url.startswith(('http://', 'https://')):
                return url
            return url
        return None
    
    class Meta:
        model = CheckIn
        fields = ('id', 'userId', 'userName', 'timestamp', 'location_lat', 
                  'location_lng', 'photo', 'date', 'checkOutTime', 'workingHours')
        read_only_fields = ('userId', 'timestamp', 'date', 'photo')
