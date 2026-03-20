from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.models import Sale, CheckIn, Message, DailyReport, User, Rule, MonthlyTarget, Tariff, SalesLink, OperatorRating
from .tasks import async_broadcast_data_update

@receiver(post_save, sender=Sale)
def broadcast_sale(sender, instance, created, **kwargs):
    if created:
        async_broadcast_data_update.delay(
            "everyone", "NEW_SALE", 
            model_meta={"model_path": "apps.Sale", "pk": str(instance.pk), "serializer_path": "api_v1.serializers.SaleSerializer"}
        )

@receiver(post_save, sender=CheckIn)
def broadcast_checkin(sender, instance, created, **kwargs):
    if created:
        async_broadcast_data_update.delay(
            "everyone", "NEW_CHECKIN", 
            model_meta={"model_path": "apps.CheckIn", "pk": instance.pk, "serializer_path": "api_v1.serializers.CheckInSerializer"}
        )

@receiver(post_save, sender=Message)
def broadcast_message(sender, instance, created, **kwargs):
    if created:
        model_meta = {"model_path": "apps.Message", "pk": instance.pk, "serializer_path": "api_v1.serializers.MessageSerializer"}
        if instance.recipient:
             async_broadcast_data_update.delay(f"user_{instance.recipient.id}", "NEW_MESSAGE", model_meta=model_meta)
             async_broadcast_data_update.delay(f"user_{instance.sender.id}", "NEW_MESSAGE", model_meta=model_meta)
        else:
             async_broadcast_data_update.delay("everyone", "NEW_MESSAGE", model_meta=model_meta)

@receiver(post_save, sender=DailyReport)
def broadcast_report(sender, instance, created, **kwargs):
    if created:
        async_broadcast_data_update.delay(
            "everyone", "NEW_REPORT", 
            model_meta={"model_path": "apps.DailyReport", "pk": instance.pk, "serializer_path": "api_v1.serializers.DailyReportSerializer"}
        )

@receiver(post_save, sender=User)
def broadcast_user_update(sender, instance, created, **kwargs):
    if not created:
        async_broadcast_data_update.delay(
            "everyone", "USER_UPDATED", 
            model_meta={"model_path": "apps.User", "pk": str(instance.pk), "serializer_path": "api_v1.serializers.UserSerializer"}
        )

@receiver(post_save, sender=Rule)
def broadcast_rule_update(sender, instance, created, **kwargs):
    async_broadcast_data_update.delay("everyone", "RULE_UPDATED", {"id": instance.id})

@receiver(post_save, sender=MonthlyTarget)
def broadcast_target_update(sender, instance, created, **kwargs):
    async_broadcast_data_update.delay("everyone", "TARGET_UPDATED", {"month": instance.month})

@receiver(post_save, sender=Tariff)
def broadcast_tariff_update(sender, instance, created, **kwargs):
    async_broadcast_data_update.delay("everyone", "TARIFF_UPDATED", {"id": instance.id})

@receiver(post_save, sender=SalesLink)
def broadcast_link_update(sender, instance, created, **kwargs):
    async_broadcast_data_update.delay("everyone", "LINK_UPDATED", {"id": instance.id})

# Also handle deletions if needed
@receiver(post_delete, sender=Sale)
def broadcast_sale_delete(sender, instance, **kwargs):
    async_broadcast_data_update.delay("everyone", "NEW_SALE", {"id": str(instance.id), "deleted": True})
@receiver(post_save, sender=OperatorRating)
def broadcast_rating_update(sender, instance, created, **kwargs):
    async_broadcast_data_update.delay("everyone", "NEW_RATING", {"id": instance.id})
    async_broadcast_data_update.delay(f"user_{instance.operator.id}", "NEW_RATING", {"id": instance.id})
