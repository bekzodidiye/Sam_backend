from rest_framework import serializers
from apps.models import Sale, SalesLink, Company, Tariff

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
        company_name = validated_data.pop('company')
        company_obj, _ = Company.objects.get_or_create(name=company_name)
        tariff_obj, _ = Tariff.objects.get_or_create(
            company=company_obj, 
            name=validated_data.get('name'),
            defaults=validated_data
        )
        return tariff_obj

class SaleSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.get_full_name', read_only=True)
    userId = serializers.CharField(source='user.id', read_only=True)
    company = serializers.CharField(write_only=True)
    tariff = serializers.CharField(write_only=True)

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
        company_name = validated_data.pop('company')
        tariff_name = validated_data.pop('tariff')
        company_obj, _ = Company.objects.get_or_create(name=company_name)
        tariff_obj, _ = Tariff.objects.get_or_create(company=company_obj, name=tariff_name)
        return Sale.objects.create(company=company_obj, tariff=tariff_obj, **validated_data)
        
    def update(self, instance, validated_data):
        if 'company' in validated_data:
            company_name = validated_data.pop('company')
            company_obj, _ = Company.objects.get_or_create(name=company_name)
            instance.company = company_obj
            
        if 'tariff' in validated_data:
            tariff_name = validated_data.pop('tariff')
            tariff_obj, _ = Tariff.objects.get_or_create(company=instance.company, name=tariff_name)
            instance.tariff = tariff_obj
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

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
        mutable_data = data.copy() if hasattr(data, 'copy') else data.dict() if hasattr(data, 'dict') else data.copy()
        for field in ['url', 'mobileUrl']:
            val = mutable_data.get(field)
            if val and isinstance(val, str) and not val.startswith(('http://', 'https://')):
                if hasattr(mutable_data, 'setlist'):
                    mutable_data.setlist(field, [f'https://{val}'])
                else:
                    mutable_data[field] = f'https://{val}'
        return super().to_internal_value(mutable_data)
