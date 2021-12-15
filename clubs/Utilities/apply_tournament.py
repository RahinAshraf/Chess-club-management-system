from ..models import User,Tournament
from ..Utilities import message_adder, tournament_deadline_manager,tournament_capacity_manager
from django.shortcuts import redirect
REDIRECT_URL = "tournaments"

def apply_for_tournament(request,tournament):
    """This method applies the user to the tournament and manages the success string."""
    tournament.participating_players.add(User.objects.get(email = request.user.email))
    process_success_message(request=request, tournament=tournament)

def help_redirect():
    """ redirect the url to 'tournaments' """
    return redirect(REDIRECT_URL)

def get_tournament_object(tournament_id):
    """ return the tournament related to the given tournament id"""
    return Tournament.objects.get(id = tournament_id)

def process_success_message(request,tournament):
    """This method constructs the success string and add the message."""
    tournament_name = tournament.name
    success_string = "You are now added to the tournament: " + tournament_name
    message_adder.add_success_message(request=request, success_string=success_string)

def process_deadline_error(request):
    """ The method constructs the message when the deadline has passed"""
    error_string = "It is now too late to join the tournament."
    message_adder.add_error_message(request=request, error_string=error_string)
    return help_redirect()

def process_capacity_error(request):
    """ The method constructs the message when there is an capacity error """
    error_string = "The tournament is full, try join some other tournaments."
    message_adder.add_error_message(request=request, error_string=error_string)
    return help_redirect()

def manage_tournament_application(request,tournament_id):
    """This function is main control which manages the tournament application, by calling subfunctions.
    and returns by redirecting to the redirect url."""

    tournament = get_tournament_object(tournament_id=tournament_id)

    if not tournament_deadline_manager.is_time_left_to_enter(tournament = tournament):
        return process_deadline_error(request=request)

    if not tournament_capacity_manager.is_tournament_vacant_to_enter(tournament=tournament):
        return process_capacity_error(request=request)

    apply_for_tournament(request=request, tournament=tournament)

    return help_redirect()
