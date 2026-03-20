from rest_framework import permissions
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'

def broadcast_data_update(update_type, data=None, group="everyone"):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "send_notification",
                    "message": {
                        "type": update_type,
                        "data": data or {}
                    }
                }
            )
            print(f"[WS BROADCAST] Sent '{update_type}' to group '{group}'")
    except Exception as e:
        print(f"[WS ERROR] Failed to broadcast '{update_type}': {e}")

def index_view(request):
    return JsonResponse({
        "status": "online",
        "message": "Sam Brend Backend API is running.",
        "admin_panel": "/admin/"
    })
