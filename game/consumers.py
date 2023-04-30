import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from game.models import Clicker, ClickerReward


class ClickerConsumer(WebsocketConsumer):
    def connect(self):
        self.room = self.scope["url_route"]["kwargs"]["room"]
        self.room_group = "chat_%s" % self.room

        room = get_object_or_404(Clicker, name=self.room)
        room.active_player += 1
        room.save()

        async_to_sync(self.channel_layer.group_add)(self.room_group, self.channel_name)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group,
            {
                "type": "clicker_player_up",
                "total": room.active_player,
            },
        )

        self.accept()

    def disconnect(self, close_code):
        room = get_object_or_404(Clicker, name=self.room)
        room.active_player -= 1
        room.save()

        async_to_sync(self.channel_layer.group_send)(
            self.room_group,
            {"type": "clicker_player_down", "total": room.active_player},
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        options = json.loads(text_data)
        room = get_object_or_404(Clicker, name=self.room)
        active_rewards = room.active_rewards()
        click_power_upgrade = active_rewards.filter(effect_type="click_power").order_by(
            "-threshold"
        ).all()
        click_power = 0
        if len(click_power_upgrade) == 0:
            click_power = 1
        elif click_power_upgrade[0].name == "Teamwork":
            click_power = room.active_player
        elif click_power_upgrade[0].name == "contributor must be rewarded":
            click_power = room.active_player * max(1, options["contrib"])

        room.total += click_power
        room.save()
        active_rewards = room.active_rewards()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group,
            {
                "type": "clicker_total_up",
                "total": room.total,
                "options": options,
                "active_rewards": [r.name for r in active_rewards.only("name").all()],
                "next_reward": room.next_reward(),
                "click_power": click_power,
            },
        )

    def clicker_player_up(self, event):
        self.send(text_data=json.dumps(event))

    def clicker_player_down(self, event):
        self.send(text_data=json.dumps(event))

    def clicker_total_up(self, event):
        self.send(text_data=json.dumps(event))
