from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

from db import insert_user, get_user_by_id, get_user_by_username, \
    insert_boardgame, update_boardgame, get_all_boardgames, get_boardgame_by_name, get_all_boardgames_by_search_word, get_boardgame_categories, \
    upsert_review, get_reviews_by_boardgame_id, \
    get_users_game_count_by_boardgame_id
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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/boardgame/<boardgame_name>", methods=["GET", "POST"])
@app.route("/boardgame/<boardgame_name>/edit", methods=["GET", "POST"])
@app.route("/boardgame/<boardgame_name>/update", methods=["GET", "POST"])
@app.route("/boardgame/<boardgame_name>/review", methods=["GET", "POST"])
@app.route("/boardgame/<boardgame_name>/plus", methods=["GET", "POST"])
@app.route("/boardgame/<boardgame_name>/minus", methods=["GET", "POST"])
def boardgame(boardgame_name: str):
    boardgame = get_boardgame_by_name(boardgame_name)
    if boardgame:
        reviews = get_reviews_by_boardgame_id(boardgame.id)
        if request.method == "POST":
            if current_user.is_authenticated:
                if request.path.endswith("edit"):
                    user_boardgames, _ = get_users_game_count_by_boardgame_id(boardgame.id)
                    boardgame_categories = get_boardgame_categories()
                    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=user_boardgames)
                elif request.path.endswith("update"):
                    user_boardgames, _ = get_users_game_count_by_boardgame_id(boardgame.id)
                    boardgame = Boardgame.from_form(request.form)
                    if "users_games" in session and user_boardgames != session["users_games"]:
                        update_boardgame(boardgame, session["users_games"])
                    else:
                        update_boardgame(boardgame)
                    del session["users_games"]
                elif request.path.endswith("review"):
                    review = Review.from_form(request.form)
                    upsert_review(boardgame.id, review)
                elif request.path.endswith("minus"):
                    boardgame_categories = get_boardgame_categories()
                    user_boardgames, reserved_boardgames = get_users_game_count_by_boardgame_id(boardgame.id)
                    if "users_games" in session and user_boardgames - 1 < user_boardgames - reserved_boardgames:
                        session["users_games"] -= 1
                    else:
                        if user_boardgames - 1 < user_boardgames - reserved_boardgames:
                            session["users_games"] = user_boardgames - 1
                        else:
                            session["users_games"] = user_boardgames
                    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"])
                elif request.path.endswith("plus"):
                    boardgame_categories = get_boardgame_categories()
                    user_boardgames, _ = get_users_game_count_by_boardgame_id(boardgame.id)
                    if "users_games" in session:
                        session["users_games"] += 1
                    else:
                        session["users_games"] = user_boardgames + 1
                    return render_template("boardgame.html", boardgame=boardgame, reviews=reviews, boardgame_categories=boardgame_categories, n=session["users_games"])

            else:
                pass

        return render_template("boardgame.html", boardgame=boardgame, reviews=reviews)
    return redirect("/")

@app.route("/add_boardgame", methods=["GET", "POST"])
@app.route("/add_boardgame/plus", methods=["GET", "POST"])
@app.route("/add_boardgame/minus", methods=["GET", "POST"])
@login_required
def add_boardgame():
    boardgame_categories = get_boardgame_categories()
    if request.method == "POST":
        if "cancel" in request.form:
            return redirect("/")
        if request.path.endswith("minus"):
            if "users_games" in session and session["users_games"] < 1:
                session["users_games"] -= 1
            else:
                session["users_games"] = 1
            return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])
        elif request.path.endswith("plus"):
            if "users_games" in session:
                session["users_games"] += 1
            else:
                session["users_games"] = 2
            return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])

        boardgame: Boardgame = Boardgame.from_form(request.form)
        if "users_games" in session:
            insert_boardgame(boardgame, session["users_games"])
            del session["users_games"]
        else:
            insert_boardgame(boardgame)

        return redirect("/")
    if "users_games" in session:
        return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=session["users_games"])
    return render_template("boardgame.html", boardgame_categories=boardgame_categories, n=1)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)