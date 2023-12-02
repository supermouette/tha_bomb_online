from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from game.consumers import ClickerConsumer
from game.models import Clicker
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

def room_page(request, room_name):
    
    if room_name in ClickerConsumer.rooms:
        room = ClickerConsumer.rooms[room_name]
    else:
        room = {"total": 0, "active_player": 1}
    
    active_rewards = [r for r in ClickerConsumer.rewards if r.threshold<= room["total"]]

    return render(
        request,
        "game/clicker.html",
        {
            "room": {**room, "name": room_name},
            "active_rewards": active_rewards,
            "next_reward": None if len(ClickerConsumer.rewards) == len(active_rewards) else ClickerConsumer.rewards[len(active_rewards)],

        },
    )
