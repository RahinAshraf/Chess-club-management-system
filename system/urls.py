"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.HomeView.as_view(), name = 'home'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('test/', views.TestView.as_view(), name='test'),
    path('log_out/', views.log_out, name='log_out'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('password/', views.password, name='password'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('clubs/', views.ClubListView.as_view(), name='club_list'),
    path('officer_list/<int:tournament_id>/', views.OfficerListView.as_view(), name='officer_list'),
    path('match_list/<int:tournament_id>/', views.MatchListView.as_view(), name='match_list'),
    path('switch_club/', views.switch_club, name='switch_club'),
    path('promote/<int:user_id>/', views.promote, name='promote'),
    path('apply_to_club/<str:club_name>/', views.apply_to_club, name='apply_to_club'),
    path('demote/<int:user_id>/', views.demote, name='demote'),
    path('create_new_club/', views.CreateNewClubView.as_view(), name='create_new_club'),
    path('transfer_ownership/<int:user_id>/', views.transfer_ownership, name='transfer_ownership'),
    path('tournaments/', views.TournamentListView.as_view(), name='tournaments'),
    path('withdraw_from_tournament/<int:tournament_id>/', views.withdraw_from_tournament, name='withdraw_from_tournament'),
    path('create_new_tournament/', views.CreateNewTournamentView.as_view(), name='create_tournament'),
    path('participate_in_tournament/<int:tournament_id>/', views.participate_in_tournament, name='participate_in_tournament'),
    path('assign_coorganiser/<int:tournament_id>/<int:user_id>/', views.assign_coorganiser, name='assign_coorganiser'),
    path('generate_matches/<int:tournament_id>/', views.generate_matches, name='generate_matches')
]
