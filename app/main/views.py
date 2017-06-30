from flask import render_template, session, redirect, url_for, flash, request, jsonify
from . import main
from ..models import User, Closet, Activity, Category, Type, Item
from flask_login import login_required, current_user
from .forms import CreatePackingList, UpdateCloset
from app import db


@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/home/<username>')
@login_required
def home(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/home.html', user=user)


@main.route('/closet/<username>', methods=['GET', 'POST'])
@login_required
def closet(username):
    user = User.query.filter_by(username=username).first()
    form = UpdateCloset()
    categories = Category.query.order_by('name')
    form.category.choices = [(c.id, c.name) for c in categories]
    form.type.choices = [(t.id, t.name) for t in Type.query.order_by('name')]
    if form.validate_on_submit():
        item = Item(
            name=form.name.data,
            cat_id=form.category.data,
            type_id=form.type.data,
            weight=form.weight.data
        )
        db.session.add(item)
        db.session.commit()
        user.closet.items.append(item)
        db.session.commit()
    return render_template('user/closet.html', user=user, form=form, categories=categories)


@main.route('/friends/<username>')
@login_required
def friends(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/friends.html', user=user)


@main.route('/groups/<username>')
@login_required
def groups(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/groups.html', user=user)


@main.route('/messages/<username>')
@login_required
def messages(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/messages.html', user=user)


@main.route('/packing_lists/<username>')
@login_required
def packing_lists(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/packing_list.html', user=user)


@main.route('/add_inventory/<username>', methods=['GET', 'POST'])
@login_required
def add_packing_list(username):
    user = User.query.filter_by(username=username).first()
    form = CreateInventory()
    form.activity.choices = [(a.id, a.name) for a in Activity.query.order_by('name')]
    if form.validate_on_submit():
        inventory = Closet(
            name=form.name.data,
            user_id=user.id,
            primary=form.primary.data,
            activity_id=form.activity.data
        )
        db.session.add(inventory)
        db.session.commit()
        flash('%s Added to inventories' % inventory.name)
        return redirect(url_for('main.update_closet', username=user.username, inventory=inventory.name))
    return render_template('user/add_packing_list.html', user=user, form=form)


@main.route('/create_opts')
def create_opts():
    cat = request.args.get('a', type=int)
    types = [name for name in Type.query.filter_by(cat_id=cat).with_entities(Type.id, Type.name)]
    return jsonify(result=types)


@main.route('/delete_inv/<inv_id>')
def delete_inv(inv_id):
    inventory = Closet.query.get(int(inv_id))
    db.session.delete(inventory)
    db.session.commit()
    return redirect(url_for('main.profile', username=current_user.username))

