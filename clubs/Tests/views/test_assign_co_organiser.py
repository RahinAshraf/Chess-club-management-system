from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class ParticipateInTournament(TestCase):
    """ Unit tests of the assign co-organiser methods """
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

    def test_successful_assign_coorganisr(self):
        """ Test case for successful assignment of co-organiser to a tournament when all conditions are satisifed """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.get(club = self.club)

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
        tournament = Tournament.objects.get(club = self.club)

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

    def test_unsuccessful_assign_coorganisr_from_member(self):
        """ Test case for unsuccessful assignment of co-organiser to a tournament when
        the subject is a member instead of an officer """
        self.client.login(email=self.officer.email, password='Password123')
        self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        create_tournament = reverse('create_tournament')

        response = self.client.post(create_tournament, self.form_input, follow=True)
        response_url = reverse('tournaments')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        tournament = Tournament.objects.get(club = self.club)

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
        tournament = Tournament.objects.get(club = self.club)

        before_count = tournament.get_number_of_co_organisers()
        response_url = reverse("assign_coorganiser", kwargs={"tournament_id":tournament.pk, "user_id":self.user.pk})
        response = self.client.post(response_url, follow=True)
        after_count = tournament.get_number_of_co_organisers()
        self.assertEqual(after_count, before_count)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
