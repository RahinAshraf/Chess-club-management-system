from django.shortcuts import redirect, render
from .forms import CreateNewTournamentForm, SignUpForm
from django.contrib.auth import login, logout
from django.conf import settings
from django.views.generic.edit import UpdateView
from .forms import LogInForm, UserForm, PasswordForm, CreateNewClubForm
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic.edit import CreateView
from .models import Round, Tournament, User, Club, MembershipType
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.urls import reverse
from .Utilities import promote_demote_helper,create_applicant_membership_to_clubs
from .Utilities import apply_tournament,switch_user_club,club_tournament_helper
from .Utilities import withdraw_tournament,assign_organiser,generate_match_helper,score_player_helper

def get_club_choice(request):
    """Utility function to return the name of the club the user has selected."""
    return request.session['club_choice']


@login_required
def promote(request, user_id):
    try:
        request.session['club_choice']
        return promote_demote_helper.help_promote(request=request,user_id=user_id)
    except:
        return redirect('user_profile') 

@login_required
def demote(request, user_id):
    try:
        request.session['club_choice']
        return promote_demote_helper.help_demote(request=request,user_id=user_id)
    except:
        return redirect('user_profile')
@login_required
def transfer_ownership(request, user_id):
    try:
        request.session['club_choice']
        return promote_demote_helper.help_tansfer_ownership(request=request,user_id=user_id)
    except:
        return redirect('user_profile')

@login_required
def assign_coorganiser(request, tournament_id, user_id):
    try:
        request.session['club_choice']
        return assign_organiser.help_assign_organiser(request=request,user_id=user_id,tournament_id=tournament_id)
    except:
        return redirect('user_profile')

def log_out(request):
    logout(request)
    return redirect('home')

def edit_details(request):
    return redirect('edit_details')

@login_required
def switch_club(request):
    return switch_user_club.help_switch_club(request=request)

@login_required
def participate_in_tournament(request,tournament_id):
    try:
        request.session['club_choice']
        return apply_tournament.manage_tournament_application(request=request,tournament_id=tournament_id)
    except:
        return redirect('user_profile')

@login_required
def withdraw_from_tournament(request,tournament_id):
    try:
        request.session['club_choice']
        return withdraw_tournament.manage_tournament_withdrawal(request=request, tournament_id=tournament_id)
    except:
        return redirect('user_profile')

@login_required
def generate_matches(request, tournament_id):
    try:
        request.session['club_choice']
        return generate_match_helper.help_generate_mathes(request,tournament_id)
    except:
        return redirect('user_profile')
    

@login_required
def score_player(request,round_id,match_id,player_id):
    try:
        request.session['club_choice']
        return score_player_helper.help_score_player(request,round_id,match_id,player_id)
    except:
        return redirect('user_profile')

@login_required
def draw_match(request,round_id,match_id):
    try:
        request.session['club_choice']
        return score_player_helper.help_draw_match(request,round_id,match_id)
    except:
        return redirect('user_profile')

@login_required
def apply_to_club(request, club_name):
    create_applicant_membership_to_clubs.create_applicant_of_club(request=request, club_name=club_name)
    return redirect('club_list')

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

class UserProfileView(LoginRequiredMixin,View):
    http_method_names = ['get']
    
    def get(self, request):
       self.club = None
       self.membership_type = None
       try:
           self.club = request.session['club_choice']
           self.membership_type = request.user.get_membership_type_in_club(self.club)
       except:
            render(request, 'user_profile.html', {'club':None, 'membership_type':None})
       return render(request, 'user_profile.html', {'club':self.club, 'membership_type':self.membership_type})

class HomeView(LoginProhibitedMixin,View):
    http_method_names = ['get']

    redirect_when_logged_in_url = 'user_profile'

    def get(self, request):
        return render(request, 'home.html')

class LogInView(LoginProhibitedMixin,View):
    """ View that handles Log in. """

    http_method_names = ['get', 'post']

    redirect_when_logged_in_url = 'user_profile'

    def get(self, request):
        """ Display Log In template. """
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle Log In attempt."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or 'user_profile'
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
    redirect_when_logged_in_url = 'user_profile'

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('user_profile')

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
        return reverse('user_profile')

class UserListView (LoginRequiredMixin, ListView):
    """View that shows a list of all users."""

    model = MembershipType
    template_name  = "user_list.html"
    context_object_name = "users"
    paginate_by = settings.USERS_PER_PAGE

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        current_user = self.request.user
        context = super().get_context_data(*args, **kwargs)

        context['current_user'] = current_user
        try:
            current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
            current_user_club_name = self.request.session['club_choice']
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('user_profile')
        else:
            context['type'] = current_user.get_membership_type_in_club(current_user_club_name)
        return context

    def get_queryset(self):
        current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
        return MembershipType.objects.filter(club = current_user_club).order_by('user__last_name', 'user__first_name')

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to user_list if user_id invalid."""
        try:
            current_user_club_name = self.request.session['club_choice']
            if current_user_club_name is None:
                return self.redirect_url('test')
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('user_profile')
        except KeyError:
            return self.redirect_url('user_profile')

    def redirect_url(self, url):
        return redirect(url)

class OfficerListView(LoginRequiredMixin, ListView):
    """View that shows a list of all officers."""
    model = User
    template_name  = "officer_list.html"
    context_object_name = "officers"
    pk_url_kwarg = 'user_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""
        current_user = self.request.user
        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        tournament_id = self.kwargs['tournament_id']
        tournament = Tournament.objects.get(id=tournament_id)
        try:
            current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
            current_user_club_name = self.request.session['club_choice']
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('user_profile')
        else:
            context['users'] = current_user_club.get_all_officers_with_types(current_user)
            context['type'] = current_user.get_membership_type_in_club(current_user_club_name)
            context['tournament'] = tournament
        return context

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""
        try:
            self.request.session['club_choice']
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('user_profile')
        except KeyError:
            return self.redirect_url('user_profile')

    def redirect_url(self, url):
        return redirect(url)

class MatchListView(LoginRequiredMixin, ListView):
    """View that shows a list of ongoing matches."""
    model = User
    template_name  = "match_list.html"
    context_object_name = "users"
    pk_url_kwarg = 'user_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""
        current_user = self.request.user
        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        tournament_id = self.kwargs['tournament_id']
        tournament = Tournament.objects.get(id=tournament_id)
        context['tournament'] = tournament
        context['rounds'] = Round.objects.filter(Tournament = tournament)
        try:
            current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
            current_user_club_name = self.request.session['club_choice']
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('user_profile')
        else:
            context['matches'] =tournament.get_all_matches()
        return context

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""
        try:
            club_name = self.request.session['club_choice']
            club = Club.objects.get(pk=club_name)
            club_tournament_helper.does_club_have_some_tournament(club)
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('user_profile')
        except KeyError:
            return self.redirect_url('user_profile')
        except ObjectDoesNotExist:
            return self.redirect_url('user_profile')

    def redirect_url(self, url):
        return redirect(url)

class AllMatchListView(LoginRequiredMixin, ListView):
    """View that shows a list of matches."""
    model =  User
    template_name  = "all_match_list.html"
    context_object_name = "users"
    pk_url_kwarg = 'user_id'

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""
        try:
            club_name = self.request.session['club_choice']
            club = Club.objects.get(pk=club_name)
            club_tournament_helper.does_club_have_some_tournament(club)
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('user_profile')
        except KeyError:
            return self.redirect_url('user_profile')
        except ObjectDoesNotExist:
            return self.redirect_url('user_profile')

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""
        current_user = self.request.user
        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        tournament_id = self.kwargs['tournament_id']
        tournament = Tournament.objects.get(id=tournament_id)
        context['tournament'] = tournament
        try:
            current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
            current_user_club_name = self.request.session['club_choice']
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('user_profile')
        return context

    def redirect_url(self, url):
        return redirect(url)

class ClubListView(LoginRequiredMixin, ListView):
    """View that shows a list of all clubs."""
    model = Club
    template_name  = "club_list.html"
    context_object_name = "clubs"
    pk_url_kwarg = 'club_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        current_user = self.request.user

        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        context['existing_clubs'] = current_user.get_clubs()
        return context

class CreateNewClubView(LoginRequiredMixin,CreateView):
    """View for creating a new club """
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
        return redirect('user_profile')

class TournamentListView(LoginRequiredMixin, ListView):
    """View that shows a list of all tournaments."""

    model = Tournament
    template_name  = "tournament_list.html"
    context_object_name = "tournaments"
    pk_url_kwarg = 'tournament_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        current_user = self.request.user
        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        try:
            current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
            current_user_club_name = self.request.session['club_choice']
            tournaments = Tournament.objects.filter(club = current_user_club)
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('user_profile')
        else:
            context['tournaments'] = tournaments
            context['type'] = current_user.get_membership_type_in_club(current_user_club_name)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""

        try:
            self.request.session['club_choice']
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('user_profile')
        except KeyError:
            return self.redirect_url('user_profile')

    def redirect_url(self, url):
        return redirect(url)


class CreateNewTournamentView(LoginRequiredMixin,CreateView):
    """View for creating a new tournament."""
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

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""

        try:
            self.request.session['club_choice']
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('user_profile')
        except KeyError:
            return self.redirect_url('user_profile')

    def handle_no_permission(self):
        return redirect('user_profile')

    def redirect_url(self, url):
        return redirect(url)
