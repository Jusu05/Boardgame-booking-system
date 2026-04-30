from flask import Flask, render_template, redirect, request, flash, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

import db
from security import CSRFProtect, LoginManager, login_user, login_required, logout_user, current_user
from env_parser import load_dotenv
from datatypes import Boardgame, Photo, Review, User

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
    boardgames = db.get_all_boardgames()

    if request.method == "POST":
        boardgames = db.get_all_boardgames_by_search_word(request.form["search_word"])

    if boardgames:
        return render_template("index.html", boardgames=boardgames)
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login()-> Response | str:
    if request.method == "POST":
        username = request.form["username"]
        user = db.get_user_by_username(username)

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect("/")
        else:
            flash("Väärä salasana tai käyttäjätunnus")

    return render_template("login.html", login_screen=True)

@app.route("/create_user", methods=["GET", "POST"])
def create_user() -> Response | str:
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        try:
            db.insert_user(username, password)
        except Exception:
            flash("Käyttäjää ei voi luoda")
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

@app.route("/user", methods=["GET"])
@login_required
def user() -> str:
    boardgames = db.get_user_boardgames(current_user.id)
    review_stats = db.get_user_review_stats()
    return render_template("user.html", user=current_user, boardgames=boardgames, review_stats=review_stats)

@app.route("/boardgame/<boardgame_name>", methods=["GET", "POST"])
def boardgame(boardgame_name: str) -> Response | str:
    boardgame = db.get_boardgame_by_name(boardgame_name)
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, 0)

    if not boardgame:
        return redirect("/")
    
    reviews = db.get_reviews_by_boardgame_id(boardgame.id)

    if request.method == "POST":
        match request.form["target"]:
            case "cancel":
                pass
            case "confirm":
                return boardgame_update(boardgame_name)
            case "review":
                return boardgame_review(boardgame)
            case "edit":
                return boardgame_edit(boardgame_name, reviews)
            case "delete":
                return boardgame_delete(boardgame_name)
            case "confirm delete":
                return boardgame_delete_confirm(boardgame_name)
            case "next photo":
                pass
            case "previous photo":
                pass
            case "minus":
                return boardgame_minus(boardgame, reviews)
            case "plus":
                return boardgame_plus(boardgame, reviews)
            case "reserve":
                return boardgame_reserve()
            case _:
                pass

    if current_user.is_authenticated:
        users_boardgames = db.get_user_boardgame_ids(current_user.id)
        users_has_boardgames = boardgame.id in users_boardgames
        today, next_day, next_month = get_dates()
    else:
        users_has_boardgames = False
        today = next_day = next_month = None 

    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, users_has_boardgames=users_has_boardgames, photo=photo, today=today, next_day=next_day, next_month=next_month)

@login_required
def boardgame_edit(boardgame: Boardgame, reviews: list[Review]) -> str:
    boardgame_categories = db.get_boardgame_categories()
    user_boardgames, _ = db.get_users_game_count_by_boardgame_id(boardgame.id)    
    photo = Photo(None, 0, None, None)

    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=user_boardgames, photo=photo)

@login_required
def boardgame_delete(boardgame_name: str, reviews: list[Review]) -> str:
    user_boardgames, reserved_user_boardgames = db.get_users_game_count_by_boardgame_id(boardgame.id)
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, 0)
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, n=user_boardgames, delete=True, reserved_user_boardgames=reserved_user_boardgames, photo=photo)

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
def boardgame_update(boardgame_name: str) -> Response:
    boardgame = Boardgame.from_form(request.form)
    if "users_games" in session:
        db.update_boardgame(boardgame, session["users_games"])
        del session["users_games"]
    else:
        db.update_boardgame(boardgame)
    return redirect(f"/boardgame/{boardgame_name}")

@login_required
def boardgame_review(boardgame: Boardgame) -> Response:
    review = Review.from_form(request.form)
    db.upsert_review(boardgame.id, review)
    return redirect(f"/boardgame/{boardgame.name}")

@login_required
def boardgame_plus(boardgame: Boardgame, reviews: list[Review]) -> str:
    boardgame_categories = db.get_boardgame_categories()
    boardgame.update(request.form)
    user_games, _ = db.get_users_game_count_by_boardgame_id(boardgame.id)
    session["users_games"] = session.get("users_games", user_games) + 1
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"])

@login_required
def boardgame_minus(boardgame: Boardgame, reviews: list[Review]) -> str:
    boardgame_categories = db.get_boardgame_categories()
    user_games, reserved = db.get_users_game_count_by_boardgame_id(boardgame.id)
    boardgame.update(request.form)
    current = session.get("users_games", user_games)
    if current - 1 >  reserved:
        session["users_games"] = current - 1
    else:
        session["users_games"] = current
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"])

@login_required
def bardgame_reserve(boardgame: Boardgame, reviews: list[Review]) -> str:
    users_boardgames = db.get_user_boardgame_ids(current_user.id)
    users_has_boardgames = boardgame.id in users_boardgames
    today, next_day, next_month = get_dates()
    
    # TODO reservation logick

    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, users_has_boardgames=users_has_boardgames, photo=photo, today=today, next_day=next_day, next_month=next_month)

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
    boardgame_categories = db.get_boardgame_categories()
    if request.method == "POST":
        match request.form["target"]:
            case "confirm":
                boardgame = Boardgame.from_form(request.form)
                if "users_games" in session:
                    db.insert_boardgame(boardgame, session.pop("users_games"))
                else:
                    db.insert_boardgame(boardgame)
            case "plus":
                return add_boardgame_plus()
            case "minus":
                return add_boardgame_minus()
            case "photo":
                return add_boargame_photo()
    
        return redirect("/")

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
    boardgame = Boardgame.from_form(request.form)
    if "users_games" in session:
        db.update_boardgame(boardgame, session.pop("users_games"))
    else:
        db.update_boardgame(boardgame)
    return redirect("/")

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
    return render_template("boardgame.html", boardgame=boardgame, boardgame_categories=boardgame_categories, n=session["users_games"])

@login_required
def add_boardgame_minus() -> str:
    boardgame = db.get_boardgame_by_name(request.form["boardgame_name"])
    boardgame.update(request.form)
    session["users_games"] = max(1, session.get("users_games", 1) - 1)
    boardgame_categories = db.get_boardgame_categories()
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])

def add_boargame_photo() -> str:
    photo = request.files["photo"]
    db.add_boargame_photo_by_boardgmae_name(request.form["name"], photo.filename, photo.read(), photo.mimetype)
    boardgame_categories = db.get_boardgame_categories()
    boardgame = db.get_boardgame_by_name(request.form["name"])
    photo = db.get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame.id, boardgame.number_of_photos - 1)
    return render_template("boardgame.html", add_boardgame=True, boardgame=boardgame, boardgame_categories=boardgame_categories, photo=photo)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)