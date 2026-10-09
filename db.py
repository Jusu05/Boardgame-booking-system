import os
import sqlite3
from datetime import datetime
from datatypes import Boardgame, DatabaseError, Photo, Review, User

class SqlConnection:
    def __init__(self, file: str) -> None:
        self._file = file

    def write(self, command: str, params: tuple = None):
        connection = sqlite3.connect(self._file)
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        if params:
            cursor.execute(command, params)
        else:
            cursor.execute(command)

        connection.commit()
        connection.close()

    def read(self, command: str, params: tuple = None) -> list:
        connection = sqlite3.connect(self._file)
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

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
    user = conn.read(
        "SELECT username, password FROM users WHERE id = ?;",
        (user_id,)
    )

    if len(user) > 0:
        return User(user_id, user[0][0], user[0][1])
    return None

def get_user_by_username(username: str) -> User | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read(
        "SELECT id, password FROM users WHERE username = ?;",
        (username,)
    )

    if len(user) > 0:
        return User(user[0][0], username, user[0][1])
    return None

def insert_user(username: str, password: str) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if len(username) > 100:
        raise ValueError("username is longer than 100 character")
    try:
        conn.write(
            "INSERT INTO users (username, password) VALUES (?,?);",
            (username, password)
        )
    except sqlite3.Error as e:
        raise DatabaseError from e

def get_avatar_by_username(username: str) -> Photo:
    b = bytes.fromhex("""
        89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52 00 00 01 f4 00 00 01 f4
        08 06 00 00 00 cb d6 df 8a 00 00 00 01 73 52 47 42 01 d9 c9 2c 7f 00 00
        00 04 67 41 4d 41 00 00 b1 8f 0b fc 61 05 00 00 00 20 63 48 52 4d 00 00
        7a 26 00 00 80 84 00 00 fa 00 00 00 80 e8 00 00 75 30 00 00 ea 60 00 00
        3a 98 00 00 17 70 9c ba 51 3c 00 00 09 a2 49 44 41 54 78 da ed dc 51 6a
        03 c9 12 44 d1 96 56 5c 4b a9 1d cb 1f 6d 81 c1 02 5b 26 1b 57 45 9e b3
        80 f7 a1 e1 cd 25 b2 7a 7c 1c 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00 ac e5 e6 27 80 35 cd 39 1f 55 ff 5b 63 0c ff 5f 07 41 07
        56 8e b5 e8 03 82 0e 0d c3 2d f4 20 e8 40 78 bc 45 1e 04 1d 04 bc 31 81
        07 41 07 11 17 77 40 d0 41 c0 05 1e 10 74 10 71 71 07 41 07 21 47 d8 41
        d0 41 c4 11 77 10 74 10 72 61 07 04 1d 11 47 dc 41 d0 41 c8 11 76 10 74
        10 72 84 1d 04 1d 84 5c d8 01 41 47 c8 11 76 10 74 10 73 44 1d 04 1d 84
        1c 61 07 41 07 21 47 d8 41 d0 11 72 84 1d 04 1d c4 1c 51 07 41 07 21 47
        d8 41 d0 11 73 10 75 10 74 84 1c 61 17 76 04 1d c4 1c 51 07 41 07 31 47
        d4 41 d0 11 72 10 76 10 74 c4 1c 44 1d 41 07 31 47 d4 41 d0 41 c8 11 76
        10 74 c4 1c 44 1d 04 1d 31 07 51 47 d0 41 cc 11 75 10 74 10 73 44 1d 04
        1d 31 07 51 07 41 47 cc 41 d4 11 74 10 73 10 75 04 1d c4 1c 51 07 41 47
        cc 41 d4 41 d0 11 73 10 75 04 1d c4 1c 44 1d 41 47 cc 41 d4 41 d0 11 73
        10 75 10 74 c4 1c 44 1d 41 07 31 07 51 47 d0 11 73 10 75 51 47 d0 11 73
        10 75 10 74 c4 1c 44 1d 8e bb 9f 00 00 2c 74 ac 73 c0 4a 47 d0 11 73 10
        75 10 74 c4 1c 44 1d 8e e3 f0 86 0e 00 16 3a d6 39 60 a5 23 e8 88 39 88
        3a 08 3a 62 0e a2 0e 4f de d0 01 c0 42 c7 3a 07 ac 74 04 1d 31 07 51 87
        12 4e ee 00 60 a1 63 9d 03 56 3a 82 8e 98 83 a8 43 09 27 77 00 b0 d0 b1
        ce 01 2b 1d 0b 1d 00 b0 d0 b1 ce c1 4a 07 0b 1d 00 2c 74 ac 73 c0 4a 47
        d0 11 73 40 d4 29 e4 e4 0e 00 16 3a d6 39 60 a5 63 a1 03 00 16 3a d6 39
        58 e9 60 a1 03 80 85 8e 75 0e 58 e9 58 e8 00 80 85 8e 75 0e 56 3a 58 e8
        00 20 e8 00 c0 6a 9c 74 1a 70 6e 87 3d 39 bb 63 a1 03 80 85 8e 75 0e 58
        e9 58 e8 00 80 a0 03 00 ef 73 ca 09 e6 dc 0e 19 9c dd b1 d0 01 c0 42 c7
        3a 07 ac 74 2c 74 00 40 d0 01 80 df 73 c2 09 e4 dc 0e 99 9c dd b1 d0 01
        40 d0 01 00 41 07 00 2e e7 3d 26 8c f7 73 c8 e6 1d 1d 0b 1d 00 04 1d 00
        58 99 d3 4d 10 e7 76 e8 c1 d9 1d 0b 1d 00 04 1d 00 10 74 00 e0 32 de 61
        42 78 3f 87 5e bc a3 63 a1 03 80 a0 03 00 82 0e 00 08 3a 00 f0 9a 8f 2a
        02 f8 20 0e 7a f2 61 1c 16 3a 00 08 3a 00 20 e8 00 80 a0 03 00 82 0e 00
        91 7c 21 b9 39 5f b8 43 6f be 74 c7 42 07 00 41 07 00 04 1d 00 10 74 00
        40 d0 01 40 d0 01 00 41 07 00 04 1d 00 78 c5 1f 24 d8 98 3f 2a 03 1c 87
        3f 2e 83 85 0e 00 82 0e 00 08 3a 00 20 e8 00 80 a0 03 80 a0 03 00 82 0e
        00 08 3a 00 20 e8 00 20 e8 00 80 a0 03 00 82 0e 00 08 3a 00 08 3a 00 20
        e8 00 80 a0 03 00 82 0e 00 82 0e 00 ac ef e6 27 d8 db 9c f3 e1 57 80 be
        c6 18 fe 3d 8e 85 0e 00 82 0e 00 08 3a 00 20 e8 00 80 a0 03 80 a0 03 00
        82 0e 00 08 3a 00 f0 8d 3f 48 10 c0 1f 97 81 9e fc 51 19 2c 74 00 10 74
        00 40 d0 01 00 41 07 00 04 1d 00 22 f9 42 32 84 2f dd a1 17 5f b8 63 a1
        03 80 a0 03 00 82 0e 00 08 3a 00 f0 9a 8f 2a 82 f8 30 0e 7a f0 41 1c 16
        3a 00 08 3a 00 20 e8 00 c0 65 bc c3 84 f1 8e 0e d9 bc 9f 63 a1 03 80 a0
        03 00 2b 73 ba 09 e4 ec 0e 99 9c db b1 d0 01 40 d0 01 00 41 07 00 2e e7
        3d 26 94 77 74 c8 e2 fd 1c 0b 1d 00 04 1d 00 d8 81 13 4e 30 67 77 c8 e0
        dc 8e 85 0e 00 16 3a 56 3a 60 9d 63 a1 03 00 82 0e 00 fc 9e 53 4e 03 ce
        ee b0 27 e7 76 2c 74 00 b0 d0 b1 d2 01 eb 1c 0b 1d 00 10 74 00 e0 7d 4e
        3a 8d 38 bb c3 1e 9c db b1 d0 01 c0 42 c7 4a 07 ac 73 2c 74 00 c0 42 c7
        4a 07 eb dc 3a c7 42 07 00 0b 1d 2b 1d b0 ce b1 d0 01 00 0b 1d 2b 1d ac
        73 bf 02 82 8e a8 83 98 83 93 3b 00 58 e8 58 e9 80 75 8e 85 0e 00 58 e8
        58 e9 60 9d 83 85 0e 00 16 3a 56 3a 60 9d 23 e8 88 3a 88 39 54 72 72 07
        00 0b 1d 2b 1d b0 ce 11 74 44 1d c4 1c 4a 38 b9 03 80 85 8e 95 0e 58 e7
        08 3a a2 0e 62 0e 82 8e a8 83 98 c3 c9 1b 3a 00 58 e8 58 e9 80 75 8e a0
        23 ea 20 e6 20 e8 88 3a 88 39 9c bc a1 03 80 85 8e 95 0e 58 e7 08 3a a2
        0e 62 0e 82 8e a8 83 98 83 a0 23 ea 20 e6 08 3a 88 3a 62 2e e6 08 3a a2
        0e 62 0e 82 8e a8 83 98 83 a0 23 ea 20 e6 08 3a 88 3a 62 0e 82 8e a8 83
        98 83 a0 23 ea 20 e6 20 e8 88 3a 88 39 82 0e a2 8e 98 83 a0 23 ea 20 e6
        20 e8 88 3a 88 3b 08 3a a2 0e c2 8e a0 83 a8 83 b0 23 e8 20 e4 08 3b 08
        3a 42 0e c2 0e 82 8e 98 83 a8 23 e8 20 e4 20 ec 08 3a 42 0e c2 0e 82 8e
        90 83 b0 83 a0 23 e6 20 ea 08 3a 08 39 08 3b 82 8e 90 03 c2 8e a0 23 e6
        20 ea 20 e8 08 39 08 3b 82 0e 62 0e a2 8e a0 23 e4 80 b0 23 e8 88 39 88
        3a 08 3a 42 0e c2 8e a0 23 e6 80 a8 23 e8 08 39 20 ec 08 3a 62 0e 88 3a
        82 8e 98 83 a8 23 e8 08 39 20 ec 08 3a 62 0e 88 3a 82 8e 98 03 a2 8e a0
        23 e6 20 ea 08 3a 42 0e 08 3b 82 8e 98 03 a2 8e a0 23 e6 80 a8 23 e8 88
        39 20 ea 08 ba 98 03 a2 8e a0 23 e6 80 a8 23 e8 08 39 20 ec 08 3a 62 0e
        88 3a 82 2e e6 80 a8 23 e8 88 39 20 ea 08 3a 62 0e 88 3a 82 2e e6 00 a2
        8e a0 8b 39 80 a8 0b 3a 62 0e 88 3a 82 8e 98 03 a2 8e a0 8b 39 80 a8 23
        e8 62 0e 20 ea 82 8e 98 03 a2 8e a0 23 e6 80 a8 23 e8 62 0e 20 ea 08 ba
        98 03 88 7a b6 bb 9f 00 00 2c 74 ac 73 c0 4a 47 d0 11 73 40 d4 11 74 31
        07 10 75 04 5d cc 01 44 5d d0 11 73 40 d4 11 74 31 07 10 75 ea f8 cf d6
        00 c0 42 c7 3a 07 ac 74 04 5d cc 01 44 1d 41 17 73 00 51 47 d0 c5 1c 40
        d4 63 f8 28 0e 00 2c 74 ac 73 00 2b 5d d0 c5 1c 40 d4 11 74 31 07 10 75
        4e de d0 01 c0 42 c7 3a 07 b0 d2 05 5d cc 01 44 9d 12 4e ee 00 60 a1 63
        9d 03 58 e9 82 2e e6 00 a2 4e 09 27 77 00 b0 d0 b1 ce 01 ac 74 41 17 73
        00 51 a7 84 93 3b 00 58 e8 d6 b9 5f 01 c0 4a 17 74 31 07 10 75 4a 38 b9
        03 80 85 6e 9d 03 60 a5 5b e8 00 80 85 6e 9d 03 58 e9 08 ba 98 03 88 7a
        0c 27 77 00 b0 d0 ad 73 00 ac 74 0b 1d 00 b0 d0 ad 73 00 2b 1d 0b 1d 00
        2c 74 eb 1c 00 2b 5d d0 c5 1c 00 51 2f e4 e4 0e 00 16 ba 75 0e 80 95 6e
        a1 03 00 16 ba 75 0e 60 a5 63 a1 03 80 85 6e 9d 03 60 a5 5b e8 00 80 85
        6e 9d 03 58 e9 58 e8 00 20 e8 00 c0 6a 9c 33 3e 39 b7 03 ac c7 d9 dd 42
        07 00 0b dd 3a 07 c0 4a b7 d0 01 00 0b dd 3a 07 c0 4a b7 d0 01 c0 42 b7
        ce 01 b0 d2 2d 74 00 40 d0 01 80 bf 69 7b be 70 6e 07 d8 8f b3 bb 85 0e
        00 16 ba 75 0e 80 95 6e a1 03 00 82 0e 00 fc a4 dd d9 c2 b9 1d 60 7f ce
        ee 16 3a 00 08 3a 00 b0 a6 56 27 0b e7 76 80 1c ce ee 16 3a 00 08 3a 00
        b0 9e 36 e7 0a e7 76 80 3c ce ee 16 3a 00 08 3a 00 b0 96 16 a7 0a e7 76
        80 5c ce ee 16 3a 00 08 3a 00 b0 8e f8 33 85 73 3b 40 3e 67 77 0b 1d 00
        04 1d 00 10 74 00 a0 48 f4 9b 83 f7 73 80 3e ba bf a3 5b e8 00 20 e8 00
        80 a0 03 00 25 62 df 1b bc 9f 03 f4 d3 f9 1d dd 42 07 00 41 07 00 04 1d
        00 28 11 f9 d6 e0 fd 1c a0 af ae ef e8 16 3a 00 08 3a 00 20 e8 00 80 a0
        03 00 a7 b8 0f 07 7c 10 07 40 c7 0f e3 2c 74 00 10 74 00 40 d0 8b 39 b7
        03 20 e8 00 c0 b6 62 3e 1a b0 ce 01 f8 aa db 87 71 16 3a 00 08 3a 00 20
        e8 00 80 a0 03 00 82 0e 40 b0 6e 1f 4b df fd 43 03 00 41 07 00 04 1d 00
        10 74 00 40 d0 01 40 d0 01 00 41 07 00 04 1d 00 10 74 00 10 74 00 d8 42
        a7 3f 3c 26 e8 00 20 e8 00 80 a0 03 00 82 0e 00 08 3a 00 08 3a 00 20 e8
        00 80 a0 03 00 82 0e 00 82 0e 00 08 3a 00 20 e8 00 80 a0 03 80 a0 03 00
        82 0e 00 08 3a 00 20 e8 00 20 e8 00 80 a0 03 00 82 0e 00 08 3a 00 08 3a
        00 20 e8 00 80 a0 03 00 82 0e 00 82 0e 00 08 3a 00 20 e8 00 80 a0 03 80
        a0 03 00 82 0e 00 08 3a 00 20 e8 00 20 e8 00 80 a0 03 00 82 0e 00 08 3a
        00 08 3a 00 20 e8 00 80 a0 03 00 82 0e 00 82 0e 00 08 3a 00 20 e8 00 80
        a0 03 00 82 0e 00 82 0e 00 08 3a 00 20 e8 00 80 a0 03 80 a0 03 00 82 0e
        00 08 3a 00 20 e8 00 20 e8 00 80 a0 03 00 82 0e 00 08 3a 00 08 3a 00 20
        e8 00 80 a0 03 00 82 0e 00 82 0e 00 08 3a 00 20 e8 00 80 a0 03 80 a0 03
        00 82 0e 00 08 3a 00 20 e8 00 20 e8 00 80 a0 03 00 82 0e 00 08 3a 00 3c
        cd 39 1f 82 0e 00 08 3a 00 20 e8 00 80 a0 03 80 a0 03 00 82 0e 00 08 3a
        00 20 e8 00 20 e8 00 80 a0 03 00 82 0e 00 08 3a 00 08 3a 00 20 e8 ff 67
        8c 71 f3 8f 12 00 41 07 00 04 1d 00 10 74 00 40 d0 01 00 41 07 00 41 07
        00 04 1d 00 10 74 00 40 d0 01 40 d0 01 00 41 07 00 04 1d 00 10 74 00 10
        74 00 40 d0 01 80 72 1f 73 39 6d e7 9e ac c7 c8 00 00 00 00 49 45 4e 44
        ae 42 60 82""")
    return Photo(f"{username} avatar", None, "image/png", b)

def get_users_game_count_by_boardgame_id(
        boardgame_id: int
    ) -> list[int] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT user_games, reserved_user_games
        FROM users_boardgames
        WHERE boardgame_type = ?;
    """, (boardgame_id,))

    if len(result) > 0:
        return result[0]
    return (1, 0)

def set_user_boardgames_to_zero(user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("""
        UPDATE users_boardgames
        SET user_games = 0
        WHERE user_id = ?;
    """, (user_id,))

def delete_users_boardgames_by_boardgame_id(
    boardgame_id: int
) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write(
        "DELETE FROM users_boardgames WHERE boardgame_id = ?;",
        (boardgame_id,)
    )

def get_user_boardgame_ids(
    user_id: int
) -> set[int] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read(
        "SELECT boardgame_type FROM users_boardgames WHERE user_id = ?;",
        (user_id,)
    )

    if len(result) > 0:
        return {value[0] for value in result}
    return None

def insert_boardgame(boardgame_name: str, user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if len(boardgame_name) > 100:
        raise ValueError("Boardgame's name is longer than 100 character")
    try:
        conn.write(
            "INSERT INTO boardgames (name) VALUES (?);",
             (boardgame_name,)
        )
        conn.write("""
            INSERT INTO users_boardgames (user_id, boardgame_type, user_games)
            SELECT ?, b.id, 0
            FROM boardgames b
            WHERE b.name = ?
        """, (user_id, boardgame_name))

        id = conn.read("SELECT id FROM boardgames where name = ?;", (boardgame_name))[0][0]

    except sqlite3.Error as e:
        raise DatabaseError from e

    return id

def update_boardgame(
    boardgame: Boardgame,
    user_id: int,
    users_games: int = None
) -> None:
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
        boardgame.id
    )

    conn.write("""
        UPDATE boardgames
        SET name = ?,
            description = ?,
            number_of_players = ?,
            duration = ?,
            category_id = ?
        WHERE id = ?;
    """, values)

    if users_games:
        conn.write("""
            UPDATE users_boardgames
            SET user_games = ?
            WHERE user_id = ? AND boardgame_type = ?
        """, (users_games, user_id, boardgame.id))

def delete_boardgame(boardgame: Boardgame, user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("DELETE FROM photos WHERE boardgame_id = ?;", (boardgame.id,))
    conn.write(
        "DELETE FROM users_boardgames WHERE boardgame_id = ? AND user_id = ?;",
        (boardgame.id, user_id)
    )
    conn.write("DELETE FROM boardgames WHERE id = ?;", (boardgame.id,))

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
            IIF(
                AVG(r.rating) - FLOOR(AVG(r.rating))
                BETWEEN 0.25 AND 0.75, 1, 0
            ) AS half_star,
            COUNT(p.id) AS number_of_photos
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN ratings r ON r.boardgame_id = b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type = b.id
        LEFT JOIN photos p ON p.boardgame_id = b.id
        WHERE b.name = ?
        GROUP BY b.id;
    """, (boardgame_name,))

    if len(result) > 0:
        return Boardgame(
            boardgame_name,
            result[0][0],
            result[0][1],
            result[0][2],
            result[0][3],
            result[0][4],
            result[0][5],
            category=result[0][6],
            stars=result[0][7],
            half_star=bool(result[0][8]),
            number_of_photos=result[0][9]
        )
    return None

def get_number_of_boardgames() -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    n = conn.read("SELECT COUNT(id) FROM boardgames")
    return n[0][0]

def get_boardgame_page(page_num: int) -> list[Boardgame] | None:
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
            CAST(AVG(r.rating) AS INTEGER),
            IIF(
                AVG(r.rating) - FLOOR(AVG(r.rating))
                       BETWEEN 0.25 AND 0.75, 1, 0
            ) AS half_star
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN ratings r ON r.boardgame_id = b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type = b.id
        GROUP BY b.id
        HAVING COALESCE(
            SUM(ub.user_games), 0) + COALESCE(SUM(ub.reserved_user_games),
            0
        ) > 0
        LIMIT ?
        OFFSET ?;
    """, (int(os.getenv("PAGE_SIZE")), page_num * int(os.getenv("PAGE_SIZE"))))

    if len(result) > 0:
        return list(map(lambda r: Boardgame(
            r[0], r[1], r[2], r[3], r[4], r[5], r[6],
            category=r[7],
            stars=r[8],
            half_star=bool(result[9])
        ),
        result))
    return None

def get_user_boardgames(user_id: int, page_num: int) -> list[Boardgame] | None:
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
            IIF(
                AVG(r.rating) - FLOOR(AVG(r.rating))
                BETWEEN 0.25 AND 0.75, 1, 0
            ) AS half_star
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN ratings r ON r.boardgame_id = b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type = b.id
        WHERE ub.user_id = ?
        GROUP BY b.id
        LIMIT ?
        OFFSET ?;
    """, (
        user_id,
        int(os.getenv("PAGE_SIZE")),
        page_num * int(os.getenv("PAGE_SIZE"))
    ))

    if len(result) > 0:
        return list(
            map(lambda r:
                Boardgame(
                    r[0], r[1], r[2], r[3], r[4], r[5], r[6],
                    category=r[7],
                    stars=r[8],
                    half_star=bool(r[9])
                ),
                result))
    return None

def get_number_of_user_boardgames(user_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    n = conn.read(
        "SELECT COUNT(id) FROM users_boardgames WHERE user_id = ?",
        (user_id,)
    )
    return n[0][0]

def search_boardgames(
    search_word: str,
    longer_duration: int,
    shorter_duration: int,
    category_id: int | None,
    more_players: int,
    less_players: int,
    page_num: int
) -> list[Boardgame] | None:
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
            IIF(
                AVG(r.rating) - FLOOR(AVG(r.rating))
                BETWEEN 0.25 AND 0.75, 1, 0
            ) AS half_star
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id = c.id
        LEFT JOIN ratings r ON r.boardgame_id = b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type = b.id
        WHERE b.name LIKE ?
            AND b.number_of_players BETWEEN ? AND ?
            AND b.duration BETWEEN ? AND ?
            AND (b.category_id = ? OR ? IS NULL)
        GROUP BY b.id
        HAVING COALESCE(
            SUM(ub.user_games), 0) + COALESCE(SUM(ub.reserved_user_games), 0
        ) > 0
        LIMIT ?
        OFFSET ?;
    """, (
            f"%{search_word}%",
            more_players,
            less_players,
            longer_duration,
            shorter_duration,
            category_id,
            category_id,
            int(os.getenv("PAGE_SIZE")),
            page_num * int(os.getenv("PAGE_SIZE")),
        )
    )

    if len(result) > 0:
        return list(
            map(lambda r: Boardgame(
                r[0], r[1], r[2], r[3], r[4], r[5], r[6],
                category=r[7],
                stars=r[8],
                half_star=bool(r[9])
            ),
            result)
        )

    return None

def get_boardgame_categories() -> list[tuple[int, str]]:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT id, category
        FROM categories
        ORDER BY IIF(id = 0, 1, 0), id;
    """)

    if len(result) > 0:
        return result
    return [(0, "muu")]

def get_max_boardgame_category_id() -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("SELECT MAX(id) FROM categories")

    if len(result) > 0:
        return result[0][0]
    return 0

def get_photo_by_boardgame_name_and_photo_id(name: str, photo_id: int) -> Photo:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT p.name, p.id, p.file_format, p.photo
        FROM photos p
        JOIN boardgames b ON p.boardgame_id = b.id
        WHERE b.name = ? AND p.id = ?;
    """, (name, photo_id))

    if len(result) > 0:
        return Photo(result[0][0], result[0][1], result[0][2], result[0][3])

    b = bytes.fromhex("""
        89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52 00 00 01 f4 00 00 01 f4
        08 06 00 00 00 cb d6 df 8a 00 00 00 01 73 52 47 42 01 d9 c9 2c 7f 00 00
        00 04 67 41 4d 41 00 00 b1 8f 0b fc 61 05 00 00 00 20 63 48 52 4d 00 00
        7a 26 00 00 80 84 00 00 fa 00 00 00 80 e8 00 00 75 30 00 00 ea 60 00 00
        3a 98 00 00 17 70 9c ba 51 3c 00 00 20 00 49 44 41 54 78 da ed dd 57 90
        dd e9 59 e7 f1 ef e9 a0 38 9a d1 e4 20 4d 4e 8e 8c 13 36 d1 66 04 5e da
        ac 8d 09 36 b6 f1 62 82 01 1b 8c 8d 08 05 c5 96 66 2f dc b0 dc ec 56 9d
        aa dd 9b bd 61 b7 d8 ad 5d 2e 5c b0 50 b0 25 6c 8c 6c e3 c0 d8 33 e3 c9
        39 69 46 9a 91 d4 0a 1d d4 ea ee d3 27 ec c5 f3 fe e7 fc d5 ee 96 ba 8f
        ce f9 9f f4 fd 54 9d ea d6 8c e2 e9 f0 3b cf fb 3e ef f3 82 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 d2 50 2b f9 14 48 1a 36 e5 72 f9 bc df fb f6 ee dd db f0 99
        92 81 2e 49 bd 19 e4 bb 81 5f 07 76 00 e7 0a ec 1a 30 0d dc 0f 3c 04 4c
        ed dd bb b7 ee 33 28 03 5d 92 da 13 c8 6f 07 6e 3f 4f 18 af a5 0a bc 01
        f8 63 60 fb 3a 7e fe 09 e0 5f 80 af 01 df 49 c1 7e da ca 5d 06 ba a4 61
        0f e3 ad c0 6e 60 ac c5 df 62 14 f8 13 e0 c3 a9 82 6e c5 08 30 be ce ef
        7d 8d f4 e7 9c 4c a1 fe df 52 c5 3e 63 b5 2e 03 5d 52 bf 87 f2 38 b0 a9
        c5 ea f8 1d 40 19 b8 bc c5 0a 1b e0 4a 62 b9 bc 48 75 60 06 78 20 fd fd
        ff 35 fd b8 6a b5 2e 03 5d 52 bf 06 fa 7b 81 df 4a d5 f2 46 34 80 2b 80
        1f 68 e1 d7 f6 8a 59 e0 9b c0 df a7 8a fd 79 e0 8c a1 2e 03 5d 52 d1 61
        bc 09 f8 18 70 13 ad 2d 59 d7 53 20 7f 60 48 9f c2 06 70 06 78 1c b8 17
        f8 06 f0 65 e0 84 4b f0 32 d0 25 6d 24 90 77 01 6f 6a f1 eb b6 01 5c 0a
        fc 07 e0 f5 3e 9b 17 1c ec 33 c4 7e fa 5f a6 50 3f b2 77 ef de 9a 4f 8d
        0c 74 69 f0 c3 78 84 d8 ff dd 42 6b fb c7 35 e0 23 c0 3e 5a 5f b2 2e 01
        db e8 df 25 ef 5e ac d6 9f 01 fe 0b f0 cf c0 31 60 d1 6a 5d 06 ba d4 fb
        81 dc 6a 77 76 03 b8 0c f8 4f c0 db 89 06 b1 56 7e 8f cb 81 5d 7e 34 7a
        2a d4 17 81 27 80 ff 07 fc 63 7a 7f da 6a 5d 06 ba d4 bb 81 fe 6e e0 d7
        5a ac 6e 1b c0 56 60 4f 0a 76 0d 96 25 e0 65 e0 11 e0 eb c0 5f 03 87 f6
        ee dd 5b f5 a9 91 81 2e b5 37 8c c7 81 9f 26 ce 40 b7 b2 1c 5a 03 de 03
        fc 82 cf a6 ce 61 01 78 0a f8 02 f0 37 c4 72 bc 47 db 64 a0 4b 2b 42 79
        1b f0 46 36 7e 06 ba 9e aa e2 ff 08 7c 5f 8b 81 9e 7d ad f8 f5 a2 f3 59
        06 0e 03 7f 01 fc 03 70 90 18 44 63 b5 2e 03 5d 03 13 c8 17 11 0d 59 ad
        a8 02 77 01 ff 15 b8 ba 85 50 1e 01 2e 26 26 84 49 9d 56 05 0e 11 dd ef
        7f 0f 3c 0c bc 02 2c 59 ad ab 93 c6 7c 0a b4 ce 40 1e b9 80 5f 3e 02 7c
        8a d6 47 76 36 52 20 df e1 e7 ac fa e4 fb ea 6e 62 9b e7 4d c4 30 9a ff
        49 34 cc 2d fa f4 c8 0a 5d dd 0c f3 eb 80 cf 00 3b 69 6d c9 ba 04 fc 18
        b1 64 2e 0d 93 65 a2 61 ee 9f 80 ff 05 dc 97 2a 75 8f b6 c9 40 57 4b 81
        fc 8e 14 a6 ad 9e 7f be 1d f8 03 e0 22 9f 4d 69 c3 ea c4 05 2f 7f 0d fc
        5f e0 51 e2 cc 7a c5 25 78 19 e8 c3 15 c6 5b 81 9b 89 fd df 56 be f8 47
        80 3f 04 3e 4a eb 37 54 95 88 65 44 3f 5f a4 d6 34 52 a8 7f 8b 38 b3 7e
        3f d1 11 3f 6b a8 cb 40 ef 9f 40 de 02 6c be 80 ea f8 2e 62 12 55 2b cd
        60 99 4b ad ae a5 9e a8 d4 17 80 a3 c4 fd ea 7f 01 7c 9b e8 82 37 d4 65
        a0 f7 78 98 97 88 9b a9 7e 96 d6 9b c1 76 12 d7 4e da 0c 26 0d 86 ec 8e
        f5 fb 80 ff 0e 7c 09 38 ed d1 36 19 e8 9d 0d e4 ab 81 5f 21 3a ac 1b 2d
        3e bf ef 03 de ea b3 29 69 85 d3 c0 57 81 bf 25 3a e1 0f 02 f3 56 eb 32
        d0 d7 0e e5 5d c0 db 88 bd e4 8d be 8a 7e 1d 71 19 c6 25 7e aa 48 ea 80
        79 e0 b1 54 a5 7f 3b 55 ed 47 ec 82 d7 c0 05 7a 3a fb 7c 0d 31 90 a4 95
        57 ad 55 e0 e7 88 2b 23 5b 19 2a 32 42 dc 8e e5 4a 86 a4 4e 68 a4 e2 61
        86 98 05 ff 3f 88 81 34 af 02 75 ab 75 15 12 e8 7f fe e7 7f 5e 1a 1b 1b
        2b 8d 8d 8d 51 2a 95 1a ab 7d e2 95 cb e5 d1 14 a4 ad fc 39 75 62 ff f8
        3f 03 ef a2 b5 1b aa 48 d5 f5 b5 7e a8 25 f5 b0 3a cd eb 58 ff 92 98 07
        7f 12 af 63 d5 06 b4 d4 68 f5 f9 cf 7f 7e 0b b0 b3 54 2a 65 4b d1 87 89
        fd a0 95 7e 88 68 0a 6b e5 cf 69 10 dd e1 3f 8a 37 54 49 1a 6c 23 c4 49
        94 37 00 1f 4f df f3 be 08 3c 59 2e 97 4f 79 1d ab 3a 56 a1 7f fe f3 9f
        bf 6a 7c 7c fc 5d a3 a3 a3 77 8f 8d 8d 6d 1d 19 19 99 02 66 57 fc 7e 35
        e0 07 88 71 9f 92 a4 f5 a9 00 2f 11 67 d6 ef 25 96 e0 9f db bb 77 ef b2
        4f 8d da 5e a1 97 4a a5 db ea f5 fa 07 4b a5 d2 07 ea f5 fa e5 a5 52 69
        b4 54 72 9b 59 92 da 60 13 70 1b 31 0f fe ad c4 1c 89 bf 2b 97 cb 4f 01
        cb 2e c1 ab ad 81 0e fc 60 bd 5e ff 00 50 6a 34 1a 8d 52 a9 c4 e8 e8 a8
        cf a6 24 b5 cf 66 e2 42 a2 df 48 a1 fe 97 c0 cb e5 72 79 0e ef 59 d7 2a
        5a bd 41 6b 13 70 51 bd 5e df 5a af d7 a9 d7 eb 34 1a 7e 6e 49 52 1b 95
        d2 f7 da 5d c4 69 9d 3f 00 f6 00 37 00 5b d3 e0 2a e9 82 2b f4 7a f6 c9
        d6 68 34 1a b5 5a ad 3e 32 32 32 62 95 2e 49 6d 37 0a 5c 0f fc 64 7a fb
        5d e0 1f 88 f1 b1 b3 3e 3d ba d0 40 1f 4d bf 76 04 a8 d7 6a 35 46 46 46
        18 19 19 c1 bd 74 49 ea 48 a8 5f 05 5c 41 2c c3 5f 09 5c 5c 2e 97 bf 0e
        9c 72 6c ac 2e 34 d0 c7 81 5a a3 d1 18 01 a8 d7 eb 8d 7a bd 5e b2 4a 97
        a4 8e 19 21 e6 6a fc 2c 70 39 31 74 eb a1 72 b9 7c 08 98 f3 78 9b 9f 1c
        17 a2 94 1e d4 eb 75 6a b5 9a 7b e9 92 d4 59 a5 14 e4 ef 06 fe 98 68 9a
        fb 51 e0 9a 34 cc 4b 06 7a eb 81 de 68 34 4a 36 c7 49 52 a1 a1 be 1d b8
        13 f8 79 e0 77 81 0f 02 bb d3 c8 6c 0d a1 b1 36 7c 52 65 09 5e ca aa f4
        52 a9 e4 5e ba 24 75 5e d6 05 7f 69 0a f8 1d c0 df a4 25 f8 05 8f b6 59
        a1 b7 14 ec 8d 46 83 d4 f1 6e 95 2e 49 c5 da 06 bc 93 18 1b fb 8b c0 0f
        a7 6a 7d 93 4f 8d 15 fa 46 ab 74 00 b2 a5 77 ab 74 49 ea 4a 81 f6 7a e0
        53 c0 9b 80 7f 02 fe a5 5c 2e 3f 07 2c 59 ad 5b a1 6f 48 a3 d1 a0 5e af
        53 ad 56 a9 d7 9d 4e 28 49 5d 28 d2 ae 04 de 0b fc 4e aa d8 5f 07 6c 72
        10 8d 81 de 72 a8 db 20 27 49 5d 31 0a 5c 4c 9c 57 ff 05 e0 37 89 99 f0
        3b ed 82 37 d0 5b 0a f5 6a b5 4a ad e6 91 48 49 ea 92 71 e0 56 e0 03 29
        d4 7f 1a 78 5d b9 5c de ee 53 33 98 c6 3a f1 9b ae ac d2 dd 4b 97 a4 ae
        d9 45 5c 63 7d 5b 7a 7c b9 5c 2e 3f 40 0c a2 71 19 d5 40 df 58 a8 3b 3d
        4e 92 ba 26 3b b3 fe 2e e0 16 62 1e fc 18 70 5f ba b9 ad 6e b0 0f 86 8e
        0d 20 68 34 1a d4 6a 35 aa d5 aa 7b e9 92 d4 fd 50 df 04 5c 03 fc 5b e0
        73 a4 e9 72 d8 30 67 85 6e 95 2e 49 7d 67 94 b8 e0 e5 47 80 2d c0 57 80
        7f 01 1e 07 4e f8 f4 18 e8 e7 0d f4 ec 36 36 f7 d2 25 a9 27 5c 0a bc 07
        b8 8e 68 9c fb 52 b9 5c 3e 00 4c ed dd bb d7 33 c7 06 fa da a1 5e ab d5
        18 1d 1d b5 4a 97 a4 de b1 09 78 03 b0 3b 05 fb 38 f0 cf e5 72 79 0a 58
        76 5f bd ff 74 7c 88 bf e7 d2 25 a9 67 95 88 33 eb ef 06 3e 0b bc 8f e8
        84 df e1 99 75 03 7d cd 50 f7 5c ba 24 f5 6c a8 6f 23 c6 c5 7e 0e f8 0c
        f0 13 c0 75 e5 72 79 cc a7 c7 40 b7 4a 97 a4 fe b2 15 78 23 31 80 e6 d7
        89 b3 eb 37 95 cb e5 71 9f 9a fe 50 d8 ab 2f 3b de 25 a9 2f 8a bc dd 44
        27 fc 55 44 27 fc df 96 cb e5 17 f0 3a 56 03 3d 1f e8 59 b7 bb 1d ef 92
        d4 d3 b6 00 77 11 dd f0 e3 c0 01 e0 99 72 b9 7c 12 a8 18 ec bd fb 6a ac
        30 f9 2a 5d 92 d4 f3 05 df f5 c4 1c f8 bd c0 07 81 db 81 2d 0e a2 19 f2
        0a dd 2a 5d 92 fa ce 38 70 2d f0 63 c0 8d c4 0d 6e ff 9b 18 44 73 c6 a7
        67 88 03 3d 1f ea 9e 4b 97 a4 be 50 22 96 de 77 00 3b 89 e6 b9 ff 53 2e
        97 1f 01 66 1c 44 33 e4 81 ee f4 38 49 ea cb bc b8 19 f8 50 7a ff 9f 80
        87 ca e5 f2 21 60 de 7d f5 ee 1b e9 c6 1f 9a 55 e9 ee a5 4b 52 df 55 eb
        97 01 1f 25 06 d1 7c 0c 78 3b 70 49 b9 5c 1e f1 e9 19 d2 40 f7 5c ba 24
        f5 6d 6e 6c 07 de 06 fc 32 f0 db c0 0f 02 3b 6d 96 1b c2 40 cf 42 dd e9
        71 92 d4 b7 95 fa 56 a2 0b fe 6e ce 9e 2e b7 c9 a7 a7 3b ba 36 d6 6f 65
        95 ee 5e ba 24 f5 65 51 78 25 d1 05 3f 92 02 fe de 72 b9 fc 24 70 d2 86
        b9 21 a9 d0 57 86 ba 24 a9 6f 6d 4f 15 fa 27 81 4f e4 aa 75 c7 c6 0e 43
        85 9e 05 7a ad 56 a3 54 2a d9 f1 2e 49 fd 6d 9c 18 3c 73 0d f0 ba 14 f2
        5f 2e 97 cb 87 81 aa 5d f0 03 5e a1 5b a5 4b d2 c0 15 89 3b 81 b7 02 bf
        03 fc 7c 0a 77 af 63 1d a6 40 af d5 6a 76 bc 4b 52 ff 2b 01 17 11 37 b7
        fd 12 f0 69 e0 fd c0 6d e5 72 79 8b 4f 4f 67 5f 4d 75 9d d3 e3 24 69 e0
        8c 03 df 07 5c 0d dc 06 dc 0a 7c 31 35 cc cd ba 04 3f c0 81 9e 55 e9 d9
        7e ba 24 69 20 aa f5 ab 81 f7 00 b7 10 43 69 be 04 3c 5a 2e 97 a7 80 45
        83 bd 7d 7a 26 39 b3 2a dd 65 77 49 1a b8 50 df 44 5c ee f2 31 e2 e6 b6
        8f 00 af 07 b6 39 8c 66 c0 2a 74 ab 74 49 1a f8 50 1f 27 ce ac ff 00 70
        15 71 8b db 17 80 47 80 39 9f a2 01 0a f4 7c 95 9e 5d af 2a 49 1a 28 23
        c4 ad 6d af 07 b6 11 cd 73 5f 28 97 cb 0f e0 20 9a c1 0b 74 a7 c7 49 d2
        c0 db 44 ec a9 ef 00 b6 10 fb ec 0f 94 cb e5 97 88 9b db 0c f6 16 5f 2d
        f5 94 ac 4a 77 c6 bb 24 0d b4 51 62 e9 fd 83 c4 05 2f bf 48 dc dc b6 d3
        33 eb 03 14 e8 9e 4b 97 a4 a1 c9 a0 1d c0 5b 88 2b 59 7f 8d d8 63 bf d4
        eb 58 07 20 d0 57 56 e9 86 ba 24 0d b4 12 b1 ec 7e 03 f0 e3 c0 a7 80 9f
        04 76 97 cb e5 31 9f 9e f5 eb c9 27 2b 5f a5 3b e3 5d 92 86 26 8f ae 25
        ce ac 6f 06 76 03 df 2a 97 cb 4f 10 0d 73 ee c3 9e c7 86 f7 29 26 27 27
        c7 81 3d c0 bb 3b fa 92 2d 85 78 16 e8 86 ba 24 0d 4d b5 7e 3d 70 13 31
        88 a6 0e 4c 4f 4c 4c 9c d9 bf 7f bf cd 72 e7 79 f2 36 12 e6 25 62 f0 fe
        1f 01 bf 4f 9c 2b ec 58 d2 8e 8c 8c 30 3e 3e ce d8 d8 98 c7 d8 24 69 78
        34 52 90 9f 04 ee 07 fe 0a f8 1a 70 08 6f 6e 6b 4f 85 7e e0 c0 01 f6 ec
        d9 53 25 ae c7 bb 85 e8 50 ec 78 d2 7a 2e 5d 92 86 ae d8 1c 01 b6 a6 9c
        b9 39 85 fc 29 e0 f4 c4 c4 44 6d ff fe fd 86 fa 85 04 7a 0a f5 fa 9e 3d
        7b ea c0 c5 c4 6d 3a 5b 3a 59 a5 67 81 ee b2 bb 24 0d 65 b0 6f 01 2e 07
        ae 23 ce ab 6f 06 e6 d3 12 bc fb ea f9 ac 6c f1 d7 bd 04 3c 00 1c 03 96
        3b f9 17 cc 3a de bd 2f 5d 92 86 d6 56 e2 e6 b6 9f 03 3e 41 9c 5d f7 3a
        d6 15 5a ed 72 9f 07 0e 02 8f 13 b3 79 2f eb 54 95 ee f4 38 49 12 b1 a2
        7c 1d b1 3a 7c 75 0a f9 7f 2c 97 cb 4f 03 67 dc 57 6f 61 c9 1d e0 c0 81
        03 8d b4 ec 3e 02 dc 4e 2c 87 74 fc 08 5c b6 ec 6e a8 4b d2 d0 1a 4f 99
        73 2b 31 42 76 96 58 82 af 4e 4c 4c d4 f7 ef df 6f 85 de 82 ac fb f0 7e
        a2 69 61 77 a7 fe 92 f9 73 e9 a3 a3 4e 04 94 a4 21 96 ed ab df 04 7c 88
        68 d0 3e 00 7c 15 78 9e 58 41 1e 4a 17 d2 3a be 44 ec a5 7f 2b 3d 89 8b
        44 17 62 47 43 3d 5b 7a 97 24 0d 7d a5 7e 23 70 37 f0 71 e2 ae f5 bb ca
        e5 f2 8e 61 7d 42 5a 2e 77 d3 11 b6 1a 71 56 f0 46 62 6c df 0e 3a dc f1
        9e dd 95 ee b2 bb 24 59 ad 13 7b e9 57 12 c7 a9 b7 00 0b 13 13 13 33 13
        13 13 4b c3 76 b4 ed 42 f7 bd ab c4 41 ff 87 81 37 03 57 d0 c1 61 33 59
        c7 bb cb ee 92 a4 9c cd c0 6d 44 c3 dc ce f4 f6 c1 72 b9 7c 94 68 98 1b
        8a 63 52 17 94 8c 7b f6 ec c9 42 bd 44 74 1d de 42 5c 5a df f1 73 e9 56
        e9 92 a4 7c 34 a4 fc b9 3e 85 fb 4e 60 01 98 1d 96 6a fd 82 02 3d 2d bb
        67 4f d2 95 29 d0 af b8 d0 df f7 7c b2 65 77 a7 c7 49 92 56 84 fa d6 94
        43 37 a4 b7 67 80 93 69 10 8d 81 7e 9e 50 6f a4 bd f4 6d c0 ae f4 24 16
        32 3d ce 2a 5d 92 b4 b2 e6 23 8e b3 ed 24 56 8e 2f 25 56 92 07 fe 82 97
        b6 54 d2 69 be fb 28 71 36 f0 0e e0 12 ab 74 49 52 97 ab f5 1d a9 d0 bc
        2c 65 52 7d 62 62 62 69 62 62 a2 32 88 c1 de 96 d0 cd 2d bd 5f 0c bc 9e
        38 97 be b9 e3 2f c3 ec 78 97 24 9d bb 5a df 4c 4c 98 bb 23 65 d3 32 30
        37 88 d5 7a 3b a7 bb cd 02 cf 10 e3 60 6f 26 96 e0 3b 36 3d 2e 7f 2e dd
        ae 77 49 d2 39 42 7d 1b 31 59 ee 32 62 08 da e5 c0 3f 97 cb e5 83 0c d0
        75 ac 6d 4b c2 74 0b 5b 83 58 e2 c8 5e 09 8d 5b a5 4b 92 7a 20 d4 47 81
        ed 44 a3 dc b5 c4 3e fb 0c 71 1d 6b 75 10 ba e0 db bd 01 3d 07 3c 01 1c
        21 26 c9 75 94 37 b1 49 92 36 18 ec 3b 81 b7 03 1f 26 6e 6e 9b 00 6e 2d
        97 cb db ac d0 73 52 85 de 20 96 36 6e 24 ba 0b 3b 5e 3a db f1 2e 49 da
        80 f1 54 a9 df 42 2c c1 6f 02 ce 4c 4c 4c 9c 4e 0d 73 06 7a ee 16 b6 d1
        f4 24 ed 4a 4f 54 61 a1 2e 49 d2 3a f3 6f 3b b1 fc 7e 13 71 7e 7d 8e 38
        de 56 ed c7 86 b9 b6 77 93 a5 40 5f a2 79 b0 ff 32 da bf b4 6f 95 2e 49
        ba 50 a5 54 ad 5f 92 8a d0 6b d2 7f 3f 31 31 31 b1 d8 6f d7 b1 76 a2 0b
        bd 06 1c 05 fe 95 18 bf 77 2d b1 67 d1 b1 50 cf f6 d2 47 46 46 ec 78 97
        24 6d 34 d4 37 a7 02 34 9b 32 77 2b f0 35 e0 11 e0 c4 d0 56 e8 e9 4c 7a
        95 b8 4e 75 3b cd 71 b0 63 1d ff a8 d8 f1 2e 49 6a cd 48 ca ac 6b 88 1e
        b0 8b 81 e5 74 73 db 7c 3f 54 ea 1d 29 67 53 a8 2f a5 10 cf ef 4f 14 72
        b5 aa 7b e9 92 a4 16 ab f5 6c 6c ec f5 e9 ed 32 b1 af de f3 4b f0 9d 4c
        be 65 e0 25 e0 3b c0 61 a0 d2 c9 7f 48 b6 ec 5e ab d5 68 34 1a 7e 5a 4a
        92 5a 35 46 5c 38 b6 07 f8 0d e0 63 c0 9d c0 45 e5 72 b9 67 f7 75 3b f6
        17 cb 8d 83 dd 42 2c bb ef 22 a6 f5 74 f6 e5 95 55 ba 24 a9 3d 05 ef 16
        a2 b1 fb fa f4 18 01 66 26 26 26 e6 7a 71 10 4d a7 53 6f 21 55 e9 0f 11
        c3 66 96 ad d2 25 49 7d a2 44 4c 3f bd 13 78 1f f0 ef 80 f7 03 b7 97 cb
        e5 b1 5e fb cb 76 74 e9 20 8d 83 ad a7 ca fc 0e 62 3f 7d 73 11 ff 30 ab
        74 49 52 1b b3 f2 a2 94 61 59 93 f7 e9 34 88 66 b9 57 f6 d5 8b 48 bc 05
        e0 c5 f4 98 01 3a 7a 58 3f 7f 69 8b 55 ba 24 a9 cd d5 fa f7 03 bf 04 fc
        32 f0 2e e0 9a 72 b9 bc b9 17 fe 82 1d df dc 4f fb e8 cb c4 51 80 1b 88
        46 83 31 9c 1e 27 49 ea bf 50 1f 23 06 d1 dc 48 cc 5a d9 42 5c c7 3a dd
        ed 2e f8 8e 07 7a 6e 1c ec 96 f4 04 dc 94 de 77 c6 bb 24 a9 5f 43 7d 3b
        71 ab e8 6e 62 39 fe 34 70 7c ff fe fd cb dd fa 8b 15 b5 a9 5f 05 5e 00
        0e 02 f3 c4 d9 be 8e 72 7a 9c 24 a9 c3 05 f1 4e e0 cd 29 d0 77 02 97 97
        cb e5 6f 03 c7 f6 ee dd 5b f8 2c f8 a2 02 bd 0e 4c 01 cf 01 87 d2 ab 9a
        91 4e 56 e9 f9 40 b7 4a 97 24 75 c8 66 e0 f6 14 e8 57 a7 c7 bd e5 72 f9
        45 60 6e ef de bd 85 35 73 15 52 ba a6 33 e9 b5 f4 e7 5d 46 ec 3b 6c a3
        80 a6 3c cf a5 4b 92 3a 6c 84 98 86 ba 1b 78 23 71 75 f8 69 e0 64 ba 8e
        b5 90 50 2f 6c 2d 3a ed a5 57 d2 3f fa 16 a2 39 6e 53 11 7f b6 33 de 25
        49 05 84 fa 26 9a 0d 73 57 00 d3 c0 d1 89 89 89 a5 22 9a e5 8a 2e 5b a7
        81 47 81 6f 00 c7 89 9b d9 3a 2a 7f 8c 4d 92 a4 4e d6 8f 29 d4 af 05 ee
        26 c6 c6 7e 00 b8 b1 88 41 34 85 76 8b a5 41 33 95 f4 42 e2 0e 62 2f bd
        90 f3 7b 56 e9 92 a4 02 83 7d 7b 0a f6 2b 89 f3 eb a5 89 89 89 33 13 13
        13 0b 9d 5a 82 ef c6 c6 f2 1c f0 04 70 3f 70 8c 0e 0f 9a c9 aa f4 5a ad
        66 95 2e 49 2a d2 0e e0 47 80 5f 4f 8f bb 81 ab 3b 55 ad 17 7e 9e 2b 55
        e9 d9 52 fb cd c0 75 14 b4 97 6e c7 bb 24 a9 e0 4a 7d 34 05 fb 8d 29 ef
        e6 81 a9 54 ad 37 da b9 b7 de ad d6 ef 33 a9 4a 7f 04 38 0a 74 bc 03 d0
        2a 5d 92 d4 a5 50 1f 23 8e b5 7d 3f f0 69 e0 a3 c0 1b 80 ad e5 72 b9 6d
        15 66 57 26 ae e4 c6 c1 6e 23 ae 55 bd 9e 82 c7 c1 5a a5 4b 92 0a 0e f6
        cd c0 e5 c4 de fa 35 c4 d4 d4 f9 89 89 89 d3 fb f7 ef bf e0 6a b3 2b 81
        9e ce a5 d7 89 2e f7 6b 88 43 f9 17 e1 b9 74 49 d2 60 1b 27 1a c2 6f 4a
        c1 3e 0a 9c 48 77 ac 5f d0 c9 af ae cd 44 4d 55 fa 12 71 56 ef f6 f4 0f
        2c a4 4a b7 e3 5d 92 d4 45 23 34 57 a8 77 13 2b d6 27 d3 75 ac d5 56 f7
        d5 bb 16 e8 a9 4a af 02 17 13 b7 b0 dd 40 0c 9d b1 4a 97 24 0d ba 6c 6f
        fd 52 e0 d6 94 7f f3 c0 ec c4 c4 44 b5 95 86 b9 ae de 5a 92 a6 c7 8d 10
        e3 60 df 40 4c d8 29 64 be 7c a9 54 7a ed 21 49 52 17 43 fd e2 54 ad df
        94 de 3f 0d cc ec df bf bf ba d1 b2 bf db a6 80 c7 80 e7 d3 ab 93 c2 3a
        de 1b 8d 06 8d 46 c3 4f 29 49 52 37 8d a7 30 bf 1b f8 18 d1 05 ff e6 72
        b9 bc ad 6f 2a f4 54 a5 57 52 95 7e 4d fa 07 5d 52 d4 df cb bd 74 49 52
        0f 55 eb 9b 89 be b2 6b d2 8f e7 26 26 26 e6 d6 3b 0b be 27 2e 0a 4f 0d
        72 e3 c4 bd b2 d7 a4 f7 0b 91 05 ba a1 2e 49 ea 81 50 1f 25 c6 c6 ee 22
        f6 d5 cf 10 fb ea cb 13 13 13 f5 73 05 fb 58 8f fc 23 e6 89 bb d2 5f 05
        16 88 ee bf 8e ca 5f da 62 95 2e 49 ea 11 d9 55 ac bb 80 f7 a4 70 bf 1a
        f8 26 f0 12 50 39 d7 2f ec 05 cb c4 c4 b8 ef 00 07 81 6a 11 7f a8 d3 e3
        24 49 3d 1c ea 37 03 ef 4c 8f 1b 81 1d e5 72 79 a4 a7 03 fd 9e 7b ee 69
        10 97 b6 7c 9b 68 90 9b a6 a0 e6 b8 ac 4a 37 d4 25 49 3d 24 5b 7a bf a9
        d1 68 dc 5e ab d5 2e a9 d7 eb e3 a5 73 2c 27 8f f5 d0 5f be 02 3c 43 dc
        c2 f6 3a a2 75 7f 9c 0e 0f 9a c9 aa 74 f7 d2 25 49 dd 94 3f 75 95 de 1f
        69 34 1a 17 35 1a 8d ed d5 6a f5 cc c8 c8 48 65 7c 7c bc d1 0f 81 5e 07
        4e 12 cb ee 77 12 1d ef 97 17 11 e8 ee a5 4b 92 ba 15 e0 d9 db 7a bd fe
        da 71 ea 5c 36 9d 26 fa cb 5e ad d7 eb 67 3e fb d9 cf ae b9 9c dc 33 a3
        d2 d2 b2 fb 32 71 1e fd 21 62 2f 7d b9 a8 27 35 db 4b f7 5c ba 24 a9 93
        05 64 ad 56 a3 5a ad be f6 b6 5a ad 52 a9 54 a8 54 2a 2c 2f 2f b3 bc bc
        fc da ff 6f 34 1a 27 1a 8d c6 8b c0 74 a3 d1 38 e7 ac f7 9e 9a 7d 9a 42
        fd 14 f0 38 f0 20 30 93 2a f7 42 9e 64 03 5d 92 d4 8e 4c 59 d9 a3 95 0f
        ef 2c b4 57 86 77 3e 87 72 59 34 0b 1c 6d 34 1a 8b e7 cb c3 9e 1b 66 7e
        cf 3d f7 2c 01 2f 12 7b e9 47 8a ae d2 9d 1e 27 49 6a 25 c0 f3 21 9e 85
        77 3e c0 b3 1f d7 6a b5 d7 1e e7 28 26 b3 0b cc 0e 03 2f 03 8b 8d 46 e3
        9c 81 3e d6 a3 cf cf 89 54 a5 3f 0b 5c 47 4c cf 29 6c 29 c4 e6 38 49 d2
        6a 39 b1 56 90 e7 f7 c3 b3 80 ce de 66 79 b2 c1 62 b1 41 f4 95 3d 4d 34
        8c 2f ee db b7 af d1 8f 81 be 40 1c a0 7f 00 b8 83 e8 78 df 54 54 95 6e
        c7 bb 24 29 1f c2 2b c3 7b 65 55 be da cf 5f eb 85 c0 3a d5 80 63 44 5f
        d9 ab ac 63 3e 4b 4f de 1f 9a f6 d2 4f 10 e7 d2 9f 23 26 c9 15 f2 81 73
        2f 5d 92 86 37 bc 57 ee 7b 67 cb e7 cb cb cb 6b 36 ae e5 7f 4d 9b b6 6d
        eb c4 6c 96 7b d9 40 3f d9 58 0f 3f b7 0b 69 a9 e1 49 e2 5c fa 45 14 30
        e3 3d 5f a5 7b 5f ba 24 0d 76 e5 bd b2 aa 5e ad a8 cb 57 e1 05 15 7b d5
        54 95 3f 44 f4 94 55 ce b7 dc de b3 15 7a aa d2 ab c0 71 e0 e1 f4 0f 5a
        c4 e9 71 92 a4 16 be af e7 bf b7 67 0d 69 59 e5 bd b2 f3 3c df d0 96 3b
        3e 56 e4 ca ed 7c ca be a7 89 93 5f b5 f5 fc a2 b1 1e ff 38 54 88 51 b0
        cf 02 6f 21 c6 e0 95 8a f8 e0 bb 97 2e 49 fd 1f e2 ab 3d 80 55 97 c7 7b
        64 ab 35 6b 86 fb 26 b1 7f be b0 9e ea bc 1f 02 bd 46 b3 65 7f 86 98 1c
        37 52 c4 27 42 f6 2a ce e9 71 92 d4 3f e1 bd 56 55 be 5a 85 dd a3 bd 52
        15 60 2a e5 de ec 7a ab f3 7e 08 f4 ec d2 96 47 88 bd 84 6b 80 1d 45 55
        e9 d9 27 82 55 ba 24 f5 4e 78 af 7c 7b ae bd ef d5 ba ce 7b dc 22 b1 dd
        7c 8a 38 87 be ee bf f8 68 2f ff ab 0e 1c 38 c0 9e 3d 7b ea e9 15 ca 25
        34 8f b0 15 f6 f7 2e 95 4a 56 e9 92 d4 c5 e0 5e 79 b6 3b 3f 94 65 e5 80
        96 95 f3 d0 fb ed 9f 4d 1c d9 fe 2a f0 2d e0 f8 be 7d fb d6 7d 9d 78 cf
        b7 71 a7 23 6c 47 52 85 fe 08 d1 2c d0 28 ea 13 ca 63 6c 92 d4 f9 ef b5
        e7 9a b6 76 be c6 b5 01 ba 8b 63 11 78 81 b8 a4 6c 8a 0d 4e 4a 1d eb 93
        7f 64 76 84 ed eb c0 1b 28 f0 08 9b 7b e9 92 54 4c 90 af 55 91 e7 2b f6
        41 7e 3a 88 41 32 4f a4 bc db 70 f1 3a da 0f ff ca b4 f4 5e 4b 2f 40 6e
        07 ae 05 b6 16 f5 e7 e7 97 dd 0d 75 49 ba b0 f0 ce af 7c e6 8f 90 e5 97
        d1 57 4e 60 1b 82 30 5f 20 96 da ff 8e 18 7d 3e bf 6f df be 0d 3d 01 63
        7d f4 0f 3e 43 9c 47 bf 0f b8 8d 82 f6 d2 ad d2 25 69 63 df 33 f3 01 be
        5a 25 be d6 ff 1b 62 f5 54 9d 3f 4a 0c 53 3b 4d 0b 37 8d 8e f6 cb bf f6
        c0 81 03 8d d4 20 37 0e dc 4a 41 97 b6 ac ac d2 9d 1e 27 49 67 87 f7 ca
        02 68 b5 c6 b5 7c d3 5a 9f 37 ae 75 c2 22 f0 0d e0 8b a9 3a 3f b3 de b3
        e7 fd 5a a1 67 55 fa d3 e9 f1 46 62 d0 4c e1 55 ba a1 2e 69 d8 03 7c e5
        d9 ee 95 4b ea 86 f5 fa 9f 56 9a 73 db 1f 07 4e 6f 74 a9 bd 5f 03 bd 4a
        74 bc 3f 0e bc 0d b8 0a d8 86 e7 d2 25 a9 63 01 be d6 15 a1 ab 8d c8 36
        c4 37 6c 99 38 77 7e 18 98 66 1d b7 aa ad a5 af 4a cd 74 84 6d 91 38 c2
        f6 68 7a 55 53 e8 11 b6 ac 59 43 92 06 2d bc b3 ef 71 f9 23 61 f9 a3 62
        2b 8f 8d e5 67 9c 5b 91 b7 ac 02 1c 25 c6 bd 5e d0 9d 25 63 7d f8 8f af
        11 f3 6d 1f 01 de 45 0c 9c d9 62 95 2e 49 1b af ba 57 56 e0 f9 f3 dc 6b
        bd 55 fb 3e 1c c4 55 e1 0f a6 0a 7d b1 95 bd f3 be ac d0 53 95 5e 27 e6
        ba 3f 06 7c 37 2d 51 d4 8b fa 42 b0 4a 97 d4 6f 01 be d6 c0 96 fc d0 96
        fc fb 2b a7 af 59 7d 77 cc 02 31 19 ee 3e 62 3b 79 f9 42 7e b3 d1 7e 7c
        06 52 c7 fb 32 31 60 e6 4d c0 65 45 ae 36 78 2e 5d 52 af 56 de 2b 0b 90
        95 fb dd 59 58 af 16 da 2a dc 11 a2 bb fd 4b c0 2b fb f6 ed ab 5c c8 6f
        36 d6 c7 4f c4 34 71 2e fd 10 70 03 b0 89 02 97 dd 3d 97 2e a9 d7 2a f0
        b5 9a d7 5c 3a ef 49 75 e0 39 e0 6b c4 72 fb d2 85 fe 86 fd 1c e8 15 62
        2f fd 2b c0 4d 44 b7 fb a6 a2 be 80 b2 57 b5 1e 61 93 d4 ad f0 5e f9 fd
        68 ad bb bd 0d f0 de fb 50 12 a3 5d 0f 11 b3 db e7 d8 c0 35 a9 6b 19 ed
        d7 67 23 b7 ec 0e 71 0b 5b a1 e3 60 c1 9b d8 24 75 2e b8 f3 01 9e 1f 93
        7a ae a1 2d 76 9b f7 95 e3 c0 b7 89 25 f7 13 fb f6 ed bb e0 40 1f eb f3
        27 64 21 bd ba 79 80 18 07 7b 49 51 2f 52 ec 78 97 d4 ce f0 3e 57 90 af
        ac ce 87 68 c6 f9 a0 5a 26 9a e1 9e 07 66 69 53 63 77 5f af 17 df 73 cf
        3d 35 a2 e5 ff 5b c0 53 c4 fc 5b cf a5 4b ea d9 f0 5e d9 71 9e 9d fb 5e
        ed 8a d0 d5 ce 7d 1b e6 7d af 4e f4 80 7d 97 98 a9 32 4d 1b 96 db 07 a1
        42 87 38 88 ff 0c 71 8c ed 4d c0 0e 0a 68 8e b3 4a 97 d4 6a 90 af fc fe
        b1 5a 51 60 a1 30 d0 d5 f9 cb c4 70 b4 83 c0 f2 85 9c 3d 1f b4 40 af 11
        7b 11 0f 02 77 01 bb 28 78 1c ac 1d ef 92 f2 21 bc d6 fd de ab 35 ae 19
        dc 43 67 8e d8 37 7f 88 98 0e 57 6b d7 6f 3c da ef cf 4c ee ae 74 80 6b
        88 06 b9 8b 28 70 3b c1 73 e9 d2 70 57 dd 6b 9d f5 5e f9 be 8d 6b 43 af
        92 aa f2 2f 10 bd 5f 33 ad 5e c4 32 a8 15 3a c4 9e c4 61 62 1f fd 10 70
        05 05 75 bc 5b a5 4b c3 53 79 af 0c f2 d5 ce 78 3b 59 4d e7 30 03 3c 4c
        9c 3f 6f 5b 33 dc c0 54 e8 b9 2a 7d 19 b8 18 b8 11 b8 3e 05 ba 55 ba a4
        0b 0a f1 d5 ee f8 ce 1a d9 d6 3a 3a 26 ad f6 29 05 3c 0b fc 15 69 6c 79
        3b ab 73 e8 f3 2e f7 bc 34 e3 fd 05 e0 3b c0 29 da b8 2f b1 91 2a dd 2f
        66 a9 3f c3 3b 3b e7 7d be 9b c6 f2 41 6e 25 ae 0d 38 43 ac 20 3f 9d 2a
        f5 b6 67 d4 d8 80 3d 61 53 c4 2d 6c cf 03 57 03 e3 74 a1 e3 dd e9 71 52
        ef 57 dd ab 2d 95 af 35 26 d5 d0 56 1b cc a6 40 3f 09 54 da d5 d9 3e 90
        15 7a aa d2 17 89 86 83 7b 89 fb 65 bb 52 a5 7b 4e 54 ea 9d 00 5f b9 5c
        7e be ca db 4b 4b d4 01 59 9f d7 93 a9 3a af 76 e2 0f 19 1b c0 27 ee 04
        f0 4d e0 dd c4 a5 2d 63 dd f8 e6 e1 5e ba d4 9d ea 3b 5f 55 af d6 b8 96
        7d 8d 4a 45 7d 6a 12 cb ed 4f 13 c7 ab 3b b2 dc 3e a8 81 9e dd 2f 7b 98
        98 1c b7 95 82 97 dd ed 78 97 8a 0b f1 73 3d ce 75 61 89 54 60 75 fe 2a
        f0 04 71 43 e8 52 27 96 db 07 35 d0 6b c4 5e fa 57 88 5b d8 76 52 d0 2d
        6c 56 e9 52 67 ab ef d5 6e 1a 5b ad ea f6 9a 50 f5 90 25 62 3c f9 bd c4
        0a 72 b5 53 7f d0 e8 a0 3d 73 e9 08 5b 9d 38 c0 bf 2b 85 fa 45 45 55 e9
        19 6f 62 93 2e 3c bc b3 0a 3b 3f f3 3c bf bf ed c0 16 f5 b8 2a d1 cf f5
        37 c4 74 b8 53 ed b8 55 6d 98 2a f4 ec 49 7c 99 b8 9a ee 75 a9 4a 2f 7c
        e9 dd 2a 5d 3a ff d7 ca 6a 4b e2 ab 75 9c 7b cb 98 fa d0 32 71 9c fa 15
        62 0b b8 a3 8d da 03 79 be 2a 9d 49 9f 23 ce a4 7f 83 58 82 2f bc e3 dd
        0e 59 e9 7b c3 3b 5f 71 e7 bb ce 2b 95 ca 59 6f f3 e7 c1 3d 3d a2 7e fa
        54 4f 45 e5 02 70 8c b8 38 6c 36 e5 6d 47 03 61 74 50 9f d1 03 07 0e 34
        f6 ec d9 53 05 b6 13 d3 e3 ae a3 c0 bd f4 d7 5e 31 39 3d 4e 86 f8 59 73
        ce 57 9b ba b6 72 c9 dc 17 c2 ea c3 10 cf 82 bc 42 ec 95 3f 4d ec 9b 7f
        9b 98 8f 32 b5 6f df be e5 4e fe 25 c6 06 fc 49 3e 4d 74 16 7e 03 b8 93
        58 76 2f e4 45 cc ca 41 33 06 ba 06 3d b8 57 56 e1 f9 af 83 95 cb e5 36
        ad 69 c0 c2 7c 89 58 09 3e 94 aa f1 67 53 88 3f 47 9c ba 3a 92 7e 4e 47
        0d 7c ca 4c 4e 4e ee 04 7e 14 f8 03 e0 ed 44 83 5c 21 4a a5 12 a3 a3 a3
        8c 8f 8f 33 36 36 e6 a7 bd 06 32 bc 57 06 f9 ca ad 26 b7 9e 34 60 aa c0
        3c b1 ad bb 90 de be 44 f3 58 da 34 b1 67 7e 38 bd 3f 0f 54 db 3d b7 7d
        18 2b 74 d2 93 f9 12 d1 98 70 3b b1 04 df 95 73 e9 8e 84 55 bf 86 77 fe
        c7 ab f5 88 ac 16 ee d2 00 a8 a7 ca 7a 91 58 4a cf 96 d3 0f 12 8d d7 a7
        52 65 fe 3c b1 c4 3e 9d 7e ee 32 d1 b7 55 ef 64 57 fb d0 55 e8 a9 4a df
        05 7c 02 f8 08 d1 f5 be b9 1b 55 fa e8 e8 a8 4b ef ea 9b 00 5f d9 59 be
        5a 15 6e 70 6b c0 c2 bb b6 e2 31 93 aa ed 43 29 ac a7 53 71 f8 24 cd e5
        f5 a5 f4 a8 a4 df 23 db 4f a7 53 03 64 86 b9 42 27 7d 10 fe 15 f8 41 e0
        e6 22 03 dd e9 71 ea f5 00 5f 6b 58 cb b9 82 db 20 d7 a0 7c 09 e4 42 f8
        34 70 9c e8 4c 9f 49 d5 f7 33 c4 5e f8 4b e9 ff 57 88 31 ae f3 a9 12 af
        a5 5f 5f 78 78 0f 73 a0 2f a6 0f cc 53 c0 1b 81 6d 74 61 c6 7b f6 8d d1
        50 57 2f 86 f7 5a ff 4f 1a 50 4b c4 f2 f9 91 14 d2 cf 03 8f a6 0a 7c 96
        d8 1b 3f 91 42 fe 34 b1 77 de 95 ca 7b bd 86 26 59 26 27 27 b7 01 3f 0d
        fc 0a d1 24 b7 b5 c8 7f ff c8 c8 c8 6b cd 71 ee a5 ab 88 f0 5e f9 f6 5c
        63 52 ed 3a d7 80 cb 37 b2 2d a6 f7 0f 11 4b e7 2f a6 00 7f 39 85 fa f1
        54 89 57 7b 35 b8 87 bd 42 cf 5e 8d 3d 98 aa f4 77 a4 40 2f f4 1b 6c 7e
        d9 dd 2a 5d ed 0e ef 73 55 dc 6b 55 e1 d2 00 ca 46 7f 57 88 e6 b4 0a b1
        8c fe 62 0a ed 99 14 da cf a6 3c 38 49 74 ab 57 80 5a bf 85 f8 b0 06 7a
        9d 98 a9 9b 75 26 5e 42 97 ae 56 75 2f 5d ed aa be d7 5a 2a 5f eb b2 12
        69 d0 be 1c 68 ee 63 d7 d2 8f 67 89 db cd 8e a4 ef f5 47 81 c7 89 89 6d
        53 c4 f2 fa 52 ee 51 03 1a fd 1c e4 99 a1 4a 95 c9 c9 c9 71 62 b9 fd 57
        89 e5 f7 1d 45 3e 07 9e 4b 57 ab 01 be da bd de e7 ab ba 0d 71 0d 70 88
        67 45 da 3c cd 7d ee d9 54 7d 3f 97 02 fc a5 f4 df 4e 13 8d d1 b3 e4 3a
        d1 07 21 c0 87 3a d0 53 a8 5f 0f fc 0c f0 db c0 2d 14 3c 0e d6 bd 74 ad
        27 bc 57 0b ed 73 55 dd 86 b7 86 44 85 58 22 3f 46 2c 93 bf 40 0c 74 39
        48 b3 91 6d 8a 66 a7 7a 85 38 0b 3e 14 17 01 0c 63 99 78 1c 78 18 b8 0f
        b8 02 b8 bc c8 17 36 f9 bd 74 03 7d b8 83 7b e5 fb 59 58 af 76 15 a8 7b
        df 1a 42 35 62 79 3c 7f 5c ec 30 31 c0 e5 c5 14 e0 2f a6 8a fc 58 fa 39
        d9 f9 f1 81 ac c0 ad d0 57 af d2 77 01 3f 05 7c 96 98 f1 5e 78 95 3e 36
        36 c6 f8 f8 b8 a1 3e 84 e1 7d ae 0a 3c 1f e8 d2 10 a9 13 9d e8 cb b9 c7
        f1 54 79 1f 4a d5 f6 14 d1 c4 f6 24 cd 46 b6 a5 f4 eb 86 32 c0 ad d0 c3
        74 fa 74 80 44 7b 00 00 12 4e 49 44 41 54 c4 78 1e d8 05 5c 56 f4 37 78
        ef 4b 1f 8e 20 5f b9 54 be 5a f3 da 6a c1 2f 0d f2 97 46 0a f0 7a ee fd
        39 a2 79 ed 68 fa fe 7c 94 38 13 9e 6f 64 5b 4c 21 fe da 40 17 43 dc 40
        27 7d 52 bc 94 3e 59 ee 20 9a e3 c6 8b 0e 74 a7 c7 0d 56 05 be 56 a3 9a
        d3 d6 a4 b3 2a f1 33 a9 c2 3e 91 82 7c 96 58 36 7f 82 e6 b1 b2 b9 f4 73
        a6 19 b0 4e f4 4e 1a da 24 99 9c 9c bc 18 f8 09 e0 93 c0 8f 00 17 17 fa
        c4 a7 8e f7 4d 9b 36 19 ea 7d 1a de 2b 43 7c ad bd 6f c3 5b 43 ae 92 82
        f9 44 2a a6 5e 24 96 cd b3 2e f4 39 e2 88 d9 ab e9 e7 55 0c 70 2b f4 56
        aa f4 47 88 e3 0d 77 d2 a5 71 b0 b5 5a cd 65 f7 3e 08 ee 73 55 e0 0e 6c
        91 5e 53 4b df 5b b3 41 2d 0b 29 a8 9f 21 3a d2 e7 52 35 fe 0c d1 c8 96
        ed 81 67 01 5e f7 29 34 d0 5b 51 25 3a 26 1f 04 de 0c 5c 45 dc 95 de 95
        8e 77 43 bd fb e1 bd 32 c8 cf d7 6d 6e 78 6b c8 65 c3 5c aa b9 b7 c7 89
        65 f3 ec 2e f0 63 a9 1a 7f 32 55 e8 d9 5e f8 32 3d 74 a9 c9 a0 18 ea 04
        99 9c 9c 1c 25 ae 53 fd 15 e0 e3 29 d4 47 8b fc 3b 78 2e bd bb 41 be d6
        3e f7 ca 41 2e ab 85 bf 34 4c 5f 2e b9 b7 d9 63 9e e6 99 ef 69 62 d9 fc
        11 9a 8d 6c f3 a9 42 9f 4f 41 5e c5 46 36 2b f4 0e bf c2 cc 9a e3 0e 01
        3b 81 2d 78 2e 7d 20 2b f0 73 ed 7b e7 bb d0 0d 6f e9 7b c2 7c 91 e6 d4
        b5 a5 f4 e3 47 81 87 38 fb ae f0 63 a9 12 f7 38 99 15 7a 57 aa f4 12 f0
        fd a9 4a ff 10 31 68 a6 d0 64 b5 4a 6f 7f d5 bd 56 80 9f 6b fe b9 a4 d7
        2c 13 fb dd 59 97 f9 61 62 0f fc 68 aa b8 67 89 a3 bf cf a6 9f b3 68 05
        6e a0 f7 4a a8 5f 01 7c 00 f8 f7 c0 8d 14 78 84 0d ce 9e f1 3e 3a 3a ea
        5e 7a 1b 2b ef d5 42 de f0 96 ce 52 cb 55 dd cb e9 fd a3 c4 9c 8e 97 52
        80 bf 90 c2 fb 18 cd eb 47 cf a4 9f 6f 15 de 23 bc 21 24 cc a6 4f dc 57
        81 6b 8b 0e 74 cf a5 b7 16 e2 d9 c0 96 f3 dd 3e 26 a9 f9 25 44 73 3c 6a
        f6 38 45 2c 9b bf 42 9c 01 3f 46 9c 09 7f 2a fd bf 85 dc 23 6b 66 6b 18
        e4 06 7a af 5a 4e af 40 ff 91 98 1c 77 73 d1 ab 17 4e 8f 3b 77 78 3b b0
        45 6a 39 c0 f3 0d 6d d9 ed 64 53 b9 f0 ce 8e ef 1e 4b ff 3f bf 5f 6e 80
        f7 11 53 23 99 9c 9c dc 01 bc 13 f8 23 e0 87 88 23 6c 85 1a d6 19 ef 6b
        5d 40 b2 9e 3d 6f c3 5b 5a 33 c8 97 52 68 67 97 9b 2c a6 ca fb 51 9a f3
        d1 4f 11 2b 93 53 34 f7 c1 0d 6f 2b f4 be 77 86 d8 23 fa 16 70 3d 31 6c
        a6 d0 54 1d 96 2a fd 7c 17 94 ac 15 da 86 b7 74 4e d5 14 de 73 29 9c 5f
        22 56 1e b3 59 e8 73 a9 12 7f 36 05 79 16 e0 35 c3 db 0a 7d 10 ab f4 6d
        a9 3a ff 0c f0 5e 60 7b 37 aa f4 41 ea 78 5f 6b d2 da ca 0b 4b 80 55 8f
        8e 49 5a 55 2d 55 dd 95 dc fb c7 89 b1 aa 2f a7 c0 7e 2c 17 de 4b 29 ec
        b3 46 36 bb d1 ad d0 07 5e 25 7d 41 3c 03 bc 15 d8 da 8d 2a bd df a7 c7
        ad 35 a0 65 b5 ab 42 0d 6f e9 fc 5f 52 34 6f 27 cb a6 b3 4d 13 47 c9 8e
        d0 bc c8 e4 e9 f4 bd eb 78 0a f1 69 72 03 5d 70 29 dd 40 1f c2 57 bd 47
        89 31 85 07 81 2b 53 a8 17 3a 68 26 ab 5e 7b bd e3 7d bd 7b dd 2b 27 ae
        19 e2 d2 ba 42 3c 7b 9b bf 9d 6c 96 68 5e 7b 2c 7d 9f ca 96 d3 17 52 88
        cf a6 c2 64 19 a8 1a de c3 c5 25 f7 15 d2 38 d8 77 00 9f 20 06 cd 5c 51
        74 95 9e 3f 97 3e 36 d6 3b af b9 d6 0a ed 73 dd 32 66 80 4b 1b b2 94 2a
        ee f9 14 cc 4b 29 b8 1f 4f 15 f9 4c 0a f7 43 a9 f8 58 48 85 48 9d 58 46
        f7 72 13 2b 74 e5 d4 89 db 80 1e 04 7e 98 b8 56 75 4b d1 c1 99 3f 97 5e
        f4 5e fa b9 2e 2b 59 6d e6 b9 67 be a5 96 55 53 85 9d 1d 17 7b 99 58 1d
        9c 4a 61 3d 4b 74 a5 3f 9d 82 3c 6b 64 ab 1a de b2 42 5f 5f 95 5e 4a 61
        fe 29 e0 27 e9 c2 38 d8 a2 a6 c7 ad 76 86 7b ad ae f3 b5 ce 7d 4b 5a 97
        ec 46 b2 65 ce be 9d ec 60 aa b8 4f 01 0f 13 fb e0 d9 40 97 6c 22 5b 25
        15 1b ee 81 cb 40 6f 21 d4 77 01 ef 07 7e 17 b8 15 d8 54 f4 df a1 53 e7
        d2 d7 33 d7 7c b5 ca db 20 97 d6 ff 65 46 b3 99 2d 7b 3b 4d 9c f9 3e 4a
        74 9c 9f a0 39 0f 7d 2a 85 f8 89 14 e2 59 23 9b 21 ae 75 73 c9 7d 6d 53
        c4 4d 42 8f 13 fb e8 57 d0 a7 d3 e3 d6 ba 1e 74 ad 73 df 06 b8 74 c1 61
        9e 35 a9 9d 24 f6 c4 a7 d2 f7 92 a7 68 36 b2 65 53 db b2 0b 50 2a d8 c8
        26 2b f4 8e 55 e9 d7 02 1f 21 1a e4 de d8 eb 55 fa f9 2e 2b 59 ad db dc
        d0 96 2e 58 fe 8c 77 35 fd f8 69 a2 99 ed 95 14 d8 27 88 23 b1 47 52 d8
        67 15 78 cd bd 70 59 a1 17 63 06 f8 0e f0 1e e0 96 6e 04 7a d6 1c b7 d6
        3e fa 7a af 08 35 bc a5 b6 59 a6 79 59 c9 12 b1 ff fd 32 b1 1f be 90 2a
        f2 07 53 a8 9f c8 05 b8 03 5d 64 a0 77 f9 95 f7 4b c4 35 82 6f 21 3a de
        0b 5f d5 c8 4f 55 2b 95 4a df d3 a4 b6 b2 da 5e 59 89 4b 6a fd cb 2f 85
        71 76 33 d9 32 cd 89 6c 87 52 f5 fd 10 71 32 26 1b a7 3a 9f 2a f6 a5 f4
        6b 1a 00 06 b9 3a cd 25 f7 f3 98 9c 9c dc 0e fc 04 f0 9b c0 1e 0a 3e c2
        96 19 1d 1d 7d 6d d0 cc 6a c3 5a 56 56 ec 92 5a 92 35 b0 65 61 3e 4b 34
        b1 65 4d 6b 87 89 7d f0 17 52 b0 cf a6 2a 3c bb 99 2c bb 9e d4 46 36 59
        a1 f7 68 95 fe 18 71 c5 e0 9b 89 eb 55 0b 1f b2 be 72 5c aa c1 2d b5 3d
        c8 17 89 6d b6 99 54 65 9f 4a e1 fd 1c b1 f7 7d 32 85 f8 54 0a f2 25 9c
        c8 26 03 bd af d4 d2 17 f3 7d 29 d0 af 48 55 7a e1 1d ef 56 e1 52 5b 5f
        a8 9f a1 39 a8 65 29 05 f7 33 e9 eb 3d ab bc 5f 20 8e 9a cd 11 7b e1 15
        bc 9d 4c 3d ca 25 f7 75 48 83 66 6e 03 3e 46 0c 9b b9 1a 18 2d f4 03 95
        1a e2 f2 7b e8 92 d6 ad 9a c2 7b 29 3d 5e 21 f6 c0 4f d2 6c 64 bb 3f 55
        e4 27 69 1e 23 cb aa 70 97 d0 65 a0 0f 50 a8 5f 02 bc 0f f8 bd 54 a9 6f
        2d fc 83 55 f2 c3 25 ad 43 fe 56 b2 6c 22 db 09 62 22 db 61 56 6f 64 3b
        9d aa f2 ac 62 cf 06 c3 d8 cc a6 be e1 92 fb fa cd a5 6f 08 4f 03 37 01
        9b e9 c2 5e ba a4 ef f1 5a f8 a6 b7 b3 c4 3e f7 54 0a ef 57 d2 d7 6d d6
        c8 36 93 fe df 1c cd 91 aa 35 3c 52 26 2b f4 a1 aa d2 77 03 3f 03 fc 16
        70 3b 30 6e 85 2e 75 55 d6 c8 36 47 ec 89 4f 13 fb e0 f9 46 b6 29 a2 53
        7d 3a fd 7c 27 b2 c9 0a 5d 1c 27 f6 d9 5e 00 ae 05 2e f5 29 91 0a 53 a1
        39 cc a5 96 c2 f9 f9 f4 38 9a 2a f3 e3 c4 6c f4 57 d2 8f b3 8b 4d 9c c8
        26 2b 74 7d 4f 95 7e 1d f0 69 e0 c3 44 a3 5c 61 2f 8a ac d0 35 64 aa 29
        8c b3 c7 11 9a b7 92 2d d0 9c e4 98 5d 2d ba 40 73 8a db 32 e9 3c b9 95
        b8 ac d0 b5 96 19 e0 2b c0 db 81 1b 7c 0e a5 b6 c8 06 ba e4 1b da 4e 12
        93 1a 5f 49 21 fe 20 df db c8 36 4d 73 86 7a b6 97 6e 47 ba 0c 74 ad cb
        22 f0 04 d1 25 7b 27 d1 20 37 ea d3 22 b5 ac 4e 0c 72 39 99 1e 59 23 5b
        36 91 ed 58 fa 6f d9 f9 f0 0a cd ee 75 1b d9 a4 c4 35 dc 16 4c 4e 4e 6e
        06 26 80 5f 03 7e 1c d8 56 c4 73 e9 92 bb 06 44 b6 17 be 90 5e 20 cf 11
        cb e6 cf 12 c7 ca 8e a7 f0 ce 2a f3 6c df 7c d9 f0 96 ac d0 db 6d 99 18
        05 fb 38 f0 2e e2 4c ba 69 2b ad fe b5 92 0d 67 a9 a7 b7 87 53 58 67 c7
        ca 8e a6 af a5 17 52 85 9e 5d 6c 52 b5 91 4d 32 d0 3b ad 41 2c 03 3e 4f
        8c 85 dc 49 9c 4b 97 86 5d 76 23 59 d6 d0 36 95 aa ed 99 f4 e3 79 9a 7b
        e1 47 53 80 67 b3 d3 b3 33 e1 ee 81 4b 2d b0 aa 6c d1 e4 e4 e4 08 f0 36
        e0 97 80 8f 02 97 d3 e1 bd 74 97 dc d5 83 2f 6c b3 47 d6 c8 76 8a e8 44
        3f 9a de 7f 28 55 de d9 65 26 f3 34 2f 37 a9 d0 bc 9a d4 10 97 0c f4 ae
        86 fa 15 c0 7b 81 df 21 ee 4b df 66 a0 6b 88 c2 fc 4c 0a ed e9 f4 78 95
        18 ea 92 6f 64 3b 9c ab ce b3 46 b6 ea be 7d fb 6a 3e 85 52 7b b9 e4 7e
        61 a6 89 ab 55 bf 09 5c 4f dc c2 e6 38 58 0d a2 7c 23 5b 85 d8 e7 7e 96
        d8 76 ca f6 c3 8f 00 2f 13 cb e8 67 52 45 5e 71 1f 5c b2 42 ef 97 2a fd
        32 e0 3d c0 1f 02 6f a5 83 97 b6 58 a1 ab a0 ca bb c6 d9 cb e1 8b 29 ac
        0f 13 97 9c 4c a7 00 7f 34 55 e3 27 68 36 b2 2d e3 51 32 c9 0a bd 4f cd
        d3 1c 3f 79 2b 1d ba 2b dd 30 57 07 d5 72 8f 0a cd f9 e7 33 29 a8 4f 10
        7b e1 cf d3 ec 4c 9f 4d 9f fb d9 18 56 6f 26 93 0c f4 be 57 21 1a 80 9e
        06 ee 22 e6 bb 6f f2 69 51 8f 57 e1 f9 66 b6 53 c4 b2 79 76 13 d9 13 c4
        cd 82 c7 53 78 9f cc 55 e1 af 55 ee 2e a5 4b bd c5 b2 af 0d 26 27 27 b7
        03 ef 26 66 bc df 0d 5c d4 ee e7 d6 0a 5d 6d 0a f2 6c 06 fa 4c aa b2 8f
        11 7b e1 2f a6 00 3f 45 ec 83 9f a2 b9 0f be 94 02 dc ea 5b b2 42 1f 78
        8b c4 7e e2 13 c0 f7 11 dd ee 8e 83 55 b7 2d a7 cf cd c5 f4 fe 69 62 cf
        fb 05 a2 23 7d 2a bd 7d 29 55 e0 67 d2 63 d1 2e 74 c9 0a 7d 98 ab f4 cd
        c0 cf 03 bf 0a fc 30 6d de 4b b7 42 d7 79 2a ef 6c a0 4b 8d 58 46 5f 22
        b6 82 5e 4d 61 3d 93 aa f1 87 53 a0 1f 27 46 ae 66 f7 83 3b d0 45 b2 42
        57 ae 1a fa 0e f0 66 62 2f 7d b3 2f 98 d4 41 f5 5c 78 2f 13 4b e4 d9 1e
        f8 3c 67 37 b2 65 67 c2 67 52 88 2f e5 7e ad 21 2e 59 a1 6b 95 2a 7d 0b
        f0 33 c0 e7 88 41 33 6d 3b c2 66 85 2e ce 6e 64 9b 49 d5 77 36 3a f5 09
        62 e9 3c df c8 76 8c e6 84 b6 6c a0 8b 8d 6c 92 81 ae 75 86 fa 5d c0 2f
        03 1f 07 ae a0 4d 83 66 0c f4 a1 b6 90 82 79 2e 3d a6 88 59 e8 07 d3 fb
        27 d3 fb 27 53 75 be 48 f3 72 13 ab 6f 69 48 b8 e4 de 7e 2f 03 f7 03 3f
        45 1c 61 73 72 9c 36 22 bb 9d ac 92 de 9f 27 3a d0 0f 12 c3 5d a6 88 01
        2f 2f a6 6a 7c 9e 68 64 5b d8 b7 6f 5f d5 a7 4f 32 d0 d5 3e b3 44 d3 d1
        8b c0 b5 c0 b8 4f 89 56 91 35 b2 55 89 25 f4 ac 91 2d 1b a1 7a 2a 7d 2e
        1d 01 be 4b 73 22 db 5c 0a f0 ec 3c b8 03 5d 24 01 2e b9 77 c4 e4 e4 e4
        6e e0 c3 c0 6f 00 77 b6 a3 4a 77 c9 7d 20 d4 69 ee 81 2f d1 6c 64 cb 42
        fa 38 d1 c8 f6 22 cd 89 6c d9 54 b6 45 bc 99 4c 92 15 7a e1 4e 02 f7 02
        3f 92 aa f4 9d 3e 25 43 5f 8d d7 53 70 1f 4d c1 3d 05 3c 49 f3 32 93 d9
        14 f0 47 89 26 b7 6c d9 dd 46 36 49 06 7a 17 2d 12 c7 85 be 0e dc 44 1c
        63 73 d0 cc f0 7d 0e cc e7 1e d3 a9 f2 7e 36 85 f8 11 a2 2b 3d bb 99 6c
        31 17 e0 56 df 92 36 cc 75 dc 0e 49 83 66 ee 02 3e 03 7c 10 b8 f8 42 9e
        6f 97 dc 7b ba fa ce 2e 35 59 26 96 c5 e7 81 43 e9 71 94 d8 fb 7e 35 bd
        c8 3b 9c 2a f4 d3 c4 d5 a2 4e 64 93 64 85 de e3 96 53 35 f6 18 f0 2e 62
        be bb 55 7a ff 87 77 7e a0 4b 3d 05 f9 71 9a c3 5b e6 52 f5 fd 20 cd 89
        6c d9 cd 64 0b e9 f3 c2 81 2e 92 ac d0 fb ac 4a 1f 03 7e 16 f8 24 f0 43
        5c c0 a5 2d 56 e8 5d 0d f1 ec b1 94 42 3b bb 79 6c 81 66 23 5b fe 76 b2
        53 34 2f 37 c9 02 bc ee 5e b8 24 2b f4 fe 55 4b 15 fa 7d c0 1b 88 c9 71
        3e e7 fd a3 4e f3 46 b2 93 29 b0 9f 26 96 d2 4f a5 6a fc 24 b1 8c 3e 93
        02 7e 09 58 36 bc 25 59 a1 0f 5e 95 be 8d 18 32 f3 fb 34 6f 62 db f0 f3
        6e 85 5e 88 0a b1 34 7e 3a 3d 66 52 e5 fd 5c 0a ed 23 e9 c7 27 68 4e 64
        5b c4 46 36 49 06 fa d0 84 fa db 88 33 e9 1f 04 ae a6 85 73 e9 06 7a db
        55 73 8f 7a 0a e6 57 88 ce f3 ac 0b fd 08 d1 99 7e 98 e6 32 fb 12 b1 7c
        6e 80 4b ea 29 2e ff 16 e3 20 f0 15 62 1f fd 72 60 93 4f 49 61 b2 fd ef
        5a ee fd 0a 67 0f 75 59 20 96 d5 1f 04 1e 4f 81 3e 9d fe bb 03 5d 24 19
        e8 7a cd 74 0a 8a c7 80 6b 80 2b 71 75 a4 d3 21 4e 2e bc 67 38 fb bc f7
        71 e0 d1 54 8d 9f a0 79 3b 59 d6 91 be 48 34 b3 19 e0 92 fa 86 a1 52 90
        c9 c9 c9 2b 80 9f 03 3e 4d ec a5 6f e8 08 9b 4b ee eb 96 4d 64 cb 3a ce
        4f 00 cf 10 cb e6 59 23 db 09 9a 8d 6d 59 15 be e4 99 70 49 56 e8 5a 8f
        39 a2 db fd 10 f0 3a da 78 57 fa 90 ab a4 50 ce 6e 1d 9b a5 d9 c8 f6 0a
        31 d0 25 bb d8 24 3b 6a b6 80 23 55 25 19 e8 6a d1 72 0a 98 e7 80 b7 02
        bb 7d 4a 36 24 1b ea 92 ed 67 67 17 9c 1c 21 f6 bc b3 2e f4 57 89 81 3e
        59 23 db 5c aa c0 b3 8b 51 bc 99 4c d2 40 72 1d b7 40 93 93 93 5b 81 1f
        07 3e 05 fc 1b 36 d0 1c 37 84 4b ee 59 00 67 8f 65 be 77 a8 cb 31 e2 6a
        d1 7c 23 5b 7e 22 5b 0d 3b d2 25 59 a1 ab 03 2a c0 23 c0 03 c4 3e fa 6e
        da 70 b5 ea 00 56 e2 d5 54 59 67 d3 d6 16 89 db c9 1e 4b c1 7d 82 68 74
        3b 41 cc 4a 9f 4e 3f af 6a 80 4b 32 d0 55 54 d5 79 0c f8 0e f0 66 e0 0a
        62 2f 7d d8 57 4a 1a 29 b4 67 88 3d f0 29 62 d9 3c 6b 5c cb fe db 41 a2
        1b 3d ab c2 97 f6 ed db 57 f5 d3 4a 92 0c 92 c2 4d 4e 4e 96 80 1b 80 0f
        03 9f 05 ae 5b cf 0b ab 01 5b 72 af a6 d5 8a ec 86 b2 33 c4 11 b2 e7 52
        88 bf 4c 8c 58 3d 4a 2c af 67 0d 6f cb 76 a2 4b 92 81 de 4b a1 be 19 d8
        03 fc 09 f0 36 60 fb 00 87 f9 5a b7 93 65 d7 8a 66 4b e7 df 25 8e 97 bd
        ca d9 4b e8 d9 1e ba cd 6c 92 64 a0 f7 64 a8 bf 35 55 e8 13 c0 55 9c e3
        5c 7a 1f 05 7a 7e a0 4b 7e 2f 7c 3a 05 f7 7c 0a f3 07 81 a7 68 2e a9 9f
        a1 39 b1 6d 19 6f 26 93 a4 0d 73 0f bd 7b 0e 03 5f 05 de 42 8c 83 ed f7
        bb d2 ab 29 b0 67 49 37 8e a5 b0 7e 92 58 3e 3f 4c ec 7f cf a4 ea 3c 0b
        f2 25 c3 5b 92 0c f4 7e 76 8a 58 66 7e 11 b8 11 b8 94 fe 5a 31 c9 ee 07
        9f a3 39 7d ed 05 62 c9 7c 86 d8 fb 3e 4e f3 a6 b2 ac 99 6d d9 a5 73 49
        6a 3f 97 dc bb 68 72 72 f2 2a e0 93 c0 c7 88 e9 71 e3 ab 7e 90 7a 63 c9
        bd 9a aa ee e5 f4 fe 02 b1 64 fe 7c 0a ec 97 89 65 f4 63 a9 4a cf ae 20
        5d 02 6a 86 b8 24 59 a1 0f b2 19 e0 8b c4 b2 fb 4d e9 e3 d1 ed f4 ce f6
        bf b3 26 b6 fc ed 64 c7 68 4e 5f 3b 0e dc 4f 2c a7 bf 9a fe ff 3c cd eb
        48 1b 78 b9 89 24 19 e8 43 a2 92 2a dc 47 81 bb 80 5b ba 10 ea f9 46 b6
        12 cd 46 b6 99 f4 f6 0c 71 06 fc a1 14 de 87 72 e1 9d 75 a3 57 52 15 ee
        5e b8 24 75 89 4b ee 5d 36 39 39 39 06 bc 9b 58 7a 7f 3f 71 84 6d 24 ff
        b1 29 95 4a 8d 0e 7d bc aa 34 3b cc 2b e9 c7 a7 88 a5 f3 6c ef 7b 3a fd
        b7 57 68 8e 5d 5d 34 bc 25 c9 0a 5d 67 ab 11 23 4d 1f 07 ee 06 b6 e5 aa
        e6 76 07 78 d6 c8 96 0d 6b 39 49 0c 74 79 35 85 fa 69 62 59 fd 59 62 4f
        fc 78 fa 6f 15 97 ce 25 c9 0a 5d e7 af d2 37 03 1f 02 3e 47 8c 84 dd 94
        3e 36 a5 5c 85 5e 6a e1 e3 55 a3 d9 cc 56 23 1a d9 5e 21 ba d1 5f 21 46
        a9 3e 45 1c 23 9b a5 d9 b1 be 98 7e be 7b e0 92 64 85 ae 0d a8 10 7b d4
        5f 06 ae 27 ce a5 8f e4 42 7c 3d 15 7b d6 c8 96 bf 9d ec 54 aa b2 4f a6
        a0 9e e2 ec 46 b6 93 a9 02 5f a6 d9 04 e7 e5 26 92 64 85 ae 0b a8 d2 2f
        21 96 dc 7f 2f 55 e9 d9 a5 2d a3 e9 d8 da c8 2a 55 7a 16 bc d9 50 97 99
        5c 85 7d 1c 78 98 e6 50 97 e9 14 de d9 3e f8 12 50 75 2f 5c 92 ac d0 d5
        5e a7 81 27 88 e9 71 d7 02 57 e7 3e 46 a3 29 c8 47 88 a5 f0 ec b2 92 85
        5c 25 fe 34 b1 94 7e 34 05 fb 34 b1 3f 3e 45 9a de e6 c5 26 92 64 85 ae
        62 aa f4 1d c0 3b 81 7d c0 1d 59 a0 97 a2 44 5f a2 79 a4 ec 50 aa ba 4f
        a4 70 9f a2 39 1b 3d fb 6f cb 56 df 92 64 85 ae ee 55 e9 8f 11 f7 a5 cf
        01 5b d2 63 91 e8 3a 3f 45 f3 ae f0 17 d3 fb a7 d3 ff af 90 f6 d0 dd 03
        97 24 2b 74 75 bf 4a 1f 23 9a e2 ae 2c 95 4a d7 02 97 a5 c0 9e a2 79 b9
        c9 7c aa d8 6b 86 b8 24 c9 40 ef 61 7f f6 67 7f 36 da 68 34 b6 01 9b 53
        70 57 d2 a3 6a 78 4b 92 54 80 3f fd d3 3f 2d ad e7 bf 49 92 a4 3e 0b 74
        49 92 d4 9f a1 6e c3 a1 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24
        49 92 24 49 92 24 49 92 24 49 92 24 0d b9 ff 0f ae 2c 1c 2a aa 3f 50 4a
        00 00 00 00 49 45 4e 44 ae 42 60 82""")
    return Photo("oletus lautapelin kuva", 0, "image/png", b)

def add_boardgame_photo_by_boardgame_name(
    boardgame_name: str,
    photo_name: str,
    photo: bytes,
    file_format: str
) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("""
        INSERT INTO photos (boardgame_id, id, name, file_format, photo)
        SELECT
            b.id,
            COALESCE((
                SELECT MAX(p.id) + 1
                FROM photos p
                WHERE p.boardgame_id = b.id
            ), 0),
            ?, ?, ?
        FROM boardgames b
        WHERE b.name = ?;
    """, (photo_name, file_format, photo, boardgame_name))

def delete_boardgame_photo_by_boardgame_id_and_photo_id(
    boardgame_id: int,
    photo_id: int,
) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("DELETE FROM photos WHERE boardgame_id = ? AND id = ?;", (boardgame_id, photo_id))

    conn.write("""
        UPDATE photos
        SET id = id - 1
        WHERE boardgame_id = ? AND id > ?;
    """, (boardgame_id, photo_id))

def get_reviews_by_boardgame_id(
    boardgame_id: int,
    page_num: int
) -> list[Review] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            u.id,
            u.username,
            r.review,
            r.rating,
            CAST(r.rating AS INTEGER) AS stars,
            IIF(
                r.rating - FLOOR(r.rating)
                BETWEEN 0.25 AND 0.75, 1, 0
            ) AS half_star
        FROM ratings r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.boardgame_id = ?
        LIMIT ?
        OFFSET ?;
    """, (
        boardgame_id,
        int(os.getenv("PAGE_SIZE")),
        page_num * int(os.getenv("PAGE_SIZE"))
    ))

    if len(result) > 0:
        return list(
            map(lambda r: Review(
                User(r[0], r[1], None),
                r[2], r[3], r[4], r[5]
            ),
            result))
    return None

def get_number_of_user_ratings(user_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    n = conn.read("SELECT COUNT(*) FROM ratings WHERE user_id = ?", (user_id,))
    return n[0][0]

def get_number_of_boardgame_reviews(boardgame_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    n = conn.read(
        "SELECT COUNT(id) FROM ratings WHERE boardgame_id = ?",
        (boardgame_id,)
    )
    return n[0][0]

def get_user_review_stats(user_id: int) -> tuple[int, int, bool] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            COUNT(r.rating),
            CAST(SUM(r.rating) AS INTEGER) AS stars,
            IIF(
                SUM(r.rating) - FLOOR(SUM(r.rating))
                BETWEEN 0.25 AND 0.75, 1, 0
            ) AS half_star
        FROM ratings r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE u.id = ?;
    """, (user_id,))

    if len(result) > 0:
        return result[0]
    return None

def upsert_review(boardgame_id: int, review: Review) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("""
        INSERT INTO ratings (boardgame_id, user_id, rating, review)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(boardgame_id, user_id) DO UPDATE SET
            rating = excluded.rating,
            review = excluded.review
        WHERE excluded.boardgame_id = ratings.boardgame_id AND
            excluded.user_id = ratings.user_id;
    """, (boardgame_id, review.user.id, review.rating, review.text))

def insert_reservation(
    user_id: int,
    boardgame_id: int,
    start: datetime,
    end: datetime
) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    game_owner = conn.read("""
        SELECT user_games, reserved_user_games, user_id
        FROM users_boardgames
        WHERE user_games - reserved_user_games > 0
          AND boardgame_type = ?
        ORDER BY user_id ASC
        LIMIT 1;
    """, (boardgame_id,))

    if not game_owner:
        return

    conn.write("""
        UPDATE users_boardgames
        SET user_games = ? - 1, reserved_user_games = ? + 1
        WHERE user_id = ?
    """, game_owner[0])

    conn.write("""
        INSERT INTO reservation 
            (start_time, end_time, reserver, game_owner, boardgame_id) 
        VALUES
            (?,?,?,?,?);
    """, (start, end, user_id, game_owner[0][2], boardgame_id))

def has_user_reserved_boardgame(user_id: int, boardgame_id: int) -> bool:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    date = datetime.today()
    reserved = conn.read("""
        SELECT 1
        FROM reservation
        WHERE reserver = ?
            AND boardgame_id = ?
            AND ? BETWEEN start_time AND end_time
    """, (user_id, boardgame_id, date))

    if reserved:
        return True
    return False

def can_be_reserved(boardgame_id: int, start: datetime, end: datetime) -> bool:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    can_reserved = conn.read("""
        SELECT NOT EXISTS (
            SELECT 1
            FROM reservation
            WHERE boardgame_id = ?
            AND NOT (
                end_time <= ?
                OR start_time >= ?
            )
        );
    """, (boardgame_id, start, end))
    return bool(can_reserved[0][0])

def get_boardgame_names_with_user_has_active_reservation(
    user_id: int,
    page_num: int
) -> list[str] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    date = datetime.today()
    reservations = conn.read("""
        SELECT b.name
        FROM reservation r
        LEFT JOIN boardgames b ON b.id = r.boardgame_id
        WHERE ? BETWEEN r.start_time AND r.end_time
            AND r.reserver = ?
        LIMIT ?
        OFFSET ?;
    """,
    (
        date,
        user_id,
        int(os.getenv("PAGE_SIZE")),
        page_num * int(os.getenv("PAGE_SIZE"))
    ))

    if len(reservations) == 0:
        return None
    return [name[0] for name in reservations]

def set_boardgame_returned(boardgame: Boardgame, user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    date = datetime.today()
    conn.write("""
        UPDATE reservation
        SET end_time = ?
        WHERE boardgame_id = ?
            AND reserver = ?
    """, (date, boardgame.id, user_id))

def get_number_of_user_reservations(user_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    date = datetime.today()
    n = conn.read("""
        SELECT COUNT(*)
        FROM reservation
        WHERE reserver = ?
          AND ? BETWEEN start_time AND end_time
    """, (user_id, date))
    return n[0][0]
