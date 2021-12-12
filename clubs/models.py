from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db.models.constraints import UniqueConstraint
from django.db.models.expressions import F
from django.db.models.fields import AutoField, proxy
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .Constants import consts,scores
from libgravatar import Gravatar
from django.utils import timezone
import itertools
import random
import copy

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


class scoreModelManager(models.Manager):
    def _is_user_a_part_of_the_same_club(self, player, match):
        """This function tests whether a user has a score already within a specific match.
        If yes, then it would raise a value error."""
        if len(Score.objects.filter(player = player).filter(match = match)) >= 1:
            raise ValueError('Player cannot have the different scores in same match')
        return False

    def create(self, **obj_data):
        player = obj_data['player']
        match = obj_data['match']
        self._is_user_a_part_of_the_same_club(player,match)
        score = super().create(**obj_data)
        return score

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

    def get_all_officers_with_types(self, user):
        """Return a list of officers with their type in club exclude the given user"""
        memberships = MembershipType.objects.filter(club=self, type='officer').exclude(user=user)

        users_membership_type = {}
        for membership in memberships:
            users_membership_type[membership.user] = membership.type

        return users_membership_type

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



"""Add some custom validators for the Score model."""
def validate_scores(value):
        if value not in scores.score_list:
            raise ValidationError('Score value used is invalid')

class Match(models.Model):
    id = models.AutoField(primary_key=True)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Player1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Player2')
    date = models.DateField()

    def is_player_in_the_match(self,player):
        """Tests whether the given player is one of the above players."""
        return player == self.player1 or player == self.player2

    def is_organising_officer_in_the_match(self,officer):
        """This tests if organiser is one of the players. If so, it raises a Validation Error."""
        if self.is_player_in_the_match(officer):
            raise ValidationError('Officer cannot be in the match.')

    def are_co_organising_officers_a_part_of_the_match(self,co_organising_officers):
        """This tests if organiser is one of the players. If so, it raises a Validation Error."""
        for co_organising_officer in co_organising_officers:
            self.is_organising_officer_in_the_match(co_organising_officer)

    def validate_two_players_are_not_the_same(self):
        """This tests whether a match has been created between the same player."""
        if self.player1 == self.player2:
            raise ValidationError('A player cannot enter a match with themself.')

    def get_all_players(self):
        """This method returns the players in the match as a list."""
        list_of_players = []
        list_of_players.append(self.player1)
        list_of_players.append(self.player1)
        return list_of_players

    def get_other_player(self,player):
        """This method gives the other player in the match than the one given in the parameters."""
        if self.player1 != player:
            return self.player1
        return self.player2

    def put_score_for_player(self,round,score,player):
        Score.objects.create(player = player, match = self, round = round, score=score)

    def put_score_for_player2(self, round, score):
        Score.objects.create(player = self.player2, match = self, round = round, score=score)

    def has_match_been_scored(self,round):
        try:
            Score.objects.get(player = self.player1, match = self, round = round)
            Score.objects.get(player = self.player2, match = self, round = round)
            return True
        except:
            return False

    def save(self, *args, **kwargs):
        self.validate_two_players_are_not_the_same()
        return super().save(*args, **kwargs)


class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    participating_players = models.ManyToManyField(User,related_name='participating players+')
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=190)
    capacity = models.IntegerField(blank=False, validators = [MinValueValidator(2),MaxValueValidator(96)])
    organising_officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organising officer+')
    co_organising_officers = models.ManyToManyField(User, blank=True, related_name='co-organising officers+')
    deadline_to_apply = models.DateTimeField(blank=False)
    matches = models.ManyToManyField(Match,blank=True,related_name='matches+')

    def _validate_participating_players_capacity(self):
        tournament = Tournament.objects.filter(pk = self.id)[0]
        if tournament.participating_players.all().count() > int(self.capacity):
            raise ValidationError('The number of participating players are not confirming to the capacity constraints.')

    def _validate_participating_players_must_not_include_organizers(self):
        tournament = Tournament.objects.filter(pk = self.id)[0]
        if tournament.participating_players.all().count() != 0:
            for player in tournament.participating_players.all():
                if player == self.organising_officer:
                    raise ValidationError('The organiser cannot participate.')

    def is_co_organiser_a_participating_player(self, co_organiser):
        tournament = Tournament.objects.filter(pk = self.id)[0]
        existing_players = tournament.participating_players.all()
        if co_organiser in existing_players:
            raise ValidationError('Co-organising player cannot be a participating player.')

    def _validate_participating_players_must_not_include_co_organizers(self):
        tournament = Tournament.objects.filter(pk = self.id)[0]
        for co_organising_officer in tournament.co_organising_officers.all():
            self.is_co_organiser_a_participating_player(co_organising_officer)

    def _validate_co_organiser_type(self):
        tournament = Tournament.objects.filter(pk = self.id)[0]
        for co_organising_officer in tournament.co_organising_officers.all():
            if co_organising_officer.get_membership_type_in_club(self.club.name) != consts.OFFICER:
                raise ValidationError('The co orginising officers must be an officer.')

    def _validate_organizer_type(self):
        if self.organising_officer.get_membership_type_in_club(self.club.name) != consts.OFFICER:
            raise ValidationError('The organiser must be an officer.')

    def get_associated_members(self):
        """ Returns all associated players and organizers of the tournament."""
        associated_member_list = []
        tournament = Tournament.objects.get(pk = self.id)
        # Adding Players
        for player in tournament.participating_players.all():
            associated_member_list.append(player)
        # Adding the organising officer
        associated_member_list.append(self.organising_officer)
        # Adding the co - organizing officer(s)
        for co_organising_officer in tournament.co_organising_officers.all():
            associated_member_list.append(co_organising_officer)
        return associated_member_list

    def get_all_matches(self):
        """Returns all matches"""
        matches = []
        tournament = Tournament.objects.get(pk = self.id)

        for match in tournament.matches.all():
            matches.append(match)

        return matches

    def get_number_of_co_organisers(self):
        tournament = Tournament.objects.get(pk = self.id)
        return tournament.co_organising_officers.all().count()

    def get_number_of_participating_players(self):
        tournament = Tournament.objects.get(pk = self.id)
        return tournament.participating_players.all().count()

    def _validate_that_the_organising_officer_a_part_of_any_matches(self):
        """This method returns a validation error if the organising officer is in any match."""
        tournament = Tournament.objects.get(pk = self.id)
        existing_matches = tournament.matches.all()
        for match in existing_matches:
            match.is_organising_officer_in_the_match(self.organising_officer)

    def _validate_that_the_co_organising_officers_a_part_of_any_matches(self):
        """This method returns a validation error if the organising officer is in any match."""
        tournament = Tournament.objects.get(pk = self.id)
        existing_matches = tournament.matches.all()
        co_organising_officers = tournament.co_organising_officers.all()
        for match in existing_matches:
            match.are_co_organising_officers_a_part_of_the_match(co_organising_officers)

    def save(self, *args, **kwargs):
        tournament = super().save(*args, **kwargs)
        self._validate_participating_players_capacity()
        self._validate_participating_players_must_not_include_organizers()
        self._validate_participating_players_must_not_include_co_organizers()
        self._validate_organizer_type()
        self._validate_co_organiser_type()
        self._validate_that_the_organising_officer_a_part_of_any_matches()
        self._validate_that_the_co_organising_officers_a_part_of_any_matches()
        return tournament


class Round(models.Model):
    id=models.AutoField(primary_key=True)
    players = models.ManyToManyField(User, related_name='Players playing+')
    Tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    winners = models.ManyToManyField(User, related_name='Winners+')
    matches = models.ManyToManyField(Match, related_name='Matches+')
    has_started = models.BooleanField(default=False)
    def createMatches(self):
        player_list_copy=self.create_copy_of_player_list()
        while len(player_list_copy)>=2:
            choice = random.sample(player_list_copy,2)
            self.make_a_match(choice)
            player_list_copy = set(player_list_copy) - set(choice)

    def get_all_matches(self):
        """Returns all matches as a list."""
        matches = []
        round = Round.objects.get(pk = self.id)

        for match in round.matches.all():
            matches.append(match)

        return matches

    def make_a_match(self,choices):
        newMatch = Match.objects.create(player1 = choices[0], player2 = choices[1], date = timezone.now())
        round=Round.objects.get(pk=self.id)
        round.matches.add(newMatch)
        round.Tournament.matches.add(newMatch)

    def create_copy_of_player_list(self):
        round = Round.objects.get(pk=self.id)
        return  set(copy.deepcopy(round.players.all()))

    def go_to_next_round(self,winnerList):
        for winner in winnerList:
            self.nextRound.players.add(winner)
        self.remove_losers_from_tournament_participant_list(winnerList)

    def remove_losers_from_tournament_participant_list(self,winnerList):
        round = Round.objects.get(id = self.id)
        losers = set(round.players.all()) - set(winnerList)
        for loser in losers:
            self.Tournament.participating_players.remove(loser)

    def decideWinners(self):
        round = Round.objects.get(pk=self.id)
        player_to_score_map = self.get_player_score_map()
        for k,v in player_to_score_map.items():
            self.put_winner_in_winner_list(v,k,round)
        self.remove_losers_from_tournament_participant_list(round.winners.all())

    def put_winner_in_winner_list(self, score, player, round):
        if score == scores.win_score and player not in round.winners.all():
            round.winners.add(player)

    def get_player_score_map(self):
        copy_player_list = self.create_copy_of_player_list()
        player_to_score_map={}
        for player in copy_player_list:
            try:
                score_of_player=Score.objects.get(player=player,round=self)
            except:
                pass # This pass signifies that the score for this player has not been added and so we should not add it to the player score map.
            else:
                player_to_score_map[player] = score_of_player.score
        return player_to_score_map

    def has_winners_been_decided(self):
        return self.winners.all().count() == self.players.all().count() / 2

    def is_group(self):
        """Checks if the instance of round is a group."""
        return isinstance(self,Group)

class Group(Round):
    class Meta:
        proxy = True

    def have_all_matches_been_marked(self,group):
        for match in group.matches.all():
            if not match.has_match_been_scored(group):
                return False
        return True

    def decideWinners(self):
        group=Group.objects.get(pk=self.id)
        if self.have_all_matches_been_marked(group):
            score_map=self.get_player_score_map()
            self.put_two_best_players(score_map=score_map,group=group)
            self.remove_losers_from_tournament_participant_list(group.winners.all())


    def put_two_best_players(self,score_map,group):
        score_list = sorted(score_map.values())
        for k,v in score_map.items():
            self.add_winner(score_list,v,k,group)

    def add_winner(self,score_list,score,player,group):
        if score == score_list[len(score_list)-1] or score == score_list[len(score_list)-2]:
            group.winners.add(player)


    def get_player_score_map(self):
        copy_player_list = self.create_copy_of_player_list()
        player_to_score_map={}
        for player in copy_player_list:
            score_of_player=Score.objects.filter(player=player,round=self)
            total_score = self.get_total_score(score_of_player)
            player_to_score_map[player]=total_score
        return player_to_score_map

    def get_total_score(self,score_list):
        total_score=0
        for score in score_list:
            total_score+=score.score
        return total_score


    def createMatches(self):
        copy_player_list = self.create_copy_of_player_list()
        choices=list((itertools.combinations(copy_player_list,2)))
        for choice in choices:
            self.make_a_match(choice)

    def create_copy_of_player_list(self):
        group = Group.objects.get(pk=self.id)
        return  set(copy.deepcopy(group.players.all()))

    def make_a_match(self, choices):
        newMatch = Match.objects.create(player1 = choices[0], player2 = choices[1], date = timezone.now())
        group=Group.objects.get(pk=self.id)
        group.matches.add(newMatch)
        group.Tournament.matches.add(newMatch)

    def remove_losers_from_tournament_participant_list(self,winnerList):
        group = Group.objects.get(id = self.id)
        losers = set(group.players.all()) - set(winnerList)
        for loser in losers:
            self.Tournament.participating_players.remove(loser)

    def has_winners_been_decided(self):
        return self.winners.all().count() == 2

class Score(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Player+')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match+')
    score = models.DecimalField(decimal_places=1,max_digits=2,validators=[validate_scores])
    round = models.ForeignKey(Round, on_delete=models.CASCADE,blank=True,null=True)

    def check_lose_score(self, score1, score2):
        """This method checks if two scores are the same lose score."""
        if score1 == scores.lose_score and score2 == scores.lose_score:
            raise ValidationError("Both cannot lose")
        return False

    def check_win_score(self, score1, score2):
        """This method checks if two scores are the same win score."""
        if score1 == scores.win_score and score2 == scores.win_score:
            raise ValidationError("Both cannot win")
        return False

    objects = scoreModelManager()