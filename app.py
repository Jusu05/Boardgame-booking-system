from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import CSRFProtect
import os, bcrypt

app = Flask(__name__)
app.config.from_mapping(
    SESSION_COOKIE_SAMESITE="Strict",
    SECRET_KEY=os.getenv("SECRET_KEY"),
)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id: int, username: str, password: str):
        super().__init__()
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    pass

@app.route("/")
def index():
    pass

@app.route("/login")
def login():
    pass

@app.route("/logout")
@login_required
def logout():
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)