from django import template
from clubs.models import Tournament

register = template.Library()

def officer(value,id):
    tournament = Tournament.objects.get(id = id)
    participants = tournament.participating_players.all()
 
    for i in participants:
        print(i)
        if i == value:
            return True
      
register.filter(officer)
