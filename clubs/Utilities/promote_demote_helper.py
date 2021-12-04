from ..Constants import consts
from django.shortcuts import redirect
from ..models import User, MembershipType, Club, Tournament
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
promote_user = {consts.APPLICANT:consts.MEMBER,
                consts.MEMBER:consts.OFFICER,
                consts.OFFICER:consts.CLUB_OWNER,
                consts.CLUB_OWNER:consts.CLUB_OWNER}

demote_user = {consts.APPLICANT:consts.APPLICANT,
               consts.MEMBER:consts.MEMBER,
               consts.OFFICER:consts.MEMBER,
               consts.CLUB_OWNER:consts.OFFICER}

def get_promote_and_demote_subject_user_with_club(request, user_id):
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

def help_promote(request, user_id):
    """user_id: the primary key of the user being promoted to 'member'
    Officers and Club Owners are able to promote specific applicants to members"""
    try:
        subject_user_details = get_promote_and_demote_subject_user_with_club(request, user_id)
        user_club = subject_user_details['user_club']
        membership = subject_user_details['membership']

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user to promote")
        return redirect("user_list")
    else:
        current_user = request.user
        membership_type_of_current_user = current_user.get_membership_type_in_club(user_club)
        if membership_type_of_current_user==consts.OFFICER or membership_type_of_current_user==consts.CLUB_OWNER:
            new_type = promote_user[membership.type]
            membership.type = new_type
            membership.save()
            message_string = "User has been successfully promoted to" + new_type
            messages.add_message(request,messages.SUCCESS, message_string)
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to promote users")
        return redirect("user_list")

def help_demote(request, user_id):
    try:
        subject_user_details = get_promote_and_demote_subject_user_with_club(request, user_id)
        user_club = subject_user_details['user_club']
        membership = subject_user_details['membership']
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user")
        return redirect("user_list")
    else:
        current_user = request.user
        membership_type_of_current_user = current_user.get_membership_type_in_club(user_club)
        if membership_type_of_current_user==consts.CLUB_OWNER:
            new_type = demote_user[membership.type]
            membership.type = new_type
            membership.save()
            message_string = "User has been successfully demoted to" + new_type
            messages.add_message(request,messages.SUCCESS, message_string)
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to deomote users")
        return redirect("user_list")

def help_tansfer_ownership(request, user_id):
    try:
        subject_user_details = get_promote_and_demote_subject_user_with_club(request, user_id)
        user_club = subject_user_details['user_club']
        membership = subject_user_details['membership']
        user = subject_user_details['subject_user']
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user")
        return redirect("user_list")
    else:
        current_user = request.user
        owner_membership = MembershipType.objects.get(user=current_user, club = user_club)
        if owner_membership.type==consts.CLUB_OWNER:
            if (membership.type=="officer"):
                new_type = demote_user[owner_membership.type]
                owner_membership.type = new_type
                owner_membership.save()
                membership.type = promote_user[membership.type]
                membership.save()
                # Modifying the club owner of the Club model
                club = Club.objects.get(pk = user_club)
                club.club_owner = user
                club.save()
                messages.add_message(request, messages.SUCCESS, "Ownership successfully transferred")
            else:
                messages.add_message(request, messages.ERROR, "You are only allowed to transfer the ownership to an officer")
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to transfer ownership")
        return redirect("user_list")

def help_assign_organiser(request, user_id, tournament_id):
    try:
        subject_user_details = get_promote_and_demote_subject_user_with_club(request, user_id)
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
