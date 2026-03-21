import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import User
from rest_framework.test import APIClient
u = User.objects.filter(role='manager').first()
if not u: u = User.objects.first()
client = APIClient()
client.force_authenticate(user=u)
r = client.get('/api/v1/sales/')
print(json.dumps(r.data, indent=2))
