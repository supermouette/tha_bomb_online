from django.test import TestCase
from game.models import Game, Player
from django.contrib.auth.models import User


def _create_game(nb_player=4, game_name='test'):
    game = Game(name=game_name)
    game.save()
    user_names = ['Clément'] + ["bot_"+str(i) for i in range(nb_player-1)]
    players = []
    for user_name in user_names:
        user = User(username=user_name)
        user.save()
        player = Player(user=user)
        player.save()
        players.append(player)

    return game, players


class TestBugClement(TestCase):
    def SetUp(self):
        self.game, self.players = _create_game(nb_player=4)
        self.clement = self.players[0]
        self.game.init_game()
        for player in self.players:
            player.make_claim(0, 0)

    def test_bug_clement(self):
        if self.game.next_player != self.clement:

