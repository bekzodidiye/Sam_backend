from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.apps import apps
import importlib

@shared_task
def async_broadcast_data_update(group, message_type, data=None, model_meta=None):
    """
    Broadcasts a data update notification asynchronously.
    If 'model_meta' is provided as {"model_path": "apps.Sale", "pk": "...", "serializer_path": "api_v1.serializers.SaleSerializer"},
    it fetches and serializes the object before broadcasting.
    """
    channel_layer = get_channel_layer()
    
    if model_meta:
        try:
            model_path = model_meta['model_path']
            pk = model_meta['pk']
            serializer_path = model_meta['serializer_path']
            
            # Dynamically get model and serializer
            app_label, model_name = model_path.split('.')
            model = apps.get_model(app_label, model_name)
            obj = model.objects.get(pk=pk)
            
            # Dynamically import serializer
            module_name, class_name = serializer_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            serializer_class = getattr(module, class_name)
            
            data = serializer_class(obj).data
        except Exception as e:
            # Fallback for errors or if not found
            print(f"Error in async serialization: {e}")
            if not data:
                return

    notification_data = {
        "type": "send_notification",
        "message": {
            "type": message_type,
            "data": data
        }
    }
    async_to_sync(channel_layer.group_send)(group, notification_data)
