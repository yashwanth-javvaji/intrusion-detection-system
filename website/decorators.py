from flask import redirect, url_for, flash, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first", category='error')
            return redirect(url_for('views.index'))
    return decorated_function