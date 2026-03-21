import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api_v1.views.sales_views import SaleViewSet
from apps.models import Sale
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.get('/api/v1/sales/')
view = SaleViewSet.as_view({'get': 'list'})
response = view(request)
print("Status Code:", response.status_code)

if isinstance(response.data, list):
    print("Is list, length:", len(response.data))
    if len(response.data) > 0:
        print(response.data[:2])
elif hasattr(response.data, 'get'):
    print("Is dict, count:", response.data.get('count', 'N/A'))
    print("Is dict, results:", len(response.data.get('results', [])))
else:
    print("Other type:", type(response.data))
    print(response.data)
