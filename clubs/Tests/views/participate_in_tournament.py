from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class ParticipateInTournament(TestCase):
    """ Unit tests of the participate in tournament methods """
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.officer = User.objects.get(first_name = "Valentina")
        self.club = Club.objects.get(pk="Kerbal Chess Club")
        MembershipType.objects.create(user = self.user, club = self.club, type = consts.CLUB_OWNER)
        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)

        self.form_input = {
            'name': 'Tournament1',
            'description': 'Description1',
            'deadline_to_apply': '2035-12-05 23:59',
            'capacity':'12'
        }


    def test_successful_participating_in_tournament(self):
        """" Test case for successful participation of tournament when all conditions are satisifed """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.filter(club = self.club)[1]

        self.client.logout()
        self.client.login(email=self.user.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)

        before_count = tournament.get_number_of_participating_players()
        response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_count = tournament.get_number_of_participating_players()
        self.assertEqual(after_count, before_count+1)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_unsuccessful_participating_in_tournament_due_to_deadline(self):
        """ Test case for unsuccessful participation of tournament when the deadline has passed """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        outdatd_deadline_form_input = {
            'name': 'Tournament2',
            'description': 'Description2',
            'deadline_to_apply': '2015-12-05 23:59',
            'capacity':'12'
        }

        response = self.client.post(create_tournament, outdatd_deadline_form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.get(name = 'Tournament2')

        self.client.logout()
        self.client.login(email=self.user.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)

        before_count = tournament.get_number_of_participating_players()
        response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_count = tournament.get_number_of_participating_players()

        self.assertEqual(after_count, after_count)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_unsuccessful_creation_of_tournament_due_to_capacity(self):
        """ Test case for unsuccessful participation of tournament when reaches the limit of the capacity """
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        capacity_form_input = {
            'name': 'Tournament3',
            'description': 'Description3',
            'deadline_to_apply': '2035-12-05 23:59',
            'capacity':'2'
        }

        response = self.client.post(create_tournament, capacity_form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.get(name = 'Tournament3')

        self.client.logout()
        self.client.login(email=self.user.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
        self.client.post(response_url, follow=True)

        self.client.logout()
        test_user_2 = User.objects.create_user(
            email = 'user2@test.org',
            password = 'Password123',
            first_name = 'First2',
            last_name = 'Last',
            public_bio = 'Bio',
            chess_experience_level = 1,
            personal_statement = 'personal_statement')
        MembershipType.objects.create(user = test_user_2, club = self.club, type = consts.MEMBER)
        self.client.login(email='user2@test.org', password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)

        test_user_3 = User.objects.create_user(
            email = 'user3@test.org',
            password = 'Password123',
            first_name = 'First3',
            last_name = 'Last',
            public_bio = 'Bio',
            chess_experience_level = 1,
            personal_statement = 'personal_statement')
        MembershipType.objects.create(user = test_user_3, club = self.club, type = consts.MEMBER)
        self.client.login(email= 'user2@test.org', password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)

        count = tournament.get_number_of_participating_players()
        self.assertEqual(count, tournament.capacity)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_redirect_url_when_participating_in_tournament_without_club_choice(self):
        self.client.login(email=self.officer.email, password='Password123')
        tournament = Tournament.objects.filter(club = self.club)[0]
        url = reverse("participate_in_tournament", kwargs={"tournament_id":tournament.pk})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)