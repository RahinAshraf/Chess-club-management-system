from ..models import Group, Round, Tournament
from ..Constants import GroupStageCapacity
from ..Utilities import LinkedList
import math


############## Section for creation of rounds. ###############
###################################################################
def manage_round_creation(number_of_players, tournament_id):
   tournament = Tournament.objects.get(pk=tournament_id)
   if GroupStageCapacity.is_allowed_for_round_creation(number_of_players=number_of_players):
       create_rounds(number_of_players,tournament)


def get_number_of_rounds(number_of_players):
    return math.ceil(math.log(number_of_players, 2))

def get_round(tournament):
    return Round.objects.create(Tournament = tournament)

def create_rounds(number_of_players, tournament):
    """This method creates a bunch of rounds based on number of players. This method should be called
    only if the number of players is fit for round creation."""
    number_of_rounds = get_number_of_rounds(number_of_players=number_of_players)
    roundList = LinkedList()
    for i in range(1,number_of_rounds + 1):
        newRound = get_round(tournament)
        roundList.add(newRound)
    return roundList

###################################################################

############## Section for creation of groups. ###############
###################################################################

def manage_group_creation(number_of_players, tournament_id):
    group_size = GroupStageCapacity.GroupStageCapacityMap(number_of_players)

def get_number_of_groups(group_size, number_of_players):
    return math.floor(number_of_players / group_size)

def get_Group(tournament):
    return Group.objects.create(Tournament = tournament)

def create_rounds(number_of_players, tournament):
    """This method creates a bunch of rounds based on number of players. This method should be called
    only if the number of players is fit for round creation."""
    number_of_rounds = get_number_of_groups(number_of_players=number_of_players)
    groupList = LinkedList()
    for i in range(1,number_of_rounds + 1):
        newGroup = get_Group(tournament)
        groupList.add(newGroup)
    return groupList

###################################################################