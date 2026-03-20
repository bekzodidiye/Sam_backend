import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.models import User, Company, Tariff, Sale, DailyReport

def run():
    # 1. Ensure basic companies and tariffs exist
    companies = ['Ucell', 'Uztelecom', 'Mobiuz', 'Beeline']
    company_objs = {}
    for c in companies:
        obj, _ = Company.objects.get_or_create(name=c)
        company_objs[c] = obj

        # Create at least one tariff per company
        Tariff.objects.get_or_create(name=f"Standard {c}", company=obj)

    # 2. Setup user
    username = "testuser"
    phone = "+998991234567"
    
    user, created = User.objects.get_or_create(username=username, phone=phone)
    user.set_password("testpass")
    user.role = 'operator'
    user.is_approved = True
    user.first_name = "Test"
    user.last_name = "User"
    user.plain_password = "testpass"
    user.save()

    print(f"User ready: {user.username} (Phone: {user.phone}, Pass: testpass)")

    # 3. Create mock data for 3 months
    now = timezone.now()
    tariffs = list(Tariff.objects.all())
    
    sales_created = 0
    reports_created = 0

    # Clean old mock data for this user
    Sale.objects.filter(user=user).delete()
    DailyReport.objects.filter(user=user).delete()

    # Iterate over the past 90 days
    for day_offset in range(90):
        target_date = now - timedelta(days=day_offset)
        
        # Decide if this day has sales (80% chance)
        if random.random() < 0.8:
            num_sales = random.randint(3, 10)
            
            for _ in range(num_sales):
                t = random.choice(tariffs)
                comp = t.company
                count = random.randint(1, 3)
                
                # Create sale with random bonus sometimes
                bonus = random.randint(1, 5) if random.random() < 0.3 else 0
                s = Sale.objects.create(
                    user=user,
                    company=comp,
                    count=count,
                    bonus=bonus,
                    tariff=t
                )
                
                # Bypass auto_now_add
                Sale.objects.filter(id=s.id).update(
                    date=target_date.date(),
                    timestamp=target_date
                )
                sales_created += 1
                
        # Decide if this day has a daily report (70% chance)
        if random.random() < 0.7:
            r = DailyReport.objects.create(
                user=user,
                summary=f"Bugun yaxshi ishladim! Kunlik reja bajarildi. (Mock data, {target_date.date()})"
            )
            # Bypass auto_now_add
            DailyReport.objects.filter(id=r.id).update(
                date=target_date.date(),
                timestamp=target_date
            )
            reports_created += 1

    print(f"Data generated successfully!")
    print(f"Total Sales generated: {sales_created}")
    print(f"Total Daily Reports generated: {reports_created}")

if __name__ == '__main__':
    run()
