-- SQL script to set up the database schema for player statistics

-- Create Players table
CREATE TABLE IF NOT EXISTS Players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- Create Maps table
CREATE TABLE IF NOT EXISTS Maps (
    map_id SERIAL PRIMARY KEY,
    map_name VARCHAR(255) UNIQUE NOT NULL
);

-- Create Match_Types table
CREATE TABLE IF NOT EXISTS Match_Types (
    match_type_id SERIAL PRIMARY KEY,
    description VARCHAR(255) UNIQUE NOT NULL
);

-- Modify the Matches table to include a score column
CREATE TABLE IF NOT EXISTS Matches (
    match_id SERIAL PRIMARY KEY,
    map_id INT NOT NULL,
    match_type_id INT NOT NULL,
    score VARCHAR(10),  -- assuming the score format "X-Y"
    date TIMESTAMP NOT NULL,
    FOREIGN KEY (map_id) REFERENCES Maps(map_id),
    FOREIGN KEY (match_type_id) REFERENCES Match_Types(match_type_id)
);


-- Create Player_Stats table
CREATE TABLE IF NOT EXISTS Player_Stats (
    stat_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL,
    match_id INT NOT NULL,
    kills INT NOT NULL,
    deaths INT NOT NULL,
    assists INT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);

CREATE TABLE IF NOT EXISTS Player_Aggregate_Stats (
    agg_stat_id SERIAL PRIMARY KEY,
    player_id INT NOT NULL,
    map_id INT,
    match_type_id INT,
    total_kills INT DEFAULT 0,
    total_deaths INT DEFAULT 0,
    total_assists INT DEFAULT 0,
    matches_played INT DEFAULT 0,
    matches_won INT DEFAULT 0,
    matches_lost INT DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (map_id) REFERENCES Maps(map_id),
    FOREIGN KEY (match_type_id) REFERENCES Match_Types(match_type_id),
    UNIQUE (player_id, map_id, match_type_id)  -- Adding a composite unique constraint
);


-- Create H2H_Records table
CREATE TABLE IF NOT EXISTS H2H_Records (
    h2h_id SERIAL PRIMARY KEY,
    player_one_id INT NOT NULL,
    player_two_id INT NOT NULL,
    player_one_wins INT DEFAULT 0,
    player_two_wins INT DEFAULT 0,
    FOREIGN KEY (player_one_id) REFERENCES Players(player_id),
    FOREIGN KEY (player_two_id) REFERENCES Players(player_id),
    UNIQUE (player_one_id, player_two_id)
);

ALTER TABLE Players
ADD COLUMN profile_pic_url VARCHAR(255);
