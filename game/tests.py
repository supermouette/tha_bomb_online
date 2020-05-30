from django.test import TestCase
from game.models import Game, Player, Card
from django.contrib.auth.models import User


def _create_game(nb_player=4, game_name='test'):
    game = Game(name=game_name)
    game.save()
    user_names = ['Clément'] + ["bot_"+str(i) for i in range(nb_player-1)]
    players = []
    for user_name in user_names:
        user = User(username=user_name)
        user.save()
        player = Player(user=user, game=game)
        player.save()
        players.append(player)

    return game, players


class TestBugClement(TestCase):
    def test_bug_clement(self):
        from multiprocessing import Pool

        self.game, self.players = _create_game(nb_player=4)
        self.clement = self.players[0]
        self.game.init_game()
        for player in self.players:
            player.make_claim(0, 0)

        if self.game.next_player != self.clement:
            # Be sure not to play a bomb in Clément's game
            if Card.objects.get(player=self.clement, order_in_hand=0).value == 'b':
                order_in_hand = 1
            else:
                order_in_hand = 0
            self.game.next_player.discover_card(self.clement, order_in_hand)
        # Here we know that it's Clément's turn
        """pool = Pool()
        try:
            pool.map(self.clement.discover_card, [[self.players[1], i] for i in range(4)])
        except:
            pass
        """
        try:
            self.clement.discover_card(self.players[1], 0)
            self.clement.discover_card(self.players[1], 1)
            self.clement.discover_card(self.players[1], 2)
        except:
            pass
        self.assertEqual(Card.objects.filter(player=self.players[1], discovered=False).count(), 4)
