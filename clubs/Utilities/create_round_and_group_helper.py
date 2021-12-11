from ..models import Group, Round, Tournament
from ..Constants import GroupStageCapacity
import math
import random
import copy
def randomly_choose_players_from_a_set(player_set):
    return random.sample(player_set,len(player_set)-1)

def get_copy_of_player_list(player_set):
    return  set(copy.deepcopy(player_set))

############## Section for creation of rounds. ###############
###################################################################

def get_round(tournament):
    return Round.objects.create(Tournament = tournament)

###################################################################

############## Section for creation of groups. ###############
###################################################################

def manage_group_creation(number_of_players):
    return get_number_of_groups(GroupStageCapacity.get_group_capacity(number_of_players),number_of_players)

def get_number_of_groups(group_size, number_of_players):
    return math.floor(number_of_players / group_size)

def get_Group(tournament):
    return Group.objects.create(Tournament = tournament)

def create_groups(number_of_players, tournament):
    """This method creates a bunch of rounds based on number of players. This method should be called
    only if the number of players is fit for round creation."""
    number_of_rounds = manage_group_creation(number_of_players=number_of_players)
    groupList = []
    for i in range(1,number_of_rounds + 1):
        newGroup = get_Group(tournament)
        groupList.append(newGroup)
    return groupList

###################################################################

############## Section for distributing players into rounds. ###############
###################################################################################

def manage_distribute_players_into_rounds(tournament):
    round = get_round(tournament)
    player_filled_round = odd_even_capacity_manager(tournament,round)
    player_filled_round_list = []
    player_filled_round_list.append(player_filled_round)
    return player_filled_round_list

def distribute_players_into_a_round(round,player_list):
    """Adds players to the round and returns the round."""
    for player in player_list:
        round.players.add(player)
    round.has_started = True
    return round

def odd_even_capacity_manager(tournament,round):
    if tournament.participating_players.all().count() % 2 != 0:
       player_list = randomly_choose_players_from_a_set(set(tournament.participating_players.all()))
       return distribute_players_into_a_round(round,player_list)
    else:
        return distribute_players_into_a_round(round,tournament.participating_players.all())

def has_round_started(round):
    return round.has_started

###################################################################################

############## Section for distributing players into groups. ###############
###################################################################################

def manage_distribute_players_into_groups(number_of_players,tournament):
    group_list = create_groups(number_of_players=number_of_players,tournament=tournament)
    player_list = get_copy_of_player_list(tournament.participating_players.all())
    put_players_in_groups(player_list, group_list)
    return group_list

def remove_players_from_player_list(player_list,choice):
    player_list = set(player_list) - set(choice)
    return player_list

def get_selection_of_players(player_list,group_size):
    if len(player_list) >= group_size:
        choice = random.sample(player_list,group_size)
        return choice

def put_players_in_groups(player_list, group_list):
    group_size = GroupStageCapacity.get_group_capacity(len(player_list))
    for group in group_list:
        choice_of_players = get_selection_of_players(player_list,group_size)
        player_list = remove_players_from_player_list(player_list,choice_of_players)
        put_players_in_a_group(choice_of_players, group)

def put_players_in_a_group(player_list, group):
    for player in player_list:
        group.players.add(player)

###################################################################################

def check_winners_for_a_round(round):
    if round.winners.all().count() == round.players.all().count() / 2:
        return True
    return False

def check_winners_for_a_group(group):
    if group.winners.all().count()==2:
        return True
    return False

def manage_round_and_group_winners(round):
    if isinstance(round,Group):
        return check_winners_for_a_group(round)
    return check_winners_for_a_round(round)

def check_if_all_rounds_and_groups_have_required_winners(tournament):
    group_list = Round.objects.filter(Tournament = tournament)
    for group in group_list:
        if not manage_round_and_group_winners(group):
            return False
    return True

def is_match_list_empty(tournament):
    matches = tournament.get_all_matches()
    if len(matches) == 0:
        return True
    else:
        return False

def can_generate_matches(tournament):
    if check_if_all_rounds_and_groups_have_required_winners(tournament) or is_match_list_empty(tournament):
        return True
    return False

def create_round_or_groups(tournament):
    number_of_players = tournament.participating_players.all().count()
    if GroupStageCapacity.is_allowed_for_round_creation(number_of_players):
        return list(manage_distribute_players_into_rounds(tournament))
    else:
        return manage_distribute_players_into_groups(number_of_players,tournament)

def match_creator_helper(tournament):
    if can_generate_matches(tournament):
        return create_round_or_groups(tournament)
