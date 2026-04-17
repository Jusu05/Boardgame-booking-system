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
    get_users_game_count_by_boardgame_id, get_user_boardgame_ids, get_user_boardgames, get_boardgame_photo_by_boardgame_name_and_photo_id, \
    upsert_review, get_reviews_by_boardgame_id, get_user_review_stats
from security import CSRFProtect, LoginManager, login_user, login_required, logout_user, current_user
from env_parser import load_dotenv
from datatypes import Review, Boardgame

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
def load_user(user_id: int):
    return get_user_by_id(user_id)

@app.context_processor
def inject_flags():
    flags = dict()
    if current_user.is_authenticated:
        flags["username"] = current_user.username
    return flags

@app.route("/", methods=["GET", "POST"])
def index():
    boardgames = get_all_boardgames()

    if request.method == "POST":
        boardgames = get_all_boardgames_by_search_word(request.form["search_word"])

    if boardgames:
        return render_template("index.html", boardgames=boardgames)
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
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
def create_user():
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
def avatar(username: str):
    avatar = get_avatar_by_username(username)
    return Response(avatar.bytes, mimetype=avatar.file_type)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/user", methods=["GET"])
@login_required
def user():
    boardgames = get_user_boardgames(current_user.id)
    review_stats = get_user_review_stats()
    return render_template("user.html", user=current_user, boardgames=boardgames, review_stats=review_stats)

def load_boardgame_context(name: str):
    boardgame = get_boardgame_by_name(name)
    if not boardgame:
        return None
    return {
        "boardgame": boardgame,
        "reviews": get_reviews_by_boardgame_id(boardgame.id),
        "boardgame_categories": get_boardgame_categories(),
    }

@app.route("/boardgame/<boardgame_name>", methods=["GET", "POST"])
def boardgame(boardgame_name: str):
    context = load_boardgame_context(boardgame_name)
    if not context:
        return redirect("/")

    if current_user.is_authenticated:
        users_boardgames = get_user_boardgame_ids()
    else:
        users_boardgames = None

    photo = get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, 0)

    return render_template("boardgame.html", boardgame=context["boardgame"], reviews=context["reviews"], users_boardgames=users_boardgames, photo=photo)

@app.route("/boardgame/<boardgame_name>/edit", methods=["GET", "POST"])
@login_required
def boardgame_edit(boardgame_name: str):
    context = load_boardgame_context(boardgame_name)
    if not context:
        return redirect("/")
    user_boardgames, _ = get_users_game_count_by_boardgame_id(context["boardgame"].id)
    return render_template("boardgame.html", boardgame=context["boardgame"], reviews=context["reviews"], boardgame_categories=context, n=user_boardgames)

@app.route("/boardgame/<boardgame_name>/update", methods=["POST"])
@login_required
def boardgame_update(boardgame_name: str):
    context = load_boardgame_context(boardgame_name)
    if not context:
        return redirect("/")
    boardgame = Boardgame.from_form(request.form)
    if "users_games" in session:
        update_boardgame(boardgame, session["users_games"])
        del session["users_games"]
    else:
        update_boardgame(boardgame)
    return redirect(f"/boardgame/{boardgame_name}")

@app.route("/boardgame/<boardgame_name>/review", methods=["POST"])
@login_required
def boardgame_review(boardgame_name: str):
    context = load_boardgame_context(boardgame_name)
    if not context:
        return redirect("/")
    review = Review.from_form(request.form)
    upsert_review(context["boardgame"].id, review)
    return redirect(f"/boardgame/{boardgame_name}")

@app.route("/boardgame/<boardgame_name>/plus", methods=["POST"])
@login_required
def boardgame_plus(boardgame_name: str):
    context = load_boardgame_context(boardgame_name)
    if not context:
        return redirect("/")
    user_games, _ = get_users_game_count_by_boardgame_id(context["boardgame"].id)
    session["users_games"] = session.get("users_games", user_games) + 1
    return render_template("boardgame.html", boardgame=context["boardgame"], reviews=context["reviews"], boardgame_categories=context["boardgame_categories"], n=session["users_games"])

@app.route("/boardgame/<boardgame_name>/minus", methods=["POST"])
@login_required
def boardgame_minus(boardgame_name: str):
    context = load_boardgame_context(boardgame_name)
    if not context:
        return redirect("/")
    user_games, reserved = get_users_game_count_by_boardgame_id(context["boardgame"].id)
    current = session.get("users_games", user_games)
    if current - 1 >  reserved:
        session["users_games"] = current - 1
    else:
        session["users_games"] = current
    return render_template("boardgame.html", boardgame=context["boardgame"], reviews=context["reviews"], boardgame_categories=context["boardgame_categories"], n=session["users_games"])

@app.route("/boardgame/<boardgame_name>/photo/<int:id>", methods=["GET"])
def boardgame_photo(boardgame_name: str, id: int):
    photo = get_boardgame_photo_by_boardgame_name_and_photo_id(boardgame_name, id)
    return Response(photo.bytes, mimetype=photo.file_type)

@app.route("/add_boardgame", methods=["GET", "POST"])
@login_required
def add_boardgame():
    boardgame_categories = get_boardgame_categories()
    if request.method == "POST":
        if "cancel" in request.form:
            return redirect("/")
        boardgame = Boardgame.from_form(request.form)
        if "users_games" in session:
            insert_boardgame(boardgame, session.pop("users_games"))
        else:
            insert_boardgame(boardgame)
        return redirect("/")
    n = session.get("users_games", 1)
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=n)

@app.route("/add_boardgame/plus", methods=["POST"])
@login_required
def add_boardgame_plus():
    session["users_games"] = session.get("users_games", 1) + 1
    boardgame_categories = get_boardgame_categories()
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])

@app.route("/add_boardgame/minus", methods=["POST"])
@login_required
def add_boardgame_minus():
    session["users_games"] = max(1, session.get("users_games", 1) - 1)
    boardgame_categories = get_boardgame_categories()
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)