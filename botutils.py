# helper functions for bot operations

import matplotlib.pyplot as plt
from imageio import imread

STAT_TYPE_ORDER = ["Kills", "Deaths", "Assists"]

def format_player_stats(team_info):
    formatted_message = ""
    for player, stats in team_info.items():
        formatted_message += f"{player}: Kills - {stats[0]}, Deaths - {stats[1]}, Assists - {stats[2]}\n"
    return formatted_message

def get_image(url):
    try:
        image = imread(url)
        return image
    except Exception as e:
        print(f"Failed to fetch or decode image from {url}: {e}")
        return None
