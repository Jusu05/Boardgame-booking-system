from string import ascii_letters, punctuation, digits, whitespace
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from env_parser import load_dotenv
import sqlite3
import random
import io
import struct
import zlib
import os

PASSWORD_STARS = ascii_letters + punctuation + digits
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
    (8, "Perhepeli")
]

def delete_all(conn: sqlite3.Connection):
    conn.executescript("""
        DELETE FROM categories;
        DELETE FROM boardgames;
        DELETE FROM users;
        DELETE FROM users_boardgames;
        DELETE FROM ratings;
        DELETE FROM reservation;
        DELETE FROM photos;
    """)
    conn.commit()

def seed_categories(conn: sqlite3.Connection) -> list[int]:
    for category in CATEGORIES:
        conn.execute("INSERT INTO categories (id, category) VALUES (?, ?);", category)

def seed_users(conn: sqlite3.Connection, n: int):
    password_chars = ascii_letters+punctuation+digits
    for i in range(n):
        password = "".join(random.choices(password_chars, k=12))
        hash = generate_password_hash(password)
        conn.execute("INSERT INTO users (username, password) VALUES (?,?);", (f"user {i}", hash))
        
def seed_boardgames(conn: sqlite3.Connection, n: int):
    for i in range(n):
        conn.execute("""
            INSERT INTO boardgames
                (name, description, number_of_players, duration, category_id)
            VALUES (?,?,?,?,?);
        """, ("".join(random.choices(LETTERS, k=10)), random.randint(2,10), random.randint(30,120), random.randint(0,8)))
        if random.random() < 0.9:
            for _ in range(random.randint(1,5)):
                conn.execute("""
                    INSERT INTO photos (boardgame_id, id, name, file_format, photo)
                    SELECT
                        ?,
                        COALESCE((
                            SELECT MAX(p.id) + 1
                            FROM photos p
                            WHERE p.boardgame_id = ?
                        ), 0),
                        ?, ?, ?
                    FROM boardgames b
                """, (i, i, f"{random.choices(LETTERS, k=12)}.png", "image/png", random_png_bytes(100, 100)))

def random_png_bytes(width: int, height: int) -> bytes:
    png_signature = b'\x89PNG\r\n\x1a\n'

    def make_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = struct.pack(">I", len(data)) + chunk_type + data
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        chunk += struct.pack(">I", crc)
        return chunk

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_chunk = make_chunk(b'IHDR', ihdr)

    row_bytes = bytearray()
    for y in range(height):
        row_bytes.append(0)
        for x in range(width):
            row_bytes.extend((random.getrandbits(8), random.getrandbits(8), random.getrandbits(8)))

    compressed_data = zlib.compress(bytes(row_bytes), level=9)
    idat_chunk = make_chunk(b'IDAT', compressed_data)
    iend_chunk = make_chunk(b'IEND', b'')

    png_data = io.BytesIO()
    png_data.write(png_signature)
    png_data.write(ihdr_chunk)
    png_data.write(idat_chunk)
    png_data.write(iend_chunk)
    return png_data.getvalue()

def seed_user_boardgames(conn: sqlite3.Connection, n: int, users_num: int, boardgames_num: int):
    for _ in range(n):
        conn.execute("""
            INSERT INTO users_games
                (user_id, boardgame_type, user_games, reserved_user_games)
            VALUES
                (?, ?, ?, ?)
        """, (random.randint(0, users_num), random.randint(0, boardgames_num), random.randint(1,5), random.randint(0,5)))

def seed_ratings(conn: sqlite3.Connection, n: int, user_num: int, boardgame_num: int) -> None:
    seen = set()
    attempts = 0
    inserted = 0
    while inserted < n and attempts < n * 5:
        attempts += 1
        user_id = random.randint(1, user_num)
        boardgame_id = random.randint(1, boardgame_num)
        if (user_id, boardgame_id) in seen:
            continue
        seen.add((user_id, boardgame_id))
        rating = round(random.uniform(1.0, 5.0) * 2) / 2
        review = random.choices(LETTERS, r=500) if random.random() < 0.7 else None
        conn.execute("""
            INSERT INTO ratings (boardgame_id, user_id, rating, review)
            VALUES (?, ?, ?, ?);
        """, (boardgame_id, user_id, rating, review))
        inserted += 1

def seed_reservations(conn: sqlite3.Connection, n: int, user_num: int, boardgame_num: int) -> None:
    for _ in range(n):
        reserver =random.randint(1, user_num)
        game_owner =random.randint(1, user_num)
        boardgame_id = random.randint(1, boardgame_num)

        start_offset = random.randint(-30, 30)
        duration_days = random.randint(1, 14)
        start = datetime.now() + timedelta(days=start_offset)
        end = start + timedelta(days=duration_days)

        conn.execute("""
            INSERT INTO reservation
                (start_time, end_time, reserver, game_owner, boardgame_id)
            VALUES (?, ?, ?, ?, ?);
        """, (
            start.strftime("%Y-%m-%d %H:%M:%S"),
            end.strftime("%Y-%m-%d %H:%M:%S"),
            reserver,
            game_owner,
            boardgame_id
        ))


if __name__ == "__main__":
    load_dotenv()
    conn = sqlite3.connect(os.getenv("DATABASE_NAME"))

    delete_all(conn)

    users = 10**4
    boardgames = 10**4
    ratings = 10**5
    user_games = 10**3
    reservations = 10**4
    
    seed_categories(conn)
    seed_users(conn, users)
    seed_boardgames(conn, boardgames)
    seed_user_boardgames(conn, user_games, users, boardgames)
    seed_ratings(conn, ratings, users, boardgames)
    seed_reservations(conn, reservations, users, boardgames)

    conn.commit()
    conn.close()
