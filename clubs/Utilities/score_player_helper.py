from copy import error
from django.shortcuts import render,redirect
from ..models import Round,Group,Match, Tournament,User
from ..Utilities import message_adder
from ..Constants import scores


def get_round(round_id):
    return Round.objects.get(pk=round_id)

def get_match(match_id):
    return Match.objects.get(pk=match_id)

def get_player(player_id):
    return User.objects.get(pk=player_id)

def has_match_been_scored(match,round):
    return match.has_match_been_scored(round)

def process_already_scored_matches(request,round):
    error_string = "Match has already been scored."
    message_adder.add_error_message(request,error_string)
    return render_match_list(request,round)

def process_success_in_scoring(request,round):
    success_string = "Match has been scored."
    message_adder.add_success_message(request,success_string)
    return render_match_list(request,round)

def render_match_list(request,round):
    tournament = round.Tournament
    matches = tournament.matches.all()
    rounds = Round.objects.filter(Tournament=tournament)
    return render(request, 'match_list.html', {'matches': matches, 'rounds':rounds})

def score_player(request,round,match,player):
    match.put_score_for_player(round,scores.win_score,player)
    player2 = match.get_other_player(player)
    match.put_score_for_player(round,scores.lose_score,player2)
    round.decideWinners()
    return process_success_in_scoring(request,round)

def draw_match(request,round,match,player):
    player_list_for_match = match.get_all_players()
    for player in player_list_for_match:
        match.put_score_for_player(round,scores.draw_score,player)
    round.decideWinners()
    return process_success_in_scoring(request,round)

def help_score_player(request,round_id,match_id,player_id):
    round = get_round(round_id)
    match = get_match(match_id)
    if has_match_been_scored(match,round):
       return process_already_scored_matches(request,round)
    else:
        player = get_player(player_id)
        return score_player(request,round,match,player)

def help_draw_match(request,round_id,match_id):
    round = get_round(round_id)
    match = get_match(match_id)
    if has_match_been_scored(match,round):
       return process_already_scored_matches(request,round)
