CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS avatars (
    user_id INTEGER PRIMARY KEY,
    file_format TEXT NOT NULL,
    avatar BLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users_boardgames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    boardgame_type INTEGER,
    user_games INTEGER DEFAULT 1,
    reserved_user_games INTEGER DEFAULT 0,
    FOREIGN KEY (boardgame_type) REFERENCES boardgames(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS boardgames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    number_of_players INTEGER,
    category_id INTEGER,
    duration INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(200) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS photos (
    boardgame_id INTEGER NOT NULL,
    id INTEGER NOT NULL,
    name TEXT NOT NULL,
    file_format TEXT NOT NULL,
    photo BLOB NOT NULL,
    PRIMARY KEY (boardgame_id, id),
    FOREIGN KEY (boardgame_id) REFERENCES boardgames(id)
);

CREATE TABLE IF NOT EXISTS ratings (
    boardgame_id INTEGER,
    user_id INTEGER,
    rating REAL NOT NULL,
    review TEXT,
    PRIMARY KEY (boardgame_id, user_id),
    FOREIGN KEY (boardgame_id) REFERENCES boardgames(id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TEXT NOT NULL,
    reserver INTEGER NOT NULL,
    game_owner INTEGER NOT NULL,
    boardgame_id INTEGER NOT NULL,
    FOREIGN KEY (boardgame_id) REFERENCES boardgames(id),
    FOREIGN KEY (reserver) REFERENCES users(id),
    FOREIGN KEY (game_owner) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_boardgames_name ON boardgames(name);
CREATE INDEX IF NOT EXISTS idx_users_boardgames_user_id ON users_boardgames(user_id);
CREATE INDEX IF NOT EXISTS idx_users_boardgames_boardgame_type ON users_boardgames(boardgame_type);
CREATE INDEX IF NOT EXISTS idx_reservation_reserver ON reservation(reserver);
CREATE INDEX IF NOT EXISTS idx_reservation_boardgame_id ON reservation(boardgame_id);
CREATE INDEX IF NOT EXISTS idx_reservation_boardgame_reserver ON reservation(boardgame_id, reserver);
CREATE INDEX IF NOT EXISTS idx_ratings_boardgame_id ON ratings(boardgame_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON ratings(user_id);