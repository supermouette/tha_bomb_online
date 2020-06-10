from django.test import TestCase, TransactionTestCase
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
        self.game, self.players = _create_game(nb_player=4)
        self.clement = self.players[0]
        self.game.init_game()
        other_player = self.players[1]
        print(other_player)
        card_left = 20
        for player in self.players:
            player.make_claim(0, 0)
        if self.game.next_player != self.clement:
            print(str(self.game.next_player) + " have to cut Clément")
            # Be sure not to play a bomb in Clément's game
            if Card.objects.get(player=self.clement, order_in_hand=0).value == 'b':
                order_in_hand = 1
            else:
                order_in_hand = 0
            self.game.next_player.discover_card(self.clement, order_in_hand)
            self.game = Game.objects.get(id=self.game.id)
            card_left -= 1
            self.assertEqual(Card.objects.filter(game=self.game, discovered=False).count(), card_left)
        print("it is", self.game.next_player, "turn")
        # Here we know that it's Clément's turn
        self.assertEqual(self.game.next_player, self.clement)

        self.clement.discover_card(other_player, 0)
        card_left -= 1
        try:
            self.clement.discover_card(other_player, 1)
            self.clement.discover_card(other_player, 2)

        except Exception as e:
            pass
        print(other_player)
        self.assertEqual(Card.objects.filter(game=self.game, discovered=False).count(), card_left)
        print("discovered cards : ")
        for card in Card.objects.filter(game=self.game, discovered=True):
            print(card.player)
        self.assertEqual(Card.objects.filter(game=self.game, player=other_player, discovered=False).count(), 4)


class TestNextGame(TestCase):

    def test_next_game(self):
        game = Game(name="test")
        game.save()
        game.create_next_game()
        self.assertEqual("test 2", game.next_game.name)
        game = game.next_game
        game.create_next_game()
        self.assertEqual("test 3", game.next_game.name)
        long_name = ''.join([str(i % 10)for i in range(29)]) + 'a'
        game = Game(name=long_name)
        game.save()
        game.create_next_game()

        self.assertEqual(long_name[2:]+" 2", game.next_game.name)