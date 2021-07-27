from flask import Blueprint, request, redirect, url_for, flash, session
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .decorators import login_required


auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        name = request.form.get('register_name')
        email = request.form.get('register_email')
        password = request.form.get('register_password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists!", category="error")
        else:
            newUser = User(
                name=name,
                email=email,
                password=generate_password_hash(password, method='sha256')
            )

            db.session.add(newUser)
            db.session.commit()

            session['logged_in'] = True
            session['user_id'] = newUser.id
            session['user_name'] = newUser.name
            session['user_email'] = newUser.email

            flash("Account created successfully!", category="success")

        return redirect(request.referrer)


@auth.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        email = request.form.get('login_email')
        password = request.form.get('login_password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                session['logged_in'] = True
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                flash("Logged-in successfully!", category="success")
            else:
                session['num_failed_logins'] = session.get('num_failed_logins', 0) + 1 
                flash("Incorrect Password", category="error")
        else:
            session['num_failed_logins'] = session.get('num_failed_logins', 0) + 1
            flash("Email does not exist", category="error")

        return redirect(request.referrer)


@auth.route('/logout')
@login_required
def logout():
    if 'logged_in' in session:  
        session.pop('logged_in', None)
    if 'user_id' in session:
        session.pop('user_id', None)
    if 'user_name' in session:  
        session.pop('user_name', None)
    if 'user_email' in session:  
        session.pop('user_email', None)
    return redirect(request.referrer)