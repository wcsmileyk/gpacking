from flask import render_template, redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import User, Closet
from .forms import LoginForm, RegisterForm
from .. import db
# from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.home', username=user.username))
        flash('Invalid Username or Password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        closet = Closet(user_id=user.id)
        db.session.add(closet)
        user.closet = closet
        db.session.commit()
        # TODO: Fix email confirmation system. Low priority
        # token = user.confirm_token()
        # send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('Thanks for registering. You can now login')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
