import sqlite3, os
from typing import LiteralString

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
    user = conn.read("SELECT username, password FROM Users WHERE id = ?", (user_id, ))
    return user[0]

def get_user_by_username(username: str) -> tuple[int, str, str] | None:
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    user = conn.read("SELECT * FROM Users WHERE username = ?", (username, ))

    if len(user) > 0:
        return user[0]

    return None

def insert_user(username: str, password: str):
    conn = SqlConnection(os.getenv("DATABASE_NAME"))
    conn.write("INSERT INTO Users (username, password) VALUES (?,?)", (username, password))
