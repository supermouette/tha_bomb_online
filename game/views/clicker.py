from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from game.consumers import ClickerConsumer
from django.contrib.auth.decorators import user_passes_test


def room_page(request, room_name):
    if room_name in ClickerConsumer.rooms:
        room = ClickerConsumer.rooms[room_name]
    else:
        room = {"total": 0, "active_player": 1}

    active_rewards = [
        r for r in ClickerConsumer.rewards if r.threshold <= room["total"]
    ]

    return render(
        request,
        "game/clicker.html",
        {
            "room": {**room, "name": room_name},
            "active_rewards": active_rewards,
            "next_reward": None
            if len(ClickerConsumer.rewards) == len(active_rewards)
            else ClickerConsumer.rewards[len(active_rewards)],
        },
    )


@user_passes_test(lambda u: u.is_superuser)
def admin_clicker_page(request):
    return JsonResponse(ClickerConsumer.rooms)


@user_passes_test(lambda u: u.is_superuser)
def reset_rooms(request):
    ClickerConsumer.reset_rooms()
    return HttpResponse(status=200)
