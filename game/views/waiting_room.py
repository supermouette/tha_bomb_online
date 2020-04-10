from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from game.models import Game, Player
from django.contrib.auth.decorators import login_required


def get_room_list(request):
    rooms = Game.objects.filter(status=Game.UNINITIALIZED)
    return JsonResponse(list(rooms), safe=False)  # safe=False allow to pass non dict objects


def get_game_info(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    info = {"status":game.status, "players": list(game.get_players())}
    return JsonResponse(info)


@login_required
def join_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    player = Player(user=request.user, game=game)
    player.save()
    # TODO: redirect to game page


@login_required
def create_game(request):
    print(request.POST)
    # TODO: get the right game name
    game = Game(name='toto')
    game.save()
    player = Player(user=request.user, game=game)
    player.save()
    # TODO: redirect to game page


def waiting_room(request):
    context = {}
    return HttpResponse(200)
