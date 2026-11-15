from functools import wraps

from flask import session, redirect, url_for, flash


def current_user_id():
    return session["user_id"]


def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get("user_id"):
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if session.get("user_role") not in roles:
                flash("You do not have access to that page.", "error")
                return redirect(url_for("main.home"))
            return f(*args, **kwargs)
        return decorated
    return wrapper
