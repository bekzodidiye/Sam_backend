import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def broadcast_event(event_type, data=None, group="everyone"):
    """
    Helper to broadcast a WebSocket event to a specific group.
    
    :param event_type: String type of the event (e.g., 'NEW_SALE', 'USER_UPDATED')
    :param data: Dictionary containing the payload
    :param group: The channel group to send to (default: 'everyone')
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "send_notification",
                    "message": {
                        "type": event_type,
                        "data": data or {}
                    }
                }
            )
            print(f"[WS BROADCAST] Sent '{event_type}' to group '{group}'")
    except Exception as e:
        print(f"[WS ERROR] Failed to broadcast '{event_type}': {e}")
