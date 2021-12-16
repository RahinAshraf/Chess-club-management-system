from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
from django.contrib import messages

class WithdrawFromTournament(TestCase):
    """ Unit tests of withdraw from tournament"""
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

    def test_successful_withdraw_from_tournament(self):
        """ Test case for successfull withdraw from the tournament when required
            conditions are satisifed """
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

        before_join = tournament.get_number_of_participating_players()
        response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_join = tournament.get_number_of_participating_players()
        self.assertEqual(after_join, before_join+1)

        before_withdraw = tournament.get_number_of_participating_players()
        response_url = reverse("withdraw_from_tournament", kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_withdraw = tournament.get_number_of_participating_players()
        self.assertEqual(before_withdraw-1, after_withdraw)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_unsuccessful_withdraw_from_tournament_due_to_deadline(self):
        """ Test case for unsuccessfull withdraw from the tournament when the
            deadline is passed"""
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

        before_join = tournament.get_number_of_participating_players()
        response_url = reverse("participate_in_tournament",kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_join = tournament.get_number_of_participating_players()
        self.assertEqual(after_join, before_join+1)

        tournament.deadline_to_apply = '2015-12-05 23:59'
        tournament.save()

        before_withdraw = tournament.get_number_of_participating_players()
        response_url = reverse("withdraw_from_tournament", kwargs={"tournament_id":tournament.pk})
        response = self.client.post(response_url, follow=True)
        after_withdraw = tournament.get_number_of_participating_players()
        self.assertEqual(before_withdraw, after_withdraw)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_redirect_url_when_withdrawing_from_tournament_without_club_choice(self):
        self.client.login(email=self.officer.email, password='Password123')
        tournament = Tournament.objects.filter(club = self.club)[0]
        url = reverse("withdraw_from_tournament", kwargs={"tournament_id":tournament.pk})
        response = self.client.get(url, follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)