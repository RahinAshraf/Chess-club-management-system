"""Forms for the clubs app."""
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db.models import fields
from django.forms import widgets
from .models import Tournament, User
from .models import MembershipType, Club
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

    def make_applicant(self,user):
        MembershipType.objects.create(user = user, type = consts.APPLICANT)

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""
        user = None
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')
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


class CreateNewClubForm(forms.ModelForm):

    class Meta:
        #Form options
        model = Club
        fields = ['name','location','mission_statement']

class CreateNewTournamentForm(forms.ModelForm):

    class Meta:
       model = Tournament
       fields = ['name', 'description','deadline_to_apply'] 
       widgets = {'description':forms.Textarea()}

    capacity = forms.IntegerField(min_value=2, max_value=96,required=True,
                                error_messages={'required':'Please enter a capacity',
                                'max_value':'The max value is 96','min_value':'The min value is 2'})
        
    
