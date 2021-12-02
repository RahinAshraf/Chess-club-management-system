from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User, Club
import random

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100
    CLUB_COUNT = 10

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self._create_base_users()
        self._create_base_club()
        user_count = 3
        club_count = 4
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except (django.db.utils.IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

        while club_count < Command.CLUB_COUNT:
            print(f'Seeding club {club_count}',  end='\r')
            try:
                self._create_club()
            except (django.db.utils.IntegrityError):
                continue
            club_count += 1
        print('Club seeding complete')

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
        club_owner = self._create_user()
        Club.objects.create(
            club_owner = club_owner,
            name = 'Kerbal Chess Club',
            location = 'London',
            mission_statement = self.faker.text(max_nb_chars=200)
        )

    def _create_user(self):
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
        return user

    def _create_club(self):
        club_owner = self._create_user()
        Club.objects.create(
            club_owner = club_owner,
            name = f'{self.faker.last_name()} Chess Club',
            location = self.faker.city(),
            mission_statement = self.faker.text(max_nb_chars=200)
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email
