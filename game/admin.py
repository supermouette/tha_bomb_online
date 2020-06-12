from django.contrib import admin

from .models import Game, Player, Card, Sky


def delete_card_if_not_used(modeladmin, request, queryset):
    queryset.objects.filter(game__status__in=[Game.BLUE_WIN, Game.RED_WIN]).delete()


class CardAdmin(admin.ModelAdmin):
    # list_display = ['title', 'status']
    # ordering = ['title']
    actions = [delete_card_if_not_used]


admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Card, CardAdmin)
admin.site.register(Sky)
