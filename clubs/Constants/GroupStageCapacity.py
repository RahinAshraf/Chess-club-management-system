mediumGroupStage = 4
largeGroupStage = 6
max_number_for_round_creation = 16
GroupStageCapacityMap = {(17, 32): mediumGroupStage, (33, 96): largeGroupStage}

def is_allowed_for_round_creation(number_of_players):
    if number_of_players <= max_number_for_round_creation:
        return True
    
    return False