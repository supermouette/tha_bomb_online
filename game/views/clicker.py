from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from game.models import Clicker
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

def room_page(request, room_name):
    room = Clicker.objects.filter(name=room_name).first()
    if not room : 
        room = Clicker(name=room_name)
        room.save()

    return render(
        request,
        "game/clicker.html",
        {
            "room": room,
            "active_rewards": room.active_rewards(),
            "next_reward": room.next_reward(),
        },
    )
