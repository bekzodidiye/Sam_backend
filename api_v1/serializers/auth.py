from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    firstName = serializers.CharField(source='first_name', required=False, write_only=True)
    lastName = serializers.CharField(source='last_name', required=False, write_only=True)
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ('phone', 'username', 'nickname', 'password', 'first_name', 'last_name', 'firstName', 'lastName', 'role')

    def create(self, validated_data):
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        username = validated_data.get('nickname', validated_data.get('username'))
        
        phone = validated_data['phone']
        clean_digits = ''.join(filter(str.isdigit, str(phone)))
        normalized_phone = f'+{clean_digits}' if clean_digits else ''
        
        user = User.objects.create_user(
            phone=normalized_phone,
            username=username,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            role=validated_data.get('role', 'operator')
        )
        return user

class NormalizedTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user_model = get_user_model()
        username_field = user_model.USERNAME_FIELD
        
        identifier = attrs.get(username_field) or attrs.get('phone') or attrs.get('username')
        
        if identifier:
            identifier = str(identifier)
            user = user_model.objects.filter(username=identifier).first()
            
            if not user:
                normalized_phone = ''.join(filter(str.isdigit, identifier))
                if normalized_phone:
                    user = user_model.objects.filter(phone=normalized_phone).first()
                    if not user:
                        user = user_model.objects.filter(phone=f"+{normalized_phone}").first()
            
            if user:
                attrs[username_field] = user.username
                if username_field != 'username':
                    attrs['username'] = user.username
                
        return super().validate(attrs)
