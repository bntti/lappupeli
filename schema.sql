CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    players INT DEFAULT 5 NOT NULL,
    current_word TEXT,
    suggester_uuid UUID,
    previous_word TEXT,
    admin_uuid UUID
);
CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms ON DELETE CASCADE NOT NULL,
    word TEXT UNIQUE NOT NULL,
    suggester_uuid UUID NOT NULL
);
CREATE TABLE IF NOT EXISTS player_words (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms ON DELETE CASCADE NOT NULL,
    word TEXT NOT NULL,
    uuid UUID
);