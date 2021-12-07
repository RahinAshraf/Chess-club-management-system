from django.shortcuts import redirect, render
from .forms import CreateNewTournamentForm, SignUpForm
from django.contrib.auth import login, logout
from django.views.generic.edit import UpdateView
from .forms import LogInForm, UserForm, PasswordForm, CreateNewClubForm
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic.edit import CreateView
from .models import Tournament, User, Club
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.urls import reverse
from .Utilities import promote_demote_helper,create_applicant_membership_to_clubs,apply_tournament,switch_user_club,withdraw_tournament,assign_organiser

def get_club_choice(request):
    """Utility function to return the club name the user has selected."""
    return request.session['club_choice']

@login_required
def promote(request, user_id):
    return promote_demote_helper.help_promote(request=request,user_id=user_id)

@login_required
def demote(request, user_id):
    return promote_demote_helper.help_demote(request=request,user_id=user_id)

@login_required
def transfer_ownership(request, user_id):
    return promote_demote_helper.help_tansfer_ownership(request=request,user_id=user_id)

@login_required
def assign_coorganiser(request, tournament_id, user_id):
    return assign_organiser.help_assign_organiser(request=request,user_id=user_id,tournament_id=tournament_id)

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
    return apply_tournament.manage_tournament_application(request=request,tournament_id=tournament_id)

@login_required
def withdraw_from_tournament(request,tournament_id):
    return withdraw_tournament.manage_tournament_withdrawal(request=request, tournament_id=tournament_id)

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

class UserListView (LoginRequiredMixin, ListView):
    """View that shows a list of all users."""

    model = User
    template_name  = "user_list.html"
    context_object_name = "users"
    pk_url_kwarg = 'user_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""
        current_user = self.request.user
        current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
        current_user_club_name = self.request.session['club_choice']
        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        try:
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('test')
        else:
            context['users'] = current_user_club.get_all_users_with_types()
            context['type'] = current_user.get_membership_type_in_club(current_user_club_name)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('test')

    def redirect_url(self, url):
        return redirect('test')

class OfficerListView(LoginRequiredMixin, ListView):
    """View that shows a list of all officers."""
    model = User
    template_name  = "officer_list.html"
    context_object_name = "officers"
    pk_url_kwarg = 'user_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""
        current_user = self.request.user
        current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
        current_user_club_name = self.request.session['club_choice']
        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        try:
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('test')
        else:
            context['users'] = current_user_club.get_all_officers_with_types(current_user)
            context['type'] = current_user.get_membership_type_in_club(current_user_club_name)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('test')

    def redirect_url(self, url):
        return redirect('test')

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

class TournamentListView(LoginRequiredMixin, ListView):
    """View that shows a list of all tournaments."""

    model = Tournament
    template_name  = "tournament_list.html"
    context_object_name = "tournaments"
    pk_url_kwarg = 'tournament_id'

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        current_user = self.request.user
        current_user_club = Club.objects.get(pk = self.request.session['club_choice'])
        current_user_club_name = self.request.session['club_choice']
        tournaments = Tournament.objects.filter(club = current_user_club)

        context = super().get_context_data(*args, **kwargs)
        context['current_user'] = current_user
        try:
            context['current_user_club_name'] = current_user_club_name
            context['current_user_club'] = current_user_club
        except:
            return self.redirect_url('test')
        else:
            context['tournaments'] = tournaments
            context['type'] = current_user.get_membership_type_in_club(current_user_club_name)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get   request, and redirect   to user_list if user_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return self.redirect_url('test')

    def redirect_url(self, url):
        return redirect('test')


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
