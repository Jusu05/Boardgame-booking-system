import sqlite3, os
from typing import LiteralString

from datatypes import Boardgame

class SqlConnection:
    def __init__(self, file: str) -> None:
        self._file = file

    def write(self, command: LiteralString, params: tuple = None):
        connection = sqlite3.connect(self._file)
        cursor = connection.cursor()

        if params:
            cursor.execute(command, params)
        else:
            cursor.execute(command)

        connection.commit()
        connection.close()

    def read(self, command: LiteralString, params: tuple = None) -> list:
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

def get_user_by_id(user_id: int) -> tuple[str, str]:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read("SELECT username, password FROM Users WHERE id = ?;", (user_id, ))
    return user[0]

def get_user_by_username(username: str) -> tuple[int, str, str] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read("SELECT * FROM Users WHERE username = ?;", (username, ))

    if len(user) > 0:
        return user[0]

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

def get_boardgame_by_name(boardgame_name: str) -> Boardgame | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("SELECT * FROM Boardgames WHERE name = ?", (boardgame_name,))
    if len(result) > 0:
        return Boardgame(boardgame_name, result[0][3], result[0][5], result[0][0], result[0][2], result[0][4], result[0][6], result[0][7])
    return None

def get_all_boardgames() -> list[Boardgame] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    result = conn.read("SELECT * FROM Boardgames;")
    if len(result) > 0:
        return list(map(lambda result: Boardgame(result[1], result[3], result[5], result[0], result[2], result[4], result[6], result[7]), result))
    return None
