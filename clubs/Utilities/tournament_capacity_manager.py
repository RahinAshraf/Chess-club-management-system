from ..models import Tournament

def get_current_participating_players(tournament):
    return tournament.get_number_of_participating_players()

def get_tournament_capacity(tournament):
    return tournament.capacity

def is_tournament_vacant_to_enter(tournament):
    return (get_current_participating_players(tournament) + 1) <= get_tournament_capacity(tournament)
