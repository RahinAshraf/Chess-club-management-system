from ..models import User,Tournament

def apply_for_tournament(request,tournament_id):
    """This method applies the user to the tournament and returns the success string."""
    tournament = Tournament.objects.get(id = tournament_id)
    tournament.participating_players.add(User.objects.get(email = request.user.email))
    tournament_name = tournament.name
    success_string = "You have successfully joined the tournament: " + tournament_name
    return success_string