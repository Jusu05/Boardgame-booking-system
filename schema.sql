CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    avatar BLOB
);

CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(200) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Boardgames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    number_of_players INTEGER,
    category_id INTEGER,
    duration INTEGER,
    free_games INTEGER DEFAULT 1,
    reserved_games INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES Categories(id)
);

CREATE TABLE IF NOT EXISTS Photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boardgame_id INTEGER NOT NULL,
    photo BLOB NOT NULL,
    FOREIGN KEY (boardgame_id) REFERENCES Boardgames(id)
);

CREATE TABLE IF NOT EXISTS Ratings (
    boardgame_id INTEGER,
    user_id INTEGER,
    rating REAL NOT NULL,
    review TEXT,
    PRIMARY KEY (boardgame_id, user_id),
    FOREIGN KEY (boardgame_id) REFERENCES Boardgames(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE IF NOT EXISTS Reservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    boardgame_id INTEGER NOT NULL,
    FOREIGN KEY (boardgame_id) REFERENCES Boardgames(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- TODO add indexes