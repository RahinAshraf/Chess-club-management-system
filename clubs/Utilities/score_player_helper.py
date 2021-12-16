from copy import error
from django.shortcuts import render,redirect
from ..models import Round,Group,Match, Tournament,User
from ..Utilities import message_adder,get_round_or_group
from ..Constants import scores


def get_round(round_id):
    try:
        round = Group.objects.get(pk=round_id)
    except:
        round = Round.objects.get(pk=round_id)
    return round

def get_match(match_id):
    return Match.objects.get(pk=match_id)

def get_player(player_id):
    return User.objects.get(pk=player_id)

def has_match_been_scored(match,round):
    return match.has_match_been_scored(round)

def process_already_scored_matches(request,round):
    """This method processes already scored matches"""
    error_string = "Match has already been scored."
    message_adder.add_error_message(request,error_string)
    return render_match_list(request,round)

def process_success_in_scoring(request,round):
    """This method processes success in scoring"""
    success_string = "Match has been scored."
    message_adder.add_success_message(request,success_string)
    return render_match_list(request,round)

def render_match_list(request,round):
    """This method renders the current match list in tournament."""
    tournament = round.Tournament
    matches = tournament.matches.all()
    rounds = get_round_or_group.get_rounds_and_groups(tournament)
    return render(request, 'match_list.html', {'matches': matches, 'rounds':rounds})

def score_player(request,round,match,player):
    """This method takes in a player in puts a win score for that player and a lose score for the other player"""
    match.put_score_for_player(round,scores.win_score,player)
    player2 = match.get_other_player(player)
    match.put_score_for_player(round,scores.lose_score,player2)
    if isinstance(round,Group):
        round.decideWinnersForGroup()
    else:
        round.decideWinners()
    return process_success_in_scoring(request,round)

def draw_match(request,round,match):
    """This method puts the draw score for both players in a match"""
    player1 = match.player1
    player2 = match.player2
    match.put_score_for_player(round,scores.draw_score,player1)
    match.put_score_for_player(round,scores.draw_score,player2)
    round.decideWinners()
    return process_success_in_scoring(request,round)

def help_score_player(request,round_id,match_id,player_id):
    """This method helps score a player"""
    round = get_round(round_id)
    match = get_match(match_id)
    if has_match_been_scored(match,round):
       return process_already_scored_matches(request,round)
    else:
        player = get_player(player_id)
        return score_player(request,round,match,player)

def help_draw_match(request,round_id,match_id):
    """This method helps draw a match"""
    round = get_round(round_id)
    match = get_match(match_id)
    if has_match_been_scored(match,round):
       return process_already_scored_matches(request,round)
    else:
        return draw_match(request,round,match)
