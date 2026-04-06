import base64, hmac, hashlib, os, time
from functools import wraps
from flask import Flask, session, request, abort, g


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
