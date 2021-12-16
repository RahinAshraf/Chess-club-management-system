from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ...Constants import consts
from ...models import User,MembershipType,Club

class transferOwnershipViewTestCase(TestCase):
    """ Unit tests of transfer club owner's ownership """
    fixtures = ['clubs/Tests/fixtures/default_user.json','clubs/Tests/fixtures/default_set_up_of_clubs_and_tournament_with_owners_and_officers.json']
    def setUp(self):
        self.club_owner = User.objects.get(first_name = "Russell")
        self.officer = User.objects.get(first_name = 'Valentina')
        self.club = Club.objects.get(pk = 'Kerbal Chess Club')

        MembershipType.objects.create(user=self.club_owner, type=consts.CLUB_OWNER,club=self.club)
        MembershipType.objects.create(user=self.officer,type=consts.OFFICER, club=self.club)

        self.client.login(email=self.club_owner.email, password='Password123')

        self.url = reverse("transfer_ownership",kwargs={"user_id":self.officer.pk})

    def test_transfer_ownership_url(self):
        """ Test case to check if the redirected url is equivalent to the
            expected url for transfering the ownership """
        self.assertEqual(self.url, "/transfer_ownership/" + str(self.officer.pk) + "/")

    def test_transfer_ownership_successful(self):
        """ Test case for successfull transfer of ownership when all conditions
            in a valid state """
        officerType = MembershipType.objects.filter(user = self.officer)[0].type
        self.assertEqual(officerType, consts.OFFICER)

        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url, follow=True)

        officerType = MembershipType.objects.filter(user = self.officer)[0].type
        self.assertEqual(officerType, consts.CLUB_OWNER)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_transfer_nonexisting_user(self):
        """ Test case for unsuccessfull transfer of ownership when the request user
            attempts to transfer the ownership to a non-existing user """
        userLength = len(User.objects.all())
        self.url = reverse("transfer_ownership",kwargs={"user_id": userLength+1})

        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url, follow=True)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_cannot_transfer_ownership_to_member(self):
        """ Test case for unsuccessfull transfer of ownership when the request user
            attempts to transfer the ownership to a member instead of an officer """
        officerMembership = MembershipType.objects.get(user = self.officer)
        officerMembership.type = "member"
        officerMembership.save()

        officerType = MembershipType.objects.get(user = self.officer).type
        self.assertEqual(officerType, consts.MEMBER)

        response = self.client.get('/switch_club/', {'club_choice' : self.club.name}, follow = True)
        response = self.client.get(self.url, follow=True)

        officerType = MembershipType.objects.get(user = self.officer, club = self.club).type
        self.assertEqual(officerType, consts.MEMBER)

        response_url = reverse("user_list")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

        messages_list = list(response.context["messages"])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_redirect_url_when_transfering_ownership_without_club_choice(self):
        self.client.login(email=self.officer.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('user_profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)