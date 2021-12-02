from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from .forms import CreateNewTournamentForm, SignUpForm
from django.contrib.auth import authenticate, login, logout
from .helpers import login_prohibited
from .forms import LogInForm, UserForm, PasswordForm, CreateNewClubForm
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from .models import Tournament, User, MembershipType, Club
from django.core.exceptions import ObjectDoesNotExist
from .Constants import consts
from .Utilities import promote_demote_helper
def get_club_choice(request):
    """Utility function to return the club name the user has selected."""
    return request.session['club_choice']



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

class LogInView(View):
    """ View that handles Log in. """

    http_method_names = ['get', 'post']

    @method_decorator(login_prohibited)
    def dispatch(self, request):
        return super().dispatch(request)

    def get(self, request):
        """ Display Log In template. """
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle Log In attempt."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or 'test'
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """ Render Log in template with blank log in form."""
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})
        
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

def get_promote_and_demote_subject_user_with_club(request, user_id):
    """This function returns a dictionary of the subject user along with
        the current selection of club in the session and the membership object.
        It raises an exception with the membership object is not found."""
    try:
        user = User.objects.get(pk=user_id)
        user_club = get_club_choice(request=request)
        if user_club:
            membership = MembershipType.objects.get(user=user, club = user_club)
        else:
            membership = None
        return {'membership':membership,'subject_user':user,'user_club':user_club}
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist

@login_required
def promote(request, user_id):
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
            new_type = promote_demote_helper.promote_user[membership.type]
            membership.type = new_type
            membership.save()
            message_string = "User has been successfully promoted to" + new_type
            messages.add_message(request,messages.SUCCESS, message_string)
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to promote users")
        return redirect("user_list")

@login_required
def demote(request, user_id):
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
            new_type = promote_demote_helper.demote_user[membership.type]
            membership.type = new_type
            membership.save()
            message_string = "User has been successfully demoted to" + new_type
            messages.add_message(request,messages.SUCCESS, message_string)
        else:
            messages.add_message(request, messages.ERROR, "You are not are not allowed to deomote users")
        return redirect("user_list")

@login_required
def transfer_ownership(request, user_id):
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
                new_type = promote_demote_helper.demote_user[owner_membership.type]
                owner_membership.type = new_type 
                owner_membership.save()
                membership.type = promote_demote_helper.promote_user[membership.type]
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
