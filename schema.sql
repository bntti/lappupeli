CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    current_word TEXT,
    previous_word TEXT,
    admin_username TEXT
);
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms ON DELETE CASCADE NOT NULL,
    word TEXT UNIQUE NOT NULL,
    suggester_username TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cards (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms ON DELETE CASCADE NOT NULL,
    word TEXT NOT NULL,
    assigned_to TEXT,
    seen BOOL DEFAULT false
);
CREATE TABLE IF NOT EXISTS ready_players (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms ON DELETE CASCADE NOT NULL,
    username TEXT NOT NULL
);