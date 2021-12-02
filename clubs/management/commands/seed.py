from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from clubs.models import User
import random

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self._create_base_users()
        user_count = 3
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
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

    def _create_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        chess_experience_level=random.randint(1, 5)
        public_bio = self.faker.text(max_nb_chars=520)
        personal_statement = self.faker.text(max_nb_chars=300)
        User.objects.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            chess_experience_level=chess_experience_level,
            password=Command.PASSWORD,
            public_bio=public_bio,
            personal_statement=personal_statement
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email
