import abc
from copy import copy
from dataclasses import replace
from typing import Callable, Dict, Type

from tqdm import tqdm
from ortools.linear_solver import pywraplp

from biwenger_knapsack.models import Player, Team, TeamConstraints


class BaseSolver(abc.ABC):
    team: Team
    players: Dict[str, Player]

    @abc.abstractmethod
    def solve(self) -> Team: ...


class Solver(BaseSolver):
    def __init__(
        self,
        player_value: Callable[[Player], float],
        player_cost: Callable[[Player], float],
        constraints: TeamConstraints,
        players: Dict[str, Player],
    ):
        self.player_value = player_value
        self.player_cost = player_cost
        self.players = players
        self.constraints = constraints

    def solve(self) -> Team:
        solver = pywraplp.Solver(
            "FantasyKnapsack", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
        )
        take = [solver.IntVar(0, 1, f"take_{p}") for p in self.players]
        value = solver.Sum(
            [
                self.player_value(p) * take[i]
                for i, p in enumerate(self.players.values())
            ]
        )
        solver.Maximize(value)

        salary = solver.Sum(
            [self.player_cost(p) * take[i] for i, p in enumerate(self.players.values())]
        )

        solver.Add(salary <= self.constraints.max_salary)

        # number of players constraints
        min_pt, max_pt = self.constraints.range_pt
        number_of_gk = solver.Sum(
            take[i] for i, p in enumerate(self.players.values()) if p.position == 1
        )
        solver.Add(number_of_gk >= min_pt)
        solver.Add(number_of_gk <= max_pt)

        min_df, max_df = self.constraints.range_df
        number_of_df = solver.Sum(
            take[i] for i, p in enumerate(self.players.values()) if p.position == 2
        )
        solver.Add(number_of_df >= min_df)
        solver.Add(number_of_df <= max_df)

        min_mc, max_mc = self.constraints.range_mc
        number_of_mc = solver.Sum(
            take[i] for i, p in enumerate(self.players.values()) if p.position == 3
        )
        solver.Add(number_of_mc >= min_mc)
        solver.Add(number_of_mc <= max_mc)
        min_dl, max_dl = self.constraints.range_dl

        number_of_dl = solver.Sum(
            take[i] for i, p in enumerate(self.players.values()) if p.position == 4
        )
        solver.Add(number_of_dl >= min_dl)
        solver.Add(number_of_dl <= max_dl)

        number_of_players = solver.Sum(
            take[i] for i, p in enumerate(self.players.values())
        )
        solver.Add(number_of_players == self.constraints.max_n_players)

        # solving
        solver.Solve()
        assert solver.VerifySolution(1e-7, True)

        team = Team(
            player_value=self.player_value,
            player_cost=self.player_cost,
            players=[],
            constraints=self.constraints,
        )
        for i, p in enumerate(self.players.values()):
            if take[i].SolutionValue():
                team.add_player(p)

        team.check_constraints()
        return team


class SolverWithCaptain(BaseSolver):
    def __init__(
        self,
        solver: Type[Solver],
        player_value: Callable[[Player], float],
        player_cost: Callable[[Player], float],
        possible_captains: Dict[str, Player],
        constraints: TeamConstraints,
        players: Dict[str, Player],
    ):
        self.solver = solver
        self.possible_captains = possible_captains
        self.players = players
        self.player_value = player_value
        self.player_cost = player_cost
        self.constraints = constraints

    def solve(self) -> Team:
        # sorted_players = sorted(players.values(), key=lambda x: x.points, reverse=True)
        max_expected_value = 0
        best_team = Team(
            players=[],
            player_cost=self.player_cost,
            player_value=self.player_value,
            constraints=self.constraints,
        )
        for captain_id, captain in tqdm(self.possible_captains.items()):
            captain = replace(captain, is_captain=True)
            players_with_captain = copy(self.players)
            players_with_captain[captain_id] = captain

            solver = self.solver(
                player_cost=self.player_cost,
                player_value=self.player_value,
                constraints=self.constraints,
                players=players_with_captain,
            )
            team = solver.solve()
            expected_value = team.expected_value()
            if expected_value > max_expected_value:
                max_expected_value = expected_value
                best_team = team
        return best_team
