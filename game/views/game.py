from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from game.models import Game


def game_page(request, game_id):
    context = {}
    game = get_object_or_404(Game, pk=game_id)
    return HttpResponse(game.name)