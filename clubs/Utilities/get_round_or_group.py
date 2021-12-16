from ..models import Round,Group

def get_rounds_and_groups(tournament):
        group_round_list = []
        groups = Group.objects.filter(Tournament = tournament)
        for group in groups:
            group_round_list.append(group)
        rounds = Round.objects.filter(Tournament=tournament)
        for round in rounds:
            if round not in group_round_list:
                group_round_list.append(round)
        return group_round_list