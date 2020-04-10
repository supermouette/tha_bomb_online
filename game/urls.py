from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('skys_of_denmark', views.skys_of_denmark, name='skys'),
    path('verysecure/register', views.signup, name='signup'),
    path('game', views.waiting_room, name="waiting_room"),
    path('game/<int:game_id>', views.game_page, name="game_page"),
    path('game/room_list', views.get_room_list, name="room_list"),
    path('game/<int:game_id>/info', views.get_game_info, name="game_info"),
    path('game/<int:game_id>/join', views.join_game, name="join_game"),
    path('game/create', views.create_game, name="create_game"),
]
