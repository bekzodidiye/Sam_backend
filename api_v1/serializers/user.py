from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.models import OperatorRating

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
    nickname = serializers.CharField(source='username', required=False)

    class Meta:
        model = User
        fields = ('id', 'phone', 'nickname', 'firstName', 'lastName', 'role', 'isApproved', 
                  'password', 'photo', 'league', 'inventory', 'workingHours', 'department', 
                  'workLocation', 'workRadius', 'workType', 'achievements', 'leagueHistory', 'createdAt')

    def update(self, instance, validated_data):
        if 'phone' in validated_data:
            clean_digits = ''.join(filter(str.isdigit, str(validated_data['phone'])))
            validated_data['phone'] = f'+{clean_digits}' if clean_digits else ''
            
        password = validated_data.pop('plain_password', None)
        if password:
            instance.set_password(password)
            instance.plain_password = password
        
        return super().update(instance, validated_data)

class OperatorRatingSerializer(serializers.ModelSerializer):
    operatorId = serializers.CharField(source='operator.id', read_only=True)
    ratedById = serializers.CharField(source='rated_by.id', read_only=True)
    operator_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='operator', write_only=True)
    
    class Meta:
        model = OperatorRating
        fields = ('id', 'operatorId', 'operator_id', 'ratedById', 'date', 'stars', 'comment', 'timestamp')
        read_only_fields = ('ratedById', 'timestamp')
