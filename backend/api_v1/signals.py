from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.models import Sale, CheckIn, Message, DailyReport, User, Rule, MonthlyTarget, Tariff, SalesLink
from .notifications import broadcast_event

@receiver(post_save, sender=Sale)
def broadcast_sale(sender, instance, created, **kwargs):
    if created:
        broadcast_event("NEW_SALE", {"id": str(instance.id)})

@receiver(post_save, sender=CheckIn)
def broadcast_checkin(sender, instance, created, **kwargs):
    if created:
        broadcast_event("NEW_CHECKIN", {"id": instance.id})

@receiver(post_save, sender=Message)
def broadcast_message(sender, instance, created, **kwargs):
    if created:
        # Send to everyone or specific recipient group if you want more privacy
        # For now, following the 'everyone' pattern used in ArrivalChecker
        broadcast_event("NEW_MESSAGE", {"id": instance.id})

@receiver(post_save, sender=DailyReport)
def broadcast_report(sender, instance, created, **kwargs):
    if created:
        broadcast_event("NEW_REPORT", {"id": instance.id})

@receiver(post_save, sender=User)
def broadcast_user_update(sender, instance, created, **kwargs):
    # Only broadcast for existing users being updated (like approval status)
    if not created:
        broadcast_event("USER_UPDATED", {"id": str(instance.id)})

@receiver(post_save, sender=Rule)
def broadcast_rule_update(sender, instance, created, **kwargs):
    broadcast_event("RULE_UPDATED", {"id": instance.id})

@receiver(post_save, sender=MonthlyTarget)
def broadcast_target_update(sender, instance, created, **kwargs):
    broadcast_event("TARGET_UPDATED", {"month": instance.month})

@receiver(post_save, sender=Tariff)
def broadcast_tariff_update(sender, instance, created, **kwargs):
    broadcast_event("TARIFF_UPDATED", {"id": instance.id})

@receiver(post_save, sender=SalesLink)
def broadcast_link_update(sender, instance, created, **kwargs):
    broadcast_event("LINK_UPDATED", {"id": instance.id})

# Also handle deletions if needed
@receiver(post_delete, sender=Sale)
def broadcast_sale_delete(sender, instance, **kwargs):
    broadcast_event("NEW_SALE", {"id": str(instance.id), "deleted": True})
