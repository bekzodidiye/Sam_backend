from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import render
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.models import CheckIn, Sale, Message, Rule, MonthlyTarget, Tariff, DailyReport, SalesLink, OperatorRating
from .serializers import (UserSerializer, RegisterSerializer, CheckInSerializer, 
                          SaleSerializer, MessageSerializer, RuleSerializer, 
                          MonthlyTargetSerializer, TariffSerializer, 
                          DailyReportSerializer, SalesLinkSerializer,
                          OperatorRatingSerializer,
                          NormalizedTokenObtainPairSerializer)

class OperatorRatingViewSet(viewsets.ModelViewSet):
    queryset = OperatorRating.objects.all()
    serializer_class = OperatorRatingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Prevent double rating for the same operator on the same day
        operator = serializer.validated_data['operator']
        date = serializer.validated_data['date']
        OperatorRating.objects.filter(operator=operator, date=date).delete()
        
        serializer.save(rated_by=self.request.user)
        broadcast_data_update("NEW_RATING", group="everyone")

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("NEW_RATING", group="everyone")

    def perform_destroy(self, instance):
        instance.delete()
        broadcast_data_update("NEW_RATING", group="everyone")



User = get_user_model()

class NormalizedTokenObtainPairView(TokenObtainPairView):
    serializer_class = NormalizedTokenObtainPairSerializer

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'

def broadcast_data_update(update_type, data=None, group="everyone"):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "send_notification",
                    "message": {
                        "type": update_type,
                        "data": data or {}
                    }
                }
            )
            print(f"[WS BROADCAST] Sent '{update_type}' to group '{group}'")
    except Exception as e:
        print(f"[WS ERROR] Failed to broadcast '{update_type}': {e}")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        if self.action in ['destroy']:
            return [IsManager()]
        return super().get_permissions()

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("USER_UPDATED", serializer.data)

    def perform_destroy(self, instance):
        instance.delete()
        broadcast_data_update("USER_UPDATED")

    @decorators.action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['get'], permission_classes=[IsManager])
    def approvals(self, request):
        pending_users = User.objects.filter(is_approved=False)
        serializer = self.get_serializer(pending_users, many=True)
        return Response(serializer.data)

    @decorators.action(detail=True, methods=['post'], permission_classes=[IsManager])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.is_approved = True
        user.save()
        broadcast_data_update("USER_UPDATED", UserSerializer(user).data)
        return Response({'status': 'approved'})

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckInViewSet(viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Save without photo first
        instance = serializer.save(user=self.request.user)
        
        # Save photo if provided
        if 'photo' in request.FILES:
            instance.photo = request.FILES['photo']
            instance.save()
        
        # Re-serialize for fresh data with photo
        final_serializer = self.get_serializer(instance)
        broadcast_data_update("NEW_CHECKIN", data=final_serializer.data)
        
        headers = self.get_success_headers(final_serializer.data)
        return Response(final_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # We handle this manually in create() now
        pass

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("USER_UPDATED")

    def perform_destroy(self, instance):
        instance.delete()
        broadcast_data_update("USER_UPDATED")

    def get_queryset(self):
        if self.request.user.role == 'manager':
            return CheckIn.objects.all()
        return CheckIn.objects.filter(user=self.request.user)


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(user=user)
        
        # Update user inventory
        inventory = dict(user.inventory or {})
        company_name = instance.company.name
        total_to_remove = instance.count + instance.bonus
        
        current_amount = inventory.get(company_name, 0)
        inventory[company_name] = max(0, int(current_amount) - total_to_remove)
        
        user.inventory = inventory
        user.save()
        
        broadcast_data_update("NEW_SALE", data=SaleSerializer(instance).data)
        broadcast_data_update("USER_UPDATED", data=UserSerializer(user).data)

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_total = old_instance.count + old_instance.bonus
        old_company = old_instance.company.name
        
        instance = serializer.save()
        new_total = instance.count + instance.bonus
        new_company = instance.company.name
        
        user = instance.user
        inventory = dict(user.inventory or {})
        
        # Add back old total
        inventory[old_company] = int(inventory.get(old_company, 0)) + old_total
        # Remove new total
        inventory[new_company] = max(0, int(inventory.get(new_company, 0)) - new_total)
        
        user.inventory = inventory
        user.save()
        
        broadcast_data_update("NEW_SALE", data=SaleSerializer(instance).data)
        broadcast_data_update("USER_UPDATED", data=UserSerializer(user).data)

    def perform_destroy(self, instance):
        user = instance.user
        total_to_restore = instance.count + instance.bonus
        company_name = instance.company.name
        
        inventory = dict(user.inventory or {})
        inventory[company_name] = int(inventory.get(company_name, 0)) + total_to_restore
        
        user.inventory = inventory
        user.save()
        
        instance.delete()
        broadcast_data_update("NEW_SALE")
        broadcast_data_update("USER_UPDATED", data=UserSerializer(user).data)

    def get_queryset(self):
        if self.request.user.role == 'manager':
            return Sale.objects.all()
        return Sale.objects.filter(user=self.request.user)


class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        broadcast_data_update("NEW_REPORT", data=serializer.data)

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("NEW_REPORT", data=serializer.data)

    def perform_destroy(self, instance):
        instance.delete()
        broadcast_data_update("NEW_REPORT")

    def get_queryset(self):
        if self.request.user.role == 'manager':
            return DailyReport.objects.all()
        return DailyReport.objects.filter(user=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        message = serializer.save(sender=self.request.user)
        
        # Real-time WebSocket Notification
        channel_layer = get_channel_layer()
        notification_data = {
            "type": "send_notification",
            "message": {
                "type": "NEW_MESSAGE",
                "data": serializer.data
            }
        }
        
        if message.recipient:
            # Send to specific user
            async_to_sync(channel_layer.group_send)(
                f"user_{message.recipient.id}",
                notification_data
            )
        else:
            # If no recipient:
            # 1. If sender is manager -> Broadcast to everyone
            # 2. If sender is operator -> Only to managers
            if self.request.user.role == 'manager':
                async_to_sync(channel_layer.group_send)(
                    "everyone",
                    notification_data
                )
            else:
                async_to_sync(channel_layer.group_send)(
                    "managers",
                    notification_data
                )
        
        # Also trigger a global reload signal for those who should see it
        # Note: broadcast_data_update defaults to "everyone", we use custom logic above for per-user alerts
        # but the data refresh signal can be global or targeted. For simplicity, NEW_MESSAGE triggers sync for all.
        broadcast_data_update("NEW_MESSAGE", data=serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            # Managers see:
            # - Messages to them
            # - Messages they sent
            # - Messages to "all" (recipient is null)
            return Message.objects.filter(
                models.Q(recipient=user) | 
                models.Q(recipient__isnull=True) | 
                models.Q(sender=user)
            )
        else:
            # Operators see:
            # - Messages to them
            # - Messages they sent
            # - Messages from managers with no recipient (Broadcasts)
            return Message.objects.filter(
                models.Q(recipient=user) | 
                models.Q(sender=user) |
                models.Q(recipient__isnull=True, sender__role='manager')
            )

    @decorators.action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'read'})

class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()
        broadcast_data_update("RULE_UPDATED", group="everyone")

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("RULE_UPDATED", group="everyone")

    def perform_destroy(self, instance):
        instance.delete()
        broadcast_data_update("RULE_UPDATED", group="everyone")

class MonthlyTargetViewSet(viewsets.ModelViewSet):
    queryset = MonthlyTarget.objects.all()
    serializer_class = MonthlyTargetSerializer
    permission_classes = [IsManager]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def create(self, request, *args, **kwargs):
        month = request.data.get('month')
        instance = MonthlyTarget.objects.filter(month=month).first()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()
        broadcast_data_update("TARGET_UPDATED", group="everyone")

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("TARGET_UPDATED", group="everyone")

    def perform_destroy(self, instance):
        instance.delete()
        broadcast_data_update("TARGET_UPDATED", group="everyone")

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def perform_create(self, serializer):
        serializer.save()
        broadcast_data_update("TARIFF_UPDATED", group="everyone")

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("TARIFF_UPDATED", group="everyone")

    @decorators.action(detail=False, methods=['post'], url_path='remove')
    def remove_tariff(self, request):
        company = request.data.get('company')
        name = request.data.get('tariff') or request.data.get('name')
        Tariff.objects.filter(company__name=company, name=name).delete()
        broadcast_data_update("TARIFF_UPDATED", group="everyone")
        return Response(status=status.HTTP_204_NO_CONTENT)

class SalesLinkViewSet(viewsets.ModelViewSet):
    queryset = SalesLink.objects.all()
    serializer_class = SalesLinkSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def create(self, request, *args, **kwargs):
        print(f"[DEBUG] SalesLink Request Data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"[DEBUG] SalesLink Validation Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()
        broadcast_data_update("LINK_UPDATED", group="everyone")

    def perform_update(self, serializer):
        serializer.save()
        broadcast_data_update("LINK_UPDATED", group="everyone")

    def perform_destroy(self, instance):
        instance.delete()
        broadcast_data_update("LINK_UPDATED", group="everyone")
def index_view(request):
    return render(request, 'index.html')
