from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.models import CheckIn
from ..serializers import CheckInSerializer
from .base import broadcast_data_update

class CheckInViewSet(viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        instance = serializer.save(user=self.request.user)
        
        if 'photo' in request.FILES:
            instance.photo = request.FILES['photo']
            instance.save()
        
        final_serializer = self.get_serializer(instance)
        # Real-time update
        broadcast_data_update("NEW_CHECKIN", final_serializer.data)
        
        headers = self.get_success_headers(final_serializer.data)
        return Response(final_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        pass

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


    def get_queryset(self):
        qs = CheckIn.objects.select_related('user')
        if self.request.user.role == 'manager':
            return qs.all()
        return qs.filter(user=self.request.user)
