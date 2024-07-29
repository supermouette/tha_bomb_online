from django.contrib import admin

from .models import Game, Player, Card, Sky, Clicker, ClickerReward, Friend


admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Card)
admin.site.register(Sky)
admin.site.register(Clicker)
admin.site.register(ClickerReward)
admin.site.register(Friend)