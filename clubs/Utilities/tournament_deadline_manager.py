from django.utils import timezone

def get_tournament_deadline(tournament):
    return tournament.deadline_to_apply

def get_current_time():
    return timezone.now()

def is_time_left_to_enter(tournament):
    return get_current_time() < get_tournament_deadline(tournament=tournament)