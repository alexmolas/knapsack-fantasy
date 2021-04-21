from typing import Sequence

from biwenger_knapsack.models import Player


def parse_players(players) -> Sequence[Player]:
    parsed_players = []
    for player_id, player_info in players.items():
        player = Player(name=player_info['name'],
                        position=player_info['position'],
                        price=player_info['fantasyPrice'],
                        status=player_info['status'],
                        played_away=player_info['playedAway'],
                        played_home=player_info['playedHome'],
                        points=player_info['points'],
                        points_away=player_info['pointsAway'],
                        points_home=player_info['pointsHome'],
                        fitness=player_info['fitness'],
                        player_id=player_id,
                        is_captain=False)
        parsed_players.append(player)
    return parsed_players
