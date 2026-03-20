from rest_framework import serializers
from apps.models import DailyReport, MonthlyTarget

class DailyReportSerializer(serializers.ModelSerializer):
    userId = serializers.CharField(source='user.id', read_only=True)
    locationLat = serializers.FloatField(source='location_lat', required=False, allow_null=True)
    locationLng = serializers.FloatField(source='location_lng', required=False, allow_null=True)
    
    def validate_photos(self, value):
        if not isinstance(value, list):
            return value
        for img in value:
            if len(img) > 15 * 1024 * 1024:
                raise serializers.ValidationError("Har bir rasm hajmi 10MB dan oshmasligi kerak")
        return value
    
    class Meta:
        model = DailyReport
        fields = ('id', 'userId', 'date', 'summary', 'timestamp', 'photos', 'locationLat', 'locationLng')
        read_only_fields = ('userId', 'timestamp', 'date')

class MonthlyTargetSerializer(serializers.ModelSerializer):
    officeCounts = serializers.JSONField(source='office_counts', required=False)
    mobileOfficeCounts = serializers.JSONField(source='mobile_office_counts', required=False)

    class Meta:
        model = MonthlyTarget
        fields = ('id', 'month', 'targets', 'officeCounts', 'mobileOfficeCounts')
