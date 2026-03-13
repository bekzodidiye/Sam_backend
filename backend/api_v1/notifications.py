import logging
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

def broadcast_event(event_type: str, data: dict = None, group: str = "everyone"):
    """
    Broadcasts a WebSocket message to a specific consumer group.
    Unified utility for all real-time notifications.
    """
    try:
        # Guarantee data is JSON-serializable primitives to avoid msgpack errors
        safe_data = json.loads(json.dumps(data)) if data else {}
        
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "send_notification",
                    "message": {
                        "type": event_type,
                        "data": safe_data
                    }
                }
            )
            # logger.debug(f"[WS BROADCAST] Sent '{event_type}' to group '{group}'")
    except Exception as e:
        logger.error(f"[WS ERROR] Failed to broadcast '{event_type}': {e}", exc_info=True)

# Alias for backward compatibility if needed, but we'll migrate the code
broadcast_data_update = broadcast_event
