from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from game.models import Game, Player, Card
from django.contrib.auth.decorators import login_required
from django.urls import reverse


@login_required
def game_page(request, game_id):
    context = {}
    game = get_object_or_404(Game, pk=game_id)
    current_player = get_object_or_404(Player, user=request.user, game=game)
    context['players'] = game.get_players()
    context['current_player'] = current_player
    context['other_players'] = context['players'].exclude(id=current_player.id)
    context['game'] = game
    if game.status == Game.UNINITIALIZED:
        return render(request, 'game/game_uninitialized.html', context)
    else:
        context['nb_nothing'] = context['players'].count()*4
        return render(request, 'game/game.html', context)


@login_required
def init_game(request, game_id):
    context = {}
    game = get_object_or_404(Game, pk=game_id)
    try:
        game.init_game()
        return HttpResponse(status=200)
    except AssertionError as e:

        print(e)
        return HttpResponse(str(e), status=500)


@login_required
def discover_card(request, game_id, player_id, card_in_hand):

    game = get_object_or_404(Game, pk=game_id)
    current_player = Player.objects.filter(game=game, user=request.user)[0]
    player_picked = get_object_or_404(Player, id=player_id)

    try:
        current_player.discover_card(player_picked, card_in_hand)
        return HttpResponse(status=200)
    except AssertionError as e:
        print(str(e))
        return HttpResponse(str(e), status=500)


@login_required
def leave_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    player = Player.objects.filter(game=game, user=request.user)[0]
    player.delete()
    return redirect('waiting_room')


def is_init(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    if game.status == Game.UNINITIALIZED:
        return HttpResponse('0')
    else:
        return HttpResponse('1')


def turn_count(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    return HttpResponse(str(game.count_discovered+10*game.turn))


@login_required
def game_info(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    player = Player.objects.filter(game=game, user=request.user)[0]
    cards = Card.objects.filter(game=game)
    own_cards = cards.filter(player=player, discovered=False)
    own_cards_values = [card.value for card in own_cards]
    discovered_cards = cards.filter(discovered=True)
    bomb = discovered_cards.filter(value='b').count()
    wire = discovered_cards.filter(value='w').count()
    nothing = discovered_cards.filter(value='n').count()
    others = game.get_players().exclude(id=player.id)
    others_card = {}
    for other in others:
        others_card[other.id] = [other.get_card_left_binary(), other.claim_wire, other.claim_bomb]

    info = {
        "own_cards": own_cards_values,
        "own_claim": [player.claim_wire, player.claim_bomb],
        "turn": game.turn,
        'others': others_card,
        'next_player': game.next_player.id if game.next_player.id != player.id else -1,
        'state': game.status,
        'discovered': [nothing, wire, bomb],
        'cut_left': len(others)+1-game.count_discovered,
        'last_card_value': game.last_card_cut.get_value_display() if game.last_card_cut is not None else None,
        'last_card_owner': game.last_card_cut.player.user.username if game.last_card_cut is not None else None,
        'last_player': game.last_player.user.username if game.last_player is not None else None
    }
    if game.status == Game.BLUE_WIN or game.status == Game.RED_WIN:
        print(game.status)
        colors = {}
        for other in others:
            colors[other.id] = other.team
        info['colors'] = colors
        info['replay_link'] = reverse("join_game", kwargs={'game_id': game.next_game.id})
    print(info)
    return JsonResponse(info, safe=False)


@login_required
def make_claim(request, game_id, claim_wire, claim_bomb):
    game = get_object_or_404(Game, pk=game_id)
    player = Player.objects.filter(game=game, user=request.user)[0]

    try:
        player.make_claim(claim_wire, claim_bomb)
    except AssertionError as e:
        return HttpResponse(str(e), status=500)
    return HttpResponse(status=200)
