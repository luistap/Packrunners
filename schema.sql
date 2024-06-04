
-- Create Teams Table
CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY,
    team_name VARCHAR(255)
);

-- Create Players Table
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    rank VARCHAR(255),
    ranked_kd DECIMAL
);

-- Create Matches Table
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    map_id INTEGER REFERENCES maps(map_id),
    date_played DATE,
    type_id INTEGER REFERENCES match_types(type_id),
    team1_id INTEGER REFERENCES teams(team_id),
    team2_id INTEGER REFERENCES teams(team_id),
    score_team1 INTEGER,
    score_team2 INTEGER
);

-- Create Team Matches Table
CREATE TABLE IF NOT EXISTS team_matches (
    team_match_id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES matches(match_id),
    team_id INTEGER REFERENCES teams(team_id),
    is_winner BOOLEAN
);

-- Create Player Stats Table
CREATE TABLE IF NOT EXISTS player_stats (
    stats_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    team_match_id INTEGER REFERENCES team_matches(team_match_id),
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER
);

-- Indexes for faster query performance
CREATE INDEX IF NOT EXISTS idx_player_id ON player_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_match_id ON player_stats(team_match_id);
CREATE INDEX IF NOT EXISTS idx_team_id ON team_matches(team_id);
CREATE INDEX IF NOT EXISTS idx_map_id ON matches(map_id);

