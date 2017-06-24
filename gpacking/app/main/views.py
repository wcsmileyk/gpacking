from flask import render_template, session, redirect, url_for
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/inventory')
def inventory():
    return render_template('inventory.html')


@main.route('/register')
def register():
    return render_template('register.html')
