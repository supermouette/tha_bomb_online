import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from game.models import Clicker, ClickerReward


class ClickerConsumer(WebsocketConsumer):

    rooms = {}
    rewards = ClickerReward.objects.order_by("threshold").all()

    def connect(self):
        self.room = self.scope["url_route"]["kwargs"]["room"]
        self.room_group = "chat_%s" % self.room

        if self.room in ClickerConsumer.rooms:
            room = ClickerConsumer.rooms[self.room]
        else:
            room = {"total": 0, "active_player": 0}
            ClickerConsumer.rooms[self.room] = room
            
        room["active_player"] += 1

        async_to_sync(self.channel_layer.group_add)(self.room_group, self.channel_name)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group,
            {
                "type": "clicker_player_up",
                "total": room["active_player"],
            },
        )

        self.accept()

    def disconnect(self, close_code):

        if self.room in ClickerConsumer.rooms:
            room = ClickerConsumer.rooms[self.room]
        else:
            raise ValueError("roomp does not exist")
        
        room["active_player"] -= 1

        async_to_sync(self.channel_layer.group_send)(
            self.room_group,
            {"type": "clicker_player_down", "total": room["active_player"]},
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        options = json.loads(text_data)

        if self.room in ClickerConsumer.rooms:
            room = ClickerConsumer.rooms[self.room]
        else:
            raise ValueError("roomp does not exist")

        active_rewards = [r for r in ClickerConsumer.rewards if r.threshold<= room["total"]]

        click_power_upgrade = [r for r in active_rewards if r.effect_type=="click_power"]

        click_power = 0
        if len(click_power_upgrade) == 0:
            click_power = 1
        elif click_power_upgrade[-1].name == "Teamwork":
            click_power = room["active_player"]
        elif click_power_upgrade[-1].name == "contributor must be rewarded":
            click_power = room["active_player"] * max(1, options["contrib"])

        room["total"] += click_power

        active_rewards = [r for r in ClickerConsumer.rewards if r.threshold<= room["total"]]



        async_to_sync(self.channel_layer.group_send)(
            self.room_group,
            {
                "type": "clicker_total_up",
                "total": room["total"],
                "options": options,
                "active_rewards": [r.name for r in active_rewards],
                "next_reward": None if len(ClickerConsumer.rewards) == len(active_rewards) else ClickerConsumer.rewards[len(active_rewards)].threshold,
                "click_power": click_power,
            },
        )

    def clicker_player_up(self, event):
        self.send(text_data=json.dumps(event))

    def clicker_player_down(self, event):
        self.send(text_data=json.dumps(event))

    def clicker_total_up(self, event):
        self.send(text_data=json.dumps(event))
