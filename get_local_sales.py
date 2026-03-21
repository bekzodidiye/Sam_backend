import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.models import Sale
print("Sales from SQLite:", Sale.objects.count())
