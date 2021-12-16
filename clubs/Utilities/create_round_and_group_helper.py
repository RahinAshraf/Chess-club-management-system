from ..models import Group, Round, Tournament
from ..Constants import GroupStageCapacity
import math
import random
import copy

def randomly_choose_players_from_a_set(player_set):
    """ Returns a random list a number which coresponds to the players in the
        given set """
    return random.sample(player_set,len(player_set)-1)

def get_copy_of_player_list(player_set):
    """ Returns a deep copy of the given player set """
    return  set(copy.deepcopy(player_set))

############## Section for creation of rounds. ###############
###################################################################

def get_round(tournament):
    """ return the round object given the tournament """
    return Round.objects.create(Tournament = tournament)

###################################################################

############## Section for creation of groups. ###############
###################################################################

def manage_group_creation(number_of_players):
    """ return the number of groups required for the given number of players """
    return get_number_of_groups(GroupStageCapacity.get_group_capacity(number_of_players),number_of_players)

def get_number_of_groups(group_size, number_of_players):
    """ Calculates and return the number of groups according the group size and
        number of players """
    return math.floor(number_of_players / group_size)

def get_Group(tournament):
    """ return the group object given the tournament """
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
    """ Distribute the players into a round  and return the list containing the
        round """
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
    """ Checks the number of players in a round is even or odd, and proceed to other
        methods depending on the case """
    if tournament.participating_players.all().count() % 2 != 0:
       player_list = randomly_choose_players_from_a_set(set(tournament.participating_players.all()))
       return distribute_players_into_a_round(round,player_list)
    else:
        return distribute_players_into_a_round(round,tournament.participating_players.all())

def has_round_started(round):
    """ Return true if the round has started, false otherwise """
    return round.has_started

###################################################################################

############## Section for distributing players into groups. ###############
###################################################################################

def manage_distribute_players_into_groups(number_of_players,tournament):
    """ Distribute the players into groups and return the list containing the
        groups """
    group_list = create_groups(number_of_players=number_of_players,tournament=tournament)
    player_list = get_copy_of_player_list(tournament.participating_players.all())
    put_players_in_groups(player_list, group_list)
    return group_list

def remove_players_from_player_list(player_list,choice):
    """ remove the given choice of players from the given player list """
    player_list = set(player_list) - set(choice)
    return player_list

def get_selection_of_players(player_list,group_size):
    """ randomly selects players from the given player list accodring to the given
        group size and return the selected choices """
    if len(player_list) >= group_size:
        choice = random.sample(player_list,group_size)
        return choice

def put_players_in_groups(player_list, group_list):
    """ place the given player list into the given groups """
    group_size = GroupStageCapacity.get_group_capacity(len(player_list))
    for group in group_list:
        choice_of_players = get_selection_of_players(player_list,group_size)
        player_list = remove_players_from_player_list(player_list,choice_of_players)
        put_players_in_a_group(choice_of_players, group)

def put_players_in_a_group(player_list, group):
    """ add players in the given group """
    for player in player_list:
        group.players.add(player)

###################################################################################

def check_scores_for_round(round):
    for match in round.matches.all():
        if not match.has_match_been_scored(round):
            return False
    return True

def check_winners_for_a_group(group):
    if group.winners.all().count() == 2:
        return True
    return False

def manage_round_and_group_winners(round):
    """ checks wheather the given round is a round or group, and return true if
        there is a winner for all matches """
    if type(round) == Group:
        return check_winners_for_a_group(round)
    return check_scores_for_round(round)

def check_if_all_rounds_and_groups_have_required_winners(tournament):
    """ return ture if all rounds have required winners """
    group_list = Round.objects.filter(Tournament = tournament)
    for group in group_list:
        if not manage_round_and_group_winners(group):
            return False
    return True

def is_match_list_empty(tournament):
    """ return ture if ther is no matches in the given tournament , false otherwise"""
    matches = tournament.get_all_matches()
    if len(matches) == 0:
        return True
    else:
        return False

def can_generate_matches(tournament):
    """ return true if the tournament has no matches or if all rounds/groups have
        required winners """
    if check_if_all_rounds_and_groups_have_required_winners(tournament) or is_match_list_empty(tournament):
        return True
    return False

def create_round_or_groups(tournament):
    """ given the tournament a round or groups will be created according to the
        size of the players participated in the tournament """
    number_of_players = tournament.participating_players.all().count()
    Round.objects.filter(Tournament=tournament).delete()
    Group.objects.filter(Tournament=tournament).delete()
    if GroupStageCapacity.is_allowed_for_round_creation(number_of_players):
        return list(manage_distribute_players_into_rounds(tournament))
    else:
        return manage_distribute_players_into_groups(number_of_players,tournament)

def match_creator_helper(tournament):
    """ the method calls the creates round or groups if the conditions are satisifed
        for generating mathces """
    if can_generate_matches(tournament):
        return create_round_or_groups(tournament)
