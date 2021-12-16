from django.core.management.base import BaseCommand, CommandError
from clubs.models import User, Club, MembershipType, Tournament, Match, Round, Score, Group

class Command(BaseCommand):
        """The database unseeder : delete every object exept the superuser."""

        def handle(self, *args, **options):
            User.objects.filter(is_staff=False, is_superuser=False).delete()
            Club.objects.all().delete()
            MembershipType.objects.all().delete()
            Tournament.objects.all().delete()
            Match.objects.all().delete()
            Round.objects.all().delete()
            Score.objects.all().delete()
            Group.objects.all().delete()
