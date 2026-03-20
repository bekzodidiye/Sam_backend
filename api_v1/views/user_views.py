from rest_framework import viewsets, permissions, decorators
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.models import OperatorRating
from ..serializers import UserSerializer, OperatorRatingSerializer
from .base import IsManager, broadcast_data_update

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    # Assuming User model might have related fields like 'profile' or 'role'
    # If not, select_related might not be necessary here.
    # For a generic User model, often no direct foreign keys are accessed in a simple list/retrieve.
    # However, if the UserSerializer accesses related fields, this would be the place to add them.
    # For example, if User has a 'profile' OneToOneField: queryset = User.objects.select_related('profile').all()
    queryset = User.objects.only(
        'id', 'phone', 'username', 'first_name', 'last_name', 'role', 
        'is_approved', 'avatar', 'league', 'inventory', 'working_hours', 
        'department', 'work_location', 'work_radius', 'work_type', 
        'achievements', 'league_history', 'plain_password', 'date_joined'
    ).all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        if self.action in ['destroy']:
            return [IsManager()]
        return super().get_permissions()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

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
        
        # Real-time update
        broadcast_data_update("USER_UPDATED", data=UserSerializer(user).data)
        
        return Response({'status': 'approved'})

class OperatorRatingViewSet(viewsets.ModelViewSet):
    queryset = OperatorRating.objects.select_related('operator', 'rated_by').all()
    serializer_class = OperatorRatingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        operator = serializer.validated_data['operator']
        date = serializer.validated_data['date']
        OperatorRating.objects.filter(operator=operator, date=date).delete()
        serializer.save(rated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
