from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class GenerateMatches(TestCase):
    """ Unit tests of generating new matches """
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    def setUp(self):
        self.user = User.objects.get(first_name = 'Russell')
        self.officer = User.objects.get(first_name = 'Valentina')
        self.club = Club.objects.get(pk='Kerbal Chess Club')
        MembershipType.objects.create(user=self.user,club=self.club,type=consts.CLUB_OWNER)
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
        return Tournament.objects.filter(club = self.club)[1]

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

    def test_redirect_url_when_generating_matches_in_tournament_without_club_choice(self):
        self.client.login(email=self.officer.email, password='Password123')
        tournament = Tournament.objects.filter(club = self.club)[0]
        url = reverse("generate_matches", kwargs={"tournament_id":tournament.pk})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
