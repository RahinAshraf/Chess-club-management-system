mediumGroupStage = 4
largeGroupStage = 6
max_number_for_round_creation = 16
GroupStageCapacityMap = {(17, 32): mediumGroupStage, (33, 96): largeGroupStage}

def get_group_capacity(number_of_players):
    if number_of_players >= 17 and number_of_players <= 32:
        return mediumGroupStage
    else:
        return largeGroupStage

def is_allowed_for_round_creation(number_of_players):
    if number_of_players <= max_number_for_round_creation:
        return True
    
    return False