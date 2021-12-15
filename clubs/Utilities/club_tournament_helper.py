"""This file is a utility with a club and tournament."""
from django.core.exceptions import ObjectDoesNotExist
from ..models import Tournament

def does_club_have_some_tournament(club):
    """This checks if club has some tournament. If not then it raises ObjectDoesNotExist exception."""
    if Tournament.objects.filter(club=club).count() == 0:
        raise ObjectDoesNotExist('Club does not have any tournament.')
    return True