import base64, hmac, hashlib, os, time
from functools import wraps
from flask import Flask, abort, redirect, url_for, g, current_app, session, request


class UserMixin:
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self):
        return str(self.id)


class AnonymousUser:
    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def is_active(self) -> bool:
        return False

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self):
        return None


class LoginManager:
    def __init__(self, app: Flask = None):
        self._user_loader_callback = None
        self._unauthorized_callback = None
        self._app = app
        self._login_view: str | None = None
        self.session_id = "_user_id"
        self.remember_cookie = "remember_token"

        app.extensions["login_manager"] = self
        app.before_request(self._load_user_from_session)

        app.jinja_env.globals["current_user"] = self._get_current_user

    def user_loader(self, callback):
        self._user_loader_callback = callback
        return callback

    def unauthorized_handler(self, callback):
        self._unauthorized_callback = callback
        return callback

    @property
    def login_view(self) -> str | None:
        return self._login_view

    @login_view.setter
    def login_view(self, endpoint: str) -> None:
        self._login_view = endpoint

    def _load_user_from_session(self) -> None:
        user_id = session.get(self.session_id)

        if user_id and self._user_loader_callback:
            user = self._user_loader_callback(user_id)
            if user and user.is_active:
                g._current_user = user
                return

        g._current_user = AnonymousUser()

    def _get_current_user(self):
        """Returns the user bound to the current request context."""
        return getattr(g, "_current_user", AnonymousUser())

    def _unauthorized(self):
        if self._unauthorized_callback:
            return self._unauthorized_callback()
        if self._login_view:
            return redirect(url_for(self._login_view))
        abort(401)


def _get_login_manager() -> LoginManager:
    try:
        return current_app.extensions["login_manager"]
    except KeyError:
        raise RuntimeError(
            "LoginManager not initialised. Call LoginManager(app) or "
            "login_manager.init_app(app) before using auth helpers."
        )


def login_user(user, remember: bool = False) -> bool:
    if not user.is_active:
        return False

    login_manager = _get_login_manager()
    session[login_manager.session_id] = user.get_id()
    session.permanent = remember
    session.modified = True
    g._current_user = user
    return True


def logout_user():
    login_manager = _get_login_manager()
    session.pop(login_manager.session_id)
    session.modified = True
    g._current_user = AnonymousUser()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        login_manager = _get_login_manager()
        user = login_manager._get_current_user()
        if not user.is_authenticated:
            return login_manager._unauthorized()
        return view(*args, **kwargs)
    return wrapped


class CurrentUser:
    def __class_getitem__(cls, _):
        return cls

    def __getattr__(self, name):
        return getattr(_get_login_manager()._get_current_user(), name)

    def __bool__(self):
        return _get_login_manager()._get_current_user().is_authenticated


current_user = CurrentUser()


class CSRFProtect:
    def __init__(self, app: Flask, max_age: int = 3600):
        self._app = app
        self._secret = app.secret_key
        self._exempt_endpoints: set[str] = set()

        self.SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
        self.max_age = max_age

        if not self._secret:
            raise RuntimeError(
                "CSRFProtect requires app.secret_key to be set."
            )

        app.extensions["csrf"] = self
        app.jinja_env.globals["csrf_token"] = self.csrf_token
        app.before_request(self._csrf_protect)

    def _generate_token(self, session_id: str) -> str:
        noise = os.urandom(16).hex()
        timestamp = str(int(time.time()))
        message = f"{session_id}:{noise}:{timestamp}"
        signature = hmac.new(
            self._secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        base_64 = base64.b64encode(bytes(f"{message}.{signature}", "utf-8"))
        return base_64.decode("utf-8")

    def _validate_token(self, token: str, session_id: str) -> bool:
        try:
            token = base64.b64decode(token).decode("utf-8")
            message, received_sig = token.split(".", 1)
            parts = message.split(":")
            if len(parts) != 3:
                return False

            token_session_id, _, timestamp = parts

            if token_session_id != session_id:
                return False

            if int(time.time()) - int(timestamp) > self.max_age:
                return False

            expected_sig = hmac.new(
                self._secret.encode(), message.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(received_sig, expected_sig)
        except Exception:
            return False

    def csrf_token(self) -> str:
        if not hasattr(g, "_csrf_token"):
            if "session_id" not in session:
                session["session_id"] = os.urandom(24).hex()
            g._csrf_token = self._generate_token(session["session_id"])
        return g._csrf_token

    def _csrf_protect(self) -> None:
        if request.method in self.SAFE_METHODS:
            return

        if request.endpoint in self._exempt_endpoints:
            return

        session_id = session.get("session_id")
        if not session_id:
            abort(403)

        token = request.form.get("csrf_token")

        if not token or not self._validate_token(token, session_id):
            abort(403)

    def exempt(self, view_func):
        self._exempt_endpoints.add(view_func.__name__)

        @wraps(view_func)
        def wrapped(*args, **kwargs):
            return view_func(*args, **kwargs)

        return wrapped
