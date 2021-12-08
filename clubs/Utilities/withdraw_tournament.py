from django.shortcuts import redirect
from ..models import User,Tournament
from ..Utilities import message_adder, tournament_deadline_manager
REDIRECT_URL = "tournaments"

def withdraw_from_tournament(request,tournament):
    """This method withdraw the user from the tournament and manages the success string."""
    tournament.participating_players.remove(User.objects.get(email = request.user.email))
    process_success_message(request=request,tournament=tournament)

def process_success_message(request,tournament):
    """This method constructs the success string and add the message."""
    tournament_name = tournament.name
    success_string = "You are now removed from the tournament: " + tournament_name
    message_adder.add_success_message(request=request, success_string=success_string)

def process_error_message(request):
    error_string = "You can not withdraw from the tournament, it's too late!"
    message_adder.add_error_message(request=request, error_string=error_string)


def get_tournament_object(tournament_id):
    return Tournament.objects.get(id = tournament_id)

def help_redirect():
    return redirect(REDIRECT_URL)

def manage_tournament_withdrawal(request,tournament_id):
    """This function is main control which manages the tournament withdrawal, by calling subfunctions.
    and returns by redirecting to the redirect url."""

    tournament = get_tournament_object(tournament_id=tournament_id)

    if tournament_deadline_manager.is_time_left_to_enter(tournament=tournament):
        withdraw_from_tournament(request,tournament)

    else:
        process_error_message(request=request)
        
    return help_redirect()

    
