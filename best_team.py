import numpy as np
from biwenger_knapsack.api import APIHandler
from biwenger_knapsack.parser import parse_players
from biwenger_knapsack.models import Player, TeamConstraints
from biwenger_knapsack.solver import Solver, SolverWithCaptain


def player_value(player: Player):
    fitness = [value for value in player.fitness if isinstance(value, int)]
    if (
        player.team_id is not None
        and len(fitness) > 1
        and player.status in ("ok", "warned")
    ):
        value = np.min(fitness)
    else:
        value = 0
    if player.is_captain:
        return value * 2
    return value


api = APIHandler()
data = api.get_players_info(
    competition="euro", score=2
)  # 2 colegas, 4 carrousel, 1 roncero
players = parse_players(data)
constraints = TeamConstraints(
    max_salary=300_000_000,  # 300M colegas, 250M carrousel, 400M roncero
    range_pt=(1, 1),
    range_df=(3, 5),
    range_mc=(2, 6),
    range_dl=(0, 4),
    n_cap=1,
    max_n_players=11,
)


solver = Solver(
    players=players,
    player_value=player_value,
    player_cost=lambda x: x.price,
    constraints=constraints,
)
solver = SolverWithCaptain(
    solver=Solver,
    possible_captains=players,
    players=players,
    player_value=player_value,
    player_cost=lambda x: x.price,
    constraints=constraints,
)
best_team = solver.solve()

print(best_team.expected_value())
print(best_team.team_cost())
print()
cost = 0
for gk in best_team.goalkeeper:
    cost += gk.price
    print(gk.name, player_value(gk), gk.is_captain)
print()
for gk in best_team.defenders:
    cost += gk.price
    print(gk.name, player_value(gk), gk.is_captain)
print()
for gk in best_team.midfielders:
    cost += gk.price
    print(gk.name, player_value(gk), gk.is_captain)
print()
for gk in best_team.strikers:
    cost += gk.price
    print(gk.name, player_value(gk), gk.is_captain)

print(cost)
