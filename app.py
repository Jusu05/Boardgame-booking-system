from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
import os, bcrypt

from db import insert_user, insert_boardgame, get_user_by_id, get_user_by_username, get_all_boardgames, get_boardgame_by_name, get_all_boardgames_by_search_word, update_boardgame
from datatypes import User, Boardgame

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
    username, password = get_user_by_id(user_id)
    return User(user_id, username, password)

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

        if user and bcrypt.checkpw(request.form["password"].encode("utf-8"), user[2]):
            login_user(User(user[0], user[1], user[2]))
            return redirect("/")
        else:
            flash("Väärä salasana tai käyttäjätunnus")

    return render_template("login.html", login_screen=True)

@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
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

@app.route("/boardgame/<boardgame_name>", methods=["GET", "POST", "PUT"])
def boardgame(boardgame_name: str):
    boardgame = get_boardgame_by_name(boardgame_name)
    if boardgame:
        if request.method == "POST":
            try:
                boardgame = Boardgame.from_form(request.form)
            except KeyError:
                return render_template("add_boardgame.html", boardgame=boardgame)
            update_boardgame(boardgame)

        return render_template("boardgame.html", boardgame=boardgame)

@app.route("/add_boardgame", methods=["GET", "POST"])
@login_required
def add_boardgame():
    if request.method == "POST":
        boardgame: Boardgame = Boardgame.from_form(request.form)
        insert_boardgame(boardgame)
    return render_template("add_boardgame.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)