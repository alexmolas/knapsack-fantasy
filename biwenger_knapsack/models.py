import abc
from dataclasses import dataclass, replace
from typing import Tuple, Callable, Sequence, List, NewType

Value = NewType("Value", float)
Cost = NewType("Cost", float)


@dataclass(frozen=True)
class Player:
    player_id: int
    name: str
    position: int
    price: int
    status: str
    played_home: int
    played_away: int
    fitness: Tuple[int]
    points: int
    points_home: int
    points_away: int
    is_captain: bool


@dataclass(frozen=True)
class TeamConstraints:
    max_salary: int
    range_pt: Tuple[int, int] = (0, 11)
    range_df: Tuple[int, int] = (0, 11)
    range_mc: Tuple[int, int] = (0, 11)
    range_dl: Tuple[int, int] = (0, 11)
    n_cap: int = 1
    max_n_players: int = 11


class Team:
    def __init__(self,
                 constraints: TeamConstraints,
                 players: List[Player],
                 player_value: Callable[[Player], Value],
                 player_cost: Callable[[Player], Cost]):
        self.constraints = constraints
        self.constraints_fns = self.constraints_to_funcs()
        self.players = players
        self.player_value = player_value
        self.player_cost = player_cost

    @property
    def goalkeeper(self) -> Sequence[Player]:
        return [p for p in self.players if p.position == 1]

    @property
    def defenders(self) -> Sequence[Player]:
        return [p for p in self.players if p.position == 2]

    @property
    def midfielders(self) -> Sequence[Player]:
        return [p for p in self.players if p.position == 3]

    @property
    def strikers(self) -> Sequence[Player]:
        return [p for p in self.players if p.position == 4]

    def expected_value(self, player_value: Callable[[Player], Value], ):
        value = 0
        for p in self.players:
            if p.is_captain:
                value += 2 * player_value(p)
            else:
                value += player_value(p)
        return value

    def team_cost(self, player_cost: Callable[[Player], Cost]):
        return sum(player_cost(p) for p in self.players)

    def add_player(self, player: Player, is_captain: bool):
        if is_captain:
            player = replace(player, is_captain=True)
        new_players = self.players + [player]
        self.players = new_players

    def check_constraints(self):
        constraints_results = [c(self.players) for c in self.constraints_fns]
        if not all(constraints_results):
            # todo: add more info about the failed constraint(s)
            raise ValueError("Some constraint is not satisfied!")

    def constraints_to_funcs(self):
        constraints_fns = []
        for r, position in {'range_pt': 1, 'range_df': 2, 'range_mc': 3, 'range_dl': 4}.items():
            constraint = getattr(self.constraints, r)

            def _constraint_fn(ps: Sequence[Player]):
                h = len([p for p in ps if p.position == position]) >= constraint[0]
                l = len([p for p in ps if p.position == position]) <= constraint[1]
                return h & l

            constraints_fns.append(_constraint_fn)

        def _max_n_players(ps: Sequence[Player]):
            return len(ps) <= self.constraints.max_n_players

        constraints_fns.append(_max_n_players)

        def _max_salary(ps: Sequence[Player]):
            return sum(self.player_cost(p) for p in ps) <= self.constraints.max_salary

        constraints_fns.append(_max_salary)

        return constraints_fns
