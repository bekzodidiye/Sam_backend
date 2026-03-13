from .notifications import broadcast_event

class BroadcastMixin:
    """
    Mixin to handle automatic WebSocket broadcasting for ViewSets.
    Usage: Set 'broadcast_type' and optionally 'broadcast_group'.
    """
    broadcast_type = None
    broadcast_group = "everyone"

    def perform_create(self, serializer):
        instance = serializer.save()
        self.broadcast("CREATED", serializer.data)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self.broadcast("UPDATED", serializer.data)
        return instance

    def perform_destroy(self, instance):
        broadcast_data = {"id": str(instance.id), "deleted": True}
        instance.delete()
        self.broadcast("DELETED", broadcast_data)

    def broadcast(self, action, data=None):
        if self.broadcast_type:
            event_name = f"{self.broadcast_type}_{action}" if action in ["CREATED", "UPDATED", "DELETED"] else self.broadcast_type
            broadcast_event(event_name, data, group=self.broadcast_group)
