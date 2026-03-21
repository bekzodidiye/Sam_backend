import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import User
from rest_framework.test import APIClient

u = User.objects.filter(first_name='Jaloliddin').first()
if not u: u = User.objects.exclude(role='manager').first()
print("Testing as user:", u.get_full_name())

client = APIClient()
client.force_authenticate(user=u)
r = client.get('/api/v1/sales/')
data = r.data
if hasattr(r.data, 'get') and 'results' in r.data:
    data = r.data['results']
print("Sales visible to operator:")
for s in data:
    print(s.get('userName'), s.get('count'))
