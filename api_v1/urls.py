from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import (UserViewSet, CheckInViewSet, SaleViewSet, MessageViewSet, 
                    RuleViewSet, MonthlyTargetViewSet, TariffViewSet, 
                    DailyReportViewSet, SalesLinkViewSet, OperatorRatingViewSet, 
                    register_view, NormalizedTokenObtainPairView)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'checkins', CheckInViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'rules', RuleViewSet)
router.register(r'targets', MonthlyTargetViewSet)
router.register(r'tariffs', TariffViewSet)
router.register(r'reports', DailyReportViewSet)
router.register(r'sales_links', SalesLinkViewSet)
router.register(r'operator_ratings', OperatorRatingViewSet)


urlpatterns = [
    path('auth/register/', register_view, name='register'),
    path('auth/login/', NormalizedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
