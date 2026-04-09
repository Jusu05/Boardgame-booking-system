import sqlite3, os
from datatypes import Boardgame, Review, User

class SqlConnection:
    def __init__(self, file: str) -> None:
        self._file = file

    def write(self, command: str, params: tuple = None):
        connection = sqlite3.connect(self._file)
        cursor = connection.cursor()

        if params:
            cursor.execute(command, params)
        else:
            cursor.execute(command)

        connection.commit()
        connection.close()

    def read(self, command: str, params: tuple = None) -> list:
        connection = sqlite3.connect(self._file)    
        cursor = connection.cursor()

        if params:
            cursor.execute(command, params)
        else:
            cursor.execute(command)

        data = cursor.fetchall()
        connection.commit()
        connection.close()
        return data

def get_user_by_id(user_id: int) -> User | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read("SELECT username, password FROM Users WHERE id = ?;", (user_id, ))

    if len(user) > 0:
        return User(user_id, user[0][0], user[0][1])

    return None

def get_user_by_username(username: str) -> User | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read("SELECT id, password FROM Users WHERE username = ?;", (username, ))

    if len(user) > 0:
        return User(user[0][0], username, user[0][1])

    return None

def insert_user(username: str, password: str):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if len(username) > 100:
        raise ValueError("username is longer than 100 character")
    conn.write("INSERT INTO Users (username, password) VALUES (?,?);", (username, password))

def add_avatar(user_id: int, avatar):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("UPDATE Users SET avatar = ? WHERE id = ?;", (avatar, user_id))

def insert_boardgame(boardgame: Boardgame):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if not boardgame.category_id:
        raise ValueError("Boardgame does not have category")
    if len(boardgame.name) > 100:
        raise ValueError("Boardgame's name is longer than 100 character")
    values = [
        boardgame.name,
        boardgame.description,
        boardgame.number_of_players,
        boardgame.duration,
        boardgame.category_id
    ]
    
    if boardgame.free_games:
        values.append(boardgame.free_games)
        conn.write("INSERT INTO Boardgames (name, description, number_of_players, duration, category_id, free_games) VALUES (?,?,?,?,?,?);", tuple(values))
        return

    conn.write("INSERT INTO Boardgames (name, description, number_of_players, duration, category_id) VALUES (?,?,?,?,?);", tuple(values))

def update_boardgame(boardgame: Boardgame):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if not boardgame.category_id:
        raise ValueError("Boardgame does not have category")
    if len(boardgame.name) > 100:
        raise ValueError("Boardgame's name is longer than 100 character")
    
    values = (
        boardgame.name,
        boardgame.description,
        boardgame.number_of_players,
        boardgame.duration,
        boardgame.category_id,
        boardgame.free_games,
        boardgame.id
    )
    
    conn.write("UPDATE Boardgames SET name = ?, description = ?, number_of_players = ?, duration = ?, category_id = ?, free_games = ? - reserved_games WHERE id = ?;", values)

def get_boardgame_by_name(boardgame_name: str) -> Boardgame | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            b.number_of_players,
            b.duration,
            b.id,
            b.description,
            b.free_games,
            b.reserved_games,
            c.category,
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM Boardgames b
        LEFT JOIN Categories c ON b.category_id == c.id
        LEFT JOIN Ratings r ON r.boardgame_id == b.id
        WHERE name = ?
        GROUP BY b.id;
        """,
        (boardgame_name,)
    )

    if len(result) > 0:
        return Boardgame(boardgame_name, result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], category=result[0][6], stars=result[0][7], half_star=bool(result[0][8]))
    return None

def get_all_boardgames() -> list[Boardgame] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            b.name,
            b.number_of_players,
            b.duration,
            b.id,
            b.description,
            b.free_games,
            b.reserved_games,
            c.category,
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM Boardgames b
        LEFT JOIN Categories c ON b.category_id == c.id
        LEFT JOIN Ratings r ON r.boardgame_id == b.id
        GROUP BY b.id;
        """
    )
    if len(result) > 0:
        return list(map(lambda result: Boardgame(result[0], result[1], result[2], result[3], result[4], result[5], result[6], category=result[7], stars=result[8], half_star=bool(result[9])), result))
    return None

def get_all_boardgames_by_search_word(search_word: str) -> list[Boardgame] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            b.name,
            b.number_of_players,
            b.duration,
            b.id,
            b.description,
            b.free_games,
            b.reserved_games,
            c.category,
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM Boardgames b
        LEFT JOIN Categories c ON b.category_id == c.id
        LEFT JOIN Ratings r ON r.boardgame_id == b.id
        WHERE b.name LIKE ?
        GROUP BY b.id;
        """,
        (f"%{search_word}%", )
    )

    if len(result) > 0:
        return list(map(lambda result: Boardgame(result[0], result[1], result[2], result[3], result[4], result[5], result[6], category=result[7], stars=result[8], half_star=bool(result[9])), result))
    return None

def get_boardgame_categories() -> list[tuple[int, str]] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT id, category
        FROM Categories
        ORDER BY IIF(id == 0, 1, 0), id
    """)
    if len(result) > 0:
        return result
    return None

def get_reviews_by_boardgame_id(id: int) -> list[Review] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            u.username,
            r.review,
            r.rating,
            CAST(r.rating AS INTEGER) AS stars,
            IIF(r.rating - FLOOR(r.rating) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star,
            u.avatar
        FROM Ratings r
        LEFT JOIN Users u ON u.id == r.user_id
        WHERE r.boardgame_id == ?
    """, (id, ))
    if len(result) > 0:
        return list(map(lambda result: Review(result[0], result[1], result[2], result[3], result[4], result[5]), result))
    return None
