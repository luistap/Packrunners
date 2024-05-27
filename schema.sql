-- Create Maps Table first
CREATE TABLE IF NOT EXISTS maps (
    map_id SERIAL PRIMARY KEY,
    map_name VARCHAR(255)
);

-- Create Players Table
CREATE TABLE IF NOT EXISTS players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    rank VARCHAR(255),
    ranked_kd DECIMAL
);

-- Now create Matches Table after Maps Table
CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    map_id INTEGER,
    date_played DATE,
    type VARCHAR(255),
    FOREIGN KEY (map_id) REFERENCES maps(map_id)
);

-- Create Player Stats Table
CREATE TABLE IF NOT EXISTS player_stats (
    stats_id SERIAL PRIMARY KEY,
    player_id INTEGER,
    match_id INTEGER,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);
