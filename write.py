from datetime import datetime
import asyncpg

async def write_match_data(conn, team1_dict, team2_dict, gen_info):
    # Unpack general information
    map_name, match_type, final_score = gen_info
    map_id = await get_or_create_map_id(conn, map_name)
    type_id = await get_or_create_match_type_id(conn, match_type)
    score_team1, score_team2 = map(int, final_score.split('-'))
    date_played = datetime.now().date()  # Use current date for the match

    # Insert teams
    team1_id = await insert_team(conn, "Team 1")
    team2_id = await insert_team(conn, "Team 2")

    # Insert match including scores
    match_id = await insert_match(conn, map_id, type_id, date_played, team1_id, team2_id, score_team1, score_team2)

    # Insert team matches for both teams and retrieve team_match_id
    team1_match_id = await insert_team_match(conn, match_id, team1_id, score_team1 > score_team2)
    team2_match_id = await insert_team_match(conn, match_id, team2_id, score_team2 > score_team1)

    # Insert player stats for each team
    await insert_player_stats(conn, team1_match_id, team1_dict)
    await insert_player_stats(conn, team2_match_id, team2_dict)

async def get_or_create_map_id(conn, map_name):
    map_id = await conn.fetchval("SELECT map_id FROM maps WHERE map_name = $1", map_name.lower())
    if map_id is None:
        map_id = await conn.fetchval("INSERT INTO maps (map_name) VALUES ($1) RETURNING map_id", map_name.lower())
    return map_id

async def get_or_create_match_type_id(conn, match_type):
    type_id = await conn.fetchval("SELECT type_id FROM match_types WHERE description = $1", match_type.lower())
    if type_id is None:
        type_id = await conn.fetchval("INSERT INTO match_types (description) VALUES ($1) RETURNING type_id", match_type.lower())
    return type_id

async def insert_match(conn, map_id, type_id, date_played, team1_id, team2_id, score_team1, score_team2):
    try:
        # Insert the match and directly return the match_id
        return await conn.fetchval("""
            INSERT INTO matches (map_id, type_id, date_played, team1_id, team2_id, score_team1, score_team2)
            VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING match_id
        """, map_id, type_id, date_played, team1_id, team2_id, score_team1, score_team2)
    except asyncpg.exceptions.UniqueViolationError as e:
        # Log the error or handle it as necessary
        print("Failed to insert match due to unique constraint:", e)
        # Optionally, handle the situation (e.g., fetch an existing match_id or resolve conflict)
        return None

async def insert_player_stats(conn, team_match_id, player_stats):
    for player_name, stats in player_stats.items():
        player_id = await ensure_player_exists(conn, player_name)
        kills, deaths, assists = stats
        await conn.execute("""
            INSERT INTO player_stats (player_id, team_match_id, kills, deaths, assists)
            VALUES ($1, $2, $3, $4, $5)
        """, player_id, team_match_id, kills, deaths, assists)
    

async def insert_team_match(conn, match_id, team_id, is_winner):
    return await conn.fetchval("""
        INSERT INTO team_matches (match_id, team_id, is_winner)
        VALUES ($1, $2, $3)
        RETURNING team_match_id
    """, match_id, team_id, is_winner)

async def ensure_player_exists(conn, player_name):
    return await conn.fetchval("""
        INSERT INTO players (name) VALUES ($1)
        ON CONFLICT (name) DO NOTHING
        RETURNING player_id
    """, player_name)

async def insert_team(conn, team_name):
    try:
        # Attempt to insert the new team and directly return the team_id
        team_id = await conn.fetchval("""
            INSERT INTO teams (team_name) VALUES ($1)
            RETURNING team_id
        """, team_name)
        return team_id
    except asyncpg.exceptions.UniqueViolationError:
        # If there is a unique constraint violation, fetch the existing team_id
        return await conn.fetchval("""
            SELECT team_id FROM teams WHERE team_name = $1
        """, team_name)