from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from apps.models import CheckIn, Sale, Message, Rule, MonthlyTarget, Tariff, DailyReport, SalesLink, Company
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    isApproved = serializers.BooleanField(source='is_approved', read_only=True)
    workingHours = serializers.JSONField(source='working_hours', required=False)
    workLocation = serializers.JSONField(source='work_location', required=False)
    workRadius = serializers.IntegerField(source='work_radius', default=100)
    workType = serializers.CharField(source='work_type', default='office')
    leagueHistory = serializers.JSONField(source='league_history', required=False)
    createdAt = serializers.DateTimeField(source='date_joined', read_only=True)
    photo = serializers.ImageField(source='avatar', required=False, allow_null=True)
    password = serializers.CharField(source='plain_password', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'nickname', 'firstName', 'lastName', 'role', 'isApproved', 
                  'password', 'photo', 'league', 'inventory', 'workingHours', 'department', 
                  'workLocation', 'workRadius', 'workType', 'achievements', 'leagueHistory', 'createdAt')

    def update(self, instance, validated_data):
        password = validated_data.pop('plain_password', None)
        if password:
            instance.set_password(password)
            instance.plain_password = password
        
        return super().update(instance, validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    # Support both case styles just to be safe
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    firstName = serializers.CharField(source='first_name', required=False, write_only=True)
    lastName = serializers.CharField(source='last_name', required=False, write_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('phone', 'nickname', 'password', 'first_name', 'last_name', 'firstName', 'lastName', 'role')

    def create(self, validated_data):
        # Prefer snake_case if available, otherwise use camelCase source
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        
        # Normalize phone
        from .utils import normalize_phone
        phone = validated_data['phone']
        normalized_phone = normalize_phone(phone)
        
        user = User.objects.create_user(
            phone=normalized_phone,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            role=validated_data.get('role', 'operator'),
            nickname=validated_data.get('nickname')
        )
        return user

class CheckInSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.get_full_name', read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)
    checkOutTime = serializers.DateTimeField(source='check_out_time', required=False)
    workingHours = serializers.JSONField(source='working_hours_snapshot', required=False)
    # Return photo URL for reads; exclude from write validation entirely
    photo = serializers.SerializerMethodField(read_only=True)
    # Use FloatField for GPS so high-precision coordinates don't fail DecimalField validation
    location_lat = serializers.FloatField()
    location_lng = serializers.FloatField()

    def get_photo(self, obj):
        if obj.photo:
            url = obj.photo.url
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(url)
            # Fallback if request is not in context (e.g. WebSocket broadcast)
            # If the URL is already absolute, just return it
            if url.startswith(('http://', 'https://')):
                return url
            # Return relative URL; frontend should handle the base URL 
            return url
        return None
    
    class Meta:
        model = CheckIn
        fields = ('id', 'userId', 'userName', 'timestamp', 'location_lat', 
                  'location_lng', 'photo', 'date', 'checkOutTime', 'workingHours')
        read_only_fields = ('userId', 'timestamp', 'date', 'photo')


class SaleSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.get_full_name', read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)
    company = serializers.CharField(write_only=True) # Raw input for name
    tariff = serializers.CharField(write_only=True) # Raw input for name

    class Meta:
        model = Sale
        fields = ('id', 'userId', 'userName', 'company', 'count', 'bonus', 'tariff', 'date', 'timestamp')
        read_only_fields = ('userId', 'date', 'timestamp')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['company'] = instance.company.name
        ret['tariff'] = instance.tariff.name
        return ret

    def create(self, validated_data):
        from .services import create_sale
        company_name = validated_data.pop('company')
        tariff_name = validated_data.pop('tariff')
        # user will be passed via serializer.save(user=...)
        user = validated_data.pop('user')
        return create_sale(user=user, company_name=company_name, tariff_name=tariff_name, **validated_data)
        
    def update(self, instance, validated_data):
        from .services import update_sale
        company_name = validated_data.pop('company', None)
        tariff_name = validated_data.pop('tariff', None)
        return update_sale(sale=instance, company_name=company_name, tariff_name=tariff_name, **validated_data)

class DailyReportSerializer(serializers.ModelSerializer):
    userId = serializers.CharField(source='user.id', read_only=True)
    locationLat = serializers.FloatField(source='location_lat', required=False, allow_null=True)
    locationLng = serializers.FloatField(source='location_lng', required=False, allow_null=True)
    
    class Meta:
        model = DailyReport
        fields = ('id', 'userId', 'date', 'summary', 'timestamp', 'photos', 'locationLat', 'locationLng')
        read_only_fields = ('userId', 'timestamp', 'date')

class MessageSerializer(serializers.ModelSerializer):
    senderName = serializers.CharField(source='sender.get_full_name', read_only=True)
    senderId = serializers.CharField(source='sender.id', read_only=True)
    recipientId = serializers.CharField(source='recipient.id', read_only=True, allow_null=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='recipient', write_only=True, required=False, allow_null=True
    )
    isRead = serializers.BooleanField(source='is_read', required=False)
    senderRole = serializers.CharField(source='sender.role', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'senderId', 'senderName', 'senderRole', 'recipientId', 'recipient_id', 'text', 'isRead', 'timestamp')
        read_only_fields = ('senderId', 'timestamp')

class RuleSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = Rule
        fields = ('id', 'content', 'createdAt', 'updatedAt')

class TariffSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    company = serializers.CharField(write_only=True) # Raw input for name

    class Meta:
        model = Tariff
        fields = ('id', 'company', 'name', 'createdAt')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['company'] = instance.company.name
        return ret

    def create(self, validated_data):
        from .services import create_tariff
        company_name = validated_data.pop('company')
        name = validated_data.pop('name')
        return create_tariff(company_name=company_name, name=name, **validated_data)

class MonthlyTargetSerializer(serializers.ModelSerializer):
    officeCounts = serializers.JSONField(source='office_counts', required=False)
    mobileOfficeCounts = serializers.JSONField(source='mobile_office_counts', required=False)

    class Meta:
        model = MonthlyTarget
        fields = ('id', 'month', 'targets', 'officeCounts', 'mobileOfficeCounts')

class SalesLinkSerializer(serializers.ModelSerializer):
    mobileUrl = serializers.URLField(source='mobile_url', required=False)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = SalesLink
        fields = ('id', 'name', 'url', 'mobileUrl', 'image', 'createdAt')

    def validate_url(self, value):
        if value and not value.startswith(('http://', 'https://')):
            return f'https://{value}'
        return value

    def validate_mobile_url(self, value):
        if value and not value.startswith(('http://', 'https://')):
            return f'https://{value}'
        return value

    def to_internal_value(self, data):
        # Allow passing urls without protocol by pre-validating/pre-fixing
        mutable_data = data.copy() if hasattr(data, 'copy') else data.dict() if hasattr(data, 'dict') else data.copy()
        
        for field in ['url', 'mobileUrl']:
            val = mutable_data.get(field)
            if val and isinstance(val, str) and not val.startswith(('http://', 'https://')):
                # DRF URLField validation happens after this, so we fix it here
                if hasattr(mutable_data, 'setlist'): # QueryDict
                    mutable_data[field] = f'https://{val}'
                else:
                    mutable_data[field] = f'https://{val}'
        
        return super().to_internal_value(mutable_data)

class NormalizedTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Validation is now cleanly handled by apps.backends.PhoneOrNicknameBackend
        return super().validate(attrs)
