from rest_framework import viewsets, permissions
from rest_framework.response import Response
from apps.models import DailyReport, MonthlyTarget
from ..serializers import DailyReportSerializer, MonthlyTargetSerializer
from .base import IsManager, broadcast_data_update

class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    def get_queryset(self):
        qs = DailyReport.objects.select_related('user')
        if self.request.user.role == 'manager':
            return qs.all()
        return qs.filter(user=self.request.user)

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

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
