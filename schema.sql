CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY,
    word TEXT UNIQUE
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
    previous_word TEXT,
    admin_uuid UUID
);