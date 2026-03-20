from rest_framework import status, decorators, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers import RegisterSerializer, NormalizedTokenObtainPairSerializer

class NormalizedTokenObtainPairView(TokenObtainPairView):
    serializer_class = NormalizedTokenObtainPairSerializer

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
