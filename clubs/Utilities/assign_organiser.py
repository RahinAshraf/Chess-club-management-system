from ..Constants import consts
from ..Utilities import message_adder
from ..models import User, MembershipType, Club, Tournament
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

def get_subject_user_with_club(request, user_id):
    """This function returns a dictionary of the subject user along with
        the current selection of club in the session and the membership object.
        It raises an exception with the membership object is not found."""
    try:
        user = User.objects.get(pk=user_id)
        user_club = request.session['club_choice']
        if user_club:
            membership = MembershipType.objects.get(user=user, club = user_club)
        else:
            membership = None
        return {'membership':membership,'subject_user':user,'user_club':user_club}
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist


def help_assign_organiser(request, user_id, tournament_id):
    try:
        subject_user_details = get_subject_user_with_club(request, user_id)
        user_club = subject_user_details['user_club']
        membership = subject_user_details['membership']
        user = subject_user_details['subject_user']
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user")
        return redirect("user_list")
    else:
        current_user = request.user
        user_membership = MembershipType.objects.get(user=current_user, club=user_club)
        tournament = Tournament.objects.get(id = tournament_id)

        if user_membership.type == consts.OFFICER:
            if (membership.type == 'officer'):
                if Tournament.objects.filter(co_organising_officers=user).exists():
                    messages.add_message(request, messages.INFO, "The user is already co-organiser!")
                    return redirect("tournaments")
                tournament.co_organising_officers.add(user)
                messages.add_message(request, messages.SUCCESS, "You have successfully assigned " + str(user.first_name) + " as a co-organiser of the tournament: " + str(tournament.name))
            else:
                messages.add_message(request, messages.ERROR, "You are only allowed to assign officer as co-organiser!")
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to assign organisers!")
        return redirect("tournaments")
