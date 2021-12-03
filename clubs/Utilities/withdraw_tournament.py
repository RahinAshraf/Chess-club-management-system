from ..models import User,Tournament

def withdraw_from_tournament(request,tournament_id):
    """This method withdraw the user from the tournament and returns the success string."""
    tournament = Tournament.objects.get(id = tournament_id)
    tournament.participating_players.remove(User.objects.get(email = request.user.email))
    tournament_name = tournament.name
    success_string = "You are now removed from the tournament: " + tournament_name
    return success_string
