from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.models import CheckIn, Sale, DailyReport
from ..serializers import CheckInSerializer, SaleSerializer, DailyReportSerializer
from ..selectors import get_checkins, get_sales, get_daily_reports
from ..mixins import BroadcastMixin

class CheckInViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer
    broadcast_type = "NEW_CHECKIN"

    def get_queryset(self):
        return get_checkins(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save without photo first
        instance = serializer.save(user=self.request.user)
        
        # Save photo if provided
        if 'photo' in request.FILES:
            instance.photo = request.FILES['photo']
            instance.save()
        
        # Re-serialize for fresh data with photo
        final_serializer = self.get_serializer(instance)
        self.broadcast(None, data=final_serializer.data)
        
        headers = self.get_success_headers(final_serializer.data)
        return Response(final_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SaleViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    broadcast_type = "NEW_SALE"

    def get_queryset(self):
        return get_sales()

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        self.broadcast(None, data=serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.broadcast(None, data=serializer.data)

class DailyReportViewSet(BroadcastMixin, viewsets.ModelViewSet):
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer
    broadcast_type = "NEW_REPORT"

    def get_queryset(self):
        return get_daily_reports(self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        self.broadcast(None, data=serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()
        self.broadcast(None, data=serializer.data)
