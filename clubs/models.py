from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db.models.constraints import UniqueConstraint
from django.db.models.expressions import F
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .Constants import consts
from libgravatar import Gravatar
from django.utils import timezone

class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        '''Create and save a user with the given email, and
        password.
        '''
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('first_name',"Admin")
        extra_fields.setdefault('last_name',"Admin")
        extra_fields.setdefault("chess_experience_level", 1)
        extra_fields.setdefault("personal_statement","Admin Statement")

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.'
            )

        return self._create_user(email, password, **extra_fields)

class MembershipTypeManager(models.Manager):

    def _is_user_a_part_of_the_same_club(self, user, club):
        if len(MembershipType.objects.filter(user = user).filter(club = club)) >= 1:
            return True
        else:
            return False

    def create(self, **obj_data):
        type = obj_data['type']
        club = obj_data['club']
        user = obj_data['user']
        if self._is_user_a_part_of_the_same_club(user=user, club=club):
            raise ValueError('User cannot hold multiple positions in the same club')
        else :
            if type == consts.CLUB_OWNER:
                if len(MembershipType.objects.filter(type = type).filter(club = club)) >= 1:
                    raise ValueError('There can only be one club owner')
                else:
                    return super().create(**obj_data)
            else:
                return super().create(**obj_data)

class ClubModelManager(models.Manager):
    def create(self, **obj_data):
        user = obj_data['club_owner']
        club = super().create(**obj_data)

        # Creating the membership type object
        MembershipType.objects.create(user = user, club = club, type = consts.CLUB_OWNER)
        return club

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        unique=True,
        max_length=255,
        blank=False,
    )

    # All these field declarations are copied as-is
    # from `AbstractUser`
    first_name = models.CharField(
        _('first name'),
        max_length=50,
        blank=False,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=50,
        blank=False,
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into '
            'this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be '
            'treated as active. Unselect this instead '
            'of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default = timezone.now,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_type(self):
        """Returns the user's type, as in whether the user is an 'applicant','member', etc.
        If the relationship doesn't exist, return None"""

        try:
            memberType = MembershipType.objects.get(user=self)
            return memberType.type
        except MembershipType.DoesNotExist:
            return None

    def get_membership_type_in_club(self, club):
        club = Club.objects.get(pk = club)
        
        try:
            memberType = MembershipType.objects.filter(user=self,club = club)
            return memberType[0].type
        except MembershipType.DoesNotExist:
            return None
            

    def get_clubs(self):
        """Returns a list of clubs that the user is in"""

        memberships = MembershipType.objects.filter(user=self)
        clubs = []
        for membership in memberships:
            clubs.append(membership.club)

        return clubs

    def get_member_clubs(self):
        """Returns a list of clubs that the user is a member of (that means that type of the user != applicant) """

        memberships = MembershipType.objects.filter(user=self).exclude(type=consts.APPLICANT)

        clubs = []
        for membership in memberships:
            clubs.append(membership.club)

        return clubs

    chess_experience_level = models.IntegerField(blank=False, validators = [MinValueValidator(1)])
    public_bio = models.CharField(blank=True, max_length=520) # using CharField for making validation of max_length possible
    personal_statement = models.TextField(blank=False)


""" Add some custom validator methods which are used for the Membeship Type model """

def validate_membership_type(value):
    if value != consts.APPLICANT and value != consts.MEMBER and value != consts.OFFICER and value != consts.CLUB_OWNER:
        raise ValidationError(
            _('%(value)s is not a member, officer, applicant or club owner'),
            params={'value': value},
        )


class Club(models.Model):
    club_owner = models.ForeignKey(User, on_delete = models.CASCADE,)
    name = models.CharField(unique=True, blank=False, max_length=90, primary_key=True)
    location = models.CharField(blank=False, max_length=100)
    mission_statement = models.CharField(blank=False, max_length=800)

    def get_all_users(self):
        """Returns a list of the users in this club"""

        memberships = MembershipType.objects.filter(club=self)

        users = []
        for membership in memberships:
            users.append(membership.user)

        return users

    def get_all_users_with_types(self):
        """Returns a list of the users with their types in this club"""

        memberships = MembershipType.objects.filter(club=self)

        users_membership_type = {}
        for membership in memberships:
            users_membership_type[membership.user] = membership.type

        return users_membership_type
    
    def get_number_of_members(self):
        """ Returns the number of members in the club"""

        memberships = MembershipType.objects.filter(club = self)

        return len(memberships)
        
    objects = ClubModelManager()
    


class MembershipType(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE,)
    club = models.ForeignKey(Club, on_delete=models.CASCADE,)
    type = models.CharField(blank = False, max_length = 20, validators=[validate_membership_type])
    objects = MembershipTypeManager()

    def clean(self):
        if self.type == consts.CLUB_OWNER:
            if len(MembershipType.objects.filter(club = self.club).filter(type = consts.CLUB_OWNER)) >= 1:
                raise ValidationError('There can only be one club owner')
