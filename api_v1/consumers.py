"""
consumers.py - Production-ready WebSocket consumer.

Handles:
- JWT-authenticated connections
- Group membership (user-specific + broadcast groups)
- Sending server-side events to the client
- Clean disconnection and group removal
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    A WebSocket consumer that:
    1. Accepts authenticated users only.
    2. Adds them to up to 3 channel groups:
       - 'everyone': receives all global broadcasts.
       - 'managers': receives manager-specific broadcasts.
       - 'user_{id}': receives user-specific (personal) broadcasts.
    3. Forwards any 'send_notification' event sent to those groups
       down to the connected WebSocket client.
    """

    async def connect(self):
        self.user = self.scope.get("user")

        # Reject unauthenticated connections immediately.
        if not self.user or self.user.is_anonymous:
            await self.close(code=4003)
            return

        # Personal group (for direct messages)
        self.personal_group = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.personal_group, self.channel_name)

        # Global broadcast group - every authenticated user joins this
        await self.channel_layer.group_add("everyone", self.channel_name)

        # Manager-only group
        if getattr(self.user, 'role', None) == 'manager':
            await self.channel_layer.group_add("managers", self.channel_name)

        await self.accept()
        print(f"[WS] User {self.user.id} ({self.user.username}) connected.")

        # Optional: Broadcast that a user came online
        await self.channel_layer.group_send(
            "everyone",
            {
                "type": "send_notification",
                "message": {
                    "type": "USER_ACTIVITY",
                    "data": {"user_id": str(self.user.id), "status": "online"}
                }
            }
        )

    async def disconnect(self, close_code):
        if not hasattr(self, 'personal_group'):
            return  # Never successfully connected

        # Remove from all groups
        await self.channel_layer.group_discard(self.personal_group, self.channel_name)
        await self.channel_layer.group_discard("everyone", self.channel_name)

        if getattr(self.user, 'role', None) == 'manager':
            await self.channel_layer.group_discard("managers", self.channel_name)

        print(f"[WS] User {self.user.id} disconnected (code={close_code}).")

        # Optional: Broadcast that a user went offline
        await self.channel_layer.group_send(
            "everyone",
            {
                "type": "send_notification",
                "message": {
                    "type": "USER_ACTIVITY",
                    "data": {"user_id": str(self.user.id), "status": "offline"}
                }
            }
        )

    async def receive(self, text_data):
        """
        Handle messages from the WebSocket client.
        We mostly push from server → client, but we can handle client
        ping-pong or other events here in the future.
        """
        try:
            data = json.loads(text_data)
            # Example: respond to ping with pong for keep-alive
            if data.get("type") == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
        except json.JSONDecodeError:
            pass  # Ignore malformed messages

    # -----------------------------------------------------------------
    # Channel layer event handlers (called by group_send from views.py)
    # -----------------------------------------------------------------

    async def send_notification(self, event):
        """
        Forwards a channel layer message to the WebSocket client.
        Expected event format:
          {
            "type": "send_notification",
            "message": {
              "type": "NEW_SALE",
              "data": {...}
            }
          }
        """
        message = event.get("message", {})
        await self.send(text_data=json.dumps(message))
