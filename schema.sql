CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    player_count INT DEFAULT 5 NOT NULL,
    current_word TEXT,
    suggester_username TEXT,
    previous_word TEXT,
    admin_username TEXT
);
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms ON DELETE CASCADE NOT NULL,
    word TEXT UNIQUE NOT NULL,
    suggester_username TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS player_words (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms ON DELETE CASCADE NOT NULL,
    word TEXT NOT NULL,
    assigned_to TEXT
);