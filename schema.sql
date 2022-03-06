CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word TEXT UNIQUE
);
CREATE TABLE player_words (
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL,
    uuid UUID
);
CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    players INT,
    current_word TEXT,
    previous_word TEXT
);