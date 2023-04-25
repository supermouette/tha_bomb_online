import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from game.models import Clicker

class ClickerConsumer(WebsocketConsumer):
    def connect(self):
        self.room = self.scope["url_route"]["kwargs"]["room"]
        self.room_group = "chat_%s" % self.room
        
        room = get_object_or_404(Clicker, name=self.room)
        room.active_player += 1
        room.save()

        async_to_sync(self.channel_layer.group_add)(
            self.room_group, self.channel_name
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group, {"type": "clicker_player_up", "total": room.active_player}
        )

        self.accept()

    def disconnect(self, close_code):
        room = get_object_or_404(Clicker, name=self.room)
        room.active_player -= 1
        room.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group, {"type": "clicker_player_down", "total": room.active_player}
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        room = get_object_or_404(Clicker, name=self.room)
        room.total += 1
        room.save()
        self.send(text_data=json.dumps({"total": room.total}))

        async_to_sync(self.channel_layer.group_send)(
            self.room_group, {"type": "clicker_total_up", "total": room.total, "options": json.loads(text_data) }
        )

    def clicker_player_up(self, event):
        self.send(text_data=json.dumps(event))

    def clicker_player_down(self, event):
        self.send(text_data=json.dumps(event))

    def clicker_total_up(self, event):
        self.send(text_data=json.dumps(event))