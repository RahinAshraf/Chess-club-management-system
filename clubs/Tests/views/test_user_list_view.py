from django.test import TestCase
from django.urls import reverse
from ...Constants import consts
from clubs.models import User,MembershipType,Club
from clubs.Tests.helpers import reverse_with_next

class UserListTest(TestCase):

    fixtures = ['clubs/Tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('user_list')
        self.user = User.objects.get(first_name='John')
        self.club = Club.objects.create(club_owner=self.user,name = "Club1", location = 'location1', 
                                        mission_statement = 'We want to allow all to play free chess')

    def test_user_list_url(self):
        self.assertEqual(self.url,'/users/')

    def test_get_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_users(15-1)
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), 15)
        for user_id in range(15-1):
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            self.assertContains(response, f'Bio {user_id}')

    def test_get_type_for_member(self):
        user2 = User.objects.create_user(
            email="member@example.org",
            password="Pass123",
            first_name="memberFirst",
            last_name="memberLast",
            public_bio="member",
            chess_experience_level=1,
            personal_statement="memberPersonal",
        )
        MembershipType.objects.create(user=user2,type="member", club=self.club)

        self.client.login(email=user2.email, password='Pass123')
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(response.context['type'], "member")

    def test_get_type_for_officer(self):
        user2 = User.objects.create_user(
            email="officer@example.org",
            password="Pass123",
            first_name="officerFirst",
            last_name="officerLast",
            public_bio="officer",
            chess_experience_level=1,
            personal_statement="officerPersonal",
        )
        MembershipType.objects.create(user=user2,type="officer", club=self.club)

        self.client.login(email=user2.email, password='Pass123')
        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(response.context['type'], "officer")

    def _create_test_users(self, user_count=10):
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
        
