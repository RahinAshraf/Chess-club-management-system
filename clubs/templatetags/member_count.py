from django import template
from clubs.models import *
register = template.Library()


@register.filter
def member_count(value):
    qs = MembershipType.objects.filter(club = value)
    return len(qs)