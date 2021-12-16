from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class GenerateMatches(TestCase):
    """ Unit tests of generating new matches """
    def setUp(self):
        self.user = User.objects.create_user(
                    first_name = 'Test',
                    last_name = 'Case',
                    email = 'testCase@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.club = Club.objects.create(club_owner = self.user,name = "Club1.0", location = 'location1',
                                        mission_statement = 'We want to allow all to play free chess')

        self.officer = User.objects.create_user(
                    first_name = 'JohnDoe',
                    last_name = 'Case',
                    email = 'testCaseOfficer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)

        self.form_input = {
            'name': 'Tournament1',
            'description': 'Description1',
            'deadline_to_apply': '2035-12-05 23:59',
            'capacity':'12'
        }

    def test_successful_generate_matches(self):
        """" Test case for successful creation of a matches when all
         conditions are satisifed """
        tournament = self._create_tournament()
        users = self._get_test_users()

        before_join = tournament.get_number_of_participating_players()

        for user in users:
            self.client.logout()
            self.client.login(email= user.email, password='Password123')
            self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
            response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
            response = self.client.post(response_url, follow=True)

            messages_list = list(response.context["messages"])
            self.assertEqual(len(messages_list), 1)
            self.assertEqual(messages_list[0].level, messages.SUCCESS)

        after_join = tournament.get_number_of_participating_players()
        self.assertEqual(after_join, before_join+10)

        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)

        before_generate = len(tournament.get_all_matches())
        response_url = reverse("generate_matches", kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_generate = len(tournament.get_all_matches())
        self.assertEqual(after_generate, before_generate+5)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_unsuccessful_generate_matches_due_to_zero_players(self):
        """" Test case for unsuccessful creation of a matches when there are
         0 players participated in the tournament """
        tournament = self._create_tournament()

        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)

        before_generate = len(tournament.get_all_matches())
        response_url = reverse("generate_matches", kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_generate = len(tournament.get_all_matches())
        self.assertEqual(after_generate, before_generate)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def _create_tournament(self):
        """ The method helps to create a tournament """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        return Tournament.objects.get(club = self.club)

    def _get_test_users(self, user_count=10):
        """ Create test users, the default number of testing users is 10 """
        users = []
        for user_id in range(user_count):
            user = User.objects.create_user(email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                public_bio=f'Bio {user_id}',
                chess_experience_level='1',
                personal_statement=f'personal_statement{user_id}',
                )
            MembershipType.objects.create(user = user, club = self.club, type = consts.MEMBER)
            users.append(user)
        return users
