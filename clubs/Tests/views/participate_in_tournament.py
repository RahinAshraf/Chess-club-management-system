from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class ParticipateInTournament(TestCase):

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


    def test_successful_participating_in_tournament(self):
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.get(club = self.club)

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
