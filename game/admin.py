from django.contrib import admin

from .models import Game, Player, Card, Sky


def clear_card_from_finished_games():
    Card.objects.filter(game__status__in=[Game.BLUE_WIN, Game.RED_WIN]).delete()


admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Card)
admin.site.register(Sky)
admin.site.add_action(clear_card_from_finished_games)