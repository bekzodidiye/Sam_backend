import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import User
from rest_framework.test import APIClient

u = User.objects.filter(role='operator').first()
client = APIClient()
client.force_authenticate(user=u)

r = client.get('/api/v1/users/')
data = r.data
if hasattr(r.data, 'get') and 'results' in r.data:
    data = r.data['results']
print("Users visible to operator:")
for user in data:
    print(user.get('firstName'), user.get('lastName'), "Role:", user.get('role'))
