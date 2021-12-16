from django.http import request
from ..Constants import consts
from ..Utilities import message_adder
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

# This section deals with the messages of the requests.

##########################################################################################

def process_success_demote_message(request, new_type):
    message_string = "User has been successfully demoted to" + new_type
    message_adder.add_success_message(request=request, success_string=message_string)

def process_success_promote_message(request, new_type):
    message_string = "User has been successfully promoted to" + new_type
    message_adder.add_success_message(request=request, success_string=message_string)

def process_failed_demote_message(request):
    message_string = "You are not are not allowed to deomote users"
    message_adder.add_error_message(request=request, error_string=message_string)

def process_failed_promote_message(request):
    message_string = "You are not are not allowed to promote users"
    message_adder.add_error_message(request=request, error_string=message_string)

def process_non_existing_user_message(request):
    message_string = "Invalid user."
    message_adder.add_error_message(request = request, error_string=message_string)

def process_successful_transfer_message(request):
    message_string = "Ownership successfully transferred"
    message_adder.add_success_message(request,message_string)

def process_unsuccessful_transfer_message(request):
    message_string = "You are only allowed to transfer the ownership to an officer or you are not a club owner."
    message_adder.add_error_message(request,message_string)

##########################################################################################

# This section helps with checking and processing the user who wants to promote/demote/transfer ownership.

###################################################################################################################

def is_current_user_officer_or_club_owner(membership_type_of_current_user):
    return membership_type_of_current_user==consts.OFFICER or membership_type_of_current_user==consts.CLUB_OWNER

def is_current_user_club_owner(membership_type_of_current_user):
    return membership_type_of_current_user==consts.CLUB_OWNER

def process_promoting_user_existence(request, user_id):
    """This function helps process the request based on the existence of the user. 
    If user exists nothing further is done."""
    try:
        get_promote_and_demote_subject_user_with_club(request, user_id)
    except ObjectDoesNotExist:
        process_non_existing_user_message(request=request)
    else:
        process_current_user_promoting_access_rights(request,user_id)

def process_demoting_user_existence(request, user_id):
    """This function helps process the request based on the existence of the user. 
    If user exists nothing further is done."""
    try:
        get_promote_and_demote_subject_user_with_club(request, user_id)
    except ObjectDoesNotExist:
        process_non_existing_user_message(request=request)
    else:
        process_current_user_demoting_access_rights(request,user_id)

def process_transfer_ownership_user_existence(request, user_id):
    """This function helps process the request based on the existence of the user. 
    If user exists nothing further is done."""
    try:
        get_promote_and_demote_subject_user_with_club(request, user_id)
    except ObjectDoesNotExist:
        process_non_existing_user_message(request=request)
    else:
        process_current_user_transfer_ownership_rights(request,user_id)

def process_promotion_of_subject_user(request,membership):
    """This method changes the membership type by promoting it and processes success situation."""
    new_type = promote_user[membership.type]
    membership.type = new_type
    membership.save()
    process_success_promote_message(request=request, new_type=new_type)

def process_demotion_of_subject_user(request, membership):
    """This method changes the membership type by demoting it and processes success situation."""
    new_type = demote_user[membership.type]
    membership.type = new_type
    membership.save()
    process_success_demote_message(request=request, new_type=new_type)

def process_transfership_of_current_user(user,owner_membership, membership, user_club):
    """This method changes the membership type by changing the membership type of an owner to an officer."""
    new_type = demote_user[owner_membership.type]
    owner_membership.type = new_type
    owner_membership.save()
    membership.type = promote_user[membership.type]
    membership.save()
    # Modifying the club owner of the Club model
    club = Club.objects.get(pk = user_club)
    club.club_owner = user
    club.save()

def process_current_user_promoting_access_rights(request,user_id):
    """This method is a manager for the promotion of users."""
    subject_user_details = get_promote_and_demote_subject_user_with_club(request, user_id)
    user_club = subject_user_details['user_club']
    membership = subject_user_details['membership']
    current_user = request.user
    membership_type_of_current_user = current_user.get_membership_type_in_club(user_club)

    if is_current_user_officer_or_club_owner(membership_type_of_current_user):
        process_promotion_of_subject_user(request=request, membership=membership)
    
    else:
        process_failed_promote_message(request=request)

def process_current_user_demoting_access_rights(request, user_id):
    """This method is a manager for the demotion of users"""
    subject_user_details = get_promote_and_demote_subject_user_with_club(request, user_id)
    user_club = subject_user_details['user_club']
    membership = subject_user_details['membership']
    current_user = request.user
    membership_type_of_current_user = current_user.get_membership_type_in_club(user_club)
    if is_current_user_club_owner(membership_type_of_current_user):
        process_demotion_of_subject_user(request=request, membership=membership)

    else:
        process_failed_demote_message(request=request)


def process_current_user_transfer_ownership_rights(request, user_id):
    """This method is a manager for the transfer of ownership"""
    subject_user_details = get_promote_and_demote_subject_user_with_club(request, user_id)
    user_club = subject_user_details['user_club']
    membership = subject_user_details['membership']
    user = subject_user_details['subject_user']
    current_user = request.user
    owner_membership = MembershipType.objects.get(user=current_user, club = user_club)
    if is_current_user_club_owner(owner_membership.type) and membership.type == consts.OFFICER:
        process_transfership_of_current_user(user, owner_membership, membership, user_club)
        process_successful_transfer_message(request=request)
    else:
        process_unsuccessful_transfer_message(request=request)
    
###################################################################################################################

# This section is focused on the calling the above processing functions.

##################################################################################
def help_promote(request, user_id):
    process_promoting_user_existence(request=request, user_id=user_id)
    return redirect("user_list")

def help_demote(request, user_id):
    process_demoting_user_existence(request=request, user_id=user_id)
    return redirect("user_list")


def help_tansfer_ownership(request, user_id):
    process_transfer_ownership_user_existence(request=request, user_id=user_id)
    return redirect("user_list")

##################################################################################