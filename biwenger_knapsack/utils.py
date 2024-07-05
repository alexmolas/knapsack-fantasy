from biwenger_knapsack.models import Team


def player_info(player, player_value, player_cost):
    return f"{player.name}, Cost: {player_cost(player)}, Value: {player_value(player)}"


def team_information(team: Team):
    print("Goalkeeper: ")
    for g in team.goalkeeper:
        print(
            "    ",
            player_info(
                g, player_value=team.player_value, player_cost=team.player_cost
            ),
        )

    print("Defenders: ")
    for d in team.defenders:
        print(
            "    ",
            player_info(
                d, player_value=team.player_value, player_cost=team.player_cost
            ),
        )

    print("Midfielders: ")
    for m in team.midfielders:
        print(
            "    ",
            player_info(
                m, player_value=team.player_value, player_cost=team.player_cost
            ),
        )

    print("Strikers: ")
    for s in team.strikers:
        print(
            "    ",
            player_info(
                s, player_value=team.player_value, player_cost=team.player_cost
            ),
        )

    print("Captain: ")
    for p in team.players:
        if p.is_captain:
            print(p.name)

    print()
    print(
        f"Expected Value: {team.expected_value()}, " f"Total Cost: {team.team_cost()}"
    )
