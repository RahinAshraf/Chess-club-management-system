from django.shortcuts import redirect, render
from .forms import CreateNewTournamentForm, SignUpForm
from django.contrib.auth import login, logout
from django.views.generic.edit import UpdateView
from .forms import LogInForm, UserForm, PasswordForm, CreateNewClubForm
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from .models import Tournament, User, MembershipType, Club
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.urls import reverse
from .Constants import consts
from .Utilities import promote_demote_helper
def get_club_choice(request):
    """Utility function to return the club name the user has selected."""
    return request.session['club_choice']

class TestView(LoginRequiredMixin,View):
    http_method_names = ['get']

    def get(self, request):
       self.club = None
       self.membership_type = None
       try:
           self.club = request.session['club_choice']
           self.membership_type = request.user.get_membership_type_in_club(self.club)
       except:
            render(request, 'test.html', {'club':None, 'membership_type':None})
       return render(request, 'test.html', {'club':self.club, 'membership_type':self.membership_type})

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""
    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            url = self.get_redirect_when_logged_in_url()
            return redirect(url)
        return super().dispatch(*args, **kwargs)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to be redirected to"""
        if self.redirect_when_logged_in_url == None:
            raise ImproperlyConfigured()
        else:
            return self.redirect_when_logged_in_url

class HomeView(LoginProhibitedMixin,View):
    http_method_names = ['get']

    redirect_when_logged_in_url = 'test'

    def get(self, request):
        return render(request, 'home.html')
    
class LogInView(LoginProhibitedMixin,View):
    """ View that handles Log in. """

    http_method_names = ['get', 'post']

    redirect_when_logged_in_url = 'test'

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

class SignUpView(LoginProhibitedMixin, FormView):
    """View that signs up user."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = 'test'

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('test')
        
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

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse('test')

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
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            form.process_valid_data(request=request)
        else:
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
    # Make user an applicant of this club
    MembershipType.objects.create(user = request.user, club = user_club_choice, type = consts.APPLICANT)
    succes_string = 'You have successfully applied to' + club_name
    messages.add_message(request, messages.SUCCESS, succes_string)
    return club_list(request = request)

class CreateNewClubView(LoginRequiredMixin,CreateView):
    model = Club
    template_name = 'create_club.html'
    form_class = CreateNewClubForm
    http_method_names = ['post', 'get']

    def form_valid(self, form):
        """Process a valid form."""
        form.process_valid_form(user = self.request.user)
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('club_list')

    def handle_no_permission(self):
        return redirect('test')

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

class CreateNewTournamentView(LoginRequiredMixin,CreateView):
    model = Tournament
    template_name = 'create_tournament.html'
    form_class = CreateNewTournamentForm
    http_method_names = ['post', 'get']

    def form_valid(self, form):
        """Process a valid form."""
        organising_officer = self.request.user
        current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
        form.process_form_with_organiser_data(current_user_club = current_user_club, organising_officer = organising_officer)
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user too after valid form handling."""
        return reverse('tournaments')

    def handle_no_permission(self):
        return redirect('test')

@login_required
def participate_in_tournament(request,tournament_id):
    current_user = request.user
    tournament = Tournament.objects.get(id = tournament_id)
    tournament.participating_players.add(User.objects.get(email = request.user.email))
    tournament_name = tournament.name
    messages.add_message(request, messages.SUCCESS, "You have successfully joined the tournament: " + tournament_name)
    return render(request, 'tournament_list.html', {"current_user":current_user,})
