# helper functions for bot operations

def format_player_stats(team_info):
    formatted_message = ""
    for player, stats in team_info.items():
        formatted_message += f"{player}: Kills - {stats[0]}, Deaths - {stats[1]}, Assists - {stats[2]}\n"
    return formatted_message


