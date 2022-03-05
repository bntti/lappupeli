CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word TEXT UNIQUE
);
CREATE TABLE player_words (
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL
);
CREATE TABLE config (id SERIAL PRIMARY KEY, players INT);