from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.Tests.helpers import reverse_with_next

class UserListTest(TestCase):

    fixtures = ['clubs/Tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('user_list')
        self.user = User.objects.get(first_name='John')

    def test_user_list_url(self):
        self.assertEqual(self.url,'/users/')

    def test_get_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        self._create_test_users(15-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
        self.assertEqual(len(response.context['users']), 15)
        for user_id in range(15-1):
            self.assertContains(response, f'First{user_id}')
            self.assertContains(response, f'Last{user_id}')
            self.assertContains(response, f'Bio {user_id}')

    def _create_test_users(self, user_count=10):
        for user_id in range(user_count):
            User.objects.create_user(email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                public_bio=f'Bio {user_id}',
                chess_experience_level='1',
                personal_statement=f'personal_statement{user_id}',
                )
