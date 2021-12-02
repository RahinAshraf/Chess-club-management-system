from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club, MembershipType
from ...Constants import consts
import random

class UniqueFaker(Faker):
    """
    A Faker that keeps track of returned values so it can ensure uniqueness.
    """
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
    USER_COUNT = 100
    CLUB_COUNT = 10

    def __init__(self):
        super().__init__()
        self.faker = UniqueFaker('en_GB')

    def handle(self, *args, **options):
        self._create_base_users()
        self._create_base_club()
        self._create_base_types()
        user_count = 3
        club_count = 4

        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}',  end='\r')
            try:
                self._create_club()
            except (django.db.utils.IntegrityError):
                continue
            club_count += 1
        print('Club seeding complete')

        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user(True)
            except (django.db.utils.IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

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
            type = consts.MEMBER,
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

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email
