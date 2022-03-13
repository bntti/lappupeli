CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    word TEXT UNIQUE,
    suggester_uuid UUID
);
CREATE TABLE IF NOT EXISTS player_words (
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL,
    uuid UUID
);
CREATE TABLE IF NOT EXISTS config (
    id SERIAL PRIMARY KEY,
    players INT DEFAULT 5 NOT NULL,
    current_word TEXT,
    suggester_uuid UUID,
    previous_word TEXT,
    admin_uuid UUID
);