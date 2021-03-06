from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user

from .login import LoginForm, SignUpForm
from .models import Poll, Choice, Vote, User
from .poll_app import db, app


@app.route('/')
def home_page():
    return render_template('homepage.html')


@app.route('/poll/<int:poll_id>')
def poll_page(poll_id):
    poll = Poll.query.get(poll_id)
    choices = Choice.query.filter_by(poll_id=poll_id).order_by(Choice.id.asc()).all()
    return render_template('poll.html', poll_id=poll_id, poll=poll, choices=choices)


@app.route('/poll/<int:poll_id>/', methods=['POST'])
def create_vote(poll_id):
    choice_id = request.form['choice']
    user_id = request.form['user']
    # update choice votes and save to database
    choice = Choice.query.get(choice_id)
    choice.votes += 1
    db.session.commit()
    # create new vote
    vote = Vote(choice_id=choice_id, user_id=user_id)
    db.session.add(vote)
    db.session.commit()
    return redirect(url_for('poll_page', poll_id=poll_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        login_user(user)
        origin_url = request.args.get('origin')
        flash('Logged in successfully.')
        return redirect(origin_url or url_for('home_page'))

    if form.is_submitted():
        flash('Login or password incorrect.')

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

    if form.validate_on_submit():
        user = User(
            name=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        origin_url = request.args.get('origin')
        login_user(user)
        flash('Your new account has been created.')
        return redirect(origin_url or url_for('home_page'))

    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))
