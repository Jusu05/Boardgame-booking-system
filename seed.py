import io
import os
import random
import sqlite3
import struct
import zlib
from datetime import datetime, timedelta
from string import ascii_letters, punctuation, digits, whitespace

from werkzeug.security import generate_password_hash
from env_parser import load_dotenv

PASSWORD_CHARS = ascii_letters + punctuation + digits
LETTERS = ascii_letters + punctuation + digits + whitespace

CATEGORIES = [
    (0, "Muu"),
    (1, "Lasten peli"),
    (2, "Korttipeli"),
    (3, "Pakohuonepeli"),
    (4, "Yhteistyöpeli"),
    (5, "Sotapeli"),
    (6, "Partypeli"),
    (7, "Tietopeli"),
    (8, "Perhepeli"),
]


def delete_all(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    for table in (
        "reservation", "ratings", "photos",
        "users_boardgames", "boardgames", "users", "categories"
    ):
        conn.execute(f"DELETE FROM {table}")

    conn.execute("""
        DELETE FROM sqlite_sequence
        WHERE name IN (
            'users', 'boardgames', 'categories',
            'users_boardgames', 'reservation'
        )
    """)
    conn.commit()


def seed_categories(conn):
    conn.executemany(
        "INSERT INTO categories (id, category) VALUES (?, ?)",
        CATEGORIES,
    )
    return [category_id for category_id, _ in CATEGORIES]


def seed_users(conn, n):
    user_ids = []

    for i in range(n):
        password = "".join(random.choices(PASSWORD_CHARS, k=12))
        password_hash = generate_password_hash(password)

        cursor = conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (f"user {i + 1}", password_hash),
        )
        user_ids.append(cursor.lastrowid)

    return user_ids


def random_png_bytes(width, height):
    png_signature = b"\x89PNG\r\n\x1a\n"

    def make_chunk(chunk_type, data):
        chunk = struct.pack(">I", len(data)) + chunk_type + data
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return chunk + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    rows = bytearray()
    for _ in range(height):
        rows.append(0)
        for _ in range(width):
            rows.extend((
                random.getrandbits(8),
                random.getrandbits(8),
                random.getrandbits(8),
            ))

    return (
        png_signature
        + make_chunk(b"IHDR", ihdr)
        + make_chunk(b"IDAT", zlib.compress(bytes(rows), level=9))
        + make_chunk(b"IEND", b"")
    )


def seed_boardgames(conn, n, photo):
    boardgame_ids = []

    for i in range(n):
        cursor = conn.execute("""
            INSERT INTO boardgames
                (name, description, number_of_players, duration, category_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            f"Boardgame {i + 1}",
            "".join(random.choices(LETTERS, k=100)),
            random.randint(2, 10),
            random.randint(30, 120),
            random.choice(CATEGORIES)[0],
        ))

        boardgame_id = cursor.lastrowid
        boardgame_ids.append(boardgame_id)

        if random.random() < 0.9:
            for photo_id in range(random.randint(1, 5)):
                conn.execute("""
                    INSERT INTO photos
                        (boardgame_id, id, name, file_format, photo)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    boardgame_id,
                    photo_id,
                    f"boardgame_{boardgame_id}_{photo_id}.png",
                    "image/png",
                    photo,
                ))

    return boardgame_ids


def seed_user_boardgames(conn, n, user_ids, boardgame_ids):
    pairs = [
        (user_id, boardgame_id)
        for user_id in user_ids
        for boardgame_id in boardgame_ids
    ]
    random.shuffle(pairs)

    if n > len(pairs):
        raise ValueError("Not enough unique user/game pairs.")

    for user_id, boardgame_id in pairs[:n]:
        user_games = random.randint(1, 5)
        reserved_user_games = random.randint(0, user_games)

        conn.execute("""
            INSERT INTO users_boardgames
                (user_id, boardgame_id, user_games, reserved_user_games)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            boardgame_id,
            user_games,
            reserved_user_games,
        ))


def seed_ratings(conn, n, user_ids, boardgame_ids):
    pairs = [
        (boardgame_id, user_id)
        for boardgame_id in boardgame_ids
        for user_id in user_ids
    ]
    random.shuffle(pairs)

    if n > len(pairs):
        raise ValueError("Not enough unique user/game pairs for ratings.")

    for boardgame_id, user_id in pairs[:n]:
        rating = random.randint(2, 10) / 2
        review = (
            "".join(random.choices(LETTERS, k=500))
            if random.random() < 0.7
            else None
        )

        conn.execute("""
            INSERT INTO ratings (boardgame_id, user_id, rating, review)
            VALUES (?, ?, ?, ?)
        """, (boardgame_id, user_id, rating, review))


def seed_reservations(conn, n, user_ids, boardgame_ids):
    if n and (not user_ids or not boardgame_ids):
        raise ValueError("Users and board games must exist first.")

    for _ in range(n):
        reserver = random.choice(user_ids)
        game_owner = random.choice(user_ids)
        boardgame_id = random.choice(boardgame_ids)

        start = datetime.now() + timedelta(days=random.randint(-30, 30))
        end = start + timedelta(days=random.randint(1, 14))

        conn.execute("""
            INSERT INTO reservation
                (start_time, end_time, reserver, game_owner, boardgame_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S"),
            reserver,
            game_owner,
            boardgame_id,
        ))


if __name__ == "__main__":
    load_dotenv()

    database_name = os.getenv("DATABASE_NAME")
    if not database_name:
        raise RuntimeError("DATABASE_NAME is missing from the environment.")

    conn = sqlite3.connect(database_name)

    try:
        conn.execute("PRAGMA foreign_keys = ON")

        USERS = 10**3
        BOARDGAMES = 10**3
        USER_GAMES = 10**3
        RATINGS = 10**3
        RESERVATIONS = 10**3

        photo = random_png_bytes(100, 100)

        delete_all(conn)

        seed_categories(conn)
        user_ids = seed_users(conn, USERS)
        boardgame_ids = seed_boardgames(conn, BOARDGAMES, photo)

        seed_user_boardgames(conn, USER_GAMES, user_ids, boardgame_ids)
        seed_ratings(conn, RATINGS, user_ids, boardgame_ids)
        seed_reservations(conn, RESERVATIONS, user_ids, boardgame_ids)

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()