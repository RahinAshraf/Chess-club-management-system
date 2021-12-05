from ..models import Club, MembershipType
from ..Constants import consts
from ..Utilities import message_adder

def create_applicant_of_club(request, club_name):
    """ This method creates the applicant for the club and processes the success string."""
    user_club_choice = Club.objects.get(pk = club_name)
    # Make user an applicant of this club
    MembershipType.objects.create(user = request.user, club = user_club_choice, type = consts.APPLICANT)
    process_success_string(request=request, club_name=club_name)

def process_success_string(request,club_name):
    succes_string = 'You have successfully applied to' + club_name
    message_adder.add_success_message(request=request, success_string=succes_string)


