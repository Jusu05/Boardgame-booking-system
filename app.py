from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session, Response, abort
from werkzeug.security import generate_password_hash, check_password_hash
import os

try:
    from PIL import Image
    PILLOW_IMPORTED = True
except ImportError:
    import imghdr
    PILLOW_IMPORTED = False

from db import insert_user, get_user_by_id, get_user_by_username, get_avatar_by_username, \
    insert_boardgame, update_boardgame, get_all_boardgames, get_boardgame_by_name, get_all_boardgames_by_search_word, get_boardgame_categories, \
    get_users_game_count_by_boardgame_id, get_user_boardgame_ids, get_user_boardgames, get_boardgame_photo_by_boardgame_name_and_photo_id, delete_users_boardgames_by_boardgame_id, set_user_boardgames_to_zero,\
    upsert_review, get_reviews_by_boardgame_id, get_user_review_stats
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
    return get_user_by_id(user_id)

@app.context_processor
def inject_flags() -> dict:
    flags = dict()
    if current_user.is_authenticated:
        flags["username"] = current_user.username
    return flags

@app.route("/", methods=["GET", "POST"])
def index() -> str:
    boardgames = get_all_boardgames()

    if request.method == "POST":
        boardgames = get_all_boardgames_by_search_word(request.form["search_word"])

    if boardgames:
        return render_template("index.html", boardgames=boardgames)
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login()-> Response | str:
    if request.method == "POST":
        username = request.form["username"]
        user = get_user_by_username(username)

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
            insert_user(username, password)
        except Exception:
            flash("Käyttäjää ei voi luoda")
        return redirect("/")
    return render_template("login.html", login_screen=False)

@app.route("/user/<username>/avatar", methods=["GET"])
def avatar(username: str) -> Response:
    avatar = get_avatar_by_username(username)
    return Response(avatar.bytes, mimetype=avatar.file_type)

@app.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    return redirect("/")

@app.route("/user", methods=["GET"])
@login_required
def user() -> str:
    boardgames = get_user_boardgames(current_user.id)
    review_stats = get_user_review_stats()
    return render_template("user.html", user=current_user, boardgames=boardgames, review_stats=review_stats)

@app.route("/boardgame/<boardgame_name>", methods=["GET", "POST"])
def boardgame(boardgame_name: str) -> Response | str:
    boardgame = get_boardgame_by_name(boardgame_name)
    photo = get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, 0)

    if not boardgame:
        return redirect("/")
    
    reviews = get_reviews_by_boardgame_id(boardgame.id)

    if request.method == "POST":
        match request.form["target"]:
            case "cancel":
                pass
            case "confirm":
                return boardgame_update(boardgame_name)
            case "review":
                return boardgame_review(boardgame_name)
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
                return boardgame_minus()
            case "plus":
                return boardgame_plus()
            case _:
                pass

    if current_user.is_authenticated:
        users_boardgames = get_user_boardgame_ids(current_user.id)
        users_has_boardgames = boardgame.id in users_boardgames
    else:
        users_has_boardgames = False

    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, users_has_boardgames=users_has_boardgames, photo=photo)

@login_required
def boardgame_edit(boardgame: Boardgame, reviews: list[Review]) -> str:
    boardgame_categories = get_boardgame_categories()
    user_boardgames, _ = get_users_game_count_by_boardgame_id(boardgame.id)    
    photo = Photo(None, 0, None, None)

    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=user_boardgames, photo=photo)

@login_required
def boardgame_delete(boardgame_name: str, reviews: list[Review]) -> str:
    user_boardgames, reserved_user_boardgames = get_users_game_count_by_boardgame_id(boardgame.id)
    photo = get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, 0)
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, n=user_boardgames, delete=True, reserved_user_boardgames=reserved_user_boardgames, photo=photo)

@login_required
def boardgame_delete_confirm(boardgame_name: str) -> Response:
    boardgame = get_boardgame_by_name(boardgame_name)
    user_boardgames, reserved_user_boardgames = get_users_game_count_by_boardgame_id(boardgame.id)
    if reserved_user_boardgames > 0:
        set_user_boardgames_to_zero(current_user.id)
        return redirect(f"/boardgame/{boardgame.name}")
    delete_users_boardgames_by_boardgame_id(boardgame.id)
    if boardgame.free + boardgame.reserved - user_boardgames - reserved_user_boardgames > 0:
        return redirect(f"/boardgame/{boardgame.name}")
    return redirect("/")

@login_required
def boardgame_update(boardgame_name: str) -> Response:
    boardgame = Boardgame.from_form(request.form)
    if "users_games" in session:
        update_boardgame(boardgame, session["users_games"])
        del session["users_games"]
    else:
        update_boardgame(boardgame)
    return redirect(f"/boardgame/{boardgame_name}")

@login_required
def boardgame_review(boardgame: Boardgame) -> Response:
    review = Review.from_form(request.form)
    upsert_review(boardgame.id, review)
    return redirect(f"/boardgame/{boardgame.name}")

@login_required
def boardgame_plus(boardgame: Boardgame, reviews: list[Review]) -> str:
    boardgame_categories = get_boardgame_categories()
    user_games, _ = get_users_game_count_by_boardgame_id(boardgame.id)
    session["users_games"] = session.get("users_games", user_games) + 1
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"])

@login_required
def boardgame_minus(boardgame: Boardgame, reviews: list[Review]) -> str:
    boardgame_categories = get_boardgame_categories()
    user_games, reserved = get_users_game_count_by_boardgame_id(boardgame.id)
    current = session.get("users_games", user_games)
    if current - 1 >  reserved:
        session["users_games"] = current - 1
    else:
        session["users_games"] = current
    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"])

@app.route("/boardgame/<boardgame_name>/photo/<int:id>", methods=["GET"])
def boardgame_photo(boardgame_name: str, id: int) -> Response:
    photo = get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, id)
    return Response(photo.bytes, mimetype=photo.file_type)

@app.route("/add_boardgame", methods=["GET", "POST"])
@login_required
def add_boardgame() -> Response | str:
    boardgame_categories = get_boardgame_categories()
    if request.method == "POST":
        match request.form["target"]:
            case "confirm":
                boardgame = Boardgame.from_form(request.form)
                if "users_games" in session:
                    insert_boardgame(boardgame, session.pop("users_games"))
                else:
                    insert_boardgame(boardgame)
            case "plus":
                return add_boardgame_plus()
            case "minus":
                return add_boardgame_minus()
    
        return redirect("/")

    n = session.get("users_games", 1)
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=n)

def add_boardgame_plus() -> str:
    session["users_games"] = session.get("users_games", 1) + 1
    boardgame_categories = get_boardgame_categories()
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])

def add_boardgame_minus() -> str:
    session["users_games"] = max(1, session.get("users_games", 1) - 1)
    boardgame_categories = get_boardgame_categories()
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)