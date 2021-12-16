"""Forms for the clubs app."""
from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login
from .models import Tournament, User
from .models import MembershipType, Club,Score
from .Constants import consts
class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'email', 'chess_experience_level', 'public_bio', 'personal_statement']
        widgets = { 'public_bio': forms.Textarea(), 'personal_statement': forms.Textarea()}

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user and make the user an applicant."""

        super().save(commit=False)
        user = User.objects.create_user(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            chess_experience_level=self.cleaned_data.get('chess_experience_level'),
            public_bio=self.cleaned_data.get('public_bio'),
            personal_statement=self.cleaned_data.get('personal_statement'),
        )
        return user

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_email(self):
        """This method returns the email from the form"""
        return self.cleaned_data.get('email')

    def get_password(self):
        """This method returns the password"""
        return self.cleaned_data.get('password')

    def get_user(self):
        """Returns authenticated user if possible."""
        user = None
        if self.is_valid():
            email = self.get_email() #self.cleaned_data.get('email')
            password = self.get_password()# self.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
        
        return user

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'email', 'chess_experience_level', 'public_bio', 'personal_statement']
        widgets = { 'public_bio': forms.Textarea(), 'personal_statement': forms.Textarea()}


class PasswordForm(forms.Form):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def save_user(self,user):
        """This method saves the user"""
        user.save()

    def set_password_for_user(self, new_password, user):
        """This method sets the new password for the user."""
        user.set_password(new_password)

    def get_old_password(self):
        """This method returns the old password for the form."""
        return self.cleaned_data.get('password')

    def get_new_password(self):
        """This method returns the new password from a form."""
        return self.cleaned_data.get('new_password')

    def login_user(self,request):
        """This method logs in the user."""
        login(request,request.user)

    def process_valid_data(self,request):
        """This method processes valid form data."""
        password = self.get_old_password()                
        if check_password(password, request.user.password):
            new_password = self.get_new_password()                                 
            self.set_password_for_user(new_password,request.user)    
            self.save_user(request.user)     
            self.login_user(request)
            return True
        else:
            return False

class CreateNewClubForm(forms.ModelForm):

    class Meta:
        #Form options
        model = Club
        fields = ['name','location','mission_statement']

    def set_club_owner(self,club_owner,club):
        """This method sets the club owner of the club."""
        club.club_owner = club_owner

    def save_club(self, club):
        """This method saves a club"""
        club.save()

    def get_club(self):
        """This method returns the club if the form. This should be called if form is valid."""
        return self.save(commit=False)

    def set_membership_type_for_club_owner(self,user,club):
        """This method sets the membership for a club owner in a club."""
        MembershipType.objects.create(user = user, club = club, type = consts.CLUB_OWNER)

    def process_valid_form(self,user):
        """This method processes valid form data. It creates the necessary models and relationships
           when valid data is sent."""
        if self.is_valid():
            club = self.get_club()                    
            self.set_club_owner(user,club)            
            self.save_club(club)                      
            # Create the new membership type. 
            # The membership is being manually created because the club models' save method is called instead of create 
            # which does not automatically create the new membership.
            self.set_membership_type_for_club_owner(user,club)#MembershipType.objects.create(user = user, club = club, type = consts.CLUB_OWNER)

class CreateNewTournamentForm(forms.ModelForm):

    class Meta:
       model = Tournament
       fields = ['name', 'description','deadline_to_apply'] 
       widgets = {'description':forms.Textarea()}

    capacity = forms.IntegerField(min_value=2, max_value=96,required=True,
                                error_messages={'required':'Please enter a capacity',
                                'max_value':'The max value is 96','min_value':'The min value is 2'})

    def get_tournament(self):
        """This method gives the tournament. This method should be called when the form is valid."""
        return self.save(commit=False)
    
    def set_organising_officer(self, tournament, organising_officer):
        """This method sets the organising officer for the tournament"""
        tournament.organising_officer = organising_officer

    def set_club(self,tournament,club):
        """This method sets the club for the tournament"""
        tournament.club = club

    def get_capacity(self):
        """This method gives the tournament capacity"""
        return self.cleaned_data.get('capacity')

    def set_capacity(self,tournament,capacity):
        """This method sets the capacity for the tournament"""
        tournament.capacity = capacity

    def save_tournament(self,tournament):
        """This method saves the tournament"""
        return tournament.save()

    def process_form_with_organiser_data(self,current_user_club,organising_officer):
        """This method takes in the current club of the organiser and the organiser
           to create a valid instance of Tournament object. If successfully created, it will
           return the result of save being called on Tournament."""
        if self.is_valid():
            Tournament = self.get_tournament()
            self.set_organising_officer(Tournament,organising_officer)
            self.set_club(Tournament,current_user_club)
            capacity = self.get_capacity()
            self.set_capacity(Tournament,capacity)
            return self.save_tournament(Tournament) 
        else:
            return None

class Score(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['score'] 

