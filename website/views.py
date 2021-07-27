import os
from flask import Blueprint, render_template, request, redirect, flash, session
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .decorators import login_required

import pickle
from sklearn.preprocessing import MinMaxScaler

models_path = os.path.join(os.path.dirname(__file__), 'ml_models')
nb = pickle.load(open(models_path + '/nb.pickle', 'rb'))
dt = pickle.load(open(models_path + '/dt.pickle', 'rb'))
rf = pickle.load(open(models_path + '/rf.pickle', 'rb'))
svm = pickle.load(open(models_path + '/svm.pickle', 'rb'))
lr = pickle.load(open(models_path + '/lr.pickle', 'rb'))
gb = pickle.load(open(models_path + '/gb.pickle', 'rb'))


def getPrediction(test):
    sc = MinMaxScaler()
    X = sc.fit_transform(test)
    message = {}
    message["GAUSSIAN NAIVE BAYES"] = nb.predict(X)[0]
    message["DECISION TREE"] = dt.predict(X)[0]
    message["RANDOM FOREST"] = rf.predict(X)[0]
    message["SUPPORT VECTOR MACHINE"] = svm.predict(X)[0]
    message["LOGISTIC REGRESSION"] = lr.predict(X)[0]
    message["GRADIENT BOOSTING CLASSIFIER"] = gb.predict(X)[0]
    return message


views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@views.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        test = []
        for key, item in request.form.items():
            test.append(item)
        test = [test]
        message = getPrediction(test)
        return render_template('result.html', message=message)
    return render_template('predict.html')


@views.route('/profile', methods=['GET'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@views.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('edit_name')
        email = request.form.get('edit_email')

        existingUser = User.query.filter_by(email=email).first()
        if existingUser and session['user_email'] != existingUser.email:
            flash("Email already exists!", category="error")
        else:
            user = User.query.get(session['user_id'])
            if user:
                user.name = name
                user.email = email
                db.session.commit()
                session['user_name'] = user.name
                session['user_email'] = user.email
            else:
                flash("Profile not found!", category="error")

    return redirect(request.referrer)


@views.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
            
        user = User.query.get(session['user_id'])
        if user:
            if check_password_hash(user.password, old_password):
                if check_password_hash(user.password, new_password):
                    flash("New password cannot be the same as old password", category="error")
                else:
                    user.password = generate_password_hash(new_password, method='sha256')
                    db.session.commit()
                    flash("Password updated successfully!", category="success")
            else:
                flash("Incorrect password!", category="error")
        else:
            flash("Profile not found!", category="error")

    return redirect(request.referrer)