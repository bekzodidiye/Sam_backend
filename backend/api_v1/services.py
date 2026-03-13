from typing import Any, Dict, Optional
from django.contrib.auth import get_user_model
from apps.models import Sale, Company, Tariff, Message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

def create_sale(*, user: User, company_name: str, tariff_name: str, **data: Any) -> Sale:
    """Create a new sale along with the company/tariff if they don't exist."""
    company_obj, _ = Company.objects.get_or_create(name=company_name)
    tariff_obj, _ = Tariff.objects.get_or_create(company=company_obj, name=tariff_name)
    
    sale = Sale.objects.create(
        user=user,
        company=company_obj,
        tariff=tariff_obj,
        **data
    )
    return sale

def update_sale(*, sale: Sale, company_name: Optional[str] = None, tariff_name: Optional[str] = None, **data: Dict[str, Any]) -> Sale:
    """Update an existing sale and handle changing company/tariff strings."""
    if company_name is not None:
        company_obj, _ = Company.objects.get_or_create(name=company_name)
        sale.company = company_obj
        
    if tariff_name is not None:
        tariff_obj, _ = Tariff.objects.get_or_create(company=sale.company, name=tariff_name)
        sale.tariff = tariff_obj
        
    for key, value in data.items():
        setattr(sale, key, value)
    sale.save()
    return sale

def create_tariff(*, company_name: str, name: str, **data: Dict[str, Any]) -> Tariff:
    """Create a new tariff along with the company if it doesn't exist."""
    company_obj, _ = Company.objects.get_or_create(name=company_name)
    tariff_obj, _ = Tariff.objects.get_or_create(
        company=company_obj, 
        name=name,
        defaults=data
    )
    return tariff_obj

def dispatch_message_notifications(*, sender: User, recipient: Optional[User], message_data: Any):
    """Send real-time WebSocket notifications based on sender/recipient rules."""
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
        
    notification_data = {
        "type": "send_notification",
        "message": {
            "type": "NEW_MESSAGE",
            "data": message_data
        }
    }
    
    if recipient:
        # Send to specific user
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}",
            notification_data
        )
    else:
        # If no recipient:
        # 1. If sender is manager -> Broadcast to everyone
        # 2. If sender is operator -> Only to managers
        if sender.role == 'manager':
            async_to_sync(channel_layer.group_send)(
                "everyone",
                notification_data
            )
        else:
            async_to_sync(channel_layer.group_send)(
                "managers",
                notification_data
            )

def approve_user(*, user: User) -> User:
    """Approve a user and return the updated instance."""
    user.is_approved = True
    user.save()
    return user
