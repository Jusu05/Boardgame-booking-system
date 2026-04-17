import sqlite3, os
from datatypes import Boardgame, Review, User
from security import current_user

class SqlConnection:
    def __init__(self, file: str) -> None:
        self._file = file
        self.write("PRAGMA foreign_keys = ON;")

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
    user = conn.read("SELECT username, password FROM users WHERE id = ?;", (user_id, ))

    if len(user) > 0:
        return User(user_id, user[0][0], user[0][1])

    return None

def get_user_by_username(username: str) -> User | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read("SELECT id, password FROM users WHERE username = ?;", (username, ))

    if len(user) > 0:
        return User(user[0][0], username, user[0][1])

    return None

def insert_user(username: str, password: str):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if len(username) > 100:
        raise ValueError("username is longer than 100 character")
    conn.write("INSERT INTO users (username, password) VALUES (?,?);", (username, password))

def add_avatar(user_id: int, avatar):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("UPDATE users SET avatar = ? WHERE id = ?;", (avatar, user_id))

def get_users_game_count_by_boardgame_id(boardgame_id: int) -> list[int] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT user_games, reserved_user_games
        FROM users_boardgames
        WHERE boardgame_type == ?;
    """, (boardgame_id,))
    if len(result) > 0:
        return result[0]
    return (1, 0)

def get_user_boardgame_ids(user_id: int) -> set[int] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("SELECT boardgame_type FROM users_boardgames WHERE boardgame_type == ?;", (user_id, ))
    if len(result) > 0:
        return {value[0] for value in result}
    return None

def insert_boardgame(boardgame: Boardgame, users_game: int = None):
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
        boardgame.category_id
    )

    conn.write("""
        INSERT INTO
            boardgames (
                name,
                description,
                number_of_players,
                duration,
                category_id
            )
        VALUES (?, ?, ?, ?, ?);
        """, values
    )

    if users_game:
        conn.write("""
            INSERT INTO users_boardgames (user_id, boardgame_type, user_games)
            SELECT ?, b.id, ?
            FROM boardgames b
            WHERE b.name = ?
            """,
            (current_user.id, users_game, boardgame.name)
        )
    else:
        conn.write("""
            INSERT INTO users_boardgames (user_id, boardgame_type)
            SELECT ?, b.id
            FROM boardgames b
            """,
            (current_user.id,)
        )

def update_boardgame(boardgame: Boardgame, users_games: int = None):
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
        boardgame.category_id
    )

    conn.write("""
        UPDATE boardgames
        SET name = ?,
            description = ?,
            number_of_players = ?,
            duration = ?,
            category_id = ?
        WHERE id = ?;
        """, values
    )

    if users_games:
        conn.write("""
            UPDATE users_boardgames
            SET user_games = ?
            WHERE user_id = ? AND boardgame_type = ?
            """,
            (users_games, current_user.id, boardgame.id)
        )

def get_boardgame_by_name(boardgame_name: str) -> Boardgame | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            b.number_of_players,
            b.duration,
            b.id,
            b.description,
            SUM(ub.user_games) AS free_games,
            SUM(ub.reserved_user_games) AS reserved_games,
            c.category,
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id == c.id
        LEFT JOIN ratings r ON r.boardgame_id == b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type == b.id
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
            SUM(ub.user_games) AS free_games,
            SUM(ub.reserved_user_games) AS reserved_games,
            c.category,
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id == c.id
        LEFT JOIN ratings r ON r.boardgame_id == b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type == b.id
        GROUP BY b.id;
        """
    )
    if len(result) > 0:
        return list(map(lambda result: Boardgame(result[0], result[1], result[2], result[3], result[4], result[5], result[6], category=result[7], stars=result[8], half_star=bool(result[9])), result))
    return None

def get_user_boardgames(user_id: int) -> list[Boardgame] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            b.name,
            b.number_of_players,
            b.duration,
            b.id,
            b.description,
            SUM(ub.user_games) AS free_games,
            SUM(ub.reserved_user_games) AS reserved_games,
            c.category,
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
            p.name
            p.id
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id == c.id
        LEFT JOIN ratings r ON r.boardgame_id == b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type == b.id
        LEFT JOIN photos p ON p.boardgame_id = b.id
        WHERE ub.user_id == ?
        GROUP BY b.id;
    """, (user_id, ))
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
            SUM(ub.user_games) AS free_games,
            SUM(ub.reserved_user_games) AS reserved_games,
            c.category,
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id == c.id
        LEFT JOIN ratings r ON r.boardgame_id == b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type == b.id
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
        FROM categories
        ORDER BY IIF(id == 0, 1, 0), id;
    """)
    if len(result) > 0:
        return result
    return [(0, "muu")]

def get_reviews_by_boardgame_id(boardgame_id: int) -> list[Review] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            u.id,
            u.username,
            r.review,
            r.rating,
            CAST(r.rating AS INTEGER) AS stars,
            IIF(r.rating - FLOOR(r.rating) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star,
            u.avatar
        FROM ratings r
        LEFT JOIN users u ON u.id == r.user_id
        WHERE r.boardgame_id == ?;
    """, (boardgame_id, ))
    if len(result) > 0:
        return list(map(lambda result: Review(User(result[0], result[1], None), result[2], result[3], result[4], result[5], result[6]), result))
    return None

def get_user_review_stats() -> tuple[int, int, bool] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            COUNT(r.rating),
            CAST(SUM(r.rating) AS INTEGER) AS stars,
            IIF(SUM(r.rating) - FLOOR(SUM(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM ratings r
        LEFT JOIN users u ON u.id == r.user_id
        WHERE u.id == ?;
    """, (current_user.id, ))
    if len(result) > 0:
        return result[0]
    return None

def upsert_review(boardgame_id: int, review: Review):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("""
        INSERT INTO ratings (boardgame_id, user_id, rating, review)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(boardgame_id, user_id) DO UPDATE SET
            rating = excluded.rating,
            review = excluded.review
        WHERE excluded.boardgame_id == ratings.boardgame_id AND
            excluded.user_id == ratings.user_id;
    """,
    (boardgame_id, review.user.id, review.rating, review.text)
    )