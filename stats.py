# module for statistic calculations 

import pandas as pd

url = 'https://docs.google.com/spreadsheets/d/1meumcUensHq5gURLb6WC5cksqkjta9fAtMTdeMuADwc/export?format=csv&gid=1382361133'
df = pd.read_csv(url)

# known_msu ==> stores map / dict for all known players with map-specific underperformance
known_msu = {"border":['pckrnr']}

# constants for the indexing of columns in df, per google sheet
NAME_COL = 0
TOURNAMENT_KD_COL = 4
RANKED_STATS_COL = 5
TOTAL_MAP_RECORD_COL = 1
FRAUD_WATCH_THR = .24

# threshold constants
FRAUD_THRESHOLD = .3

# extract player stats by row
def get_row(name):

    player_row = df[df['Uplay'].str.lower() == name.lower()]
    if not player_row.empty:
        player_stats = player_row.iloc[0].to_dict()
        return player_stats
    else: 
        print('name not found')
        return None
 
# get a player's overall score
def player_score(name):
    
    sum = 0
    row = get_row(name)
    sum += baseScore(name, row) + adjScore(name, row)
    return sum

# determine a player's base score
# @param player's info within the dict
def baseScore(name, row : dict):

    sum = 0
    sum += (1.25 * scaleRank(row.get('Peak Rank / KD'))) + (1.5 * tourney_kd(row.get('Tournament KD'))) + (2 * finals_app(row.get('Finals W/L'))) + (1.75 * winLoss(row.get('Total Map Record')))
    return sum

def winLoss(data : str):
    
    percentage = float(data.split()[-1].rstrip("%"))
    return percentage

def finals_app(data : str):

    total_apps = sum(int(x) for x in data.split("-"))
    return total_apps

def tourney_kd(data : str):

    actual_kd = data.split('(')[-1][:-1]
    kd = float(actual_kd)
    return kd

def scaleRank(info : str):

    info = info.split()
    rank = info[0].lower()
    if rank == 'champion':
        return 5
    elif rank == 'diamond':
        return 4
    elif rank == 'emerald':
        return 3
    elif rank == 'platinum':
        return 2
    else:
        return 1

# to be implemented later.
def adjScore(name : str, row : str):
    sum = 0
    return sum


def fraud_watch():

    fraud_watch_list = {}
    for row in df.itertuples(index=False):
        name = row[NAME_COL]
        t_kd = tourney_kd(row[TOURNAMENT_KD_COL])
        ranked_kd = extract_kd(row[RANKED_STATS_COL])
        diff = ranked_kd - t_kd
        if (t_kd != 0.00 and diff >= FRAUD_WATCH_THR and diff < FRAUD_THRESHOLD):
            diff = round(diff, 2)
            fraud_watch_list[name] = str(diff * -1)
    return fraud_watch_list

def get_carried_players():

    carried = {}
    for row in df.itertuples(index=False):
        name = row[NAME_COL]
        t_kd = tourney_kd(row[TOURNAMENT_KD_COL])
        win_rate = winLoss(row[TOTAL_MAP_RECORD_COL])
        if (t_kd <= .85 and win_rate >= 67):
            win_rate_str = str(int(win_rate)) + '%'
            carried[name] = [t_kd, win_rate_str]
    return carried



def det_frauds():

    frauds = {}
    for row in df.itertuples(index=False):
        name = row[NAME_COL]
        t_kd = tourney_kd(row[TOURNAMENT_KD_COL])
        ranked_kd = extract_kd(row[RANKED_STATS_COL])
        diff = ranked_kd - t_kd
        if (t_kd != 0.00 and diff >= FRAUD_THRESHOLD):
            diff = round(diff, 2)
            frauds[name] = str(diff * -1)
    return frauds

def extract_kd(data : str):

    kd_str = data.split('(')[-1].rstrip(')')
    # Convert the extracted KD ratio to a float
    kd_float = float(kd_str)
    return kd_float

def tourneyKD(data: str):
    
    return float(data)

def get_player_stats(name):

    current = 0