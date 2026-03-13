from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..serializers import UserSerializer
from ..mixins import BroadcastMixin
from ..services import approve_user

User = get_user_model()

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'

class UserViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    broadcast_type = "USER"

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        if self.action in ['destroy']:
            return [IsManager()]
        return super().get_permissions()

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
        user = approve_user(user=user)
        self.broadcast("UPDATED", UserSerializer(user).data)
        return Response({'status': 'approved'})
