CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    avatar BLOB
);

CREATE TABLE IF NOT EXISTS avatars (
    user_id INTEGER PRIMARY KEY,
    file_format VARCHAR(100) NOT NULL,
    avatar BLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)

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
    name VARCHAR(100) NOT NULL UNIQUE,
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
    boardgame_id INTEGER NOT NULL PRIMARY KEY,
    id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    file_format VARCHAR(100) NOT NULL,
    photo BLOB NOT NULL,
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
    user_id INTEGER NOT NULL,
    boardgame_id INTEGER NOT NULL,
    FOREIGN KEY (boardgame_id) REFERENCES users_boardgames(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- TODO add indexes