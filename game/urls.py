from django.urls import path
from django.views.generic.base import TemplateView
from . import views
from django.conf.urls import url
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.index, name='index'),
    path('blue_ratio', views.blue_ratio, name='blue_ratio'),
    path('skies_of_denmark', views.skies_of_denmark, name='skies'),
    path('faq', views.faq, name='faq'),
    path('verysecure/register', views.signup, name='signup'),
    path('game', views.waiting_room, name="waiting_room"),
    path('game/<int:game_id>', views.game_page, name="game_page"),
    path('game/room_list', views.get_room_list, name="room_list"),
    path('game/<int:game_id>', views.game_page, name="game_page"),
    path('game/<int:game_id>/info', views.get_game_info, name="game_info"),
    path('game/<int:game_id>/join', views.join_game, name="join_game"),
    path('game/<int:game_id>/init', views.init_game, name="init_game"),
    path('game/<int:game_id>/leave', views.leave_game, name="leave_game"),
    path('game/<int:game_id>/isinit', views.is_init, name="isinit"),
    path('game/<int:game_id>/turn_count', views.turn_count, name="turn_count"),
    path('game/<int:game_id>/data', views.game_info, name="game_data"),
    path('game/<int:game_id>/discover/<int:player_id>/<int:card_in_hand>', views.discover_card, name="discover_card"),
    path('game/<int:game_id>/claim/<int:claim_wire>/<int:claim_bomb>', views.make_claim, name="claim"),
    path('game/create', views.create_game, name="create_game"),
    path('game/delete_unused', views.delete_unused, name='delete_unused'),
    path('game/rules', views.game_rules, name='game_rules'),
    path('scrap', views.scrap, name="scrap"),
    path('house_tracker', views.house_tracker, name="house_tracker"),
    path('house_tracker/csv', views.house_tracker_csv, name="house_tracker_csv"),
    path('house_tracker.user.js', views.generate_custom_js, name="generate_custom_js"),
    url(r'^robots\.txt$', RedirectView.as_view(url='/static/game/robots.txt')),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/game/favicon.ico')),
]
