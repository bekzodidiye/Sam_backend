import os
import django
import requests
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import User
from rest_framework_simplejwt.tokens import RefreshToken

u = User.objects.filter(role='manager').first()
if not u: u = User.objects.first()

refresh = RefreshToken.for_user(u)
token = str(refresh.access_token)

url = 'http://127.0.0.1:8003/api/v1/sales/'
headers = {'Authorization': f'Bearer {token}'}

try:
    resp = requests.get(url, headers=headers)
    print("HTTP STATUS:", resp.status_code)
    try:
        data = resp.json()
        print("Type:", type(data))
        if isinstance(data, list):
            print("List Length:", len(data))
            if len(data) > 0:
                print("First item:", json.dumps(data[0]))
        else:
            print("Dict Length:", len(data))
            print("Keys:", data.keys())
    except Exception as e:
        print("Error parsing json:", e)
        print("Text:", resp.text[:200])
except Exception as e:
    print("Network Error:", e)
