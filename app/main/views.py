from flask import render_template, session, redirect, url_for, flash, request, jsonify
from . import main
from ..models import User, Inventory, Activity, Category, Type, Item
from flask_login import login_required, current_user
from .forms import CreateInventory, UpdateInventory
from app import db


@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)


@main.route('/add_inventory/<username>', methods=['GET', 'POST'])
@login_required
def add_inventory(username):
    user = User.query.filter_by(username=username).first()
    form = CreateInventory()
    form.activity.choices = [(a.id, a.name) for a in Activity.query.order_by('name')]
    if form.validate_on_submit():
        inventory = Inventory(
            name=form.name.data,
            user_id=user.id,
            primary=form.primary.data,
            activity_id=form.activity.data
        )
        db.session.add(inventory)
        db.session.commit()
        flash('%s Added to inventories' % inventory.name)
        return redirect(url_for('main.update_inventory', username=user.username, inventory=inventory.name))
    return render_template('add_inventory.html', user=user, form=form)


@main.route('/update_inventory/<username>/<inventory>', methods=['GET', 'POST'])
@login_required
def update_inventory(username, inventory):
    user = User.query.filter_by(username=username).first()
    inventory = Inventory.query.filter_by(name=inventory, user_id=user.id).first()
    form = UpdateInventory()
    categories = Category.query.order_by('name')
    form.category.choices = [(c.id, c.name) for c in categories]
    form.type.choices = [(t.id, t.name) for t in Type.query.order_by('name')]
    if form.validate_on_submit():
        print(form.category.data)
        item = Item(
            name=form.name.data,
            cat_id=form.category.data,
            type_id=form.type.data,
            weight=form.weight.data
        )
        db.session.add(item)
        db.session.commit()
        inventory.items.append(item)
        db.session.add(inventory)
        db.session.commit()
    return render_template('update_inv.html', user=user, inventory=inventory, form=form, categories=categories)


@main.route('/create_opts')
def create_opts():
    cat = request.args.get('a', type=int)
    types = [name for name in Type.query.filter_by(cat_id=cat).with_entities(Type.id, Type.name)]
    return jsonify(result=types)


@main.route('/delete_inv/<inv_id>')
def delete_inv(inv_id):
    inventory = Inventory.query.get(int(inv_id))
    db.session.delete(inventory)
    db.session.commit()
    return redirect(url_for('main.profile', username=current_user.username))

