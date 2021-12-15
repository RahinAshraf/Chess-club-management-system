from django.contrib.messages.api import error, success
from ..models import Round, Tournament
from django.shortcuts import render,redirect
from ..Utilities import create_round_and_group_helper
from ..Utilities import message_adder

def help_generate_mathes(request, tournament_id):
    """ Decide on wheather the given tournament should be a round or gourps
        and proceed to other methods to generate the matches accordingly """
    tournament = Tournament.objects.get(pk = tournament_id)
    round_or_groups = create_round_and_group_helper.match_creator_helper(tournament)
    if process_round_or_groups(request,round_or_groups) == True:
        success_string = "Matches have been successfully generated!."
        process_success_string(request,success_string)
        return render_match_list_in_tournament(request,tournament)
    else:
        return redirect_to_tournaments()

def process_round_or_groups(request,round_or_group_list):
    """ Checks if the given list is none, if not matches will be created and returned """
    if round_or_group_list is None:
        error_string = "Cant generate matches, check if results are entered for each matches!"
        process_error_message(request,error_string)
        return False
    else:
       return create_matches_in_round_or_groups(request,round_or_group_list)

def create_matches_in_round_or_groups(request,round_or_group_list):
    """ create matches for each round or group in the given list """
    for round_or_group in round_or_group_list:
        round_or_group.createMatches()
        if round_or_group.matches.all().count() == 0: # This implies that there are no players in the tournament.
            process_no_players_in_the_tournament(request)
            return False
    return True
def process_no_players_in_the_tournament(request):
    """Adds the error message for no players in the tournament"""
    error_string = "There are currently not enough players in the tournament to generate matches."
    process_error_message(request,error_string)

def process_success_string(request,success_string):
    message_adder.add_success_message(request,success_string)

def render_match_list_in_tournament(request, tournament):
    """This renders the matches in the tournament"""
    matches = tournament.matches.all()
    rounds = Round.objects.filter(Tournament=tournament)
    return render(request, 'match_list.html', {'matches': matches, 'rounds':rounds})

def redirect_to_tournaments():
    """This method redirects to the tournament list"""
    return redirect('tournaments')

def process_error_message(request,error_string):
    """ Display the string as message """
    message_adder.add_error_message(request=request, error_string=error_string)
