from ..models import Tournament

def list_of_matches_of_tournament(request):
    pass

def get_list_of_all_matches(tournament):
    return tournament.matches.all()
