import re
import os
import sys
from flask import Flask, render_template, redirect, request, flash, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

import db
from security import CSRFProtect, LoginManager, login_user, login_required, logout_user, current_user
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
    flags = dict()
    if current_user.is_authenticated:
        flags["username"] = current_user.username
    return flags

@app.route("/", methods=["GET", "POST"])
def index() -> str:
    page = request.form.get("selected boardgames", 0, int)
    error_text = None
    better_search = request.form.get("better search bool", False, type=bool)
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
                if len(search_word) < 101:
                    boardgames = db.search_boardgames(
                        search_word,
                        0,
                        2**31 - 1,
                        "'^-?[0-9]+$'",
                        0,
                        2**31 - 1,
                        page
                    )
                else:
                    boardgames = None
            case "better search bool":
                try:
                    error_text = ""
                    duration_longer, duration_shorter, error_text_time = index_validate_time_search()
                    error_text += error_text_time

                    more_players, less_players, error_text_player = index_validate_player_search()
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
    boardgame_page = make_page_tuple(page, total, page_size)

    boardgame_categories = db.get_boardgame_categories()

    return render_template(
        "index.html",
        boardgames,
        boardgame_page=boardgame_page,
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

    if more_players < 0:
        more_players = 0

    if less_players > 101:
        less_players = 100

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
    else:
        return "^-?[0-9]+$"

def make_page_tuple(page: int, total: int, page_size: int) -> tuple[int, int, int]:
    page_count = max(1, -(-total // page_size))
    page = max(0, min(page, page_count - 1))
    window_start = max(0, min(page - 5 // 2, page_count - 5))
    return (page, window_start, page_count)

@app.route("/login", methods=["GET", "POST"])
def login()-> Response | str:
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
def avatar(username: str) -> Response:
    avatar = db.get_avatar_by_username(username)
    return Response(avatar.bytes, mimetype=avatar.file_type)

@app.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    return redirect("/")

@app.route("/user", methods=["GET", "POST"])
@login_required
def user() -> str:
    page_size = int(os.getenv("PAGE_SIZE"))

    boardgame_page_num = request.form.get("selected boardgames", 0, int)
    ratings_page_num = request.form.get("selected ratings", 0, int)

    if request.method == "POST":
        target = request.form.get("target", "")
        match target:
            case "next page boardgames":
                boardgame_page_num += 1
            case "previous page boardgames":
                boardgame_page_num = max(0, boardgame_page_num - 1)
            case "next page ratings":
                ratings_page_num += 1
            case "previous page ratings":
                ratings_page_num = max(0, ratings_page_num - 1)
            case "next page ratings":
                ratings_page_num += 1
            case "previous page ratings":
                ratings_page_num = max(0, ratings_page_num - 1)
            case _:
                if target.startswith("ratings"):
                    ratings_page_num = int(target.split(" ", 1)[1]) - 1
                elif target.startswith("boardgames"):
                    boardgame_page_num = int(target.split(" ", 1)[1]) - 1
                elif target.startswith("ratings"):
                    ratings_page_num = int(target.split(" ", 1)[1]) - 1

    boardgames = db.get_user_boardgames(current_user.id, boardgame_page_num)
    review_stats = db.get_user_review_stats(current_user.id)

    if request.method == "POST":
        boardgame = db.get_boardgame_by_name(request.form.get("return", ""))
        if boardgame:
            db.set_boardgame_returned(boardgame, current_user.id)

    reservations = db.get_boardgame_names_with_user_has_active_reservation(current_user.id)

    total_reservations = db.get_number_of_user_reservations(current_user.id)
    reservation_page = make_page_tuple(ratings_page_num, total_reservations, page_size)
    total_boardgames = db.get_number_of_boardgames()
    boardgames_page = make_page_tuple(boardgame_page_num, total_boardgames, page_size)
    total_ratings = db.get_number_of_user_ratings(current_user.id)
    ratings_page = make_page_tuple(ratings_page_num, total_ratings, page_size)

    return render_template("user.html", user=current_user, boardgames=boardgames, review_stats=review_stats, reservations=reservations, reservation_page=reservation_page, ratings_page=ratings_page, boardgames_page=boardgames_page)

@app.route("/boardgame/<boardgame_name>", methods=["GET", "POST"])
def boardgame(boardgame_name: str) -> Response | str:
    boardgame = db.get_boardgame_by_name(boardgame_name)
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, request.form.get("photo_id", 0, int))

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
    review_page = make_page_tuple(review_page_num, total_reviews, page_size)

    if request.method == "POST":
        match request.form.get("target"):
            case "cancel":
                pass
            case "confirm":
                return boardgame_update(boardgame_name)
            case "review":
                return boardgame_review(boardgame)
            case "edit":
                return boardgame_edit(boardgame, reviews, photo, review_page)
            case "delete":
                return boardgame_delete(boardgame, reviews, photo, review_page)
            case "confirm delete":
                return boardgame_delete_confirm(boardgame_name)
            case "next photo":
                boardgame.update(request.form)
                if photo.id + 1 < boardgame.number_of_photos:
                    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame.id, photo.id + 1)
            case "previous photo":
                boardgame.update(request.form)
                if photo.id - 1 >= 0:
                    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame.id, photo.id - 1)
            case "minus":
                return boardgame_minus(boardgame, reviews, photo, review_page)
            case "plus":
                return boardgame_plus(boardgame, reviews, photo, review_page)
            case "reserve":
                return boardgame_reserve(boardgame, reviews, photo, review_page)
            case "return":
                db.set_boardgame_returned(boardgame, current_user.id)
            case _:
                pass

    if current_user.is_authenticated:
        users_boardgames = db.get_user_boardgame_ids(current_user.id)
        users_has_boardgames = boardgame.id in users_boardgames
        today, next_day, next_month = get_dates()
        user_reserved_game = db.has_user_reserved_boardgame(current_user.id, boardgame.id)
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
        review_page=review_page,
    )

@login_required
def boardgame_edit(boardgame: Boardgame, reviews: list[Review], photo: Photo, review_page: tuple) -> str:
    boardgame_categories = db.get_boardgame_categories()
    user_boardgames, reserved_user_boardgames = db.get_users_game_count_by_boardgame_id(boardgame.id)
    return render_template(
        "boardgame.html",
        boardgame=boardgame,reviews=reviews,
        boardgame_categories=boardgame_categories,
        n=user_boardgames+reserved_user_boardgames,
        photo=photo,
        edit_photos=True,
        review_page=review_page
    )

@login_required
def boardgame_delete(boardgame: Boardgame, reviews: list[Review], photo: Photo, review_page: tuple) -> str:
    user_boardgames, reserved_user_boardgames = db.get_users_game_count_by_boardgame_id(boardgame.id)
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, n=user_boardgames, delete=True, reserved_user_boardgames=reserved_user_boardgames, photo=photo, review_page=review_page)

@login_required
def boardgame_delete_confirm(boardgame_name: str) -> Response:
    boardgame = db.get_boardgame_by_name(boardgame_name)
    user_boardgames, reserved_user_boardgames = db.get_users_game_count_by_boardgame_id(boardgame.id)
    if reserved_user_boardgames > 0:
        db.set_user_boardgames_to_zero(current_user.id)
        return redirect(f"/boardgame/{boardgame.name}")
    db.delete_users_boardgames_by_boardgame_id(boardgame.id)
    if boardgame.free + boardgame.reserved - user_boardgames - reserved_user_boardgames > 0:
        return redirect(f"/boardgame/{boardgame.name}")
    return redirect("/")

@login_required
def boardgame_update(reviews: list[Review], photo: Photo, review_page: tuple) -> Response:
    boardgame, error_text = Boardgame.from_form(request.form)
    if error_text:
        if "users_games" in session:
            db.update_boardgame(boardgame, session["users_games"])
            del session["users_games"]
        else:
            db.update_boardgame(boardgame)
        return redirect(f"/boardgame/{boardgame.name}")

    boardgame = db.get_boardgame_by_name(boardgame.name)
    boardgame.update(request.form)
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(
        boardgame.name,
        request.form.get("photo_id", 0, int)
    )
    boardgame_categories = db.get_boardgame_categories()
    user_boardgames, reserved_user_boardgames = db.get_users_game_count_by_boardgame_id(boardgame.id)
    return render_template(
        "boardgame.html",
        boardgame=boardgame,
        reviews=reviews,
        boardgame_categories=boardgame_categories,
        n=user_boardgames+reserved_user_boardgames,
        photo=photo,
        edit_photos=True,
        review_page=review_page,
        error_text_boardgame=error_text
    )

@login_required
def boardgame_review(boardgame: Boardgame) -> Response:
    review = Review.from_form(request.form)
    db.upsert_review(boardgame.id, review)
    return redirect(f"/boardgame/{boardgame.name}")

@login_required
def boardgame_plus(boardgame: Boardgame, reviews: list[Review], photo: Photo, review_page: tuple) -> str:
    boardgame_categories = db.get_boardgame_categories()
    boardgame.update(request.form)
    user_games, _ = db.get_users_game_count_by_boardgame_id(boardgame.id)
    session["users_games"] = session.get("users_games", user_games) + 1
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"], photo=photo, edit_photos=True, review_page=review_page)

@login_required
def boardgame_minus(boardgame: Boardgame, reviews: list[Review], photo: Photo, review_page: tuple) -> str:
    boardgame_categories = db.get_boardgame_categories()
    user_games, reserved = db.get_users_game_count_by_boardgame_id(boardgame.id)
    boardgame.update(request.form)
    current = session.get("users_games", user_games)
    if current - 1 > reserved:
        session["users_games"] = current - 1
    else:
        session["users_games"] = current
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"], photo=photo, edit_photos=True, review_page=review_page)

@login_required
def boardgame_reserve(boardgame: Boardgame, reviews: list[Review], photo, review_page: tuple) -> str:
    users_boardgames = db.get_user_boardgame_ids(current_user.id)
    users_has_boardgames = boardgame.id in users_boardgames
    today, next_day, next_month = get_dates()
    start = datetime.fromisoformat(request.form["booking-start"])
    end = datetime.fromisoformat(request.form["booking-end"])

    if db.can_be_reserved(boardgame.id, start, end):
        db.insert_reservation(current_user.id, boardgame.id, start, end)
    else:
        return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, users_has_boardgames=users_has_boardgames, photo=photo, today=today, next_day=next_day, next_month=next_month, cannot_reserve=True, review_page=review_page)

    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, users_has_boardgames=users_has_boardgames, photo=photo, today=today, next_day=next_day, next_month=next_month, user_reserved_game=True, review_page=review_page)

def get_dates():
    today = str(datetime.today()).split(" ")[0]
    next_day = str(datetime.today() + timedelta(days=1)).split(" ")[0]
    next_month = str(datetime.today() + timedelta(days=30)).split(" ")[0]
    return today, next_day, next_month

@app.route("/boardgame/<boardgame_name>/photo/<int:id>", methods=["GET"])
def boardgame_photo(boardgame_name: str, id: int) -> Response:
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, id)
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
                boardgames = db.search_boardgames(request.form["search_word"], page)
            case "cancel":
                return add_boardgame_cancel()
            case _:
                if target.startswith("boardgames"):
                    page = int(target.split(" ", 1)[1]) - 1

    search_word = request.form.get("search_word")

    total = db.get_number_of_boardgames()
    page_size = int(os.getenv("PAGE_SIZE"))
    boardgame_page = make_page_tuple(page, total, page_size)

    return render_template("add_boardgame.html", boardgames=boardgames, search_word=search_word, boardgame_page=boardgame_page)

@login_required
def add_boardgame_edit() -> str:
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame.name, request.form.get("photo_id", 0, type=int))
    boardgame_categories = db.get_boardgame_categories()
    n = session.get("users_games", 1)
    return render_template("boardgame.html", boardgame=boardgame, boardgame_categories=boardgame_categories, photo=photo, n=n, edit_photos=True)

@login_required
def add_boardgame_create() -> str:
    try:
        db.insert_boardgame(request.form["boardgame_name"], current_user.id)
    except DatabaseError:
        return add_boardgame_edit()

    session["new_game_added"] = request.form["boardgame_name"]
    boardgame_categories = db.get_boardgame_categories()
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    photo = Photo(None, 0, None, None)
    return render_template("boardgame.html", boardgame=boardgame, boardgame_categories=boardgame_categories, photo=photo, n=0, edit_photos=True)

@login_required
def add_boardgame_confirm() -> Response:
    boardgame, error_text = Boardgame.from_form(request.form)
    if not error_text:
        if "users_games" in session:
            db.update_boardgame(boardgame, session.pop("users_games"))
        else:
            db.update_boardgame(boardgame)
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
    return render_template("boardgame.html", boardgame=boardgame, boardgame_categories=boardgame_categories, n=session["users_games"], edit_photos=True)

@login_required
def add_boardgame_minus() -> str:
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    boardgame.update(request.form)
    session["users_games"] = max(1, session.get("users_games", 1) - 1)
    boardgame_categories = db.get_boardgame_categories()
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"], edit_photos=True)

def add_boardgame_photo() -> str:
    photo = request.files["photo"]
    error_text = None
    if sys.getsizeof(photo.read(), 0) > 100000:
        error_text = "Lisättävä kuva on liian suuri"
    if not error_text:
        db.add_boardgame_photo_by_boardgame_name(request.form["boardgame_name"], photo.filename, photo.read(), photo.mimetype)
    boardgame_categories = db.get_boardgame_categories()
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame.id, boardgame.number_of_photos - 1)
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