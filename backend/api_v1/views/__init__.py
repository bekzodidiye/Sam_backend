from .auth import register_view, NormalizedTokenObtainPairView
from .users import UserViewSet
from .operational import CheckInViewSet, SaleViewSet, DailyReportViewSet
from .setup import MessageViewSet, RuleViewSet, MonthlyTargetViewSet, TariffViewSet, SalesLinkViewSet
from django.shortcuts import render

def index_view(request):
    return render(request, 'index.html')
