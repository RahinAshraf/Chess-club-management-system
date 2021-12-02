from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from .forms import CreateNewTournamentForm, SignUpForm
from django.contrib.auth import authenticate, login, logout
from .helpers import login_prohibited
from .forms import LogInForm, UserForm, PasswordForm, CreateNewClubForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from .models import Tournament, User, MembershipType, Club
from django.core.exceptions import ObjectDoesNotExist
from .Constants import consts

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return redirect('test')
    else :
        return render(request, 'home.html')

def test(request):
    club = None
    membership_type = None
    try:
        club = request.session['club_choice']
        membership_type = request.user.get_membership_type_in_club(request.session['club_choice'])
    except:
        render(request, 'test.html', {'club':None, 'membership_type':None})

    return render(request, 'test.html', {'club':club, 'membership_type':membership_type})

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('test')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or 'test'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})


def log_out(request):
    logout(request)
    return redirect('home')

def edit_details(request):
    return redirect('edit_details')

@login_required
def switch_club(request):
    """Whenever the user chooses a club from the drop down in the navbar,
    the club object is saved in request.session['club_choice']
    and the user is redirected back to the same page.
    If the previous page doesn't exist, user is redirected to the test page"""

    previous_url = request.META.get('HTTP_REFERER')

    club = request.GET.get('club_choice', False)
    if club!=False:
        request.session['club_choice'] = club

    if previous_url:
        return redirect(previous_url)
    else:
        return redirect('test')

@login_required
def profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('test')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'profile.html', {'form': form})

@login_required
def promote(request, user_id):
    """user_id: the primary key of the user being promoted to 'member'
    Officers and Club Owners are able to promote specific applicants to members"""
    try:
        user = User.objects.get(pk=user_id)
        if request.session['club_choice']:
            membership = MembershipType.objects.get(user=user, club = request.session['club_choice'])
        else:
            membership = None

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user to promote")
        return redirect("user_list")
    else:
        current_user = request.user
        membership_type_of_current_user = current_user.get_membership_type_in_club(request.session['club_choice'])
        if membership_type_of_current_user==consts.OFFICER or membership_type_of_current_user==consts.CLUB_OWNER:
            if (membership.type=="applicant"):
                membership.type = "member"
                membership.save()
                messages.add_message(request, messages.SUCCESS, "User successfully promoted to member")
            elif (membership.type=="member"):
                membership.type = "officer"
                membership.save()
                messages.add_message(request, messages.INFO, "User successfully promoted to officer")
            else:
                messages.add_message(request, messages.INFO, "User is already a member")

            return redirect("user_list")
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to promote users")
            return redirect("user_list")

@login_required
def demote(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if request.session['club_choice']:
            membership = MembershipType.objects.get(user=user, club = request.session['club_choice'])
        else:
            membership = None

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user")
        return redirect("user_list")
    else:
        current_user = request.user
        membership_type_of_current_user = current_user.get_membership_type_in_club(request.session['club_choice'])
        if membership_type_of_current_user==consts.CLUB_OWNER:
            if (membership.type=="officer"):
                membership.type = "member"
                membership.save()
                messages.add_message(request, messages.SUCCESS, "User successfully demoted to member")

            return redirect("user_list")
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to deomote users")
            return redirect("user_list")

@login_required
def transfer_ownership(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        club = request.session['club_choice']
        membership = MembershipType.objects.get(user=user, club = club)

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Invalid user")
        return redirect("user_list")
    else:
        current_user = request.user

        owner_membership = MembershipType.objects.get(user=current_user, club = club)
        owner_membership_type = current_user.get_membership_type_in_club(club = club)
        if owner_membership_type==consts.CLUB_OWNER:
            if (membership.type=="officer"):
                owner_membership.type = "officer"
                owner_membership.save()
                membership.type = "club_owner"
                membership.save()
                user_club = Club.objects.get(pk = club)
                user_club.club_owner = user
                user_club.save()
                messages.add_message(request, messages.SUCCESS, "Ownership successfully transferred")
            else:
                messages.add_message(request, messages.ERROR, "You are only allowed to transfer the ownership to an officer")
                return redirect("user_list")

            return redirect("user_list")
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to transfer ownership")
            return redirect("user_list")




@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('test')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = PasswordForm()
    return render(request, 'password.html', {'form': form})

@login_required
def user_list(request):
    current_user = request.user
    try:
        current_user_club_name = request.session['club_choice']
        current_user_club = Club.objects.get(pk = request.session['club_choice'])
    except:
        return redirect('test')
    else:
        users = current_user_club.get_all_users_with_types()
        type = current_user.get_membership_type_in_club(current_user_club_name)
        return render(request, 'user_list.html', {'users': users, "type": type})


@login_required
def club_list(request):
    clubs = Club.objects.all()
    current_user = request.user
    existing_clubs_of_user = current_user.get_clubs()
    return render(request, 'club_list.html', {'clubs': clubs, 'existing_clubs':existing_clubs_of_user})


@login_required
def apply_to_club(request, club_name):
    user_club_choice = Club.objects.get(pk = club_name)
    print(user_club_choice)
    print(request.user)
    # Make user an applicant of this club
    MembershipType.objects.create(user = request.user, club = user_club_choice, type = consts.APPLICANT)
    succes_string = 'You have successfully applied to' + club_name
    messages.add_message(request, messages.SUCCESS, succes_string)
    return club_list(request = request)


@login_required
def create_new_club(request):
    if request.method == 'POST':
        form = CreateNewClubForm(request.POST)
        if form.is_valid():
            club = form.save(commit=False)
            club.club_owner = request.user
            club.save()
            form.save()
            # Create the new membership type. 
            # The membership is being manually created because the club models' save method is called instead of create 
            # which does not automatically create the new membership.
            MembershipType.objects.create(user = request.user, club = club, type = consts.CLUB_OWNER)
            messages.add_message(request, messages.SUCCESS, "You have created a new club!")
            return redirect('club_list')
    else:
        form = CreateNewClubForm()
    return render(request, 'create_club.html', {'form': form})

@login_required
def show_tournaments(request):
    current_user = request.user
    
    try:
        current_user_club_name = request.session['club_choice']
        current_user_club = Club.objects.get(pk = request.session['club_choice'])
    except:
        return redirect('test')
    else:
        tournaments = Tournament.objects.filter(club = current_user_club)
        type = current_user.get_membership_type_in_club(current_user_club_name)
        return render(request, 'tournament_list.html', {'tournaments': tournaments, "type": type,})

@login_required
def create_new_tournament(request):
    current_user_club = Club.objects.get(pk = request.session['club_choice'])
    if request.method == 'POST':
        form = CreateNewTournamentForm(request.POST)
        if form.is_valid():
            Tournament = form.save(commit=False)
            Tournament.organising_officer = request.user
            Tournament.club = current_user_club
            capacity = form.cleaned_data.get('capacity')
            Tournament.capacity = capacity
            Tournament.save()
            form.save()
            return redirect('tournaments')
        
    else:
        form = CreateNewTournamentForm()
    return render(request, 'create_tournament.html', {'form':form})


@login_required
def participate_in_tournament(request,tournament_id):
    current_user = request.user
    tournament = Tournament.objects.get(id = tournament_id)
    print(tournament)
    tournament.participating_players.add(User.objects.get(email = request.user.email))
    tournament_name = tournament.name
    messages.add_message(request, messages.SUCCESS, "You have successfully joined the tournament: " + tournament_name)
    return render(request, 'tournament_list.html', {"current_user":current_user,})





