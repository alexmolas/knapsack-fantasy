import abc
from copy import copy
from dataclasses import replace
from typing import Dict, Type

from ortools.linear_solver import pywraplp

from biwenger_knapsack.models import Player, Team


class BaseSolver(abc.ABC):
    team: Team
    players: Dict[str, Player]

    @abc.abstractmethod
    def solve(self) -> Team:
        ...


class Solver(BaseSolver):

    def __init__(self, team: Team, players: Dict[str, Player]):
        self.team = copy(team)
        self.players = players

    def solve(self) -> Team:
        solver = pywraplp.Solver('CoinsGridCLP', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        take = [solver.IntVar(0, 1, f'take_{p}') for p in self.players]
        captain = [solver.IntVar(0, 1, f'captain_{p}') for p in self.players]
        value = solver.Sum([self.team.player_value(p) * take[i] for i, p in enumerate(self.players.values())])
        # value += solver.Sum([self.team.player_value(p) * captain[i] * take[i] for i, p in enumerate(players)])
        salary = solver.Sum([self.team.player_cost(p) * take[i] for i, p in enumerate(self.players.values())])

        solver.Add(salary <= self.team.constraints.max_salary)

        # number of players constraints
        min_pt, max_pt = self.team.constraints.range_pt
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 1) >= min_pt)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 1) <= max_pt)

        min_df, max_df = self.team.constraints.range_df
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 2) >= min_df)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 2) <= max_df)

        min_mc, max_mc = self.team.constraints.range_mc
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 3) >= min_mc)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 3) <= max_mc)

        min_dl, max_dl = self.team.constraints.range_dl
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 4) >= min_dl)
        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()) if p.position == 4) <= max_dl)

        solver.Add(solver.Sum(take[i] for i, p in enumerate(self.players.values()))
                   <= self.team.constraints.max_n_players)

        # solving

        solver.Maximize(value)
        solver.Solve()
        assert solver.VerifySolution(1e-7, True)

        for i, p in enumerate(self.players.values()):
            if take[i].SolutionValue():
                self.team.add_player(p)

        self.team.check_constraints()
        return self.team


class SolverWithCaptain(BaseSolver):
    def __init__(self,
                 solver: Type[Solver],
                 possible_captains: Dict[str, Player],
                 players: Dict[str, Player],
                 team: Team):
        self.solver = solver
        self.possible_captains = possible_captains
        self.players = players
        self.team = copy(team)

    def solve(self) -> Team:
        # sorted_players = sorted(players.values(), key=lambda x: x.points, reverse=True)
        max_expected_value = 0
        best_team = Team(players=[], player_cost=self.team.player_cost, player_value=self.team.player_value,
                         constraints=self.team.constraints)
        for captain_id, captain in self.possible_captains.items():
            captain = replace(captain, is_captain=True)
            players_with_captain = copy(self.players)
            players_with_captain[captain_id] = captain

            solver = self.solver(team=self.team, players=players_with_captain)
            team = solver.solve()
            expected_value = team.expected_value()
            if expected_value > max_expected_value:
                max_expected_value = expected_value
                best_team = team
        return best_team
