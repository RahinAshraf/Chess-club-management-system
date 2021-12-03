from ..models import Club, MembershipType
from ..Constants import consts
def create_applicant_of_club(request, club_name):
    """ This method creates the applicant for the club and returns the success string."""
    user_club_choice = Club.objects.get(pk = club_name)
    # Make user an applicant of this club
    MembershipType.objects.create(user = request.user, club = user_club_choice, type = consts.APPLICANT)
    succes_string = 'You have successfully applied to' + club_name
    return succes_string