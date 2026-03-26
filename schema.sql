CREATE TABLE IF NOT EXISTS Users (
    id INTEGER,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    avatar BLOB,
    PRIMARY KEY(id AUTOINCREMENT),
);

CREATE TABLE IF NOT EXISTS Boardgames (
    id INTEGER,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    number_of_players INTEGER,
    category_id INTEGER,
    duration INTEGER,
    free_games INTEGER DEFAULT 1,
    reserved_games INTEGER DEFAULT 0,
    PRIMARY KEY(id AUTOINCREMENT),
    FOREIGN KEY (category_id) REFERENCES Categories(id),
);

CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER UNIQUE NOT NULL,
    category VARCHAR(200) UNIQUE NOT NULL,
)

CREATE TABLE IF NOT EXISTS Photos (
    boardgame_id INTEGER NOT NULL,
    photo BLOB NOT NULL,
)


CREATE TABLE IF NOT EXISTS Ratings (
    boardgame_id INTEGER,
    user_id INTEGER,
    rating Real NOT NULL,
    review TEXT,
    PRIMARY KEY(boardgame_id),
    FOREIGN KEY (boardgame_id) REFERENCES Boardgames(id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
)

CREATE TABLE IF NOT EXISTS Reservation (
    start_time VARCHAR(19),
    end_time VARCHAR(19),
    user_id INTEGER REFERENCES,
    boardgame_id REFERENCES,
    PRIMARY KEY(user_id),
    FOREIGN KEY (boardgame_id) REFERENCES Boardgames(id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
)
