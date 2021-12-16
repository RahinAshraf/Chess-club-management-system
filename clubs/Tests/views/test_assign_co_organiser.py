from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class ParticipateInTournament(TestCase):
    """ Unit tests of the assign co-organiser methods """
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

    def test_successful_assign_coorganisr(self):
        """ Test case for successful assignment of co-organiser to a tournament when all conditions are satisifed """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.filter(club = self.club)[1]

        test_officer = User.objects.create_user(
                    first_name = 'officer',
                    last_name = 'officerlast',
                    email = 'Officer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        MembershipType.objects.create(user = test_officer, club = self.club, type = consts.OFFICER)

        before_count = tournament.get_number_of_co_organisers()
        response_url = reverse("assign_coorganiser", kwargs={"tournament_id":tournament.pk, "user_id":test_officer.pk})
        response = self.client.post(response_url, follow=True)
        after_count = tournament.get_number_of_co_organisers()
        self.assertEqual(after_count, before_count+1)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_successful_assign_coorganisr_after_deadline(self):
        """" Test case for successful assignment of co-organiser to a tournament even after the deadline has passed """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.filter(club = self.club)[1]

        test_officer = User.objects.create_user(
                    first_name = 'officer',
                    last_name = 'officerlast',
                    email = 'Officer@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        MembershipType.objects.create(user = test_officer, club = self.club, type = consts.OFFICER)

        tournament.deadline_to_apply = '2015-12-05 23:59'
        tournament.save()

        before_count = tournament.get_number_of_co_organisers()
        response_url = reverse("assign_coorganiser", kwargs={"tournament_id":tournament.pk, "user_id":test_officer.pk})
        response = self.client.post(response_url, follow=True)
        after_count = tournament.get_number_of_co_organisers()
        self.assertEqual(after_count, before_count+1)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_unsuccessful_assign_coorganisor_from_member(self):
        """ Test case for unsuccessful assignment of co-organiser to a tournament when
        the subject is a member instead of an officer """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.filter(club = self.club)[1]

        test_member = User.objects.create_user(
                    first_name = 'member',
                    last_name = 'memberlast',
                    email = 'member@example.com',
                    password = 'Password123',
                    public_bio = 'Hello!!',
                    chess_experience_level = 3,
                    personal_statement = 'I want to play chess!!')

        MembershipType.objects.create(user = test_member, club = self.club, type = consts.MEMBER)

        before_count = tournament.get_number_of_co_organisers()
        response_url = reverse("assign_coorganiser", kwargs={"tournament_id":tournament.pk, "user_id":test_member.pk})
        response = self.client.post(response_url, follow=True)
        after_count = tournament.get_number_of_co_organisers()
        self.assertEqual(after_count, before_count)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_unsuccessful_assign_coorganisr_from_club_owner(self):
        """ Test case for unsuccessful assignment of co-organiser to a tournament when
         the subject is a club owner instead of an officer """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.filter(club = self.club)[1]

        before_count = tournament.get_number_of_co_organisers()
        response_url = reverse("assign_coorganiser", kwargs={"tournament_id":tournament.pk, "user_id":self.user.pk})
        response = self.client.post(response_url, follow=True)
        after_count = tournament.get_number_of_co_organisers()
        self.assertEqual(after_count, before_count)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_redirect_url_when_assigning_co_organisor_in_tournament_without_club_choice(self):
        self.client.login(email=self.officer.email, password='Password123')
        tournament = Tournament.objects.filter(club = self.club)[0]
        url = reverse("assign_coorganiser", kwargs={"tournament_id":tournament.pk, "user_id":self.user.pk})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
