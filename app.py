import re
import os
import sys
from datetime import datetime, timedelta

from flask import Flask, Response, render_template, redirect, request, \
    session
from werkzeug.security import generate_password_hash, check_password_hash

import db
from security import CSRFProtect, LoginManager, login_user, login_required, \
    logout_user, current_user
from env_parser import load_dotenv
from datatypes import Boardgame, DatabaseError, Photo, Review, User

load_dotenv()

app = Flask(__name__)
app.config.from_mapping(
    SESSION_COOKIE_SAMESITE="Strict",
    SECRET_KEY=os.getenv("SECRET_KEY"),
)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    return db.get_user_by_id(user_id)

@app.context_processor
def inject_flags() -> dict:
    flags = {}
    if current_user.is_authenticated:
        flags["username"] = current_user.username
    return flags

@app.route("/", methods=["GET", "POST"])
def index() -> str:
    page = request.form.get("selected boardgames", 0, int)
    better_search = request.form.get("better search bool", False, type=bool)
    error_text = None
    boardgames = None

    if request.method == "POST":
        target = request.form.get("target", "")
        match target:
            case "next page boardgames":
                page += 1
            case "previous page boardgames":
                page = max(0, page - 1)
            case _ as target:
                if target and target.startswith("boardgames"):
                    page = int(target.split(" ", 1)[1]) - 1

        match target:
            case "search":
                search_word = request.form.get("search_word", "")
                if len(search_word) < 100:
                    boardgames = db.search_boardgames(
                        search_word,
                        0,
                        10 * 60,
                        "'^-?[0-9]+$'",
                        0,
                        100,
                        page
                    )
                else:
                    boardgames = None
            case "better search bool":
                try:
                    error_text = ""
                    value = index_validate_time_search()
                    duration_longer, duration_shorter, error_text_time = value
                    error_text += error_text_time

                    value = index_validate_player_search()
                    more_players, less_players, error_text_player = value
                    error_text += "\n" + error_text_player

                    category_id = index_validate_category_id()
                    error_text = error_text.strip()

                    if len(error_text) < 0:
                        boardgames = db.search_boardgames(
                            search_word,
                            duration_longer,
                            duration_shorter,
                            category_id,
                            more_players,
                            less_players,
                            page
                        )
                        error_text = None
                    else:
                        boardgames = None

                except ValueError:
                    boardgames = None
            case "better search active":
                boardgames = db.get_boardgame_page(page)
                better_search = not request.form["better search bool"]
            case _:
                boardgames = db.get_boardgame_page(page)

    total = db.get_number_of_boardgames()
    page_size = int(os.getenv("PAGE_SIZE"))
    boardgame_page_info = make_page_info_tuple(page, total, page_size)

    boardgame_categories = db.get_boardgame_categories()

    return render_template(
        "index.html",
        boardgames=boardgames,
        boardgame_page_info=boardgame_page_info,
        better_search=better_search,
        boardgame_categories=boardgame_categories,
        error_text=error_text
    )

def index_validate_time_search():
    duration_longer = request.form.get("duration longer", 0, key=int)
    duration_shorter = request.form.get("duration shorter", 24 * 60, key=int)

    error_text = ""
    if duration_longer > duration_shorter:
        error_text = "Lyhin aika on pidempi kuin pisin aika"

    if duration_longer < duration_shorter:
        error_text = "Pisin aika on lyhyempi kuin lyhin aika"

    return duration_longer, duration_shorter, error_text

def index_validate_player_search():
    more_players = request.form.get("more players", 0, key=int)
    less_players = request.form.get("less players", 100, key=int)
    more_players = max(more_players, 0)
    less_players = min(less_players, 100)

    error_text = ""
    if more_players > less_players:
        error_text = "Pelaajien pienin määrä on suurempi kuin pienin määrä"

    if more_players < less_players:
        error_text = "Pelaajien suurin määrä on pienempi kuin pienin määrä"

    return more_players, less_players, error_text

def index_validate_category_id():
    if request.form["category_id"] \
        and re.fullmatch(request.form["category_id"], "^-?[0-9]+$"):
        category_id = request.form["category_id"]

        if category_id == "-1":
            category_id = "^-?[0-9]+$"

        max_category_id = db.get_max_boardgame_category_id()
        if int(category_id) > max_category_id:
            return str(max_category_id)

        if int(category_id) < 0:
            return "0"

        return category_id

    return "^-?[0-9]+$"

def make_page_info_tuple(
    page: int,
    total: int,
    page_size: int
) -> tuple[int, int, int]:
    page_count = max(1, -(-total // page_size))
    page = max(0, min(page, page_count - 1))
    window_start = max(0, min(page - 5 // 2, page_count - 5))
    return (page, window_start, page_count)

@app.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    error_text = None
    if request.method == "POST":
        username = request.form["username"]
        user = db.get_user_by_username(username)

        if user and check_password_hash(
            user.password,
            request.form["password_1"]
        ):
            login_user(user)
            return redirect("/")
        else:
            error_text = "Väärä salasana tai käyttäjätunnus"

    return render_template(
        "login.html",
        login_screen=True,
        error_text=error_text
    )

@app.route("/create_user", methods=["GET", "POST"])
def create_user() -> Response | str:
    if request.method == "POST":
        error_text = "Käyttäjää ei voi luoda:"
        if not request.form["username"] and len(request.form["username"]) > 100:
            error_text += "käyttäjä nimi liian pitkä"
        if not request.form["password_1"] \
            and len(request.form["password_1"]) < 12:
            error_text += "\nsalasana pitää olla vähintään 12 merkkiä pitkä"
        if not request.form["password_2"] \
            and request.form["password_2"] != request.form["password_1"]:
            error_text += "\nsalasanat eivät ole samoja"

        password = generate_password_hash(request.form["password1"])

        try:
            db.insert_user(request.form["username"], password)
        except DatabaseError:
            error_text += "\n valitse toinen käyttäjä nimi"

        if error_text != "Käyttäjää ei voi luoda:":
            return render_template(
                "login.html",
                login_screen=False,
                error_text=error_text
            )

        return redirect("/")

    return render_template("login.html", login_screen=False)

@app.route("/user/<username>/avatar", methods=["GET"])
def user_photo(username: str) -> Response:
    avatar = db.get_avatar_by_username(username)
    return Response(avatar.bytes, mimetype=avatar.file_type)

@app.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    return redirect("/")

@app.route("/user", methods=["GET", "POST"])
@login_required
def user_page() -> str:
    page_size = int(os.getenv("PAGE_SIZE"))

    boardgame_page_num = request.form.get("selected boardgames", 0, int)
    reservation_page_num = request.form.get("selected ratings", 0, int)

    if request.method == "POST":
        target = request.form.get("target", "")
        match target:
            case "next page boardgames":
                boardgame_page_num += 1
            case "previous page boardgames":
                boardgame_page_num = max(0, boardgame_page_num - 1)
            case "next page reservation":
                reservation_page_num += 1
            case "previous page reservation":
                reservation_page_num = max(0, reservation_page_num - 1)
            case _:
                if target.startswith("boardgames"):
                    boardgame_page_num = int(target.split(" ", 1)[1]) - 1
                elif target.startswith("reservation"):
                    reservation_page_num = int(target.split(" ", 1)[1]) - 1


    boardgames = db.get_user_boardgames(current_user.id, boardgame_page_num)
    review_stats = db.get_user_review_stats(current_user.id)

    if request.method == "POST":
        boardgame = db.get_boardgame_by_name(request.form.get("return", ""))
        if boardgame:
            db.set_boardgame_returned(boardgame, current_user.id)

    total_reservations = db.get_number_of_user_reservations(
        current_user.id
    )
    reservation_page_info = make_page_info_tuple(
        reservation_page_num,
        total_reservations,
        page_size
    )
    reservations = db.get_boardgame_names_with_user_has_active_reservation(
        current_user.id,
        reservation_page_info[2]
    )

    total_boardgames = db.get_number_of_boardgames()
    boardgames_page = make_page_info_tuple(
        boardgame_page_num,
        total_boardgames,
        page_size
    )

    return render_template(
        "user.html",
        user=current_user,
        boardgames=boardgames,
        review_stats=review_stats,
        reservations=reservations,
        reservation_page_info=reservation_page_info,
        boardgames_page=boardgames_page
    )

@app.route("/boardgame/<boardgame_name>", methods=["GET", "POST"])
def boardgame_page(boardgame_name: str) -> Response | str:
    boardgame = db.get_boardgame_by_name(boardgame_name)
    photo = db.get_photo_by_boardgame_name_and_photo_id(
        boardgame_name, request.form.get("photo_id", 0, int)
    )

    if not boardgame:
        return redirect("/")

    review_page_num = request.form.get("selected review", 0, int)

    if request.method == "POST":
        target = request.form.get("target", "")
        match target:
            case "next page review":
                review_page_num += 1
            case "previous page review":
                review_page_num = max(0, review_page_num - 1)
            case _:
                if target.startswith("review"):
                    review_page_num = int(target.split(" ", 1)[1]) - 1

    reviews = db.get_reviews_by_boardgame_id(boardgame.id, review_page_num)

    total_reviews = db.get_number_of_boardgame_reviews(boardgame.id)
    page_size = int(os.getenv("PAGE_SIZE"))
    review_page_info = make_page_info_tuple(
        review_page_num,
        total_reviews,
        page_size
    )

    if request.method == "POST":
        match request.form.get("target"):
            case "cancel":
                pass
            case "confirm":
                return boardgame_page_update(reviews, photo, review_page_info)
            case "review":
                return boardgame_page_review(
                    boardgame,
                    reviews,
                    photo,
                    review_page_info
                )
            case "edit":
                return boardgame_page_edit(
                    boardgame,
                    reviews,
                    photo,
                    review_page_info
                )
            case "delete":
                return boardgame_delete(
                    boardgame,
                    reviews,
                    photo,
                    review_page_info
                )
            case "confirm delete":
                return boardgame_page_delete_confirm(boardgame_name)
            case "next photo":
                boardgame.update(request.form)
                if photo.id + 1 < boardgame.number_of_photos:
                    photo = db.get_photo_by_boardgame_name_and_photo_id(
                        boardgame.id,
                        photo.id + 1
                    )
            case "previous photo":
                boardgame.update(request.form)
                if photo.id - 1 >= 0:
                    photo = db.get_photo_by_boardgame_name_and_photo_id(
                        boardgame.id,
                        photo.id - 1
                    )
            case "minus":
                return boardgame_page_minus(
                    boardgame,
                    reviews,
                    photo,
                    review_page_info
                )
            case "plus":
                return boardgame_page_plus(
                    boardgame,
                    reviews,
                    photo,
                    review_page_info
                )
            case "reserve":
                return boardgame_page_reserve(
                    boardgame,
                    reviews,
                    photo,
                    review_page_info
                )
            case "return":
                db.set_boardgame_returned(boardgame, current_user.id)
            case _:
                pass

    if current_user.is_authenticated:
        users_boardgames = db.get_user_boardgame_ids(current_user.id)
        users_has_boardgames = boardgame.id in users_boardgames
        today, next_day, next_month = get_dates()
        user_reserved_game = db.has_user_reserved_boardgame(
                                current_user.id,
                                boardgame.id
                            )
    else:
        user_reserved_game = users_has_boardgames = False
        today = next_day = next_month = None

    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        users_has_boardgames=users_has_boardgames,
        photo=photo,
        today=today,
        next_day=next_day,
        next_month=next_month,
        user_reserved_game=user_reserved_game,
        review_page_info=review_page_info,
    )

@login_required
def boardgame_page_edit(
    boardgame: Boardgame,
    reviews: list[Review],
    photo: Photo,
    review_page_info: tuple
) -> str:
    boardgame_categories = db.get_boardgame_categories()
    value = db.get_users_game_count_by_boardgame_id(boardgame.id)
    user_boardgames, reserved_user_boardgames = value
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        boardgame_categories=boardgame_categories,
        n=user_boardgames+reserved_user_boardgames,
        photo=photo,
        edit_photos=True,
        review_page_info=review_page_info
    )

@login_required
def boardgame_delete(
    boardgame: Boardgame,
    reviews: list[Review],
    photo: Photo,
    review_page_info: tuple
) -> str:
    count = db.get_users_game_count_by_boardgame_id(boardgame.id)
    user_boardgames, reserved_user_boardgames = count
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        n=user_boardgames,
        delete=True,
        reserved_user_boardgames=reserved_user_boardgames,
        photo=photo,
        review_page_info=review_page_info
    )


@login_required
def boardgame_page_delete_confirm(boardgame_name: str) -> Response:
    boardgame = db.get_boardgame_by_name(boardgame_name)
    values = db.get_users_game_count_by_boardgame_id(boardgame.id)
    user_boardgames, reserved_user_boardgames = values

    if reserved_user_boardgames > 0:
        db.set_user_boardgames_to_zero(current_user.id)
        return redirect(f"/boardgame/{boardgame.name}")
    db.delete_users_boardgames_by_boardgame_id(boardgame.id)
    if boardgame.free + boardgame.reserved - \
            user_boardgames - reserved_user_boardgames > 0:
        return redirect(f"/boardgame/{boardgame.name}")
    return redirect("/")

@login_required
def boardgame_page_update(
    reviews: list[Review],
    photo: Photo,
    review_page_info: tuple
) -> Response | str:
    boardgame, error_text = Boardgame.from_form(request.form)
    if error_text:
        if "users_games" in session:
            db.update_boardgame(
                boardgame,
                current_user.id,
                session["users_games"]
            )
            del session["users_games"]
        else:
            db.update_boardgame(boardgame, current_user.id)
        return redirect(f"/boardgame/{boardgame.name}")

    boardgame = db.get_boardgame_by_name(boardgame.name)
    boardgame.update(request.form)
    photo = db.get_photo_by_boardgame_name_and_photo_id(
        boardgame.name,
        request.form.get("photo_id", 0, int)
    )
    boardgame_categories = db.get_boardgame_categories()
    value = db.get_users_game_count_by_boardgame_id(boardgame.id)
    user_boardgames, reserved_user_boardgames = value
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        boardgame_categories=boardgame_categories,
        n=user_boardgames+reserved_user_boardgames,
        photo=photo,
        edit_photos=True,
        review_page_info=review_page_info,
        error_text_boardgame=error_text
    )

@login_required
def boardgame_page_review(
    boardgame: Boardgame,
    reviews: list[Review],
    photo: Photo,
    review_page_info: tuple
) -> Response | str:
    review, error_text = Review.from_form(request.form, current_user)
    if not error_text:
        db.upsert_review(boardgame.id, review)
        return redirect(f"/boardgame/{boardgame.name}")

    users_boardgames = db.get_user_boardgame_ids(current_user.id)
    users_has_boardgames = boardgame.id in users_boardgames
    today, next_day, next_month = get_dates()
    user_reserved_game = db.has_user_reserved_boardgame(
                            current_user.id,
                            boardgame.id
                        )

    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        users_has_boardgames=users_has_boardgames,
        photo=photo,
        today=today,
        next_day=next_day,
        next_month=next_month,
        user_reserved_game=user_reserved_game,
        review_page_info=review_page_info,
    )

@login_required
def boardgame_page_plus(
    boardgame: Boardgame,
    reviews: list[Review],
    photo: Photo,
    review_page_info: tuple
) -> str:
    boardgame_categories = db.get_boardgame_categories()
    boardgame.update(request.form)
    user_games, _ = db.get_users_game_count_by_boardgame_id(boardgame.id)
    session["users_games"] = session.get("users_games", user_games) + 1
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        boardgame_categories=boardgame_categories,
        n=session["users_games"],
        photo=photo,
        edit_photos=True,
        review_page_info=review_page_info
    )

@login_required
def boardgame_page_minus(boardgame: Boardgame,
        reviews: list[Review], photo: Photo, review_page_info: tuple
    ) -> str:
    boardgame_categories = db.get_boardgame_categories()
    user_games, reserved = db.get_users_game_count_by_boardgame_id(
        boardgame.id
    )
    boardgame.update(request.form)
    current = session.get("users_games", user_games)
    if current - 1 > reserved:
        session["users_games"] = current - 1
    else:
        session["users_games"] = current
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        boardgame_categories=boardgame_categories,
        n=session["users_games"],
        photo=photo,
        edit_photos=True,
        review_page_info=review_page_info
    )

@login_required
def boardgame_page_reserve(
        boardgame: Boardgame,
        reviews: list[Review],
        photo,
        review_page_info: tuple
    ) -> str:
    users_boardgames = db.get_user_boardgame_ids(current_user.id)
    users_has_boardgames = boardgame.id in users_boardgames
    today, next_day, next_month = get_dates()
    start = datetime.fromisoformat(request.form["booking-start"])
    end = datetime.fromisoformat(request.form["booking-end"])

    if db.can_be_reserved(boardgame.id, start, end):
        db.insert_reservation(current_user.id, boardgame.id, start, end)
    else:
        return render_template(
            "boardgame.html",
            boardgame=boardgame,
            reviews=reviews,
            users_has_boardgames=users_has_boardgames,
            photo=photo,
            today=today,
            next_day=next_day,
            next_month=next_month,
            cannot_reserve=True,
            review_page_info=review_page_info
        )

    return render_template("boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        users_has_boardgames=users_has_boardgames,
        photo=photo,
        today=today,
        next_day=next_day,
        next_month=next_month,
        user_reserved_game=True,
        review_page_info=review_page_info
    )

def get_dates():
    today = datetime.today().isoformat()
    next_day = (datetime.today() + timedelta(days=1)).isoformat()
    next_month = (datetime.today() + timedelta(days=30)).isoformat()
    return today, next_day, next_month

@app.route("/boardgame/<boardgame_name>/photo/<int:photo_id>", methods=["GET"])
def boardgame_photo(boardgame_name: str, photo_id: int) -> Response:
    photo = db.get_photo_by_boardgame_name_and_photo_id(
        boardgame_name,
        photo_id
    )
    return Response(photo.bytes, mimetype=photo.file_type)

@app.route("/add_boardgame", methods=["GET", "POST"])
@login_required
def add_boardgame() -> Response | str:
    boardgames = None
    page = request.form.get("selected boardgames", 0, int)

    if request.method == "POST":
        target = request.form.get("target", "")
        match target:
            case "next page boardgames":
                page += 1
            case "previous page boardgames":
                page = max(0, page - 1)
            case "edit":
                return add_boardgame_edit()
            case "create":
                return add_boardgame_create()
            case "confirm":
                return add_boardgame_confirm()
            case "plus":
                return add_boardgame_plus()
            case "minus":
                return add_boardgame_minus()
            case "photo":
                return add_boardgame_photo()
            case "search":
                search_word = request.form.get("search_word", "")
                if len(search_word) < 100:
                    boardgames = db.search_boardgames(
                        search_word,
                        0,
                        10 * 60,
                        "'^-?[0-9]+$'",
                        0,
                        100,
                        page
                    )
                else:
                    boardgames = None
            case "cancel":
                return add_boardgame_cancel()
            case _:
                if target.startswith("boardgames"):
                    page = int(target.split(" ", 1)[1]) - 1

    search_word = request.form.get("search_word")

    total = db.get_number_of_boardgames()
    page_size = int(os.getenv("PAGE_SIZE"))
    boardgame_page_info = make_page_info_tuple(page, total, page_size)

    return render_template(
        "add_boardgame.html",
        boardgames=boardgames,
        search_word=search_word,
        boardgame_page_info=boardgame_page_info
    )


@login_required
def add_boardgame_edit() -> str:
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    photo = db.get_photo_by_boardgame_name_and_photo_id(
        boardgame.name,
        request.form.get("photo_id", 0, type=int)
    )
    boardgame_categories = db.get_boardgame_categories()
    n = session.get("users_games", 1)
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        boardgame_categories=boardgame_categories,
        photo=photo,
        n=n,
        edit_photos=True
    )

@login_required
def add_boardgame_create() -> str:
    error_text = None
    if request.form["boardgame_name"] \
        and len(request.form["boardgame_name"]) > 100:
        error_text = "Virhe lautapeliä luodessa pelin nimi liian pitkä"

    if error_text:
        try:
            db.insert_boardgame(request.form["boardgame_name"], current_user.id)
        except DatabaseError:
            return add_boardgame_edit()

        session["new_game_added"] = request.form["boardgame_name"]
        boardgame_categories = db.get_boardgame_categories()
        boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
        photo = Photo(None, 0, None, None)
        return render_template(
            "boardgame.html",
            boardgame=boardgame,
            boardgame_categories=boardgame_categories,
            photo=photo,
            n=0,
            edit_photos=True
        )

    search_word = request.form.get("search_word")
    target = request.form.get("target", "")
    page = int(target.split(" ", 1)[1]) - 1
    total = db.get_number_of_boardgames()
    page_size = int(os.getenv("PAGE_SIZE"))
    boardgame_page_info = make_page_info_tuple(page, total, page_size)
    if len(search_word) < 100:
        boardgames = db.search_boardgames(
            search_word,
            0,
            10 * 60,
            "'^-?[0-9]+$'",
            0,
            100,
            page
        )
    else:
        boardgames = None

    return render_template(
        "add_boardgame.html",
        boardgames=boardgames,
        search_word=search_word,
        boardgame_page_info=boardgame_page_info,
        error_text=error_text
    )

@login_required
def add_boardgame_confirm() -> Response:
    boardgame, error_text = Boardgame.from_form(request.form)
    if not error_text:
        if "users_games" in session:
            db.update_boardgame(boardgame,
                current_user.id,
                session.pop("users_games")
            )
        else:
            db.update_boardgame(boardgame, current_user.id)
        return redirect("/")

    session["new_game_added"] = request.form["boardgame_name"]
    boardgame_categories = db.get_boardgame_categories()
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    photo = Photo(None, 0, None, None)
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        boardgame_categories=boardgame_categories,
        photo=photo,
        n=0,
        edit_photos=True,
        error_text_boardgame=error_text
    )


@login_required
def add_boardgame_cancel() -> Response:
    if "new_game_added" in session:
        boardgame = db.get_boardgame_by_name(session["new_game_added"])
        del session["new_game_added"]
        db.delete_boardgame(boardgame, current_user.id)
    return redirect("/")

@login_required
def add_boardgame_plus() -> str:
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    boardgame.update(request.form)
    boardgame_categories = db.get_boardgame_categories()
    session["users_games"] = session.get("users_games", 1) + 1
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        boardgame_categories=boardgame_categories,
        n=session["users_games"],
        edit_photos=True
    )

@login_required
def add_boardgame_minus() -> str:
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    boardgame.update(request.form)
    session["users_games"] = max(1, session.get("users_games", 1) - 1)
    boardgame_categories = db.get_boardgame_categories()
    return render_template("boardgame.html",
        boardgame_categories=boardgame_categories,
        n=session["users_games"],
        edit_photos=True
    )


def add_boardgame_photo() -> str:
    photo = request.files["photo"]
    error_text = None
    if sys.getsizeof(photo.read(), 0) > 100000:
        error_text = "Lisättävä kuva on liian suuri"
    if not error_text:
        db.add_boardgame_photo_by_boardgame_name(
        request.form["boardgame_name"],
        photo.filename,
        photo.read(),
        photo.mimetype
    )
    boardgame_categories = db.get_boardgame_categories()
    boardgame = db.get_boardgame_by_name(request.form["name"])
    photo = db.get_photo_by_boardgame_name_and_photo_id(
        boardgame.id,
        boardgame.number_of_photos - 1
    )
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        boardgame_categories=boardgame_categories,
        photo=photo,
        edit_photos=True,
        error_text_photo=error_text
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
