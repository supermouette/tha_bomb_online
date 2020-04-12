from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from game.models import Game, Player
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def get_room_list(request):
    rooms = list(Game.objects.filter(status=Game.UNINITIALIZED))
    data = [[r.name, len(r.get_players()), reverse('join_game', args=[r.id])] for r in rooms]
    return JsonResponse(data, safe=False)  # safe=False allow to pass non dict objects


def get_game_info(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    info = {"status": game.status, "players": list(game.get_players())}
    return JsonResponse(info)


@login_required
def join_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    player = Player(user=request.user, game=game)
    player.save()
    return redirect('game_page', game_id=game_id)


@login_required
def create_game(request):
    print(request.POST['name'])
    # TODO: get the right game name
    game = Game(name=request.POST['name'])
    game.save()
    player = Player(user=request.user, game=game)
    player.save()
    return redirect('game_page', game_id=game.id)


def waiting_room(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = False

    context = {"user": user}
    return render(request, 'game/waiting_room.html', context)
