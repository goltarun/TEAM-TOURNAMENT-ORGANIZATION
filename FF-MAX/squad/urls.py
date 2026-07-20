from django.urls import path
from . import views

urlpatterns = [
    # User Panel Pages
    path('', views.user_home, name='user_home'),
    path('tournaments/', views.tournaments_page, name='tournaments_page'),
    path('players/', views.players_page, name='players_page'),
    path('register/', views.register_page, name='register_page'),
    path('news/', views.news_page, name='news_page'),

    # Admin Panel
    path('manage/', views.dashboard, name='dashboard'),
    path('manage/players/', views.player_list, name='player_list'),
    path('manage/tournaments/', views.tournament_list, name='tournament_list'),
    path('manage/registrations/', views.registration_list, name='registration_list'),
    path('manage/tournaments/<int:tournament_id>/registrations/', views.tournament_registrations, name='tournament_registrations'),
    path('manage/news/', views.news_list, name='news_list'),
    path('manage/news/toggle/<int:news_id>/', views.toggle_news_status, name='toggle_news_status'),
    path('manage/news/delete/<int:news_id>/', views.delete_news, name='delete_news'),
    path('manage/tournaments/delete/<int:tournament_id>/', views.delete_tournament, name='delete_tournament'),
    path('manage/tournaments/<int:tournament_id>/cancel-alert/', views.cancel_tournament_alert, name='cancel_tournament_alert'),
    path('manage/registrations/delete/<int:registration_id>/', views.delete_registration, name='delete_registration'),

    # API Endpoints
    path('api/players/', views.api_players, name='api_players'),
    path('api/tournaments/', views.api_tournaments, name='api_tournaments'),
    path('api/news/', views.api_news, name='api_news'),
    path('api/register/', views.api_register_player, name='api_register_player'),
    path('api/tournament-register/', views.api_register_tournament, name='api_register_tournament'),
    path('api/confirm-payment/', views.api_confirm_payment, name='api_confirm_payment'),
]

