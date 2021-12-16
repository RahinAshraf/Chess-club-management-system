from django.test import TestCase
from clubs.models import Club, User, MembershipType, Tournament
from django.core.exceptions import ValidationError
from django.urls import reverse
from ...Constants import consts
class ShowTournamentTestCase(TestCase):
    """ Unit tests of showing tournaments """
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    def setUp(self):
        self.user = User.objects.get(first_name = "Russell")
        self.officer = User.objects.get(first_name = "Valentina")
        self.club = Club.objects.get(pk="Kerbal Chess Club")
        MembershipType.objects.create(user = self.user, club = self.club, type = consts.CLUB_OWNER)
        self.membership = MembershipType.objects.create(user = self.officer, club = self.club, type = consts.OFFICER)

        self.url = reverse('tournaments')

    def test_tournament_list_url(self):
        """ Test case to check if the redirected url is equivalent to the
        expected url for showing a list of tournaments """
        self.assertEqual(self.url,'/tournaments/')

    def test_tournament_redirect_url_when_club_is_not_chosen(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get('/tournaments/', follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_tournament_list(self):
        """" Test case for successfully displaying the tournament list when requird
             conditions are satisifed """
        self.client.login(email=self.officer.email, password='Password123')
        self._create_test_tournaments(15)
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament_list.html')
        self.assertEqual(len(response.context['tournaments']), 16)
        for tournament_id in range(15-1):
            self.assertContains(response, f'Tournament{tournament_id}')
            self.assertContains(response, f'Description{tournament_id}')

    def _create_test_tournaments(self, tournament_count=10):
        """ Creates given number of tournaments, the default is 10 """
        for tournament_id in range(tournament_count):
            self.Tournament = Tournament(club = self.club, name=f'Tournament{tournament_id}',
                                                    description = f'Description{tournament_id}',
                                                    capacity = '12',
                                                    organising_officer = self.officer,
                                                    deadline_to_apply = '2021-12-05 23:59')
            self.Tournament.save()
