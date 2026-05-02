import sqlite3, os
from datetime import datetime
from datatypes import Boardgame, Photo, Review, User, DatabaseError

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
    user = conn.read("SELECT username, password FROM users WHERE id = ?;", (user_id,))

    if len(user) > 0:
        return User(user_id, user[0][0], user[0][1])

    return None

def get_user_by_username(username: str) -> User | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read("SELECT id, password FROM users WHERE username = ?;", (username,))

    if len(user) > 0:
        return User(user[0][0], username, user[0][1])

    return None

def insert_user(username: str, password: str) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if len(username) > 100:
        raise ValueError("username is longer than 100 character")
    conn.write("INSERT INTO users (username, password) VALUES (?,?);", (username, password))

def add_avatar(user_id: int, avatar):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("UPDATE users SET avatar = ? WHERE id = ?;", (avatar, user_id))

def get_avatar_by_username(username: str) -> Photo:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT a.file_format, a.avatar 
        FROM avatars a
        JOIN users u ON u.id == a.user_id
        WHERE u.username = ?; 
    """, (username,))

    if len(result) > 0:
        return Photo(f"{username} avatar", None, result[0], result[1])

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
    return Photo(f"{username} avatar", 0, "image/png", b)


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

def set_user_boardgames_to_zero(user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("""
        UPDATE users_boardgames
        SET user_games = 0
        WHERE user_id == ?;
    """, (user_id,))

def delete_users_boardgames_by_boardgame_id(boardgame_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("DELETE FROM user_boardgames WHERE boardgame_id == ?;", (boardgame_id,))

def get_user_boardgame_ids(user_id: int) -> set[int] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("SELECT boardgame_type FROM users_boardgames WHERE user_id == ?;", (user_id,))

    if len(result) > 0:
        return {value[0] for value in result}
    return None

def insert_boardgame(boardgame_name: str, user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    if len(boardgame_name) > 100:
        raise ValueError("Boardgame's name is longer than 100 character")
    try:
        conn.write("INSERT INTO boardgames (name) VALUES (?);", (boardgame_name,))
        conn.write("""
            INSERT INTO users_boardgames (user_id, boardgame_type, user_games)
            SELECT ?, b.id, 0
            FROM boardgames b
            WHERE b.name = ?
        """, (user_id, boardgame_name))
    except:
        raise DatabaseError

def update_boardgame(boardgame: Boardgame, user_id: int, users_games: int = None) -> None:
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
    """, values)

    if users_games:
        conn.write("""
            UPDATE users_boardgames
            SET user_games = ?
            WHERE user_id = ? AND boardgame_type = ?
        """, (users_games, user_id, boardgame.id))

def delete_boardgame(boardgame: Boardgame, user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("DROP FROM photos WHERE boardgame_id == ?;", (boardgame.id,))
    conn.write("DROP FROM users_boardgames WHERE boardgame_id == ? AND user_id == ?;", (boardgame.id, user_id))
    conn.write("DROP FROM boardgames WHERE boardgame_id == ?;", (boardgame.id, user_id))

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
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star,
            COUNT(p.id) AS number_of_photos
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id == c.id
        LEFT JOIN ratings r ON r.boardgame_id == b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type == b.id
        LEFT JOIN photos p ON p.boardgame_id == b.id
        WHERE b.name = ?
        GROUP BY b.id;
    """, (boardgame_name,))

    if len(result) > 0:
        return Boardgame(boardgame_name, result[0][0], result[0][1], result[0][2], result[0][3], result[0][4], result[0][5], category=result[0][6], stars=result[0][7], half_star=bool(result[0][8]), number_of_photos=result[0][9])
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
            CAST(AVG(r.rating) AS INTEGER) AS stars,
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id == c.id
        LEFT JOIN ratings r ON r.boardgame_id == b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type == b.id
        GROUP BY b.id
        HAVING COALESCE(SUM(ub.user_games), 0) + COALESCE(SUM(ub.reserved_user_games), 0) > 0
        LIMIT ?
        OFFSET ?;
    """, (int(os.getenv("PAGE_SIZE")), page_num * int(os.getenv("PAGE_SIZE"))))

    if len(result) > 0:
        return list(map(lambda result: Boardgame(result[0], result[1], result[2], result[3], result[4], result[5], result[6], category=result[7], stars=result[8], half_star=bool(result[9])), result))
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
            IIF(AVG(r.rating) - FLOOR(AVG(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star,
            p.name,
            p.id
        FROM boardgames b
        LEFT JOIN categories c ON b.category_id == c.id
        LEFT JOIN ratings r ON r.boardgame_id == b.id
        LEFT JOIN users_boardgames ub ON ub.boardgame_type == b.id
        LEFT JOIN photos p ON p.boardgame_id = b.id
        WHERE ub.user_id == ?
        GROUP BY b.id;
        LIMIT ?
        OFFSET ?;
    """, (user_id, int(os.getenv("PAGE_SIZE")), page_num * int(os.getenv("PAGE_SIZE"))))

    if len(result) > 0:
        return list(map(lambda result: Boardgame(result[0], result[1], result[2], result[3], result[4], result[5], result[6], category=result[7], stars=result[8], half_star=bool(result[9])), result))
    return None

def get_number_of_user_boardgames(user_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    n = conn.read("SELECT COUNT(id) FROM users_boardgames WHERE user_id == ?", (user_id,))
    return n[0][0]

def get_all_boardgames_by_search_word(search_word: str, page_num: int) -> list[Boardgame] | None:
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
        GROUP BY b.id
        HAVING COALESCE(SUM(ub.user_games), 0) + COALESCE(SUM(ub.reserved_user_games), 0) > 0;
        LIMIT ?
        OFFSET ?;
    """, (f"%{search_word}%", int(os.getenv("PAGE_SIZE")), page_num * int(os.getenv("PAGE_SIZE"))))

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

def get_boardgame_photo_by_boardgame_name_and_photo_id(name: str, photo_id: int) -> Photo:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT p.name, p.id, p.file_format, p.photo
        FROM photos p
        JOIN boardgames b ON p.boardgame_id == b.id
        WHERE b.name == ? AND p.id == ?;
    """, (name, photo_id))

    if len(result) > 0:
        return Photo(result[0], result[1], result[2], result[3])
    
    b = bytes.fromhex("""
        89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52 00 00 01 f4 00 00 01 f4
        08 06 00 00 00 cb d6 df 8a 00 00 00 01 73 52 47 42 01 d9 c9 2c 7f 00 00
        00 04 67 41 4d 41 00 00 b1 8f 0b fc 61 05 00 00 00 20 63 48 52 4d 00 00
        7a 26 00 00 80 84 00 00 fa 00 00 00 80 e8 00 00 75 30 00 00 ea 60 00 00
        3a 98 00 00 17 70 9c ba 51 3c 00 00 20 00 49 44 41 54 78 da ed dd 67 70
        dd d9 79 df f1 ef 45 61 5d ee 72 7b 21 b7 37 69 25 79 d5 2c b9 4a 5e da
        8a 21 47 b2 5c 24 4b b2 62 b9 48 b6 64 cb 92 e9 32 f6 24 c2 e6 85 60 c7
        6f e2 99 3b 93 cc 64 f2 c6 c9 38 99 c4 93 d1 d8 b1 c7 ce d0 92 65 4a b2
        8a 57 5b b4 bd 37 ee 92 bb 24 c1 02 80 04 d1 6e c9 8b e7 fc f7 fe 09 01
        24 70 71 ef ff b6 ef 67 06 03 70 97 f5 8f f2 c3 73 ce 73 9e 03 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49 92 24 49
        92 24 49 92 24 49 03 ad e4 23 90 34 68 ca e5 f2 79 bf f6 ed dd bb b7 ee
        93 92 81 2e 49 dd 19 e4 bb 81 4f 02 3b 80 73 05 76 15 98 02 ee 07 1e 02
        26 f7 ee dd 5b f3 09 ca 40 97 a4 d6 04 f2 db 80 5b cf 13 c6 ab a9 00 77
        00 7f 04 6c 5f c3 cf 3f 0e fc 33 f0 75 e0 de 14 ec a7 ad dc 65 a0 4b 1a
        f4 30 de 0a ec 06 46 9a fc 2d 86 81 7f 0b 7c 28 55 d0 cd 18 02 46 d7 f8
        b5 af 9e fe 9c 13 29 d4 ff 6b aa d8 a7 ad d6 65 a0 4b ea f5 50 1e 05 36
        35 59 1d bf 1d 28 03 97 36 59 61 03 5c 4e 2c 97 17 a9 06 4c 03 0f a4 bf
        ff bf a4 1f 57 ac d6 65 a0 4b ea d5 40 7f 0f f0 9b a9 5a 5e 8f 3a 70 19
        f0 03 4d fc da 6e 31 03 7c 0b f8 bb 54 b1 3f 0f 9c 31 d4 65 a0 4b 2a 3a
        8c 37 01 1f 05 6e a0 b9 25 eb 5a 0a e4 f7 0f e8 23 ac 03 67 80 c7 81 7b
        80 6f 02 5f 01 8e bb 04 2f 03 5d d2 7a 02 79 17 f0 c6 26 3f 6f eb c0 c5
        c0 bf 07 5e ef d3 dc 70 b0 4f 13 fb e9 7f 91 42 fd f0 de bd 7b ab 3e 1a
        19 e8 52 ff 87 f1 10 b1 ff bb 85 e6 f6 8f ab c0 87 81 71 9a 5f b2 2e 01
        db e8 dd 25 ef 6e ac d6 9f 01 fe 13 f0 4f c0 51 60 de 6a 5d 06 ba d4 fd
        81 dc 6c 77 76 1d b8 04 f8 8f c0 db 88 06 b1 66 7e 8f 4b 81 5d be 37 ba
        2a d4 e7 81 27 80 ff 07 fc 43 7a 7b ca 6a 5d 06 ba d4 bd 81 fe 2e e0 d7
        9a ac 6e eb c0 56 60 4f 0a 76 f5 97 05 e0 65 e0 11 e0 1b c0 5f 01 07 f7
        ee dd 5b f1 d1 c8 40 97 5a 1b c6 a3 c0 4f 13 67 a0 9b 59 0e ad 02 ef 06
        7e c1 a7 a9 73 98 03 9e 02 be 08 fc 35 b1 1c ef d1 36 19 e8 d2 b2 50 de
        06 bc 81 f5 9f 81 ae a5 aa f8 3f 00 df d7 64 a0 67 9f 2b 7e be e8 7c 96
        80 43 c0 9f 03 7f 0f 1c 20 06 d1 58 ad cb 40 57 df 04 f2 05 44 43 56 33
        2a c0 9d c0 7f 06 ae 6c 22 94 87 80 0b 89 09 61 52 bb 55 80 83 44 f7 fb
        df 01 0f 03 af 00 0b 56 eb 6a a7 11 1f 81 d6 18 c8 43 1b f8 e5 43 c0 a7
        68 7e 64 67 3d 05 f2 6d 7e cc aa 47 be ae ee 26 b6 79 de 48 0c a3 f9 1f
        44 c3 dc bc 8f 47 56 e8 ea 64 98 5f 03 7c 06 d8 49 73 4b d6 25 e0 c7 88
        25 73 69 90 2c 11 0d 73 ff 08 fc 4f e0 be 54 a9 7b b4 4d 06 ba 9a 0a e4
        b7 a7 30 6d f6 fc f3 ad c0 ef 03 17 f8 34 a5 75 ab 11 17 bc fc 15 f0 7f
        81 47 89 33 eb 8b 2e c1 cb 40 1f ac 30 de 0a dc 48 ec ff 36 f3 c9 3f 04
        fc 01 f0 11 9a bf a1 aa 44 2c 23 fa f1 22 35 a7 9e 42 fd db c4 99 f5 fb
        89 8e f8 19 43 5d 06 7a ef 04 f2 16 60 f3 06 aa e3 3b 89 49 54 cd 34 83
        65 2e b6 ba 96 ba a2 52 9f 03 8e 10 f7 ab ff 39 f0 1d a2 0b de 50 97 81
        de e5 61 5e 22 6e a6 fa 59 9a 6f 06 db 49 5c 3b 69 33 98 d4 1f b2 3b d6
        ef 03 fe 1b f0 65 e0 b4 47 db 64 a0 b7 37 90 af 04 7e 85 e8 b0 ae 37 f9
        7c df 0b bc c5 a7 29 69 99 d3 c0 d7 80 bf 21 3a e1 0f 00 b3 56 eb 32 d0
        57 0f e5 5d c0 5b 89 bd e4 f5 7e 17 fd 3a e2 32 8c 8b fc 50 91 d4 06 b3
        c0 63 a9 4a ff 4e aa da 0f db 05 af be 0b f4 74 f6 f9 2a 62 20 49 33 df
        b5 56 80 9f 23 ae 8c 6c 66 a8 c8 10 71 3b 96 2b 19 92 da a1 9e 8a 87 69
        62 16 fc 7f 27 06 d2 bc 0a d4 ac d6 55 48 a0 ff e9 9f fe 69 69 64 64 a4
        34 32 32 42 a9 54 aa af f4 81 57 2e 97 87 53 90 36 f3 e7 d4 88 fd e3 3f
        03 de 49 73 37 54 91 aa eb ab 7d 57 4b ea 62 35 1a d7 b1 fe 05 31 0f fe
        04 5e c7 aa 75 68 aa d1 ea 0b 5f f8 c2 16 60 67 a9 54 ca 96 a2 0f 11 fb
        41 cb fd 10 d1 14 d6 cc 9f 53 27 ba c3 7f 14 6f a8 92 d4 df 86 88 93 28
        77 00 1f 4b 5f f3 be 04 3c 59 2e 97 4f 7a 1d ab da 56 a1 7f e1 0b 5f b8
        62 74 74 f4 9d c3 c3 c3 77 8d 8c 8c 6c 1d 1a 1a 9a 04 66 96 fd 7e 55 e0
        07 88 71 9f 92 a4 b5 59 04 5e 22 ce ac df 43 2c c1 3f b7 77 ef de 25 1f
        8d 5a 5e a1 97 4a a5 5b 6a b5 da 07 4a a5 d2 fb 6b b5 da a5 a5 52 69 b8
        54 72 9b 59 92 5a 60 13 70 0b 31 0f fe 2d c4 1c 89 bf 2d 97 cb 4f 01 4b
        2e c1 ab a5 81 0e fc 60 ad 56 7b 3f 50 aa d7 eb f5 52 a9 c4 f0 f0 b0 4f
        53 92 5a 67 33 71 21 d1 af a7 50 ff 0b e0 e5 72 b9 7c 0a ef 59 d7 0a 9a
        bd 41 6b 13 70 41 ad 56 db 5a ab d5 a8 d5 6a d4 eb 7e 6c 49 52 0b 95 d2
        d7 da 5d c4 69 9d df 07 f6 00 d7 01 5b d3 e0 2a 69 c3 15 7a 2d fb 60 ab
        d7 eb f5 6a b5 5a 1b 1a 1a 1a b2 4a 97 a4 96 1b 06 ae 05 7e 32 bd fe 2e
        f0 f7 c4 f8 d8 19 1f 8f 36 1a e8 c3 e9 d7 0e 01 b5 6a b5 ca d0 d0 10 43
        43 43 b8 97 2e 49 6d 09 f5 2b 80 cb 88 65 f8 cb 81 0b cb e5 f2 37 80 93
        8e 8d d5 46 03 7d 14 a8 d6 eb f5 21 80 5a ad 56 af d5 6a 25 ab 74 49 6a
        9b 21 62 ae c6 cf 02 97 12 43 b7 1e 2a 97 cb 07 81 53 1e 6f f3 83 63 23
        4a e9 85 5a ad 46 b5 5a 75 2f 5d 92 da ab 94 82 fc 5d c0 1f 11 4d 73 3f
        0a 5c 95 86 79 c9 40 6f 3e d0 eb f5 7a c9 e6 38 49 2a 34 d4 b7 03 b7 03
        3f 0f fc 0e f0 01 60 77 1a 99 ad 01 34 d2 82 0f aa 2c c1 4b 59 95 5e 2a
        95 dc 4b 97 a4 f6 cb ba e0 2f 4e 01 bf 03 f8 eb b4 04 3f e7 d1 36 2b f4
        a6 82 bd 5e af 93 3a de ad d2 25 a9 58 db 80 77 10 63 63 7f 11 f8 e1 54
        ad 6f f2 d1 58 a1 af b7 4a 07 20 5b 7a b7 4a 97 a4 8e 14 68 af 07 3e 05
        bc 11 f8 47 e0 9f cb e5 f2 73 c0 82 d5 ba 15 fa ba d4 eb 75 6a b5 1a 95
        4a 85 5a cd e9 84 92 d4 81 22 ed 72 e0 3d c0 6f a7 8a fd 75 c0 26 07 d1
        18 e8 4d 87 ba 0d 72 92 d4 11 c3 c0 85 c4 79 f5 5f 00 7e 83 98 09 bf d3
        2e 78 03 bd a9 50 af 54 2a 54 ab 1e 89 94 a4 0e 19 05 6e 06 de 9f 42 fd
        a7 81 d7 95 cb e5 ed 3e 9a fe 34 d2 8e df 74 79 95 ee 5e ba 24 75 cc 2e
        e2 1a eb 5b d2 cb 57 ca e5 f2 03 c4 20 1a 97 51 0d f4 f5 85 ba d3 e3 24
        a9 63 b2 33 eb ef 04 6e 22 e6 c1 8f 00 f7 a5 9b db 6a 06 7b 7f 68 db 00
        82 7a bd 4e b5 5a a5 52 a9 b8 97 2e 49 9d 0f f5 4d c0 55 c0 bf 06 3e 47
        9a 2e 87 0d 73 56 e8 56 e9 92 d4 73 86 89 0b 5e 7e 04 d8 02 7c 15 f8 67
        e0 71 e0 b8 8f c7 40 3f 6f a0 67 b7 b1 b9 97 2e 49 5d e1 62 e0 dd c0 35
        44 e3 dc 97 cb e5 f2 7e 60 72 ef de bd 9e 39 36 d0 57 0f f5 6a b5 ca f0
        f0 b0 55 ba 24 75 8f 4d c0 1d c0 ee 14 ec a3 c0 3f 95 cb e5 49 60 c9 7d
        f5 de d3 f6 21 fe 9e 4b 97 a4 ae 55 22 ce ac bf 0b f8 2c f0 5e a2 13 7e
        87 67 d6 0d f4 55 43 dd 73 e9 92 d4 b5 a1 be 8d 18 17 fb 39 e0 33 c0 4f
        00 d7 94 cb e5 11 1f 8f 81 6e 95 2e 49 bd 65 2b f0 06 62 00 cd 27 89 b3
        eb 37 94 cb e5 51 1f 4d 6f 28 ec bb 2f 3b de 25 a9 27 8a bc dd 44 27 fc
        15 44 27 fc df 94 cb e5 17 f0 3a 56 03 3d 1f e8 59 b7 bb 1d ef 92 d4 d5
        b6 00 77 12 dd f0 a3 c0 7e e0 99 72 b9 7c 02 58 34 d8 bb f7 bb b1 c2 e4
        ab 74 49 52 d7 17 7c d7 12 73 e0 f7 02 1f 00 6e 05 b6 38 88 66 c0 2b 74
        ab 74 49 ea 39 a3 c0 d5 c0 8f 01 d7 13 37 b8 fd 2f 62 10 cd 19 1f cf 00
        07 7a 3e d4 3d 97 2e 49 3d a1 44 2c bd ef 00 76 12 cd 73 ff bb 5c 2e 3f
        02 4c 3b 88 66 c0 03 dd e9 71 92 d4 93 79 71 23 f0 c1 f4 f6 3f 02 0f 95
        cb e5 83 c0 ac fb ea 9d 37 d4 89 3f 34 ab d2 dd 4b 97 a4 9e ab d6 2f 01
        3e 42 0c a2 f9 28 f0 36 e0 a2 72 b9 3c e4 e3 19 d0 40 f7 5c ba 24 f5 6c
        6e 6c 07 de 0a fc 32 f0 5b c0 0f 02 3b 6d 96 1b c0 40 cf 42 dd e9 71 92
        d4 b3 95 fa 56 a2 0b fe 2e ce 9e 2e b7 c9 c7 d3 19 1d 1b eb b7 bc 4a 77
        2f 5d 92 7a b2 28 bc 9c e8 82 1f 4a 01 7f 4f b9 5c 7e 12 38 61 c3 dc 80
        54 e8 cb 43 5d 92 d4 b3 b6 a7 0a fd 13 c0 c7 73 d5 ba 63 63 07 a1 42 cf
        02 bd 5a ad 52 2a 95 ec 78 97 a4 de 36 4a 0c 9e b9 0a 78 5d 0a f9 af 94
        cb e5 43 40 c5 2e f8 3e af d0 ad d2 25 a9 ef 8a c4 9d c0 5b 80 df 06 7e
        3e 85 bb d7 b1 0e 52 a0 57 ab 55 3b de 25 a9 f7 95 80 0b 88 9b db 7e 09
        f8 34 f0 3e e0 96 72 b9 bc c5 c7 d3 de ef a6 3a ce e9 71 92 d4 77 46 81
        ef 03 ae 04 6e 01 6e 06 be 94 1a e6 66 5c 82 ef e3 40 cf aa f4 6c 3f 5d
        92 d4 17 d5 fa 95 c0 bb 81 9b 88 a1 34 5f 06 1e 2d 97 cb 93 c0 bc c1 de
        3a 5d 93 9c 59 95 ee b2 bb 24 f5 5d a8 6f 22 2e 77 f9 28 71 73 db 87 81
        d7 03 db 1c 46 d3 67 15 ba 55 ba 24 f5 7d a8 8f 12 67 d6 7f 00 b8 82 b8
        c5 ed 8b c0 23 c0 29 1f 51 1f 05 7a be 4a cf ae 57 95 24 f5 95 21 e2 d6
        b6 d7 03 db 88 e6 b9 2f 96 cb e5 07 70 10 4d ff 05 ba d3 e3 24 a9 ef 6d
        22 f6 d4 77 00 5b 88 7d f6 07 ca e5 f2 4b c4 cd 6d 06 7b 93 df 2d 75 95
        ac 4a 77 c6 bb 24 f5 b5 61 62 e9 fd 03 c4 05 2f bf 48 dc dc b6 d3 33 eb
        7d 14 e8 9e 4b 97 a4 81 c9 a0 1d c0 9b 89 2b 59 7f 8d d8 63 bf d8 eb 58
        fb 20 d0 97 57 e9 86 ba 24 f5 b5 12 b1 ec 7e 1d f0 e3 c0 a7 80 9f 04 76
        97 cb e5 11 1f cf da 75 e5 c3 ca 57 e9 ce 78 97 a4 81 c9 a3 ab 89 33 eb
        9b 81 dd c0 b7 cb e5 f2 13 44 c3 9c fb b0 e7 b1 ee 7d 8a 89 89 89 51 60
        0f f0 ae b6 7e cb 96 42 3c 0b 74 43 5d 92 06 a6 5a bf 16 b8 81 18 44 53
        03 a6 c6 c6 c6 ce ec db b7 cf 66 b9 f3 3c bc f5 84 79 89 18 bc ff 87 c0
        ef 11 e7 0a db 96 b4 43 43 43 8c 8e 8e 32 32 32 e2 31 36 49 1a 1c f5 14
        e4 27 80 fb 81 bf 04 be 0e 1c c4 9b db 5a 53 a1 ef df bf 9f 3d 7b f6 54
        88 eb f1 6e 22 3a 14 db 9e b4 9e 4b 97 a4 81 2b 36 87 80 ad 29 67 6e 4c
        21 7f 12 38 3d 36 36 56 dd b7 6f 9f a1 be 91 40 4f a1 5e db b3 67 4f 0d
        b8 90 b8 4d 67 4b 3b ab f4 2c d0 5d 76 97 a4 81 0c f6 2d c0 a5 c0 35 c4
        79 f5 cd c0 6c 5a 82 77 5f 3d 9f 95 4d fe ba 97 80 07 80 a3 c0 52 3b ff
        82 59 c7 bb f7 a5 4b d2 c0 da 4a dc dc f6 73 c0 c7 89 b3 eb 5e c7 ba 4c
        b3 5d ee b3 c0 01 e0 71 62 36 ef 25 ed aa d2 9d 1e 27 49 22 56 94 af 21
        56 87 af 4c 21 ff 0f e5 72 f9 69 e0 8c fb ea 4d 2c b9 03 ec df bf bf 9e
        96 dd 87 80 5b 89 e5 90 b6 1f 81 cb 96 dd 0d 75 49 1a 58 a3 29 73 6e 26
        46 c8 ce 10 4b f0 95 b1 b1 b1 da be 7d fb ac d0 9b 90 75 1f de 4f 34 2d
        ec 6e d7 5f 32 7f 2e 7d 78 d8 89 80 92 34 c0 b2 7d f5 1b 80 0f 12 0d da
        fb 81 af 01 cf 13 2b c8 03 69 23 ad e3 0b c4 5e fa b7 d3 43 9c 27 ba 10
        db 1a ea d9 d2 bb 24 69 e0 2b f5 eb 81 bb 80 8f 11 77 ad df 59 2e 97 77
        0c ea 03 69 ba dc 4d 47 d8 aa c4 59 c1 eb 89 b1 7d 3b 68 73 c7 7b 76 57
        ba cb ee 92 64 b5 4e ec a5 5f 4e 1c a7 de 02 cc 8d 8d 8d 4d 8f 8d 8d 2d
        0c da d1 b6 8d ee 7b 57 88 83 fe 0f 03 6f 02 2e a3 8d c3 66 b2 8e 77 97
        dd 25 49 39 9b 81 5b 88 86 b9 9d e9 f5 83 e5 72 f9 08 d1 30 37 10 c7 a4
        36 94 8c 7b f6 ec c9 42 bd 44 74 1d de 44 5c 5a df f6 73 e9 56 e9 92 a4
        7c 34 a4 fc b9 36 85 fb 4e 60 0e 98 19 94 6a 7d 43 81 9e 96 dd b3 87 74
        79 0a f4 cb 36 fa fb 9e 4f b6 ec ee f4 38 49 d2 b2 50 df 9a 72 e8 ba f4
        fa 0c 70 22 0d a2 31 d0 cf 13 ea f5 b4 97 be 0d d8 95 1e 62 21 d3 e3 ac
        d2 25 49 cb 6b 3e e2 38 db 4e 62 e5 f8 62 62 25 b9 ef 2f 78 69 49 25 9d
        e6 bb 0f 13 67 03 6f 03 2e b2 4a 97 24 75 b8 5a df 91 0a cd 4b 52 26 d5
        c6 c6 c6 16 c6 c6 c6 16 fb 31 d8 5b 12 ba b9 a5 f7 0b 81 d7 13 e7 d2 37
        b7 fd db 30 3b de 25 49 e7 ae d6 37 13 13 e6 6e 4b d9 b4 04 9c ea c7 6a
        bd 95 d3 dd 66 80 67 88 71 b0 37 12 4b f0 6d 9b 1e 97 3f 97 6e d7 bb 24
        e9 1c a1 be 8d 98 2c 77 09 31 04 ed 52 e0 9f ca e5 f2 01 fa e8 3a d6 96
        25 61 ba 85 ad 4e 2c 71 64 df 09 8d 5a a5 4b 92 ba 20 d4 87 81 ed 44 a3
        dc d5 c4 3e fb 34 71 1d 6b a5 1f ba e0 5b bd 01 7d 0a 78 02 38 4c 4c 92
        6b 2b 6f 62 93 24 ad 33 d8 77 02 6f 03 3e 44 dc dc 36 06 dc 5c 2e 97 b7
        59 a1 e7 a4 0a bd 4e 2c 6d 5c 4f 74 17 b6 bd 74 b6 e3 5d 92 b4 0e a3 a9
        52 bf 89 58 82 df 04 9c 19 1b 1b 3b 9d 1a e6 0c f4 dc 2d 6c c3 e9 21 ed
        4a 0f aa b0 50 97 24 69 8d f9 b7 9d 58 7e bf 81 38 bf 7e 8a 38 de 56 e9
        c5 86 b9 96 77 93 a5 40 5f a0 71 b0 ff 12 5a bf b4 6f 95 2e 49 da a8 52
        aa d6 2f 4a 45 e8 55 e9 bf 1f 1f 1b 1b 9b ef b5 eb 58 db d1 85 5e 05 8e
        00 ff 42 8c df bb 9a d8 b3 68 5b a8 67 7b e9 43 43 43 76 bc 4b 92 d6 1b
        ea 9b 53 01 9a 4d 99 bb 19 f8 3a f0 08 70 7c 60 2b f4 74 26 bd 42 5c a7
        ba 9d c6 38 d8 91 b6 bf 57 ec 78 97 24 35 67 28 65 d6 55 44 0f d8 85 c0
        52 ba b9 6d b6 17 2a f5 b6 94 b3 29 d4 17 52 88 e7 f7 27 0a b9 5a d5 bd
        74 49 52 93 d5 7a 36 36 f6 da f4 7a 89 d8 57 ef fa 25 f8 76 26 df 12 f0
        12 70 2f 70 08 58 6c e7 3f 24 5b 76 af 56 ab d4 eb 75 3f 2c 25 49 cd 1a
        21 2e 1c db 03 fc 3a f0 51 e0 76 e0 82 72 b9 dc b5 fb ba 6d fb 8b e5 c6
        c1 6e 21 96 dd 77 11 d3 7a da fb ed 95 55 ba 24 a9 35 05 ef 16 a2 b1 fb
        da f4 32 04 4c 8f 8d 8d 9d ea c6 41 34 ed 4e bd b9 54 a5 3f 44 0c 9b 59
        b2 4a 97 24 f5 88 12 31 fd f4 76 e0 bd c0 bf 01 de 07 dc 5a 2e 97 47 ba
        ed 2f db d6 a5 83 34 0e b6 96 2a f3 db 88 fd f4 cd 45 fc c3 ac d2 25 49
        2d cc ca 0b 52 86 65 4d de a7 d3 20 9a a5 6e d9 57 2f 22 f1 e6 80 17 d3
        cb 34 d0 d6 c3 fa f9 4b 5b ac d2 25 49 2d ae d6 bf 1f f8 25 e0 97 81 77
        02 57 95 cb e5 cd dd f0 17 6c fb e6 7e da 47 5f 22 8e 02 5c 47 34 1a 8c
        e0 f4 38 49 52 ef 85 fa 08 31 88 e6 7a 62 d6 ca 16 e2 3a d6 a9 4e 77 c1
        b7 3d d0 73 e3 60 b7 a4 07 70 43 7a db 19 ef 92 a4 5e 0d f5 ed c4 ad a2
        bb 89 e5 f8 d3 c0 b1 7d fb f6 2d 75 ea 2f 56 d4 a6 7e 05 78 01 38 00 cc
        12 67 fb da ca e9 71 92 a4 36 17 c4 3b 81 37 a5 40 df 09 5c 5a 2e 97 bf
        03 1c dd bb 77 6f e1 b3 e0 8b 0a f4 1a 30 09 3c 07 1c 4c df d5 0c b5 b3
        4a cf 07 ba 55 ba 24 a9 4d 36 03 b7 a6 40 bf 32 bd dc 53 2e 97 5f 04 4e
        ed dd bb b7 b0 66 ae 42 4a d7 74 26 bd 9a fe bc 4b 88 7d 87 6d 14 d0 94
        e7 b9 74 49 52 9b 0d 11 d3 50 77 03 6f 20 ae 0e 3f 0d 9c 48 d7 b1 16 12
        ea 85 ad 45 a7 bd f4 c5 f4 8f be 89 68 8e db 54 c4 9f ed 8c 77 49 52 01
        a1 be 89 46 c3 dc 65 c0 14 70 64 6c 6c 6c a1 88 66 b9 a2 cb d6 29 e0 51
        e0 9b c0 31 e2 66 b6 b6 ca 1f 63 93 24 a9 9d f5 63 0a f5 ab 81 bb 88 b1
        b1 ef 07 ae 2f 62 10 4d a1 dd 62 69 d0 cc 62 fa 46 e2 36 62 2f bd 90 f3
        7b 56 e9 92 a4 02 83 7d 7b 0a f6 cb 89 f3 eb a5 b1 b1 b1 33 63 63 63 73
        ed 5a 82 ef c4 c6 f2 29 e0 09 e0 7e e0 28 6d 1e 34 93 55 e9 d5 6a d5 2a
        5d 92 54 a4 1d c0 8f 00 9f 4c 2f 77 01 57 b6 ab 5a 2f fc 3c 57 aa d2 b3
        a5 f6 1b 81 6b 28 68 2f dd 8e 77 49 52 c1 95 fa 70 0a f6 eb 53 de cd 02
        93 a9 5a af b7 72 6f bd 53 ad df 67 52 95 fe 08 70 04 68 7b 07 a0 55 ba
        24 a9 43 a1 3e 42 1c 6b fb 7e e0 d3 c0 47 80 3b 80 ad e5 72 b9 65 15 66
        47 26 ae e4 c6 c1 6e 23 ae 55 bd 96 82 c7 c1 5a a5 4b 92 0a 0e f6 cd c0
        a5 c4 de fa 55 c4 d4 d4 d9 b1 b1 b1 d3 fb f6 ed db 70 b5 d9 91 40 4f e7
        d2 6b 44 97 fb 55 c4 a1 fc 0b f0 5c ba 24 a9 bf 8d 12 0d e1 37 a4 60 1f
        06 8e a7 3b d6 37 74 f2 ab 63 33 51 53 95 be 40 9c d5 bb 35 fd 03 0b a9
        d2 ed 78 97 24 75 d0 10 8d 15 ea dd c4 8a f5 89 74 1d 6b a5 d9 7d f5 8e
        05 7a aa d2 2b c0 85 c4 2d 6c d7 11 43 67 ac d2 25 49 fd 2e db 5b bf 18
        b8 39 e5 df 2c 30 33 36 36 56 69 a6 61 ae a3 b7 96 a4 e9 71 43 c4 38 d8
        3b 88 09 3b 85 cc 97 2f 95 4a af bd 48 92 d4 c1 50 bf 30 55 eb 37 a4 b7
        4f 03 d3 fb f6 ed ab ac b7 ec ef b4 49 e0 31 e0 f9 f4 dd 49 61 1d ef f5
        7a 9d 7a bd ee 87 94 24 a9 93 46 53 98 df 05 7c 94 e8 82 7f 53 b9 5c de
        d6 33 15 7a aa d2 17 53 95 7e 55 fa 07 5d 54 d4 df cb bd 74 49 52 17 55
        eb 9b 89 be b2 ab d2 8f 4f 8d 8d 8d 9d 5a eb 2c f8 ae b8 28 3c 35 c8 8d
        12 f7 ca 5e 95 de 2e 44 16 e8 86 ba 24 a9 0b 42 7d 98 18 1b bb 8b d8 57
        3f 43 ec ab 2f 8d 8d 8d d5 ce 15 ec 23 5d f2 8f 98 25 ee 4a 7f 15 98 23
        ba ff da 2a 7f 69 8b 55 ba 24 a9 4b 64 57 b1 ee 02 de 9d c2 fd 4a e0 5b
        c0 4b c0 e2 b9 7e 61 37 58 22 26 c6 dd 0b 1c 00 2a 45 fc a1 4e 8f 93 24
        75 71 a8 df 08 bc 23 bd 5c 0f ec 28 97 cb 43 5d 1d e8 77 df 7d 77 9d b8
        b4 e5 3b 44 83 dc 14 05 35 c7 65 55 ba a1 2e 49 ea 22 d9 d2 fb 0d f5 7a
        fd d6 6a b5 7a 51 ad 56 1b 2d 9d 63 39 79 a4 8b fe f2 8b c0 33 c4 2d 6c
        af 23 5a f7 47 69 f3 a0 99 ac 4a 77 2f 5d 92 d4 49 f9 53 57 e9 ed a1 7a
        bd 7e 41 bd 5e df 5e a9 54 ce 0c 0d 0d 2d 8e 8e 8e d6 7b 21 d0 6b c0 09
        62 d9 fd 76 a2 e3 fd d2 22 02 dd bd 74 49 52 a7 02 3c 7b 5d ab d5 5e 3b
        4e 9d cb a6 d3 44 7f d9 ab b5 5a ed cc 67 3f fb d9 55 97 93 bb 66 54 5a
        5a 76 5f 22 ce a3 3f 44 ec a5 2f 15 f5 50 b3 bd 74 cf a5 4b 92 da 59 40
        56 ab 55 2a 95 ca 6b af 2b 95 0a 8b 8b 8b 2c 2e 2e b2 b4 b4 c4 d2 d2 d2
        6b ff bf 5e af 1f af d7 eb 2f 02 53 f5 7a fd 9c b3 de bb 6a f6 69 0a f5
        93 c0 e3 c0 83 c0 74 aa dc 0b 79 c8 06 ba 24 a9 15 99 b2 bc 47 2b 1f de
        59 68 2f 0f ef 7c 0e e5 b2 68 06 38 52 af d7 e7 cf 97 87 5d 37 cc fc ee
        bb ef 5e 00 5e 24 f6 d2 0f 17 5d a5 3b 3d 4e 92 d4 4c 80 e7 43 3c 0b ef
        7c 80 67 3f ae 56 ab af bd 9c a3 98 cc 2e 30 3b 04 bc 0c cc d7 eb f5 73
        06 fa 48 97 3e 9f e3 a9 4a 7f 16 b8 86 98 9e 53 d8 52 88 cd 71 92 a4 95
        72 62 b5 20 cf ef 87 67 01 9d bd ce f2 64 9d c5 62 9d e8 2b 7b 9a 68 18
        9f 1f 1f 1f af f7 62 a0 cf 11 07 e8 1f 00 6e 23 3a de 37 15 55 a5 db f1
        2e 49 ca 87 f0 f2 f0 5e 5e 95 af f4 f3 57 fb 46 60 8d aa c0 51 a2 af ec
        55 d6 30 9f a5 2b ef 0f 4d 7b e9 c7 89 73 e9 cf 11 93 e4 0a 79 c7 b9 97
        2e 49 83 1b de cb f7 bd b3 e5 f3 a5 a5 a5 55 1b d7 f2 bf a6 45 db b6 35
        62 36 cb 3d ac a3 9f 6c a4 8b 9f ed 5c 5a 6a 78 92 38 97 7e 01 05 cc 78
        cf 57 e9 de 97 2e 49 fd 5d 79 2f af aa 57 2a ea f2 55 78 41 c5 5e 25 55
        e5 0f 11 3d 65 8b e7 5b 6e ef da 0a 3d 55 e9 15 e0 18 f0 70 fa 07 cd e3
        f4 38 49 52 13 5f d7 f3 5f db b3 86 b4 ac f2 5e de 79 9e 6f 68 cb 1d 1f
        2b 72 e5 76 36 65 df d3 c4 c9 af ea 5a 7e d1 48 97 bf 1f 16 89 51 b0 cf
        02 6f 26 c6 e0 95 8a 78 e7 bb 97 2e 49 bd 1f e2 2b bd 00 2b 2e 8f 77 c9
        56 6b d6 0c f7 2d 62 ff 7c 6e 2d d5 79 2f 04 7a 95 46 cb fe 34 31 39 6e
        a8 88 0f 84 ec bb 38 a7 c7 49 52 ef 84 f7 6a 55 f9 4a 15 76 97 f6 4a 2d
        02 93 29 f7 66 d6 5a 9d f7 42 a0 67 97 b6 3c 42 ec 25 5c 05 ec 28 aa 4a
        cf 3e 10 ac d2 25 a9 7b c2 7b f9 eb 73 ed 7d af d4 75 de e5 e6 89 ed e6
        93 c4 39 f4 35 ff c5 87 bb f9 5f b5 7f ff 7e f6 ec d9 53 4b df a1 5c 44
        e3 08 5b 61 7f ef 52 a9 64 95 2e 49 1d 0c ee e5 67 bb f3 43 59 96 0f 68
        59 3e 0f bd d7 fe d9 c4 91 ed af 01 df 06 8e 8d 8f 8f af f9 3a f1 ae 6f
        e3 4e 47 d8 0e a7 0a fd 11 a2 59 a0 5e d4 07 94 c7 d8 24 a9 fd 5f 6b cf
        35 6d ed 7c 8d 6b 7d 74 17 c7 3c f0 02 71 49 d9 24 eb 9c 94 3a d2 23 ff
        c8 ec 08 db 37 80 3b 28 f0 08 9b 7b e9 92 54 4c 90 af 56 91 e7 2b f6 7e
        7e 1c c4 20 99 27 52 de ad bb 78 1d ee 85 7f 65 5a 7a af a6 6f 40 6e 05
        ae 06 b6 16 f5 e7 e7 97 dd 0d 75 49 da 58 78 e7 57 3e f3 47 c8 f2 cb e8
        cb 27 b0 0d 40 98 cf 11 4b ed 7f 4b 8c 3e 9f 1d 1f 1f 5f d7 03 18 e9 a1
        7f f0 19 e2 3c fa 7d c0 2d 14 b4 97 6e 95 2e 49 eb fb 9a 99 0f f0 95 2a
        f1 d5 fe df 00 ab a5 ea fc 51 62 98 da 69 9a b8 69 74 b8 57 fe b5 fb f7
        ef af a7 06 b9 51 e0 66 0a ba b4 65 79 95 ee f4 38 49 3a 3b bc 97 17 40
        2b 35 ae e5 9b d6 7a bc 71 ad 1d e6 81 6f 02 5f 4a d5 f9 99 b5 9e 3d ef
        d5 0a 3d ab d2 9f 4e 2f 6f 20 06 cd 14 5e a5 1b ea 92 06 3d c0 97 9f ed
        5e be a4 6e 58 af fd b1 d2 98 db fe 38 70 7a bd 4b ed bd 1a e8 15 a2 e3
        fd 71 e0 ad c0 15 c0 36 3c 97 2e 49 6d 0b f0 d5 ae 08 5d 69 44 b6 21 be
        6e 4b c4 b9 f3 43 c0 14 6b b8 55 6d 35 3d 55 6a a6 23 6c f3 c4 11 b6 47
        d3 77 35 85 1e 61 cb 9a 35 24 a9 df c2 3b fb 1a 97 3f 12 96 3f 2a b6 fc
        d8 58 7e c6 b9 15 79 d3 16 81 23 c4 b8 d7 0d dd 59 32 d2 83 ff f8 2a 31
        df f6 11 e0 9d c4 c0 99 2d 56 e9 92 b4 fe aa 7b 79 05 9e 3f cf bd da 6b
        b5 ee dd 41 5c 15 fe 60 aa d0 e7 9b d9 3b ef c9 0a 3d 55 e9 35 62 ae fb
        63 c0 77 d3 12 45 ad a8 4f 04 ab 74 49 bd 16 e0 ab 0d 6c c9 0f 6d c9 bf
        bd 7c fa 9a d5 77 db cc 11 93 e1 ee 23 b6 93 97 36 f2 9b 0d f7 e2 13 48
        1d ef 4b c4 80 99 37 02 97 14 b9 da e0 b9 74 49 dd 5a 79 2f 2f 40 96 ef
        77 67 61 bd 52 68 ab 70 87 89 ee f6 2f 03 af 8c 8f 8f 2f 6e e4 37 1b e9
        e1 07 31 45 9c 4b 3f 08 5c 07 6c a2 c0 65 77 cf a5 4b ea b6 0a 7c b5 e6
        35 97 ce bb 52 0d 78 0e f8 3a b1 dc be b0 d1 df b0 97 03 7d 91 d8 4b ff
        2a 70 03 d1 ed be a9 a8 4f a0 ec bb 5a 8f b0 49 ea 54 78 2f ff 7a b4 da
        dd de 06 78 f7 bd 2b 89 d1 ae 07 89 d9 ed a7 58 c7 35 a9 ab 19 ee d5 a7
        91 5b 76 87 b8 85 ad d0 71 b0 e0 4d 6c 92 da 17 dc f9 00 cf 8f 49 3d d7
        d0 16 bb cd 7b ca 31 e0 3b c4 92 fb f1 f1 f1 f1 0d 07 fa 48 8f 3f 90 b9
        f4 dd cd 03 c4 38 d8 8b 8a fa 26 c5 8e 77 49 ad 0c ef 73 05 f9 f2 ea 7c
        80 66 9c f7 ab 25 a2 19 ee 79 60 86 16 35 76 f7 f4 7a f1 dd 77 df 5d 25
        5a fe bf 0d 3c 45 cc bf f5 5c ba a4 ae 0d ef e5 1d e7 d9 b9 ef 95 ae 08
        5d e9 dc b7 61 de f3 6a 44 0f d8 77 89 99 2a 53 b4 60 b9 bd 1f 2a 74 88
        83 f8 cf 10 c7 d8 de 08 ec a0 80 e6 38 ab 74 49 cd 06 f9 f2 af 1f 2b 15
        05 16 0a 7d 5d 9d bf 4c 0c 47 3b 00 2c 6d e4 ec 79 bf 05 7a 95 d8 8b 78
        10 b8 13 d8 45 c1 e3 60 ed 78 97 94 0f e1 d5 ee f7 5e a9 71 cd e0 1e 38
        a7 88 7d f3 87 88 e9 70 d5 56 fd c6 c3 bd fe 64 72 77 a5 03 5c 45 34 c8
        5d 40 81 db 09 9e 4b 97 06 bb ea 5e ed ac f7 f2 b7 6d 5c 1b 78 8b a9 2a
        ff 22 d1 fb 35 dd ec 45 2c fd 5a a1 43 ec 49 1c 22 f6 d1 0f 02 97 51 50
        c7 bb 55 ba 34 38 95 f7 f2 20 5f e9 8c b7 93 d5 74 0e d3 c0 c3 c4 f9 f3
        96 35 c3 f5 4d 85 9e ab d2 97 80 0b 81 eb 81 6b 53 a0 5b a5 4b da 50 88
        af 74 c7 77 d6 c8 b6 da d1 31 69 a5 0f 29 e0 59 e0 2f 49 63 cb 5b 59 9d
        43 8f 77 b9 e7 a5 19 ef 2f 00 f7 02 27 69 e1 be c4 7a aa 74 3f 99 a5 de
        0c ef ec 9c f7 f9 6e 1a cb 07 b9 95 b8 d6 e1 0c b1 82 fc 74 aa d4 5b 9e
        51 23 7d f6 c0 26 89 5b d8 9e 07 ae 04 46 e9 40 c7 bb d3 e3 a4 ee af ba
        57 5a 2a 5f 6d 4c aa a1 ad 16 98 49 81 7e 02 58 6c 55 67 7b 5f 56 e8 a9
        4a 9f 27 1a 0e ee 21 ee 97 ed 48 95 ee 39 51 a9 7b 02 7c f9 72 f9 f9 2a
        6f 2f 2d 51 1b 64 7d 5e 4f a6 ea bc d2 8e 3f 64 a4 0f 1f dc 71 e0 5b c0
        bb 88 4b 5b 46 3a f1 c5 c3 bd 74 a9 33 d5 77 be aa 5e a9 71 2d fb 1c 95
        8a fa d0 24 96 db 9f 26 8e 57 b7 65 b9 bd 5f 03 3d bb 5f f6 10 31 39 6e
        2b 05 2f bb db f1 2e 15 17 e2 e7 7a 39 d7 85 25 52 81 d5 f9 ab c0 13 c4
        0d a1 0b ed 58 6e ef d7 40 af 12 7b e9 5f 25 6e 61 db 49 41 b7 b0 59 a5
        4b ed ad be 57 ba 69 6c a5 aa db 6b 42 d5 45 16 88 f1 e4 f7 10 2b c8 95
        76 fd 41 c3 fd f6 e4 d2 11 b6 1a 71 80 7f 57 0a f5 0b 8a aa d2 33 de c4
        26 6d 3c bc b3 0a 3b 3f f3 3c bf bf ed c0 16 75 b9 0a d1 cf f5 d7 c4 74
        b8 93 ad b8 55 6d 90 2a f4 ec 21 be 4c 5c 4d f7 ba 54 a5 17 be f4 6e 95
        2e 9d ff 73 65 a5 25 f1 95 3a ce bd 65 4c 3d 68 89 38 4e fd 0a b1 05 dc
        d6 46 ed be 3c 5f 95 ce a4 9f 22 ce a4 7f 93 58 82 2f bc e3 dd 0e 59 e9
        7b c3 3b 5f 71 e7 bb ce 17 17 17 cf 7a 9d 3f 0f ee e9 11 f5 d2 87 7a 2a
        2a e7 80 a3 c4 c5 61 33 29 6f db 1a 08 c3 fd fa 44 f7 ef df 5f df b3 67
        4f 05 d8 4e 4c 8f bb 86 02 f7 d2 5f fb 8e c9 e9 71 32 c4 cf 9a 73 be d2
        d4 b5 e5 4b e6 7e 23 ac 1e 0c f1 2c c8 17 89 bd f2 a7 89 7d f3 ef 10 f3
        51 26 c7 c7 c7 97 da f9 97 18 e9 f3 87 7c 9a e8 2c fc 26 70 3b b1 ec 5e
        c8 37 31 cb 07 cd 18 e8 ea f7 e0 5e 5e 85 e7 3f 0f 96 2f 97 db b4 a6 3e
        0b f3 05 62 25 f8 60 aa c6 9f 4d 21 fe 1c 71 ea ea 70 fa 39 6d d5 f7 29
        33 31 31 b1 13 f8 51 e0 f7 81 b7 11 0d 72 85 28 95 4a 0c 0f 0f 33 3a 3a
        ca c8 c8 88 1f f6 ea cb f0 5e 1e e4 cb b7 9a dc 7a 52 9f a9 00 b3 c4 b6
        ee 5c 7a fd 12 8d 63 69 53 c4 9e f9 a1 f4 f6 2c 50 69 f5 dc f6 41 ac d0
        49 0f f3 25 a2 31 e1 56 62 09 be 23 e7 d2 1d 09 ab 5e 0d ef fc 8f 57 ea
        11 59 29 dc a5 3e 50 4b 95 f5 3c b1 94 9e 2d a7 1f 20 1a af 4f a6 ca fc
        79 62 89 7d 2a fd dc 25 a2 6f ab d6 ce ae f6 81 ab d0 53 95 be 0b f8 38
        f0 61 a2 eb 7d 73 27 aa f4 e1 e1 61 97 de d5 33 01 be bc b3 7c a5 2a dc
        e0 56 9f 85 77 75 d9 cb 74 aa b6 0f a6 b0 9e 4a c5 e1 93 34 96 d7 17 d2
        cb 62 fa 3d b2 fd 74 da 35 40 66 90 2b 74 d2 3b e1 5f 80 1f 04 6e 2c 32
        d0 9d 1e a7 6e 0f f0 d5 86 b5 9c 2b b8 0d 72 f5 cb a7 40 2e 84 4f 03 c7
        88 ce f4 e9 54 7d 3f 43 ec 85 bf 94 fe ff 22 31 c6 75 36 55 e2 d5 f4 eb
        0b 0f ef 41 0e f4 f9 f4 8e 79 0a 78 03 b0 8d 0e cc 78 cf be 30 1a ea ea
        c6 f0 5e ed ff 49 7d 6a 81 58 3e 3f 9c 42 fa 79 e0 d1 54 81 cf 10 7b e3
        c7 53 c8 9f 26 f6 ce 3b 52 79 af d5 c0 24 cb c4 c4 c4 36 e0 a7 81 5f 21
        9a e4 b6 16 f9 ef 1f 1a 1a 7a ad 39 ce bd 74 15 11 de cb 5f 9f 6b 4c aa
        5d e7 ea 73 f9 46 b6 f9 f4 f6 41 62 e9 fc c5 14 e0 2f a7 50 3f 96 2a f1
        4a b7 06 f7 a0 57 e8 d9 77 63 0f a6 2a fd ed 29 d0 0b fd 02 9b 5f 76 b7
        4a 57 ab c3 fb 5c 15 f7 6a 55 b8 d4 87 b2 d1 df 8b 44 73 da 22 b1 8c fe
        62 0a ed e9 14 da cf a6 3c 38 41 74 ab 2f 02 d5 5e 0b f1 41 0d f4 1a 31
        53 37 eb 4c bc 88 0e 5d ad ea 5e ba 5a 55 7d af b6 54 be da 65 25 52 bf
        7d 3a d0 d8 c7 ae a6 1f cf 10 b7 9b 1d 4e 5f eb 8f 00 8f 13 13 db 26 89
        e5 f5 85 dc 4b 15 a8 f7 72 90 67 06 2a 55 26 26 26 46 89 e5 f6 5f 25 96
        df 77 14 f9 0c 3c 97 ae 66 03 7c a5 7b bd cf 57 75 1b e2 ea e3 10 cf 8a
        b4 59 1a fb dc 33 a9 fa 7e 2e 05 f8 4b e9 bf 9d 26 1a a3 67 c8 75 a2 f7
        43 80 0f 74 a0 a7 50 bf 16 f8 19 e0 b7 80 9b 28 78 1c ac 7b e9 5a 4b 78
        af 14 da e7 aa ba 0d 6f 0d 88 45 62 89 fc 28 b1 4c fe 02 31 d0 e5 00 8d
        46 b6 49 1a 9d ea 8b c4 59 f0 81 b8 08 60 10 cb c4 63 c0 c3 c0 7d c0 65
        c0 a5 45 7e 63 93 df 4b 37 d0 07 3b b8 97 bf 9d 85 f5 4a 57 81 ba f7 ad
        01 54 25 96 c7 f3 c7 c5 0e 11 03 5c 5e 4c 01 fe 62 aa c8 8f a6 9f 93 9d
        1f ef cb 0a dc 0a 7d e5 2a 7d 17 f0 53 c0 67 89 19 ef 85 57 e9 23 23 23
        8c 8e 8e 1a ea 03 18 de e7 aa c0 f3 81 2e 0d 90 1a d1 89 be 94 7b 39 96
        2a ef 83 a9 da 9e 24 9a d8 9e a4 d1 c8 b6 90 7e dd 40 06 b8 15 7a 98 4a
        1f 18 cf 99 26 7c 00 00 12 a6 49 44 41 54 cf 03 bb 80 4b 8a fe 02 ef 7d
        e9 83 11 e4 cb 97 ca 57 6a 5e 5b 29 f8 a5 7e fe d4 48 01 5e cb bd 7d 8a
        68 5e 3b 92 be 3e 1f 21 ce 84 e7 1b d9 e6 53 88 bf 36 d0 c5 10 37 d0 49
        1f 14 2f a5 0f 96 db 88 e6 b8 d1 a2 03 dd e9 71 fd 55 81 af d6 a8 e6 b4
        35 e9 ac 4a fc 4c aa b0 8f a7 20 9f 21 96 cd 9f a0 71 ac ec 54 fa 39 53
        f4 59 27 7a 3b 0d 6c 92 4c 4c 4c 5c 08 fc 04 f0 09 e0 47 80 0b 0b 7d f0
        a9 e3 7d d3 a6 4d 86 7a 8f 86 f7 f2 10 5f 6d ef db f0 d6 80 5b 4c c1 7c
        3c 15 53 2f 12 cb e6 59 17 fa 29 e2 88 d9 ab e9 e7 2d 1a e0 56 e8 cd 54
        e9 8f 10 c7 1b 6e a7 43 e3 60 ab d5 aa cb ee 3d 10 dc e7 aa c0 1d d8 22
        bd a6 9a be b6 66 83 5a e6 52 50 3f 43 74 a4 9f 4a d5 f8 33 44 23 5b b6
        07 9e 05 78 cd 47 68 a0 37 a3 42 74 4c 3e 08 bc 09 b8 82 b8 2b bd 23 1d
        ef 86 7a e7 c3 7b 79 90 9f af db dc f0 d6 80 cb 86 b9 54 72 af 8f 11 cb
        e6 d9 5d e0 47 53 35 fe 64 aa d0 b3 bd f0 25 ba e8 52 93 7e 31 d0 09 32
        31 31 31 4c 5c a7 fa 2b c0 c7 52 a8 0f 17 f9 77 f0 5c 7a 67 83 7c b5 7d
        ee e5 83 5c 56 0a 7f 69 90 3e 5d 72 af b3 97 59 1a 67 be a7 88 65 f3 47
        68 34 b2 cd a6 0a 7d 36 05 79 05 1b d9 ac d0 db fc 1d 66 d6 1c 77 10 d8
        09 6c c1 73 e9 7d 59 81 9f 6b df 3b df 85 6e 78 4b df 13 e6 f3 34 a6 ae
        2d a4 1f 3f 0a 3c c4 d9 77 85 1f 4d 95 b8 c7 c9 ac d0 3b 52 a5 97 80 ef
        4f 55 fa 07 89 41 33 85 26 ab 55 7a eb ab ee d5 02 fc 5c f3 cf 25 bd 66
        89 d8 ef ce ba cc 0f 11 7b e0 47 52 c5 3d 43 1c fd 7d 36 fd 9c 79 2b 70
        03 bd 5b 42 fd 32 e0 fd c0 bf 03 ae a7 c0 23 6c 70 f6 8c f7 e1 e1 61 f7
        d2 5b 58 79 af 14 f2 86 b7 74 96 6a ae ea 5e 4a 6f 1f 21 e6 74 bc 94 02
        fc 85 14 de 47 69 5c 3f 7a 26 fd 7c ab f0 2e e1 0d 21 61 26 7d e0 be 0a
        5c 5d 74 a0 7b 2e bd b9 10 cf 06 b6 9c ef f6 31 49 8d 4f 21 1a e3 51 b3
        97 93 c4 b2 f9 2b c4 19 f0 a3 c4 99 f0 a7 d2 ff 9b cb bd 64 cd 6c 75 83
        dc 40 ef 56 4b e9 3b d0 7f 20 26 c7 dd 58 f4 ea 85 d3 e3 ce 1d de 0e 6c
        91 9a 0e f0 7c 43 5b 76 3b d9 64 2e bc b3 e3 bb 47 d3 ff cf ef 97 1b e0
        3d c4 d4 48 26 26 26 76 00 ef 00 fe 10 f8 21 e2 08 5b a1 06 75 c6 fb 6a
        17 90 ac 65 cf db f0 96 56 0d f2 85 14 da d9 e5 26 f3 a9 f2 7e 94 c6 7c
        f4 93 c4 ca e4 24 8d 7d 70 c3 db 0a bd e7 9d 21 f6 88 be 0d 5c 4b 0c 9b
        29 34 55 07 a5 4a 3f df 05 25 ab 85 b6 e1 2d 9d 53 25 85 f7 a9 14 ce 2f
        11 2b 8f d9 2c f4 53 a9 12 7f 36 05 79 16 e0 55 c3 db 0a bd 1f ab f4 6d
        a9 3a ff 0c f0 1e 60 7b 27 aa f4 7e ea 78 5f 6d d2 da f2 0b 4b 80 15 8f
        8e 49 5a 51 35 55 dd 8b b9 b7 8f 11 63 55 5f 4e 81 fd 58 2e bc 17 52 d8
        67 8d 6c 76 a3 5b a1 f7 bd c5 f4 09 f1 0c f0 16 60 6b 27 aa f4 5e 9f 1e
        b7 da 80 96 95 ae 0a 35 bc a5 f3 7f 4a d1 b8 9d 2c 9b ce 36 45 1c 25 3b
        4c e3 22 93 a7 d3 d7 ae 63 29 c4 a7 c8 0d 74 c1 a5 74 03 7d 00 bf eb 3d
        42 8c 29 3c 00 5c 9e 42 bd d0 41 33 59 f5 da ed 1d ef 6b dd eb 5e 3e 71
        cd 10 97 d6 14 e2 d9 eb fc ed 64 33 44 f3 da 63 e9 eb 54 b6 9c 3e 97 42
        7c 26 15 26 4b 40 c5 f0 1e 2c 2e b9 2f 93 c6 c1 be 1d f8 38 31 68 e6 b2
        a2 ab f4 fc b9 f4 91 91 ee f9 9e 6b b5 d0 3e d7 2d 63 06 b8 b4 2e 0b a9
        e2 9e 4d c1 bc 90 82 fb f1 54 91 4f a7 70 3f 98 8a 8f b9 54 88 d4 88 65
        74 2f 37 b1 42 57 4e 8d b8 0d e8 41 e0 87 89 6b 55 b7 14 1d 9c f9 73 e9
        45 ef a5 9f eb b2 92 95 66 9e 7b e6 5b 6a 5a 25 55 d8 d9 71 b1 97 89 d5
        c1 c9 14 d6 33 44 57 fa d3 29 c8 b3 46 b6 8a e1 2d 2b f4 b5 55 e9 a5 14
        e6 9f 02 7e 92 0e 8c 83 2d 6a 7a dc 4a 67 b8 57 eb 3a 5f ed dc b7 a4 35
        c9 6e 24 5b e2 ec db c9 0e a4 8a fb 24 f0 30 b1 0f 9e 0d 74 c9 26 b2 2d
        a6 62 c3 3d 70 19 e8 4d 84 fa 2e e0 7d c0 ef 00 37 03 9b 8a fe 3b b4 eb
        5c fa 5a e6 9a af 54 79 1b e4 d2 da 3f cd 68 34 b3 65 af a7 88 33 df 47
        88 8e f3 e3 34 e6 a1 4f a6 10 3f 9e 42 3c 6b 64 33 c4 b5 66 2e b9 af 6e
        92 b8 49 e8 71 62 1f fd 32 7a 74 7a dc 6a d7 83 ae 76 ee db 00 97 36 1c
        e6 59 93 da 09 62 4f 7c 32 7d 2d 79 8a 46 23 5b 36 b5 2d bb 00 65 11 1b
        d9 64 85 de b6 2a fd 6a e0 c3 44 83 dc 1b ba bd 4a 3f df 65 25 2b 75 9b
        1b da d2 86 e5 cf 78 57 d2 8f 9f 26 9a d9 5e 49 81 7d 9c 38 12 7b 38 85
        7d 56 81 57 dd 0b 97 15 7a 31 a6 81 7b 81 77 03 37 75 22 d0 b3 e6 b8 d5
        f6 d1 d7 7a 45 a8 e1 2d b5 cc 12 8d cb 4a 16 88 fd ef 97 89 fd f0 b9 54
        91 3f 98 42 fd 78 2e c0 1d e8 22 03 bd c3 df 79 bf 44 5c 23 f8 66 a2 e3
        bd f0 55 8d fc 54 b5 52 a9 f4 3d 4d 6a cb ab ed e5 95 b8 a4 e6 3f fd 52
        18 67 37 93 2d d1 98 c8 76 30 55 df 0f 11 27 63 b2 71 aa b3 a9 62 5f 48
        bf a6 0e 60 90 ab dd 5c 72 3f 8f 89 89 89 ed c0 4f 00 bf 01 ec a1 e0 23
        6c 99 e1 e1 e1 d7 06 cd ac 34 ac 65 79 c5 2e a9 29 59 03 5b 16 e6 33 44
        13 5b d6 b4 76 88 d8 07 7f 21 05 fb 4c aa c2 b3 9b c9 b2 eb 49 6d 64 93
        15 7a 97 56 e9 8f 11 57 0c be 89 b8 5e b5 f0 21 eb cb c7 a5 1a dc 52 cb
        83 7c 9e d8 66 9b 4e 55 f6 c9 14 de cf 11 7b df 27 52 88 4f a6 20 5f c0
        89 6c 32 d0 7b 4a 35 7d 32 df 97 02 fd b2 54 a5 17 de f1 6e 15 2e b5 f4
        1b f5 33 34 06 b5 2c a4 e0 7e 26 7d be 67 95 f7 0b c4 51 b3 53 c4 5e f8
        22 de 4e a6 2e e5 92 fb 1a a4 41 33 b7 00 1f 25 86 cd 5c 09 0c 17 fa 8e
        4a 0d 71 f9 3d 74 49 6b 56 49 e1 bd 90 5e 5e 21 f6 c0 4f d0 68 64 bb 3f
        55 e4 27 68 1c 23 cb aa 70 97 d0 65 a0 f7 51 a8 5f 04 bc 17 f8 dd 54 a9
        6f 2d fc 9d 55 f2 dd 25 ad 41 fe 56 b2 6c 22 db 71 62 22 db 21 56 6e 64
        3b 9d aa f2 ac 62 cf 06 c3 d8 cc a6 9e e1 92 fb da 9d 4a 5f 10 9e 06 6e
        00 36 d3 81 bd 74 49 df e3 b5 f0 4d af 67 88 7d ee c9 14 de af a4 cf db
        ac 91 6d 3a fd bf 53 34 46 aa 56 f1 48 99 ac d0 07 aa 4a df 0d fc 0c f0
        9b c0 ad c0 a8 15 ba d4 51 59 23 db 29 62 4f 7c 8a d8 07 cf 37 b2 4d 12
        9d ea 53 e9 e7 3b 91 4d 56 e8 e2 18 b1 cf f6 02 70 35 70 b1 8f 44 2a cc
        22 8d 61 2e d5 14 ce cf a7 97 23 a9 32 3f 46 cc 46 7f 25 fd 38 bb d8 c4
        89 6c b2 42 d7 f7 54 e9 d7 00 9f 06 3e 44 34 ca 15 f6 4d 91 15 ba 06 4c
        25 85 71 f6 72 98 c6 ad 64 73 34 26 39 66 57 8b ce d1 98 e2 b6 44 3a 4f
        6e 25 2e 2b 74 ad 66 1a f8 2a f0 36 e0 3a 9f a1 d4 12 d9 40 97 7c 43 db
        09 62 52 e3 2b 29 c4 1f e4 7b 1b d9 a6 68 cc 50 cf f6 d2 ed 48 97 81 ae
        35 99 07 9e 20 ba 64 6f 27 1a e4 86 7d 2c 52 d3 6a c4 20 97 13 e9 25 6b
        64 cb 26 b2 1d 4d ff 2d 3b 1f be 48 a3 7b dd 46 36 29 71 0d b7 09 13 13
        13 9b 81 31 e0 d7 80 1f 07 b6 15 f1 2c 5d 72 57 9f c8 f6 c2 e7 d2 37 c8
        a7 88 65 f3 67 89 63 65 c7 52 78 67 95 79 b6 6f be 64 78 4b 56 e8 ad b6
        44 8c 82 7d 1c 78 27 71 26 dd b4 95 56 fe 5c c9 86 b3 d4 d2 eb 43 29 ac
        b3 63 65 47 d2 e7 d2 0b a9 42 cf 2e 36 a9 d8 c8 26 19 e8 ed 56 27 96 01
        9f 27 c6 42 ee 24 ce a5 4b 83 2e bb 91 2c 6b 68 9b 4c d5 f6 74 fa f1 2c
        8d bd f0 23 29 c0 b3 d9 e9 d9 99 70 f7 c0 a5 26 58 55 36 69 62 62 62 08
        78 2b f0 4b c0 47 80 4b 69 f3 5e ba 4b ee ea c2 6f 6c b3 97 ac 91 ed 24
        d1 89 7e 24 bd fd 50 aa bc b3 cb 4c 66 69 5c 6e b2 48 e3 6a 52 43 5c 32
        d0 3b 1a ea 97 01 ef 01 7e 9b b8 2f 7d 9b 81 ae 01 0a f3 33 29 b4 a7 d2
        cb ab c4 50 97 7c 23 db a1 5c 75 9e 35 b2 55 c6 c7 c7 ab 3e 42 a9 b5 5c
        72 df 98 29 e2 6a d5 6f 01 d7 12 b7 b0 39 0e 56 fd 28 df c8 b6 48 ec 73
        3f 4b 6c 3b 65 fb e1 87 81 97 89 65 f4 33 a9 22 5f 74 1f 5c b2 42 ef 95
        2a fd 12 e0 dd c0 1f 00 6f a1 8d 97 b6 58 a1 ab a0 ca bb ca d9 cb e1 f3
        29 ac 0f 11 97 9c 4c a5 00 7f 34 55 e3 c7 69 34 b2 2d e1 51 32 c9 0a bd
        47 cd d2 18 3f 79 33 6d ba 2b dd 30 57 1b 55 73 2f 8b 34 e6 9f 4f a7 a0
        3e 4e ec 85 3f 4f a3 33 7d 26 7d ec 67 63 58 bd 99 4c 32 d0 7b de 22 d1
        00 f4 34 70 27 31 df 7d 93 8f 45 5d 5e 85 e7 9b d9 4e 12 cb e6 d9 4d 64
        4f 10 37 0b 1e 4b e1 7d 22 57 85 bf 56 b9 bb 94 2e 75 17 cb be 16 98 98
        98 d8 0e bc 8b 98 f1 7e 17 70 41 ab 9f ad 15 ba 5a 14 e4 d9 0c f4 e9 54
        65 1f 25 f6 c2 5f 4c 01 7e 92 d8 07 3f 49 63 1f 7c 21 05 b8 d5 b7 64 85
        de f7 e6 89 fd c4 27 80 ef 23 ba dd 1d 07 ab 4e 5b 4a 1f 9b f3 e9 ed d3
        c4 9e f7 0b 44 47 fa 64 7a fd 52 aa c0 cf a4 97 79 bb d0 25 2b f4 41 ae
        d2 37 03 3f 0f fc 2a f0 c3 b4 78 2f dd 0a 5d e7 a9 bc b3 81 2e 55 62 19
        7d 81 d8 0a 7a 35 85 f5 74 aa c6 1f 4e 81 7e 8c 18 b9 9a dd 0f ee 40 17
        c9 0a 5d b9 6a e8 5e e0 4d c4 5e fa 66 bf 61 52 1b d5 72 e1 bd 44 2c 91
        67 7b e0 b3 9c dd c8 96 9d 09 9f 4e 21 be 90 fb b5 86 b8 64 85 ae 15 aa
        f4 2d c0 cf 00 9f 23 06 cd b4 ec 08 9b 15 ba 38 bb 91 6d 3a 55 df d9 e8
        d4 27 88 a5 f3 7c 23 db 51 1a 13 da b2 81 2e 36 b2 49 06 ba d6 18 ea 77
        02 bf 0c 7c 0c b8 8c 16 0d 9a 31 d0 07 da 5c 0a e6 53 e9 65 92 98 85 7e
        20 bd 7d 22 bd 7d 22 55 e7 f3 34 2e 37 b1 fa 96 06 84 4b ee ad f7 32 70
        3f f0 53 c4 11 36 27 c7 69 3d b2 db c9 16 d3 db b3 44 07 fa 01 62 b8 cb
        24 31 e0 e5 c5 54 8d cf 12 8d 6c 73 e3 e3 e3 15 1f 9f 64 a0 ab 75 66 88
        a6 a3 17 81 ab 81 51 1f 89 56 90 35 b2 55 88 25 f4 ac 91 2d 1b a1 7a 32
        7d 2c 1d 06 be 4b 63 22 db a9 14 e0 d9 79 70 07 ba 48 02 5c 72 6f 8b 89
        89 89 dd c0 87 80 5f 07 6e 6f 45 95 ee 92 7b 5f a8 d1 d8 03 5f a0 d1 c8
        96 85 f4 31 a2 91 ed 45 1a 13 d9 b2 a9 6c f3 78 33 99 24 2b f4 c2 9d 00
        ee 01 7e 24 55 e9 3b 7d 24 03 5f 8d d7 52 70 1f 49 c1 3d 09 3c 49 e3 32
        93 99 14 f0 47 88 26 b7 6c d9 dd 46 36 49 06 7a 07 cd 13 c7 85 be 01 dc
        40 1c 63 73 d0 cc e0 7d 0c cc e6 5e a6 52 e5 fd 6c 0a f1 c3 44 57 7a 76
        33 d9 7c 2e c0 ad be 25 ad 9b eb b8 6d 92 06 cd dc 09 7c 06 f8 00 70 e1
        46 9e b7 4b ee 5d 5d 7d 67 97 9a 2c 11 cb e2 b3 c0 c1 f4 72 84 d8 fb 7e
        35 7d 93 77 28 55 e8 a7 89 ab 45 9d c8 26 c9 0a bd cb 2d a5 6a ec 31 e0
        9d c4 7c 77 ab f4 de 0f ef fc 40 97 5a 0a f2 63 34 86 b7 9c 4a d5 f7 83
        34 26 b2 65 37 93 cd a5 8f 0b 07 ba 48 b2 42 ef b1 2a 7d 04 f8 59 e0 13
        c0 0f b1 81 4b 5b ac d0 3b 1a e2 d9 cb 42 0a ed ec e6 b1 39 1a 8d 6c f9
        db c9 4e d2 b8 dc 24 0b f0 9a 7b e1 92 ac d0 7b 57 35 55 e8 f7 01 77 10
        93 e3 7c e6 bd a3 46 e3 46 b2 13 29 b0 9f 26 96 d2 4f a6 6a fc 04 b1 8c
        3e 9d 02 7e 01 58 32 bc 25 59 a1 f7 5f 95 be 8d 18 32 f3 7b 34 6e 62 5b
        f7 73 b7 42 2f c4 22 b1 34 7e 3a bd 4c a7 ca fb b9 14 da 87 d3 8f 8f d3
        98 c8 36 8f 8d 6c 92 0c f4 81 09 f5 b7 12 67 d2 3f 00 5c 49 13 e7 d2 0d
        f4 96 ab e4 5e 6a 29 98 5f 21 3a cf b3 2e f4 c3 44 67 fa 21 1a cb ec 0b
        c4 f2 b9 01 2e a9 ab b8 fc 5b 8c 03 c0 57 89 7d f4 4b 81 4d 3e 92 c2 64
        fb df d5 dc db 8b 9c 3d d4 65 8e 58 56 7f 10 78 3c 05 fa 54 fa ef 0e 74
        91 64 a0 eb 35 53 29 28 1e 03 ae 02 2e c7 d5 91 76 87 38 b9 f0 9e e6 ec
        f3 de c7 80 47 53 35 7e 9c c6 ed 64 59 47 fa 3c d1 cc 66 80 4b ea 19 86
        4a 41 26 26 26 2e 03 7e 0e f8 34 b1 97 be ae 23 6c 2e b9 af 59 36 91 2d
        eb 38 3f 0e 3c 43 2c 9b 67 8d 6c c7 69 34 b6 65 55 f8 82 67 c2 25 59 a1
        6b 2d 4e 11 dd ee 07 81 d7 d1 c2 bb d2 07 dc 62 0a e5 ec d6 b1 19 1a 8d
        6c af 10 03 5d b2 8b 4d b2 a3 66 73 38 52 55 92 81 ae 26 2d a5 80 79 0e
        78 0b b0 db 47 b2 2e d9 50 97 6c 3f 3b bb e0 e4 30 b1 e7 9d 75 a1 bf 4a
        0c f4 c9 1a d9 4e a5 0a 3c bb 18 c5 9b c9 24 f5 25 d7 71 0b 34 31 31 b1
        15 f8 71 e0 53 c0 bf 62 1d cd 71 03 b8 e4 9e 05 70 f6 b2 c4 f7 0e 75 39
        4a 5c 2d 9a 6f 64 cb 4f 64 ab 62 47 ba 24 2b 74 b5 c1 22 f0 08 f0 00 b1
        8f be 9b 16 5c ad da 87 95 78 25 55 d6 d9 b4 b5 79 e2 76 b2 c7 52 70 1f
        27 1a dd 8e 13 b3 d2 a7 d2 cf ab 18 e0 92 0c 74 15 55 75 1e 05 ee 05 de
        04 5c 46 ec a5 0f fa 4a 49 3d 85 f6 34 b1 07 3e 49 2c 9b 67 8d 6b d9 7f
        3b 40 74 a3 67 55 f8 c2 f8 f8 78 c5 0f 2b 49 32 48 0a 37 31 31 51 02 ae
        03 3e 04 7c 16 b8 66 2d df 58 f5 d9 92 7b 25 ad 56 64 37 94 9d 21 8e 90
        3d 97 42 fc 65 62 c4 ea 11 62 79 3d 6b 78 5b b2 13 5d 92 0c f4 6e 0a f5
        cd c0 1e e0 df 02 6f 05 b6 f7 71 98 af 76 3b 59 76 ad 68 b6 74 fe 5d e2
        78 d9 ab 9c bd 84 9e ed a1 db cc 26 49 06 7a 57 86 fa 5b 52 85 3e 06 5c
        c1 39 ce a5 f7 50 a0 e7 07 ba e4 f7 c2 a7 52 70 cf a6 30 7f 10 78 8a c6
        92 fa 19 1a 13 db 96 f0 66 32 49 5a 37 f7 d0 3b e7 10 f0 35 e0 cd c4 38
        d8 5e bf 2b bd 92 02 7b 86 74 e3 58 0a eb 27 89 e5 f3 43 c4 fe f7 74 aa
        ce b3 20 5f 30 bc 25 c9 40 ef 65 27 89 65 e6 17 81 eb 81 8b e9 ad 15 93
        ec 7e f0 53 34 a6 af bd 40 2c 99 4f 13 7b df c7 68 dc 54 96 35 b3 2d b9
        74 2e 49 ad e7 92 7b 07 4d 4c 4c 5c 01 7c 02 f8 28 31 3d 6e 74 c5 77 52
        77 2c b9 57 52 d5 bd 94 de 9e 23 96 cc 9f 4f 81 fd 32 b1 8c 7e 34 55 e9
        d9 15 a4 0b 40 d5 10 97 24 2b f4 7e 36 0d 7c 89 58 76 bf 21 bd 3f 3a 9d
        de d9 fe 77 d6 c4 96 bf 9d ec 28 8d e9 6b c7 80 fb 89 e5 f4 57 d3 ff 9f
        a5 71 1d 69 1d 2f 37 91 24 03 7d 40 2c a6 0a f7 51 e0 4e e0 a6 0e 84 7a
        be 91 ad 44 a3 91 6d 3a bd 3e 43 9c 01 7f 28 85 f7 c1 5c 78 67 dd e8 8b
        a9 0a 77 2f 5c 92 3a c4 25 f7 0e 9b 98 98 18 01 de 45 2c bd bf 8f 38 c2
        36 94 7f df 94 4a a5 7a 9b de 5f 15 1a 1d e6 8b e9 c7 27 89 a5 f3 6c ef
        7b 2a fd b7 57 68 8c 5d 9d 37 bc 25 c9 0a 5d 67 ab 12 23 4d 1f 07 ee 02
        b6 e5 aa e6 56 07 78 d6 c8 96 0d 6b 39 41 0c 74 79 35 85 fa 69 62 59 fd
        59 62 4f fc 58 fa 6f 8b 2e 9d 4b 92 15 ba ce 5f a5 6f 06 3e 08 7c 8e 18
        09 bb 29 bd 6f 4a b9 0a bd d4 c4 fb ab 4a a3 99 ad 4a 34 b2 bd 42 74 a3
        bf 42 8c 52 7d 8a 38 46 36 43 a3 63 7d 3e fd 7c f7 c0 25 c9 0a 5d eb b0
        48 ec 51 7f 05 b8 96 38 97 3e 94 0b f1 b5 54 ec 59 23 5b fe 76 b2 93 a9
        ca 3e 91 82 7a 92 b3 1b d9 4e a4 0a 7c 89 46 13 9c 97 9b 48 92 15 ba 36
        50 a5 5f 44 2c b9 ff 6e aa d2 b3 4b 5b 86 d3 b1 b5 a1 15 aa f4 2c 78 b3
        a1 2e d3 b9 0a fb 18 f0 30 8d a1 2e 53 29 bc b3 7d f0 05 a0 e2 5e b8 24
        59 a1 ab b5 4e 03 4f 10 d3 e3 ae 06 ae cc bd 8f 86 53 90 0f 11 4b e1 d9
        65 25 73 b9 4a fc 69 62 29 fd 48 0a f6 29 62 7f 7c 92 34 bd cd 8b 4d 24
        c9 0a 5d c5 54 e9 3b 80 77 00 e3 c0 6d 59 a0 97 a2 44 5f a0 71 a4 ec 60
        aa ba 8f a7 70 9f a4 31 1b 3d fb 6f 4b 56 df 92 64 85 ae 0d f8 e3 3f fe
        e3 ad c0 ae dc f3 9d 06 0e af 61 6f fa 34 d1 f1 7e 6f 0a ee 2d e9 65 9e
        e8 3a 3f 49 e3 ae f0 17 d3 db a7 d3 ff 5f 24 ed a1 bb 07 2e 49 06 ba 5a
        e3 0e e0 bf d0 b8 74 e5 ff 00 9f 27 96 c7 57 75 f7 dd 77 d7 27 26 26 8e
        01 7f 06 5c 5e 2a 95 ae 06 2e 49 81 3d 49 e3 72 93 d9 54 b1 57 0d 71 49
        92 81 de 3e 5b 81 5b 88 0b 57 20 f6 c4 d7 b4 bd 71 f7 dd 77 57 80 23 7f
        f2 27 7f 72 ac 5e af 1f 00 36 a7 e0 5e 4c 2f 15 c3 5b 92 64 a0 17 a7 b4
        ca db 6b f2 f9 cf 7f be 4a e3 5c b8 24 49 06 7a 07 9c 04 be 0c ec 24 3a
        d3 1f 24 96 c6 25 49 32 d0 7b c8 93 c0 27 73 95 f9 e2 f8 f8 78 c5 c7 22
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
        49 92 24 49 83 e5 ff 03 fe 8b 34 cf 1c 28 52 9c 00 00 00 00 49 45 4e 44
        ae 42 60 82""")
    return Photo("oletus lautapelin kuva", 0, "image/png", b)

def add_boardgame_photo_by_boardgame_name(boardgame_name: str, photo_name: str, photo: bytes, file_format: str) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("""
        INSERT INTO photos (boardgame_id, photo_id, name, file_format, photo)
        SELECT 
            b.id,
            COALESCE((
                SELECT max(p.photo_id) + 1
                FROM photos p
                WHERE p.boardgame_id = b.id
            ), 0),
            ?, ?, ?
        FROM boardgames b
        WHERE b.name = ?;
    """, (photo_name, file_format, photo, boardgame_name))

def get_reviews_by_boardgame_id(boardgame_id: int, page_num: int) -> list[Review] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            u.id,
            u.username,
            r.review,
            r.rating,
            CAST(r.rating AS INTEGER) AS stars,
            IIF(r.rating - FLOOR(r.rating) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM ratings r
        LEFT JOIN users u ON u.id == r.user_id
        WHERE r.boardgame_id == ?
        LIMIT ?
        OFFSET ?;
    """, (boardgame_id, int(os.getenv("PAGE_SIZE")), page_num * int(os.getenv("PAGE_SIZE"))))

    if len(result) > 0:
        return list(map(lambda result: Review(User(result[0], result[1], None), result[2], result[3], result[4], result[5]), result))
    return None

def get_number_of_user_ratings(user_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    n = conn.read("SELECT COUNT(*) FROM ratings WHERE user_id == ?", (user_id,))
    return n[0][0]

def get_number_of_boardgame_reviews(boardgame_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    n = conn.read("SELECT COUNT(id) FROM reviews WHERE boardgame_id == ?", (boardgame_id,))
    return n[0][0]

def get_user_review_stats(user_id: int) -> tuple[int, int, bool] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("""
        SELECT
            COUNT(r.rating),
            CAST(SUM(r.rating) AS INTEGER) AS stars,
            IIF(SUM(r.rating) - FLOOR(SUM(r.rating)) BETWEEN 0.25 AND 0.75, 1, 0) AS half_star
        FROM ratings r
        LEFT JOIN users u ON u.id == r.user_id
        WHERE u.id == ?;
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
        WHERE excluded.boardgame_id == ratings.boardgame_id AND
            excluded.user_id == ratings.user_id;
    """,
    (boardgame_id, review.user.id, review.rating, review.text))

def insert_reservation(user_id: int, boardgame_id: int, start: datetime, end: datetime) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    game_owner = conn.read("""
        SELECT user_games, reserved_user_games, user_id
        FROM users_boardgames
        WHERE user_games - reserved_user_games > 0
          AND boardgame_type == ?
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
        WHERE reserver == ?
            AND boardgame_id == ?
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
            WHERE boardgame_id == ?
            AND NOT (
                end_time <= ?
                OR start_time >= ?
            )
        );
    """, (boardgame_id, start, end))

    return bool(can_reserved[0][0])

def get_boardgame_names_with_user_has_active_reservation(user_id: int, page_num: int) -> list[str] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    date = datetime.today()
    reservations = conn.read("""
        SELECT b.name
        FROM reservation r
        LEFT JOIN boardgames b ON b.id == r.boardgame_id
        WHERE ? BETWEEN r.start_time AND r.end_time
            AND r.reserver == ?
        LIMIT ?
        OFFSET ?;
    """, (date, user_id, int(os.getenv("PAGE_SIZE")), page_num * int(os.getenv("PAGE_SIZE"))))

    if len(reservations) == 0:
        return None
    return [name[0] for name in reservations]

def set_boardgame_returned(boardgame: Boardgame, user_id: int) -> None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    date = datetime.today()
    conn.write("""
        UPDATE reservation
        SET end_time = ?
        WHERE boardgame_id == ?
            AND reserver == ?
    """, (date, boardgame.id, user_id))

def get_number_of_user_reservations(user_id: int) -> int:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    date = datetime.today()
    n = conn.read("""
        SELECT COUNT(*)
        FROM reservation
        WHERE reserver == ?
          AND ? BETWEEN start_time AND end_time
    """, (user_id, date))
    return n[0][0]