from flask import render_template, session, redirect, url_for, flash, request, jsonify
from . import main
from ..models import User, Closet, Activity, Category, Type, Item, Group, PackingList
from flask_login import login_required, current_user
from .forms import CreatePackingList, AddItem, CreateGroup, FriendRequest
from app import db




# Index / Main route
@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


# User Pages
@main.route('/home/<username>')
@login_required
def home(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/home.html', user=user)


@main.route('/closet/<username>', methods=['GET', 'POST'])
@login_required
def closet(username):
    user = User.query.filter_by(username=username).first()
    form = AddItem()
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


@main.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    user = User.query.filter_by(username=username).first()
    form = FriendRequest()
    if form.validate_on_submit():
        if form.user_email.data:
            friend = User.query.filter_by(email=form.user_email.data).first()
        elif form.username.data:
            friend = User.query.filter_by(username=form.username.data).first()
        user.request_friend(friend)
        db.session.commit()
    user_friends = user.my_friends()
    return render_template('user/friends.html', user=user, friends=user_friends, form=form)


@main.route('/messages/<username>')
@login_required
def messages(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/messages.html', user=user)


# Group pages
@main.route('/groups/<username>', methods=['GET', 'POST'])
@login_required
def groups(username):
    user = User.query.filter_by(username=username).first()
    form = CreateGroup()
    user_friends = [User.query.filter_by(id=friend.requested_id).first() for friend in user.friend_requested.all()]
    form.activity.choices = [(a.id, a.name) for a in Activity.query.order_by('name')]
    form.friends.choices = [(f.id, f.username) for f in user_friends if user.friend_status(f) == 1]
    friend_count = len(form.friends.choices)
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            activity_id=form.activity.data
        )
        db.session.add(group)
        db.session.commit()
        user.group_packing_list.append(group)
        for friend in form.friends.data:
            f = User.query.get(friend)
            f.group_packing_list.append(group)
        db.session.commit()
    user_groups = user.group_packing_list.all()
    return render_template('user/groups.html', user=user, groups=user_groups, form=form, row_count=friend_count)


@main.route('/update_group/<groupname>', methods=['GET', 'POST'])
@login_required
def update_group(groupname):
    group = Group.query.filter_by(name=groupname)
    return render_template('user/update_group.html', user=user, form=form, group=group)


# Packing Lists
@main.route('/packing_lists/<username>', methods=['GET', 'POST'])
@login_required
def packing_lists(username):
    user = User.query.filter_by(username=username).first()
    form = CreatePackingList()
    form.activity.choices = [(a.id, a.name) for a in Activity.query.order_by('name')]
    form.items.choices = [(i.id, i.name) for i in user.closet.items.order_by('cat_id').order_by('type_id').all()]
    if form.validate_on_submit():
        pl = PackingList(
            name=form.name.data,
            activity_id=form.activity.data,
            user_id=user.id
        )
        db.session.add(pl)
        db.session.commit()
        for item in form.items.data:
            pl.items.append(Item.query.get(item))
        db.session.commit()
    pls = user.packing_lists
    return render_template('user/packing_list.html', user=user, packing_lists=pls, form=form)


@main.route('/update_packing_list/<packing_list>', methods=['GET', 'POST'])
@login_required
def update_packing_list(packing_list):
    user = User.query.filter_by(username=current_user.username).first()
    pl = PackingList.query.filter_by(name=packing_list).first()
    form = AddItem()
    categories = Category.query.order_by('name')
    form.category.choices = [(c.id, c.name) for c in categories]
    form.type.choices = [(t.id, t.name) for t in Type.query.order_by('name')]
    if form.validate_on_submit():
        item = Item(
            name=form.name.data,
            cat_id=form.category.data,
            type_id=form.category.data,
            weight=form.weight.data
        )
        db.session.add(item)
        db.session.commit()
        pl.items.append(item)
        user.closet.items.append(item)
        db.session.commit()
    return render_template('user/update_packing_list.html', user=user, form=form, pl=pl, categories=categories)



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

