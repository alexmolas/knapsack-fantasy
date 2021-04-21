from copy import copy
from typing import Callable, Sequence

from ortools.linear_solver import pywraplp

from biwenger_knapsack.models import Player, Team, Value, Cost


class Solver:

    def __init__(self, team: Team):
        self.team = copy(team)

    def solve(self, players: Sequence[Player]) -> Team:
        solver = pywraplp.Solver('CoinsGridCLP', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        take = [solver.IntVar(0, 1, f'take_{p.player_id}') for p in players]
        captain = [solver.IntVar(0, 1, f'captain_{p.player_id}') for p in players]
        value = solver.Sum([self.team.player_value(p) * take[i] for i, p in enumerate(players)])
        value += solver.Sum([self.team.player_value(p) * captain[i] for i, p in enumerate(players)])
        salary = solver.Sum([self.team.player_cost(p) * take[i] for i, p in enumerate(players)])

        solver.Add(salary <= self.team.constraints.max_salary)

        solver.Add(solver.Sum(captain[i] for i, p in enumerate(players)) == self.team.constraints.n_cap)

        # number of players constraints
        min_pt, max_pt = self.team.constraints.range_pt
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 1) >= min_pt)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 1) <= max_pt)

        min_df, max_df = self.team.constraints.range_df
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 2) >= min_df)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 2) <= max_df)

        min_mc, max_mc = self.team.constraints.range_mc
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 3) >= min_mc)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 3) <= max_mc)

        min_dl, max_dl = self.team.constraints.range_dl
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 4) >= min_dl)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(players) if p.position == 4) <= max_dl)

        solver.Add(solver.Sum(take[i] for i, p in enumerate(players)) <= self.team.constraints.max_n_players)

        # solving

        solver.Maximize(value)
        solver.Solve()
        assert solver.VerifySolution(1e-7, True)

        for i, p in enumerate(players):
            is_captain = False
            if take[i].SolutionValue():
                if captain[i].SolutionValue():
                    is_captain = True
                salary += p.price
                self.team.add_player(p, is_captain=is_captain)

        self.team.check_constraints()
        return self.team
