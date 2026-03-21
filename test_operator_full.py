import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import User
from rest_framework.test import APIClient

u = User.objects.filter(first_name='Jaloliddin').first()
client = APIClient()
client.force_authenticate(user=u)

r = client.get('/api/v1/sales/')
data = r.data
if hasattr(r.data, 'get') and 'results' in r.data:
    data = r.data['results']
print(json.dumps(data, indent=2))
