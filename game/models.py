from django.db import models
from django.contrib.auth.models import User
from django.db import transaction


class Game(models.Model):

    UNINITIALIZED = "u"
    IN_PROGRESS = "i"
    STOPPED = "s"
    RED_WIN = "r"
    BLUE_WIN = "b"

    STATUS_CHOICES = ((UNINITIALIZED, "Uninitialized"),
                      (IN_PROGRESS, "In progress"),
                      (STOPPED, "Stopped"),
                      (RED_WIN, "Red win"),
                      (BLUE_WIN, "Blue win"))

    turn = models.IntegerField(default=0)
    count_discovered = models.IntegerField(default=0)
    next_player = models.ForeignKey('Player', on_delete=models.SET_NULL, default=None, blank=True, null=True,
                                    related_name='+')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=UNINITIALIZED)
    name = models.CharField(max_length=30)
    next_game = models.ForeignKey('Game', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    last_card_cut = models.ForeignKey('Card', on_delete=models.SET_NULL, default=None,
                                      blank=True, null=True, related_name="+")
    last_player = models.ForeignKey('Player', on_delete=models.SET_NULL, default=None,
                                    blank=True, null=True, related_name="+")

    def get_players(self):
        return Player.objects.filter(game=self)

    def create_deck(self):
        if Card.objects.filter(game=self).count() != 0:
            # raise AssertionError("Game already have cards")
            Card.objects.filter(game=self).delete()
        nb_players = len(self.get_players())
        # bomb
        Card(value=Card.BOMB, game=self, player=None).save()
        # wires
        for i in range(nb_players):
            Card(value=Card.WIRE, game=self, player=None).save()
        # nothing
        for i in range(nb_players*4-1):
            Card(value=Card.NOTHING, game=self, player=None).save()

    def next_turn(self):
        from random import shuffle
        if self.count_discovered != len(self.get_players()) and self.turn != 0:
            raise AssertionError("Next turn is forbidden right now")
        if self.turn > 3:  # UUUUH I put 4 at first, but if this turn 4 before next_turn, it will be turn 5 after...
            raise AssertionError("Number of turn can not exceed 4")
        self.count_discovered = 0
        self.save(update_fields=['count_discovered'])
        cards = list(Card.objects.filter(game=self).filter(discovered=False))
        shuffle(cards)
        players = list(self.get_players())
        for i in range(len(cards)):
            cards[i].player = players[i % len(players)]
            cards[i].order_in_hand = i // len(players)
            cards[i].save(update_fields=['player', 'order_in_hand'])

        for p in players:
            p.reset_claim()

        self.turn += 1
        # self.last_card_cut = None
        # self.last_player = None
        self.save(update_fields=['turn']) # , 'last_card_cut', 'last_player'])

    def init_game(self):
        from random import shuffle
        with transaction.atomic():  # should hopefully resolve bugs
            game = Game.objects.select_for_update().filter(id=self.id)[0]
            if game.turn != 0 or game.status != game.UNINITIALIZED:
                raise AssertionError("Game already initialized")

            # init player team, set first player
            players = list(game.get_players())
            nb_players = len(players)
            if nb_players in [4, 5]:
                nb_blue = 3
                nb_red = 2
            elif nb_players == 6:
                nb_blue = 4
                nb_red = 2
            elif nb_players in [7, 8]:
                nb_blue = 5
                nb_red = 3
            else:
                raise AssertionError("Number of player should be between 4 and 8")
            colors = [Player.BLUE]*nb_blue + [Player.RED]*nb_red
            shuffle(colors)
            for i in range(nb_players):
                players[i].team = colors[i]
                players[i].save()
            game.create_deck()
            shuffle(players)
            game.next_player = players[0]
            game.status = game.IN_PROGRESS
            game.save()
            game.next_turn()

        return game

    def check_victory(self):
        discovered = Card.objects.filter(game=self).filter(discovered=True)
        bomb = discovered.filter(value=Card.BOMB)
        wires = discovered.filter(value=Card.WIRE)
        if wires.count() == self.get_players().count():
            self.status = self.BLUE_WIN
            self.create_next_game()
        elif bomb.count() != 0 or discovered.count() == self.get_players().count()*5:
            self.status = self.RED_WIN
            self.create_next_game()
        else:
            return self.status
        self.save(update_fields=["status"])
        return self.status

    def create_next_game(self):
        # create a reference to a new game, to allow a replay button
        if self.next_game is None:
            new_name = self.name
            last_part = self.name.split(' ')[-1]
            if last_part.isdecimal():
                last_part = str(int(last_part)+1)
            else:
                last_part += " 2"
            if self.name.split(' ')[:-1] == []:
                new_name = last_part
            else:
                new_name = ' '.join(self.name.split(' ')[:-1]) + " " + last_part
            if len(new_name) >= 30:
                new_name = new_name[2:]  # because why not ?
            self.next_game = Game(name=new_name)
            self.next_game.save()
            self.save()

    def is_ready_for_discover(self):
        players = list(self.get_players())
        for p in players:
            if p.claim_bomb is None or p.claim_wire is None:
                return False
        return True

    def __str__(self):
        return self.name


class Player(models.Model):

    BLUE = "b"
    RED = "r"
    TEAM_CHOICES = ((BLUE, "Blue"), (RED, "Red"))

    team = models.CharField(max_length=1, choices=TEAM_CHOICES, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim_bomb = models.IntegerField(null=True, blank=True, default=None)
    claim_wire = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        if self.game is not None:
            return self.user.username + " in " + self.game.name
        return self.user.username

    def discover_card(self, player, card_order):
        with transaction.atomic():
            # It should be enough to select_for_update the card
            # If there is more bug, it might be useful to select_for_update the game and/or self
            card = Card.objects.select_for_update().filter(game=self.game, order_in_hand=card_order, player=player, discovered=False)[0]
            game = Game.objects.select_for_update().filter(id=self.game.id)[0]
            if not game.is_ready_for_discover():
                raise AssertionError("Not everybody has make a claim yet")
            if game.next_player != self:
                raise AssertionError("This is not " + str(self) + " turn. It is "+str(game.next_player))
            if card.player == self:
                raise AssertionError("Impossible to discover own card")
            if card.discovered:
                raise AssertionError("Card already discovered")
            if game.status != Game.IN_PROGRESS:
                raise AssertionError('Game is not in progress')

            card.discovered = True
            card.save(update_fields=['discovered'])
            game.count_discovered += 1
            game.next_player = player
            game.last_player = self
            game.last_card_cut = card
            game.save(update_fields=["next_player", "count_discovered", "last_player", "last_card_cut"])
            game.check_victory()
            if game.count_discovered % game.get_players().count() == 0 and game.status == Game.IN_PROGRESS:
                game.next_turn()
            return card.value

    def make_claim(self, claim_wire, claim_bomb):
        if self.claim_bomb is not None and self.claim_wire is not None:
            raise AssertionError("claim already done")
        elif self.game.status != Game.IN_PROGRESS:
            raise AssertionError("game is not in progress")
        else:
            self.claim_wire = claim_wire
            self.claim_bomb = claim_bomb
            self.save(update_fields=["claim_wire", "claim_bomb"])

    def get_card_left_binary(self):
        final_number = 0
        cards = list(Card.objects.filter(game=self.game, player=self, discovered=False))
        for card in cards:
            final_number += 2**card.order_in_hand
        return final_number

    def reset_claim(self):
        self.claim_bomb = None
        self.claim_wire = None
        self.save(update_fields=["claim_wire", "claim_bomb"])

    @classmethod
    def delete_unused(cls):
        Player.objects.filter(game__status__in=[Game.RED_WIN, Game.BLUE_WIN]).delete()


class Card(models.Model):

    NOTHING = "n"
    WIRE = "w"
    BOMB = "b"
    VALUE_CHOICES = ((NOTHING, "Nothing"), (WIRE, "Wire"), (BOMB, "Bomb"))

    value = models.CharField(max_length=1, choices=VALUE_CHOICES, default=NOTHING)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True)
    discovered = models.BooleanField(default=False)
    order_in_hand = models.IntegerField(default=None, null=True, blank=True)

    @classmethod
    def delete_unused(cls):
        Card.objects.filter(game__status__in=[Game.RED_WIN, Game.BLUE_WIN]).delete()


class Sky(models.Model):

    color = models.IntegerField()
    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return str(self.day) + '/' + str(self.month) + " ("+str(self.color) + ")"

class Clicker(models.Model):
    name = models.CharField(max_length=30)
    total = models.IntegerField(null=False, blank=False, default=0)
    active_player = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return self.name + ' - ' + str(self.total)

    def active_rewards(self):
        return ClickerReward.objects.filter(threshold__lte=self.total)
    
    def next_reward(self):
        r = ClickerReward.objects.filter(threshold__gt=self.total).order_by("threshold").first()
        return r.threshold if r else None

class ClickerReward(models.Model):
    threshold = models.IntegerField(null=False)
    name = models.CharField(max_length=50)
    effect_type = models.CharField(max_length=20)
    effect_value = models.CharField(max_length=50)

    class Meta: 
        ordering = ('threshold',)

    def __str__(self):
        return self.name + ' - ' + str(self.threshold)
    
    def toDict(self):
        return {"name": self.name, "threshold": self.threshold, "effect_type":self.effect_type, "effect_value":self.effect_value}

class Friend(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    unrevelant_info = models.CharField(max_length=500, null=True, blank=True)
    website = models.CharField(max_length=200, null=True, blank=True)
    popularity = models.IntegerField(default=0, null=False)

    def __str__(self):
        return self.name