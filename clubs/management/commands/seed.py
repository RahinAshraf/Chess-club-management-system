from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club, MembershipType, Tournament, Match, Round, Score, Group
from ...Constants import consts
import random
from datetime import date, timedelta
from ...Utilities import generate_match_helper, score_player_helper, create_round_and_group_helper

class UniqueFaker(Faker):
    """A Faker that keeps track of returned values so it can ensure uniqueness."""

    def __init__(self, *args, **kwargs):
        super(UniqueFaker, self).__init__(*args, **kwargs)
        self._values = {None}

    def generate(self, extra_kwargs):
        value = None
        while value in self._values:
            value = super(UniqueFaker, self).generate(extra_kwargs)
        self._values.add(value)
        return value

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 75
    CLUB_COUNT = 10

    def __init__(self):
        super().__init__()
        self.faker = UniqueFaker('en_GB')

    def handle(self, *args, **options):
        """ Creates the hard coded users and clubs first, and then the randomized one."""

        self._create_base_users()
        self._create_base_club()
        self._create_base_types()
        user_count = 3
        club_count = 4

        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}',  end='\r')
            self._create_club()
            club_count += 1
        print('Club seeding complete')

        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            self._create_user(True)
            user_count += 1
        print('User seeding complete')

        self._create_base_tournaments()
        self._create_clubs_for_groups()

        for club in Club.objects.all():
            club_count = 0
            print(f'Seeding tournament in club {club_count}',  end='\r')
            if random.randint(1, 3) < 2 :
                self._create_tournament(club)
            club_count += 1
        print('Tournament seeding complete')

        for tournament in Tournament.objects.all():
            self._create_matches(tournament)
            self._generate_scores(tournament)
        print('Match seeding complete')

    def _create_base_users(self):
        User.objects.create_user(
            'jeb@example.org',
            first_name='Jebediah',
            last_name='Kerman',
            chess_experience_level=random.randint(1, 5),
            password=Command.PASSWORD,
            public_bio=self.faker.text(max_nb_chars=520),
            personal_statement=self.faker.text(max_nb_chars=200)
        )

        User.objects.create_user(
            'val@example.org',
            first_name='Valentina',
            last_name='Kerman',
            chess_experience_level=random.randint(1, 5),
            password=Command.PASSWORD,
            public_bio=self.faker.text(max_nb_chars=520),
            personal_statement=self.faker.text(max_nb_chars=200)
        )

        User.objects.create_user(
            'billie@example.org',
            first_name='Billie',
            last_name='Kerman',
            chess_experience_level=random.randint(1, 5),
            password=Command.PASSWORD,
            public_bio=self.faker.text(max_nb_chars=520),
            personal_statement=self.faker.text(max_nb_chars=200)
        )

    def _create_base_club(self):
        Club.objects.create(
            club_owner = self._create_user(False),
            name = 'Kerbal Chess Club',
            location = 'London',
            mission_statement = self.faker.text(max_nb_chars=200)
        )

        Club.objects.create(
            club_owner = self._create_user(False),
            name = 'Jeb Chess Club',
            location = 'London',
            mission_statement = self.faker.text(max_nb_chars=200)
        )

        Club.objects.create(
            club_owner = User.objects.get(email = 'val@example.org'),
            name = 'Val Chess Club',
            location = 'London',
            mission_statement = self.faker.text(max_nb_chars=200)
        )

        Club.objects.create(
            club_owner = self._create_user(False),
            name = 'Bill Chess Club',
            location = 'London',
            mission_statement = self.faker.text(max_nb_chars=200)
        )

    def _create_base_types(self):
        club = Club.objects.get(name = 'Kerbal Chess Club')
        MembershipType.objects.create(
            user = User.objects.get(email = 'jeb@example.org'),
            club = club,
            type = consts.MEMBER
        )
        MembershipType.objects.create(
            user = User.objects.get(email = 'val@example.org'),
            club = club,
            type = consts.OFFICER,
        )

        MembershipType.objects.create(
            user = User.objects.get(email = 'billie@example.org'),
            club = club,
            type = consts.MEMBER
        )

        MembershipType.objects.create(
            user = User.objects.get(email = 'jeb@example.org'),
            club = Club.objects.get(name = 'Jeb Chess Club'),
            type = consts.OFFICER
        )

        MembershipType.objects.create(
            user = User.objects.get(email = 'billie@example.org'),
            club = Club.objects.get(name = 'Bill Chess Club'),
            type = consts.MEMBER
        )

    def _create_base_tournaments(self):
        club = Club.objects.get(name = 'Kerbal Chess Club')
        tournament1 = Tournament.objects.create(
            club = club,
            name = f'{self.faker.last_name()} Chess Tournament',
            description = self.faker.text(max_nb_chars=200),
            capacity = 15,
            organising_officer = User.objects.get(email = 'val@example.org'),
            deadline_to_apply = date.today() + timedelta(days=1)
        )

        tournament2 = Tournament.objects.create(
            club = club,
            name = f'{self.faker.last_name()} Chess Tournament',
            description = self.faker.text(max_nb_chars=200),
            capacity = 12,
            organising_officer = User.objects.get(email = 'val@example.org'),
            deadline_to_apply = date.today() - timedelta(days=1)
        )

        users = club.get_all_users()
        tournament2.participating_players.add(User.objects.get(email = 'jeb@example.org'))
        for i in range (0, random.randint(1, len(users))) :
            tournament2.participating_players.add(random.choice(users))


    def _create_user(self, regular):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        chess_experience_level=random.randint(1, 5)
        public_bio = self.faker.text(max_nb_chars=520)
        personal_statement = self.faker.text(max_nb_chars=300)
        user = User.objects.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            chess_experience_level=chess_experience_level,
            password=Command.PASSWORD,
            public_bio=public_bio,
            personal_statement=personal_statement
        )

        if regular :
            clubs = list(Club.objects.all())
            club = random.choice(clubs)

            if random.randint(1, 10) < 3 :
                type = consts.OFFICER
            else :
                type = consts.MEMBER

            MembershipType.objects.create(
                user = user,
                club = club,
                type = type
            )

        return user

    def _create_club(self):
        club_owner = self._create_user(False)
        Club.objects.create(
            club_owner = club_owner,
            name = f'{self.faker.last_name()} Chess Club',
            location = self.faker.city(),
            mission_statement = self.faker.text(max_nb_chars=200)
        )

    def _create_tournament(self, club):
        officers = [k for k,v in club.get_all_users_with_types().items() if v == consts.OFFICER]
        if officers:
            organizer = random.choice(officers)
            tournament = Tournament.objects.create(
                    club = club,
                    name = f'{self.faker.last_name()} Chess Tournament',
                    description = self.faker.text(max_nb_chars=100),
                    capacity = random.randint(6, 20),
                    organising_officer = organizer,
                    deadline_to_apply = date.today() + timedelta(days=random.randint(1, 10))
            )
            users = club.get_all_users()
            for i in range (0, random.randint(1, len(users))) :
                tournament.participating_players.add(random.choice(users))

    def _create_clubs_for_groups(self):
        """ Creates clubs in which a tournament is organised with a sufficient number of participants
            for groups to be created."""

        self._create_club_for_group(16)
        self._create_club_for_group(32)
        self._create_club_for_group(90)

    def _create_club_for_group(self, nbr_users):
        club_owner = self._create_user(False)
        club = Club.objects.create(
            club_owner = club_owner,
            name = f'{self.faker.last_name()} Chess Club',
            location = self.faker.city(),
            mission_statement = self.faker.text(max_nb_chars=200)
        )

        for i in range(nbr_users):
            user = self._create_user(False)
            if random.randint(1, 10) < 3 :
                type = consts.OFFICER
            else :
                type = consts.MEMBER

            MembershipType.objects.create(
                user = user,
                club = club,
                type = type
            )

        officers = [k for k,v in club.get_all_users_with_types().items() if v == consts.OFFICER]
        organizer = random.choice(officers)
        tournament = Tournament.objects.create(
                club = club,
                name = f'{self.faker.last_name()} Chess Tournament',
                description = self.faker.text(max_nb_chars=100),
                capacity = nbr_users + 10,
                organising_officer = organizer,
                deadline_to_apply = date.today() - timedelta(days=random.randint(1, 10))
        )
        users = club.get_all_users()
        for user in users:
            tournament.participating_players.add(user)
            
    def _create_matches(self, tournament):
        round_or_groups = create_round_and_group_helper.match_creator_helper(tournament)
        self.process_round_or_groups(round_or_groups)
         
    def _generate_scores(self, tournament):
        pass

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def process_round_or_groups(self, round_or_group_list):
        if round_or_group_list is None:
            return False
        else:
           return self.create_matches_in_round_or_groups(round_or_group_list)

    def process_round_or_groups(self, round_or_group_list):
        if round_or_group_list is None:
            return False
        else:
           return self.create_matches_in_round_or_groups(round_or_group_list)

    def create_matches_in_round_or_groups(self, round_or_group_list):
        for round_or_group in round_or_group_list:
            round_or_group.createMatches()
            if round_or_group.matches.all().count() == 0: # This implies that there are no players in the tournament.
                return False
        return True

